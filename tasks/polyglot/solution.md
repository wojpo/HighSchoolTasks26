## Opis

Zadanie opierało się na języku ezoterycznym [**Whitespace**](https://en.wikipedia.org/wiki/Whitespace_(programming_language)), w którym znaczenie mają tylko spacje, tabulatory i znaki nowej linii.

Plik wyglądał jak losowy zrzut logów oraz podejrzany kod przypominający Pythona, ale była to zmyłka. Właściwy program był ukryty w "niewidocznych" znakach.

Proste dekodowanie spacji i tabów jako `0/1` nie wystarczało, ponieważ ukryta warstwa była działającym programem Whitespace.

## Rozwiązanie

Najprostsza metoda:

1. Rozpakować `challenge.zip`.
2. Otworzyć plik z zadania.
3. Skopiować jego zawartość do interpretera Whitespace, np.
   `https://www.jdoodle.com/execute-whitespace-online`
4. Uruchomić program.

Interpreter ignoruje widoczne znaki i wykonuje tylko spacje, tabulatory oraz nowe linie.

Po uruchomieniu otrzymujemy flagę:

```text
hack4KrakCTF{n4jl3p5zy_j3zyk_pr0gr4m0w4n14_t0_5p4cj4}
```

## Informacje dodatkowe

Widoczny kod Pythona był red herringiem. Miał sugerować dekodowanie, hashowanie i odzyskiwanie danych, ale nie był potrzebny do rozwiązania.

Ważne było zachowanie oryginalnych białych znaków - edytory lub formatery usuwające trailing whitespace mogły uszkodzić zadanie.
