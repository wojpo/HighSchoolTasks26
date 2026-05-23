#!/usr/bin/env python3
from __future__ import annotations

import os
import select
import sys
import termios
import time
import tty
from dataclasses import dataclass
from typing import Any

FLAG = os.environ.get("FLAG", "hack4KrakCTF{u64_ticket_jackpot_after_hours}")

START_X = 47
START_Y = 3
FLAG_X = 2
FLAG_Y = 18
START_TICKETS = 500
MAP_W = 60
MAP_H = 22
RIGHT_TELEPORT_X = MAP_W - 3
U64_MASK = (1 << 64) - 1
DOOR_COST = U64_MASK - 31
BROKEN_LOSS = 32
FIRE_LOSS = 64
JACKPOT_REWARD = 4096
COOLDOWN_REWARD = 3
BROKEN_MACHINE = "X"
FIRE_TILE = "^"

VIEW_W = 31
VIEW_H = 15


def build_map() -> list[str]:
    grid = [["#"] * MAP_W for _ in range(MAP_H)]

    def carve_h(y: int, x1: int, x2: int) -> None:
        for x in range(x1, x2 + 1):
            grid[y][x] = "."

    def carve_v(x: int, y1: int, y2: int) -> None:
        for y in range(y1, y2 + 1):
            grid[y][x] = "."

    def place(x: int, y: int, text: str) -> None:
        for offset, char in enumerate(text):
            grid[y][x + offset] = char

    for y in range(2, 20):
        carve_h(y, 32, 57)
    for x in (38, 45, 52):
        carve_v(x, 2, 19)
    carve_v(50, 10, 18)
    carve_h(10, 0, 57)
    carve_h(18, 2, 50)
    carve_h(19, 6, 57)

    for x in (12, 20, 28):
        carve_v(x, 4, 18)
    for y in (4, 8, 12, 16):
        carve_h(y, 6, 32)
    carve_h(18, 2, 32)

    for x, y in (
        (36, 9),
        (37, 9),
        (43, 9),
        (44, 9),
        (55, 10),
        (36, 16),
        (42, 16),
        (48, 16),
        (54, 16),
        (10, 7),
        (18, 11),
        (26, 15),
    ):
        grid[y][x] = "#"

    place(34, 3, "OOOO")
    place(41, 3, "TTTT")
    place(48, 3, "SSSS")
    place(54, 3, "DDDD")
    place(34, 6, "BBBB")
    place(41, 6, "PPPP")
    place(48, 6, "MMMM")
    place(54, 6, "KKKK")
    place(34, 13, "RRRR")
    place(41, 13, "AAAA")
    place(48, 13, "CCCC")
    place(54, 13, "DDDD")
    place(53, 10, "$X")

    place(8, 5, "OOO")
    place(16, 5, "TTT")
    place(24, 5, "SSS")
    place(8, 9, "BBB")
    place(16, 9, "PPP")
    place(24, 9, "DDD")
    place(8, 13, "RRR")
    place(16, 13, "AAA")
    place(24, 13, "CCC")

    for x, y in (
        (5, 18),
        (6, 18),
        (7, 18),
        (8, 18),
        (10, 18),
        (11, 18),
        (13, 18),
        (14, 18),
        (15, 18),
        (16, 18),
        (9, 19),
        (10, 19),
        (15, 19),
        (16, 19),
        (17, 19),
    ):
        grid[y][x] = "#"
    for x, y in (
        (5, 19),
        (7, 19),
        (8, 19),
        (11, 19),
        (13, 19),
        (14, 19),
        (15, 17),
        (17, 17),
        (18, 19),
    ):
        grid[y][x] = FIRE_TILE
    for x, y in (
        (18, 18),
        (17, 18),
        (17, 17),
        (16, 17),
        (15, 17),
        (14, 17),
        (13, 17),
        (12, 17),
        (11, 17),
        (10, 17),
        (9, 17),
        (9, 18),
        (9, 19),
        (8, 19),
        (7, 19),
        (6, 19),
        (5, 19),
        (4, 19),
        (4, 18),
    ):
        grid[y][x] = "."

    grid[14][28] = "N"
    grid[START_Y][START_X] = "@"
    grid[FLAG_Y][FLAG_X] = "F"
    grid[FLAG_Y][FLAG_X + 1] = "G"
    return ["".join(row) for row in grid]


