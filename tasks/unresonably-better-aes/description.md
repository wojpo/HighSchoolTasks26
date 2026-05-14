Niektóre wiadomości muszą być przesyłane w sposób bezpieczny, tak aby nikt niepowołany nie mógł ich odczytać. W tym celu stosuje się szyfrowanie.

Istnieje wiele znanych szyfrów – od prostych, takich jak szyfr Cezara, po zaawansowane, jak [AES](https://pl.wikipedia.org/wiki/Advanced_Encryption_Standard).

Pewien inżynier z 31. Liceum w Krakowie, po kilku iteracjach i kilku milionach pozyskanych ze stypendiów oraz funduszy europejskich, stworzył po dwóch podejściach własny, jeszcze lepszy algorytm szyfrowania - **AES++**!

## Załączniki

W załącznikach znajdziesz dwa pliki `decoder.py` i `encoder.py`, które implementują szyfrowanie AES++.

Możesz ich używać w następujący sposób:

```shell
# Zaszyfruj wiadomość
python encoder.py <tajne hasło> <wiadomość>

# Odszyfruj
python decoder.py <tajne hasło> <zaszyfrowana wiadomość>
```

## Zadanie

Spróbuj odszyfrować poniższą wiadomość:

```
LWyhq985w3glL3/ZIZPJ3C777etYn4yLDdh8owJM+QwJpSzPTZR95C2kBohXLZ/kC7/BKyL9pwgAAAAAGBb0Nw==
```

Może zawiera ona coś, co Cię interesuje!
