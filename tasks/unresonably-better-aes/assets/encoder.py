import base64
import random
import sys
from io import BytesIO


def encode(passphrase: str, msg: str | bytes):
    if isinstance(msg, bytes):
        msg_bytes = BytesIO(msg)
    elif isinstance(msg, str):
        msg_bytes = BytesIO(bytes(msg, "utf-8"))
    else:
        raise TypeError("Expected msg to be either str or bytes")
    pass_bytes = passphrase.encode("ascii")

    out = BytesIO()
    seed = random.randbytes(1)

    random.seed(seed)
    out.write(seed)

    bts = msg_bytes.read(6)
    i = 0
    while len(bts) > 0:
        num = int.from_bytes(bts, "big") * random.randint(0, 2**8 - 1) * pass_bytes[i % len(pass_bytes)]

        out.write(num.to_bytes(8, "big"))

        bts = msg_bytes.read(6)
        i += 1
    out.seek(0)
    return base64.b64encode(out.read()).decode("ascii")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: py encoder.py <passphrase> <message>")
        exit(1)
    print(encode(sys.argv[1], sys.argv[2]))
