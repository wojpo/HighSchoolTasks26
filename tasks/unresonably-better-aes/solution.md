## Opis

AES++ oczywiście **nie jest bezpieczny**. Zawsze lepiej używać sprawdzonych i szeroko analizowanych algorytmów szyfrowania, takich jak [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard).

Teoretycznie można rozwiązać to zadanie brute-forcem. Zakładając, że hasło składa się z 8 znaków, a każdy może być jednym z 95 symboli, mamy `95^8 = 6634204312890625` możliwych kombinacji.

Nawet mając superkomputer sprawdzający miliard haseł na sekundę, zajęłoby to około **76 dni**. A to znacznie dłużej niż czas trwania CTF-a.

## Rozwiązanie

Na szczęście algorytm zawiera poważną **lukę bezpieczeństwa**. Każda część wiadomości jest szyfrowana kolejną literą hasła (czyli np. pierwszy blok – pierwszą literą, drugi – drugą itd.).

Dzięki temu można zgadywać hasło znak po znaku:
1. Zgadujemy pierwszy znak hasła.
2. Sprawdzamy, czy rozszyfrowany pierwszy blok ma sens.
3. Jeśli tak, zgadujemy drugi znak, i tak dalej.

Poniżej znajduje się przykład implementacji w Pythonie, która automatyzuje ten atak. Kod nie jest idealny, ale pokazuje zasadę działania i skutecznie łamie szyfrowanie.

```python
import base64
import random
from io import BytesIO


def decode_start(passphrase: str, code_base64: str, seed: int, n=1):
    pass_bytes = passphrase.encode("ascii")
    code = BytesIO(base64.b64decode(code_base64.encode("ascii")))

    out = BytesIO()
    random.seed(seed)

    for i in range(n):
        bts = code.read(8)
        r = random.randint(0, 2**8 - 1)
        decoded_bytes = int.from_bytes(bts, "big") // r // pass_bytes[i % len(pass_bytes)]
        out.write(decoded_bytes.to_bytes(6, "big"))

    out.seek(0)
    return out.read()


def decode_bigger(passphrase: str, code_base64: str, seed: int, n: int):
    pass_bytes = passphrase.encode("ascii")
    code = BytesIO(base64.b64decode(code_base64.encode("ascii")))

    out = BytesIO()
    random.seed(seed)

    bts = code.read(8)
    r = random.randint(0, 2**8 - 1)
    decoded_bytes = int.from_bytes(bts, "big") // r // pass_bytes[0 % len(pass_bytes)]
    out.write(decoded_bytes.to_bytes(6, "big"))

    for combination in possible_values:
        try:
            combined_str = "".join(combination)

            value = decode_start(passphrase + combined_str, code_base64, seed, n + 1)
            encoded = encode_start(passphrase + combined_str, value.decode("ascii"), seed, n + 1)

            if msg_bytes.startswith(encoded):
                print(f"{n} {bytes(b for b in value if b != 0)} Seed: {seed} Passphrase: {passphrase + combined_str}")
                decode_bigger(passphrase + combined_str, code_base64, seed, n + 1)
        except:
            pass
    out.seek(0)
    return out.read()


def encode_start(passphrase: str, msg: str, seed: int, n=1):
    msg_bytes = BytesIO(bytes(msg, "utf-8"))
    pass_bytes = passphrase.encode("ascii")

    out = BytesIO()
    random.seed(seed)

    for i in range(n):
        bts = msg_bytes.read(6)

        num = int.from_bytes(bts, "big") * random.randint(0, 2**8 - 1) * pass_bytes[i % len(pass_bytes)]

        out.write(num.to_bytes(8, "big"))

    out.seek(0)
    return out.read()


possible_values = [chr(i) for i in range(32, 127)]

msg = "LWyhq985w3glL3/ZIZPJ3C777etYn4yLDdh8owJM+QwJpSzPTZR95C2kBohXLZ/kC7/BKyL9pwgAAAAAGBb0Nw=="
msg_bytes = base64.b64decode(msg)

print("Message as bytes", msg_bytes)
print("Amount of different characters", len(possible_values))

# Pick number relatively high to make sure we get the right seed
for seed in range(10000):
    for val in possible_values:
        try:
            decoded = decode_start(val, msg, seed)

            decoded = decoded.decode("utf-8")
            decoded.encode("ascii")
            encoded = encode_start(val, decoded, seed)

            if msg_bytes.startswith(encoded):
                decode_bigger(val, msg, seed, 1)
        except:
            pass
```

Dla tego konkretnego przykładu łamanie szyfrowania zajmuje około 3 sekund – więc spokojnie zdążysz podczas CTF-a.

## AI

Organizatorom udało się rozwiązać to zadanie za jednym podejściem przy użyciu modelu GPT-5.5 High. 
Podobna wersja tego zadania była dostępna w poprzednich edycjach, jednak samodzielne rozwiązanie jej przez AI nie było wtedy możliwe.