ARCADE_MAP = build_map()

MACHINE_NAMES = {
    "O": "OutRun",
    "T": "Tetris",
    "B": "Bubble Bobble",
    "P": "pinball",
    "R": "R-Type",
    "S": "Street Fighter II",
    "D": "Dance Dance Revolution",
    "A": "After Burner",
    "C": "Centipede",
    "K": "Killer Instinct",
    "M": "Mortal Kombat",
    "X": "one armed bandit",
    "N": "maintenance register",
}


@dataclass
class State:
    x: int = START_X
    y: int = START_Y
    tickets: int = START_TICKETS
    plays: int = 0
    last_machine: str = ""
    broken_cooldown: int = 0
    message: str = "Nocna zmiana. Automaty nadal pracuja."


class RawTerminal:
    def __init__(self) -> None:
        self.fd = sys.stdin.fileno()
        self.old: Any = None

    def __enter__(self) -> RawTerminal:
        if sys.stdin.isatty():
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
            sys.stdout.write("\x1b[?25l\x1b[2J")
            sys.stdout.flush()
        return self

    def __exit__(self, _exc_type: object, _exc: object, _tb: object) -> None:
        if self.old is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
            sys.stdout.write("\x1b[?25h\x1b[0m\x1b[2J\x1b[H")
            sys.stdout.flush()


def u8(value: int) -> int:
    return value & 0xFF


def u64(value: int) -> int:
    return value & U64_MASK


def reset_state() -> State:
    return State(message=f"Reset. Wracasz do lobby ze startowymi {START_TICKETS} biletami.")


def map_tile(x: int, y: int) -> str:
    if 0 <= y < len(ARCADE_MAP) and 0 <= x < len(ARCADE_MAP[y]):
        return ARCADE_MAP[y][x]
    return "#"


def walkable(x: int, y: int) -> bool:
    if map_tile(x, y) == "G":
        return False
    return map_tile(x, y) != "#"


def can_enter(state: State, x: int, y: int) -> bool:
    if map_tile(x, y) == "G":
        return state.tickets >= DOOR_COST
    return walkable(x, y)


def machine_at(x: int, y: int) -> str | None:
    name = MACHINE_NAMES.get(map_tile(x, y))
    if name == "maintenance register":
        return None
    return name


def move(state: State, dx: int, dy: int) -> State:
    nx = state.x + dx
    ny = state.y + dy

    if nx < 0:
        state.x = RIGHT_TELEPORT_X
        state.message = "POS_X=ff mignelo na ekranie. Terminal odrzuca blad i wrzuca cie z prawej."
        return state
    if nx >= MAP_W or ny < 0 or ny >= MAP_H:
        state.message = "Sciana muzeum zawraca cie do sali."
        return state

    if not can_enter(state, nx, ny):
        if map_tile(nx, ny) == "G":
            state.message = f"Czytnik miga: wymagane wszystkie punkty ({DOOR_COST:016x})."
        else:
            state.message = "Rzad automatow blokuje przejscie."
        return state

    state.x = nx
    state.y = ny
    state.broken_cooldown = max(0, state.broken_cooldown - 1)
    tile = map_tile(state.x, state.y)

    if tile == "G":
        state.x = FLAG_X
        state.y = FLAG_Y
        state.message = "Czytnik przyjmuje jackpot. Stary teleport wyrzuca cie przy klapie."
    elif tile == FIRE_TILE:
        before = state.tickets
        state.tickets = u64(state.tickets - FIRE_LOSS)
        state.message = f"Plomien zjada {FIRE_LOSS} biletow: {before:016x}->{state.tickets:016x}."
    elif (state.x, state.y) == (FLAG_X, FLAG_Y):
        state.message = "Klapa serwisowa jest otwarta."
    else:
        machine = machine_at(state.x, state.y)
        state.message = f"Stoisz przy automacie {machine}." if machine else "Ciche brzeczenie kineskopow wypelnia sale."

    return state


