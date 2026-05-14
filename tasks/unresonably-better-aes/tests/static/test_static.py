import base64
import importlib.util
import random
import re
from io import BytesIO
from pathlib import Path

from toolbox.utils.test_utils import load_flag_hash, validate_flag_hash

task_path = Path(__file__).parents[2]


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_challenge_ciphertext():
    description = (task_path / "description.md").read_text()
    ciphertexts = re.findall(r"^[A-Za-z0-9+/]+={0,2}$", description, flags=re.MULTILINE)

    assert len(ciphertexts) == 1
    return ciphertexts[0]


def _decode_challenge_flag(ciphertext: str):
    passphrase = "sjsoau2s"
    pass_bytes = passphrase.encode("ascii")
    code = BytesIO(base64.b64decode(ciphertext.encode("ascii")))
    out = BytesIO()

    random.seed(711)
    for i in range(len(pass_bytes)):
        bts = code.read(8)
        decoded_bytes = int.from_bytes(bts, "big") // random.randint(0, 2**8 - 1) // pass_bytes[i]
        out.write(decoded_bytes.to_bytes(6, "big"))

    wrapped_flag = bytes(byte for byte in out.getvalue() if byte != 0).decode("ascii")
    assert wrapped_flag.startswith("hack4KrakCTF{") and wrapped_flag.endswith("}")
    return wrapped_flag.removeprefix("hack4KrakCTF{").removesuffix("}")


def test_config_flag_hash_matches_decoded_challenge_flag():
    flag_hash = load_flag_hash(task_path)
    flag = _decode_challenge_flag(_load_challenge_ciphertext())

    assert flag_hash is not None
    assert validate_flag_hash(flag, flag_hash)


def test_solver_sources_use_challenge_ciphertext_from_description():
    cracker_source = (task_path / "src" / "cracker.py").read_text()
    solution = (task_path / "solution.md").read_text()
    ciphertext = _load_challenge_ciphertext()

    assert ciphertext in cracker_source
    assert ciphertext in solution


def test_assets_encoder_and_decoder_round_trip(monkeypatch):
    encoder = _load_module(task_path / "assets" / "encoder.py")
    decoder = _load_module(task_path / "assets" / "decoder.py")
    message = b"AES++ static"

    monkeypatch.setattr(encoder.random, "randbytes", lambda size: b"\x01" * size)

    encoded = encoder.encode("static-pass", message)
    decoded = decoder.decode("static-pass", encoded)

    assert decoded == message
