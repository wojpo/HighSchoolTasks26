## Opis

Zadanie opierało się na ciekawym zjawisku fizycznym: interferencji fal dźwiękowych.  
Jeśli w tym samym momencie odtworzymy falę dźwiękową oraz jej odwróconą wersję, może dojść do ich wzajemnego wygaszenia. Na podobnej zasadzie działają słuchawki z aktywną redukcją hałasu.

W tym zadaniu mieliśmy audycję radiową, w której nałożyły się na siebie **trzy dość znane utwory**.  
Znajdując oryginalne nagrania, dopasowując je do audycji, zmieniając ich głośność zgodnie z opisem zadania i odwracając fazę, dało się **usuwać kolejne warstwy dźwięku**.

Po zdjęciu kilku warstw można było usłyszeć finalną wiadomość zakodowaną za pomocą alfabetu fonetycznego NATO.

## Rozwiązanie

Rozwiązań, jak zawsze, jest wiele, ale przykładowe podejście wygląda następująco:

1. Znalezienie pierwszego utworu na platformie YouTube za pomocą tekstu piosenki, wiedzy własnej albo aplikacji typu Shazam.  
   Znajomość twórczości Taco Hemingwaya nie była konieczna.
2. Zmodyfikowanie jego głośności o **-10.1 dB**, zgodnie ze wskazówką z treści zadania.
3. Ręczne, np. w Audacity, albo automatyczne nałożenie utworu na odpowiednią pozycję w nagraniu.
4. Odwrócenie fazy dopasowanego utworu i odjęcie go od audycji.
5. Odsłuchanie kolejnego, lepiej słyszalnego utworu i powtórzenie całego procesu.

Po 3-4 powtórzeniach da się usłyszeć wcześniej niesłyszalny fragment w okolicach **1:15**, zawierający syntetyzowany głos.

Głos informuje, że jesteśmy już blisko flagi, a następnie podaje serię słów. Jest to alfabet fonetyczny NATO — poszczególne słowa oznaczają litery, cyfry lub znaki.

W nagraniu można usłyszeć:

> Du hast fast eine Flagge: Charlie Four Lima Lima Dash One Dash Eight Zero Zero Dash Hotel Four Kilo Dash Seven Oscar Whiskey

Po odkodowaniu otrzymujemy:

```text
C4LL-1-800-H4K-7OW
```

Ten tekst jednoznacznie można zinterpretować jako flagę:

```text
hack4KrakCTF{C4LL-1-800-H4K-7OW}
```

## AI

Organizatorom nie udało się rozwiązać tego zadania całkowicie autonomicznie z użyciem modeli językowych.
Jeśli Tobie się udało, koniecznie pochwal się tym na naszym Discordzie!

## Informacje dodatkowe

Główna piosenka: **Taco Hemingway - Wielkomiejska Bezsenność**

Nałożone utwory:

1. **Daria Zawiałow, Taco Hemingway - SUPRO**
2. **Taco Hemingway - Cichosza feat. Otsochodzi**
3. **Taco Hemingway - 900729**

Dodatkowe wstawki:

* okolice **0:40** - nagranie „Taco Hemingway stoi w korku”. Było to wskazówką innej wiadomości wewnątrz tekstu
* okolice **1:15** - własne nagranie z zakodowaną wiadomością
