## Opis

Mamy tutaj doczynienia z grą, której nie da sie przejść

Żeby otrzymać flagę będziemy zajrzeć w głąb do kodu gry i go zmodyfikować - np. za pomocą narzędzia [dnSpy](https://github.com/dnSpy/dnSpy/releases/)

## Rozwiązanie
1. Otwieramy `rybulból_Data\Managed\Assembly-CSharp.dll` w dnSpy
2. Czytając kod napotykamy się na dziwną zmienną z bezsensowną nazwą, która jest `GameObject`'em i uaktywnia się po tym jak score osiągnie `-863437832`
3. Patchujemy grę, żeby sprawdzić o co chodzi i uaktywniamy tą zmienną, po wejściu do gry ukazuję się flagą ale gra się od razu zamyka
4. Screenujemy flagę albo znajdujemy i patchujemy kod, który zamyka automatycznie grę jak `GameObject` z flagą jest aktywny
5. Uzyskujemy flagę na ekranie