def play(state: State) -> State:
    tile = map_tile(state.x, state.y)
    machine = machine_at(state.x, state.y)
    if not machine:
        state.message = "Podejdz do automatu i nacisnij P."
        return state

    state.plays += 1
    before = state.tickets

    if tile == BROKEN_MACHINE:
        if state.broken_cooldown > 0:
            state.message = f"{machine}: cooldown strat. Kasyno odblokuje bandyte za {state.broken_cooldown} ruchy."
            return state
        state.tickets = u64(state.tickets - BROKEN_LOSS)
        state.broken_cooldown = 3
        state.message = (
            f"{machine}: LOSUJEMY... wynik zawsze dobry dla kasyna."
            f" -{BROKEN_LOSS} biletow, zostaje {state.tickets:016x}."
        )
        return state

    if state.last_machine == tile:
        state.tickets = u64(state.tickets + COOLDOWN_REWARD)
        state.message = (
            f"{machine}: cooldown. Krupier wyplaca tylko +{COOLDOWN_REWARD}; zmien automat, zeby grac dalej."
        )
        return state

    state.last_machine = tile
    roll = (state.plays * 31 + ord(tile) * 7 + state.x + state.y) % 100
    if roll >= 97:
        state.tickets = u64(state.tickets + JACKPOT_REWARD)
        state.message = f"{machine}: LOSUJEMY... jackpot +{JACKPOT_REWARD}. Licznik {state.tickets:016x}."
    elif roll >= 65:
        reward = 37 + (roll % 17)
        state.tickets = u64(state.tickets + reward)
        state.message = f"{machine}: LOSUJEMY... wygrana +{reward}. Licznik {state.tickets:016x}."
    else:
        reward = 8 + ((state.plays * 11 + ord(tile)) % 29)
        state.tickets = u64(state.tickets + reward)
        if state.tickets < before:
            state.message = f"{machine}: licznik przeskoczyl z {before:016x} na {state.tickets:016x}."
        else:
            state.message = f"{machine}: LOSUJEMY... drobna wygrana +{reward}. Licznik {state.tickets:016x}."
    return state


def inspect(state: State) -> State:
    if (state.x, state.y) == (FLAG_X, FLAG_Y):
        state.message = f"FLAG: {FLAG}"
    elif map_tile(state.x, state.y) == "N":
        state.message = "Rejestr serwisowy pokazuje surowy stan licznikow automatow."
    elif map_tile(state.x, state.y) == "G":
        state.message = f"Czytnik przy drzwiach: wymagane wszystkie punkty, technicznie {DOOR_COST:016x} biletow."
    elif map_tile(state.x, state.y) == BROKEN_MACHINE:
        state.message = f"Zepsuty jednoręki bandyta. Kartka technika: bardzo dobry dla kasyna, zawsze -{BROKEN_LOSS}."
    elif map_tile(state.x, state.y) == FIRE_TILE:
        state.message = f"Palnik serwisowy. Jeden zly krok kosztuje {FIRE_LOSS} biletow."
    else:
        machine = machine_at(state.x, state.y)
        state.message = (
            f"{machine}: losowanie trwa po nacisnieciu P; powtarzanie tej samej szafy ma cooldown."
            if machine
            else "Nic ciekawego."
        )
    return state


