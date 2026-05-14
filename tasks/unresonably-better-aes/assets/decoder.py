import base64
import random
import sys
from io import BytesIO


def decode(passphrase: str, code_base64: str):
    pass_bytes = passphrase.encode("ascii")
    code = BytesIO(base64.b64decode(code_base64.encode("ascii")))

    out = BytesIO()
    random.seed(code.read(1))

    bts = code.read(8)
    i = 0
    while len(bts) > 0:
        decoded_bytes = int.from_bytes(bts, "big") // random.randint(0, 2**8 - 1) // pass_bytes[i % len(pass_bytes)]

        out.write(decoded_bytes.to_bytes(6, "big"))

        bts = code.read(8)
        i += 1

    out.seek(0)
    return out.read()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: py decoder.py <passphrase> <message>")
        exit(1)
    try:
        print(decode(sys.argv[1], sys.argv[2]).decode("utf-8"))
    except:  # noqa: E722
        print("Couldn't decode message: invalid passphrase")
