import importlib.util
import sys
from pathlib import Path

task_path = Path(__file__).parents[2]


def load_game():
    path = task_path / "src" / "game.py"
    spec = importlib.util.spec_from_file_location("arcade_game", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_ticket_underflow_opens_service_door():
    game = load_game()
    state = game.State()

    assert state.tickets == game.START_TICKETS

    for key in "sssssss" + "d" * 7:
        state, done = game.apply_key(state, key)
        assert not done

    assert (state.x, state.y) == (54, 10)

    for index in range(16):
        state, done = game.apply_key(state, "p")
        assert not done
        if index != 15:
            for key in "adad":
                state, done = game.apply_key(state, key)
                assert not done

    assert state.tickets == game.U64_MASK - 11

    maze_path = "sssss" + "a" * 19 + "s" + "a" * 18 + "s" + "a" * 8 + "ss" + "a" * 5 + "w" + "a"
    for key in maze_path:
        state, done = game.apply_key(state, key)
        assert not done

    assert (state.x, state.y) == (game.FLAG_X, game.FLAG_Y)
    state = game.inspect(state)
    assert "hack4KrakCTF{u64_ticket_jackpot_after_hours}" in state.message


def test_service_door_blocks_without_enough_tickets():
    game = load_game()
    state = game.State(x=4, y=18, tickets=game.DOOR_COST - 1)

    state, done = game.apply_key(state, "a")

    assert not done
    assert (state.x, state.y) == (4, 18)
    assert "wszystkie punkty" in state.message


def test_fire_in_service_maze_removes_points():
    game = load_game()
    state = game.State(x=12, y=19, tickets=game.U64_MASK - 11)

    state, done = game.apply_key(state, "a")

    assert not done
    assert game.map_tile(state.x, state.y) == game.FIRE_TILE
    assert state.tickets == game.U64_MASK - 75
    assert state.tickets < game.DOOR_COST
    assert "Plomien" in state.message


def test_register_and_door_hint_all_points():
    game = load_game()
    state = game.State(x=28, y=14)

    state = game.inspect(state)

    assert "surowy stan" in state.message
    state.x = 3
    state.y = 18
    state = game.inspect(state)
    assert "wszystkie punkty" in state.message


def test_ticket_counter_is_u64_wrapped():
    game = load_game()
    state = game.State(x=34, y=3, tickets=game.U64_MASK - 2)

    state, done = game.apply_key(state, "p")

    assert not done
    assert state.tickets < 100


def test_cabinet_jackpot_and_cooldown_are_visible():
    game = load_game()
    state = game.State(x=34, y=3)

    state, done = game.apply_key(state, "p")
    assert not done
    assert "LOSUJEMY" in state.message
    first_total = state.tickets

    state, done = game.apply_key(state, "p")
    assert not done
    assert state.tickets == first_total + game.COOLDOWN_REWARD
    assert "cooldown" in state.message


def test_broken_bandit_removes_fixed_amount_with_cooldown():
    game = load_game()
    state = game.State(x=54, y=10)

    state, done = game.apply_key(state, "p")
    assert not done
    assert state.tickets == game.START_TICKETS - game.BROKEN_LOSS
    assert f"-{game.BROKEN_LOSS}" in state.message

    state, done = game.apply_key(state, "p")
    assert not done
    assert state.tickets == game.START_TICKETS - game.BROKEN_LOSS
    assert "cooldown" in state.message

    for key in "adad":
        state, done = game.apply_key(state, key)
        assert not done
    state, done = game.apply_key(state, "p")
    assert not done
    assert state.tickets == game.START_TICKETS - 2 * game.BROKEN_LOSS


def test_arrow_escape_codes_do_not_move_player():
    game = load_game()
    state = game.State()

    state, done = game.apply_key(state, "A")

    assert not done
    assert (state.x, state.y) == (game.START_X, game.START_Y)
    assert "WASD ruch" in state.message


def test_start_has_path_to_underflow_edge():
    game = load_game()
    queue = [((game.START_X, game.START_Y), "")]
    seen = {(game.START_X, game.START_Y)}

    while queue:
        (x, y), path = queue.pop(0)
        if (x, y) == (0, 10):
            assert len(path) > 10
            return

        for key, (dx, dy) in {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < game.MAP_W and 0 <= ny < game.MAP_H and (nx, ny) not in seen and game.walkable(nx, ny):
                seen.add((nx, ny))
                queue.append(((nx, ny), path + key))

    raise AssertionError("spawn cannot reach the underflow edge")


def test_left_edge_teleports_back_to_right_side():
    game = load_game()
    state = game.State(x=0, y=10)

    state, done = game.apply_key(state, "a")

    assert not done
    assert state.x == game.RIGHT_TELEPORT_X
    assert state.y == 10
    assert "POS_X=ff" in state.message
    assert "@" in game.render_view(state)


def test_hatch_renders_as_flag_marker():
    game = load_game()

    assert game.screen_tile(game.FLAG_X, game.FLAG_Y, game.State()) == "F"


def test_parallel_sessions_keep_separate_state():
    game = load_game()
    first = game.State(x=54, y=10)
    second = game.State(x=54, y=10)

    first, done = game.apply_key(first, "p")

    assert not done
    assert first.tickets == game.START_TICKETS - game.BROKEN_LOSS
    assert second.tickets == game.START_TICKETS
    assert second.broken_cooldown == 0