def apply_key(state: State, key: str) -> tuple[State, bool]:
    if key == "w":
        return move(state, 0, -1), False
    if key == "s":
        return move(state, 0, 1), False
    if key == "d":
        return move(state, 1, 0), False
    if key == "a":
        return move(state, -1, 0), False
    if key == "p":
        return play(state), False
    if key in (" ", "e"):
        return inspect(state), False
    if key == "r":
        return reset_state(), False
    if key in ("q", "\x03", "\x04"):
        return state, True
    state.message = "WASD ruch, P gra, Spacja sprawdza, R reset, Q wyjscie."
    return state, False


def screen_tile(x: int, y: int, state: State) -> str:
    if x == state.x and y == state.y:
        return "@"

    char = map_tile(x, y)
    if char == "#":
        return "#"
    if char == ".":
        return "."
    if char == "@":
        return "."
    if char == "N":
        return "?"
    if char == "G":
        return "D"
    if char == "F":
        return "F"
    if char == "$":
        return "$"
    if char == FIRE_TILE:
        return "^"
    return "*"


def viewport_origin(state: State) -> tuple[int, int]:
    return state.x - VIEW_W // 2, state.y - VIEW_H // 2


def render_view(state: State) -> str:
    ox, oy = viewport_origin(state)
    lines = []
    for y in range(oy, oy + VIEW_H):
        row = []
        for x in range(ox, ox + VIEW_W):
            row.append(screen_tile(u8(x), u8(y), state))
        lines.append("".join(row))
    return "\n".join(lines)


def render(state: State) -> str:
    if (state.x, state.y) == (FLAG_X, FLAG_Y):
        flag_line = "Klapa serwisowa znaleziona."
    else:
        flag_line = "Znajdz zamknieta klape serwisowa."

    return "\n".join([
        "\x1b[H\x1b[J",
        "KRAKOW ARCADE MUSEUM // NOCNA ZMIANA",
        "WASD ruch  P gra  Spacja sprawdz  R reset  Q wyjscie",
        "",
        render_view(state),
        "",
        f"POS_X={state.x:02x} POS_Y={state.y:02x}  BILETY={state.tickets:016x}  GRY={state.plays}",
        state.message,
        flag_line,
    ])


def read_key() -> str:
    char = sys.stdin.read(1)
    if char == "\x1b" and select.select([sys.stdin], [], [], 0.02)[0]:
        seq = sys.stdin.read(2)
        if seq.startswith("[") and len(seq) == 2:
            return seq[1]
    return char.lower()


def run_interactive() -> int:
    state = State()
    with RawTerminal():
        done = False
        while not done:
            sys.stdout.write(render(state))
            sys.stdout.flush()
            key = read_key()
            state, done = apply_key(state, key)
        sys.stdout.write("\x1b[2J\x1b[HGood night.\n")
        sys.stdout.flush()
    return 0


def run_line_mode() -> int:
    state = State()
    commands = {
        "north": "w",
        "south": "s",
        "east": "d",
        "west": "a",
        "look": " ",
        "play": "p",
        "reset": "r",
        "quit": "q",
    }
    print(render(state).replace("\x1b[H\x1b[J", ""), flush=True)

    if os.environ.get("SSH_ORIGINAL_COMMAND") is None and not sys.stdin.isatty():
        print(
            "\nTen klient SSH nie przydzielil terminala. Polacz sie komenda: ssh -tt player@HOST -p PORT",
            flush=True,
        )
        while True:
            time.sleep(60)

    for line in sys.stdin:
        text = line.strip().lower()
        keys = commands.get(text)
        if keys is None:
            keys = text

        done = False
        for key in keys:
            state, done = apply_key(state, key)
            if done:
                break
        print(render(state).replace("\x1b[H\x1b[J", ""), flush=True)
        if done:
            break
        time.sleep(0.01)
    return 0


def main() -> int:
    if sys.stdin.isatty() and sys.stdout.isatty():
        return run_interactive()
    return run_line_mode()


if __name__ == "__main__":
    sys.exit(main())
