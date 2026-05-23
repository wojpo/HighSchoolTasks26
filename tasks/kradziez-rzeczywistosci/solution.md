## Opis

Plik `arnis-better` to zmodyfikowana wersja programu [Arnis](https://github.com/louis-e/arnis), narzędzia do generowania rzeczywistych miejsc w świecie Minecrafta.

Modyfikacja dodaje walidację klucza licencyjnego. Program oczekuje argumentu `--licence-key`, a następnie sprawdza go w funkcji `verify_license`.

## Rozwiązanie

Otwórz binarkę w narzędziu typu Binary Ninja, IDA lub Ghidra. Odnajdź funkcję `verify_license` - można do niej trafić przez wyszukanie stringa `Invalid license key`.

W okolicy wykonań o id 014de62f znajdujemy ogromną ilość porównań na pojedynczych bajtach zmiennej - są to sprawdzenia kolejnych liter w kluczu licencyjnym. Jeśli zatem literka po literce wyciągniemy te znaki, otrzymamy

```
l0uiZ-cO-ty-RObIsZ-j@-z-t0bOm-OsZaIeleEeEeE
```

## Użycie

Program uruchamiamy z kluczem:

```bash
./arnis-better --licence-key "l0uiZ-cO-ty-RObIsZ-j@-z-t0bom-OsZaIeleEeEeE" --bbox 50.081909,19.985826,50.087279,19.996083 --output-dir .
```

Po podaniu poprawnego klucza program nie wypisuje `"Invalid license key."` i kontynuuje normalne działanie.

Po wygenerowaniu świata w jego plikach znajdujemy `flag.txt` z rozwiązaniem.
