# Bibliotheca Jagellonica - rozwiązanie

## Opis

Zadanie udaje nieskończoną bibliotekę w duchu Borgesa. Pierwsze etapy są krótkimi manuskryptami `.txt`, które uczą gracza, że katalog nie pokazuje wszystkiego, a tekst trzeba czytać jako palimpsest.

Kluczowy mechanizm: `lorem.txt` ujawnia dwa odsyłacze jednocześnie — jeden do kontynuacji (`pi.txt`), drugi do zapieczętowanej notatki (`cipher.txt`). Klucz do odczytu (`BABEL`) jest zawarty w tym samym manuskrypcie.

`Range` jest mechaniką finalną. Dopiero ostatnia księga deklaruje 37 TB i wymaga czytania małych fragmentów.

## Etap 1: prolog i Verulam

W katalogu widać `prolog.txt` oraz `buffalo.txt`. Prolog wspomina Buffalo i kanclerza z Verulamu. Verulam prowadzi do Francisa Bacona, a więc do szyfru Bacona.

W `buffalo.txt` należy patrzeć na warianty zapisu słów `Buffalo` i `buffalo`. Wielka litera odpowiada wariantowi `B`, mała litera wariantowi `A`. Po odczytaniu szyfru Bacona dostajemy:

```text
LOREM
```

To wskazuje ukrytą księgę w tym samym woluminie:

```text
/library/0123456789abcdef0123456789abcdef/wall/2/shelf/4/volume/17/book/lorem.txt
```

## Etap 2: palimpsest lorem — dwie ścieżki

`lorem.txt` zawiera kanon oraz odpis. Porównujemy oba akapity. Różnice między kanonem a odpisem dają:

```text
QI
```

Ten sam manuskrypt wspomina Babel jako klucz. Odszyfrowujemy `QI` Vigenere'em z kluczem `BABEL` i otrzymujemy:

```text
PI
```

To wskazuje pierwszą ukrytą księgę:

```text
/library/0123456789abcdef0123456789abcdef/wall/2/shelf/4/volume/17/book/pi.txt
```

Na marginesie `lorem.txt` widnieje również bezpośredni odsyłacz do zapieczętowanej notatki:

```text
/library/0ddba11ad0ddba11ad0ddba11ad0ddba11ad/wall/1/shelf/2/volume/9/book/cipher.txt
```

## Etap 3: tablica pi i księga wędrowna

`pi.txt` wygląda jak długi zapis cyfr pi. Niektóre znaki nie są jednak cyframi. Wyciągnięcie znaków spoza alfabetu dziesiętnego z bloku liczby daje:

```text
POLYGLOTLINGUAROMAE
```

Czytamy to jako:

```text
POLYGLOT; LINGUA ROMAE
```

Następna księga to `polyglot.txt`, a jej odpowiedź ma być w języku Rzymu. W HTTP naturalnym miejscem na preferowany język odpowiedzi jest nagłówek `Accept-Language`:

```bash
curl -H 'Accept-Language: la' 'https://bibliotheca-jagellonica.hack4krak.pl/library/0123456789abcdef0123456789abcdef/wall/2/shelf/4/volume/17/book/polyglot.txt'
```

Pojawia się ścieżka do `headers.txt`.

## Etap 4: karta bez tresci widzialnej

`headers.txt` mówi, że odsyłacz widzi tylko posłaniec niosący odpowiedź. Trzeba sprawdzić nagłówki HTTP:

```bash
curl -I 'https://bibliotheca-jagellonica.hack4krak.pl/library/0123456789abcdef0123456789abcdef/wall/2/shelf/4/volume/17/book/headers.txt'
```

Nagłówek `Link` wskazuje bezpośrednio finalną księgę:

```text
/library/ffffffffffffffffffffffffffffffff/wall/4/shelf/5/volume/32/book/umbra.txt
```

## Etap 5: odszyfrowanie cipher.txt

Gracz wraca do `cipher.txt` z etapu 2. `lorem.txt` powiedział, że "Babel jest kluczem do obcego alfabetu", a `cipher.txt` mówi "zdejmij metaliczny atrament" (hex) i że klucz jest wspólny z tym, który otwierał obcy alfabet.

Dekodowanie:

1. Hex zamieniamy na bajty.
2. XOR z powtarzającym się kluczem `babel`.

Otrzymujemy:

```text
FINAL /library/ffffffffffffffffffffffffffffffff/wall/4/shelf/5/volume/32/book/umbra.txt ; sufiks 512 ; potem czytaj karty z konca: BABEL 13371337:13, E 27182818:10, PI 31415926:9, FI 16180339:11, KRAKOW 42424242:13.
```

## Etap 6: księga 37 TB

To pierwszy moment, w którym potrzebny jest HTTP `Range`. Finalna księga deklaruje 37 TB i odmawia pełnego pobrania. Czytamy tylko końcówkę:

```bash
curl -H 'Range: bytes=-512' 'https://bibliotheca-jagellonica.hack4krak.pl/library/ffffffffffffffffffffffffffffffff/wall/4/shelf/5/volume/32/book/umbra.txt'
```

Karta krańcowa potwierdza format `POCZATEK:DLUGOSC`:

```text
BABEL 13371337:13
E 27182818:10
PI 31415926:9
FI 16180339:11
KRAKOW 42424242:13
```

Zamieniamy je na zakresy bajtów:

```text
13371337-13371349
27182818-27182827
31415926-31415934
16180339-16180349
42424242-42424254
```

Po złożeniu fragmentów dostajemy flagę.

## Flaga

```text
hack4KrakCTF{c4t4l0gu5_in_umbra_ranges_non_legunt_totum}
```
