## Opis

Ten task jest wieloetapowy, wykorzystuje zarówno metody kryptografii jak i reverse engineering.

Plik `WPA000001.pdf` zawiera zasłonięty tekst czarnym paskiem jednakże ten PDF nie został spłaszczony przez co można bez problemu wydobyć tekst pod spodem np. kopiując go - [realny błąd rządu USA](https://www.redactable.com/blog/redacted-epstein-files-here-is-what-went-wrong)

Plik `WPA000002.pdf` używa homofonicznego szyfru podstawieniowego 

Plik `WielkiBrat.zip` zawiera plik `exe` aplikacji winforms, który można zdekompilować praktycznie do natywnego C#

## Rozwiązanie

1. Zapoznajemy się z prawem z pliku `ThePrawo.pdf`
2. Wyciągamy id czynów zabronionych przestępstwa z pliku `WPA000001.pdf` -  3 i 7 - liczymy lata programem `WielkiBrat.exe` - 58936329 lat
3. Odszyfrowujemy tekst pliku `WPA000002.pdf` za pomocą [analizy frekwencyjnej](https://en.wikipedia.org/wiki/Frequency_analysis) - z tekstu id czynów zabronionych przestępstwa: 1 i 2 - `WielkiBrat.exe`: 86304100 lat
4. W plikach od `WPA000003.pdf` do `WPA000005.pdf` nie znajdują się żadne istotne informacje - zawierają jedynie zabawne obrazki. Dopiero w pliku `WPA000006.pdf` można znaleźć notatkę, z której wynika, że rozpatrywane przestępstwo obejmuje czyny zabronione 2, 3, 6 oraz 7.
5. Wiemy, że program nie potrafi obliczyć kary dla przestępstwa obejmującego więcej niż dwa czyny zabronione. Konieczne jest więc ustalenie formuły wykorzystywanej przez aplikację do wyznaczania kary dla większej liczby jednoczesnych czynów zabronionych.
6. Jeśli posiadamy doświadczenie z platformą .NET, możemy szybko rozpoznać, że aplikacja została napisana w technologii WinForms. Nawet bez takiej wiedzy można łatwo potwierdzić ten fakt przy użyciu narzędzia Binary Ninja. Pozwala to stwierdzić, że mamy do czynienia z aplikacją .NET.
7. Skoro wiemy, że aplikacja jest samodzielnym plikiem wykonywalnym opartym na .NET, możemy spróbować wyodrębnić zawarte w niej zasoby i biblioteki. W tym celu używamy narzędzia sfextract, które rozpakowuje plik do wielu komponentów, w tym głównej biblioteki .dll.
8. Następnie otwieramy wyodrębnioną bibliotekę .dll w narzędziu DotPeek od JetBrains. Ponieważ kod .NET można stosunkowo łatwo zdekompilować, uzyskujemy dostęp do pełnej logiki aplikacji zapisanej w bliskim do natywnego C#'ie. Analiza tego kodu pozwala odtworzyć formułę wykorzystywaną do obliczania kary.
9. Zauważamy, że opiera się na słowniku gdzie kluczem jest id a wartościa treść czynów zabronionych, oraz na obliczaniu sumy wartości ASCII wszystkich znaków z treści tych czynów.
10. Wyciągamy formułe `(słownik[id1]+slownik[id2])*(slownik[id1]+slownik[id2])` i stosujemy ją na przestępstwie z czterema czynami zabronionymi za pomocą prostego skryptu w pythonie, który wyglądał by mniej więcej tak:
```
slownik = (skopiowany slownik)
def ascii(n):
    suma = 0
    for i in n:
        suma += ord(i)
    return suma
    
print((ascii(d[1])+ascii(d[2])+ascii(d[6])+ascii(d[7]))**2)
```
11. Wychodzi nam z tego - 415385161
12. Zatem flaga to: 415385161 * 86304100 * 58936329