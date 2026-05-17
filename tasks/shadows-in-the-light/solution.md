## Opis

Na stronie obrazy są dostępne w dwóch miejscach: na liście na dole oraz w widoku pełnoekranowym. Aby zoptymalizować działanie strony, dla każdego obrazu generowane są miniatury. W zależności od miejsca wyświetlania oraz rozdzielczości ekranu wykorzystywane są obrazy o różnych rozmiarach.

## Rozwiązanie

Strona wykorzystuje elementy `<picture>` z kilkoma wariantami obrazów zależnymi od szerokości ekranu. Jeden z wariantów obrazu `Kaplica poranna` został ukryty za praktycznie niemożliwym do spełnienia warunkiem `media`:

```html
<source media="(min-width: 999999px)" srcset="images/kaplica-poranna-bigger-preview.webp">
```

Aby utrudnić analizę, w `index.html` dodany jest też prosty anty-debugger, który regularnie wykonuje instrukcję `debugger`. Jeśli przeszkadza podczas pracy w DevTools, można wyłączyć breakpointy w przeglądarce albo obejść go przez Snippets/Local Overrides.

Aby wymusić użycie tego wariantu, wystarczy zmodyfikować warunek `media` w konsoli przeglądarki tak, aby był zawsze spełniony:

```js
document.querySelectorAll('source[media]').forEach(source => {
  source.media = '(min-width: 1px)';
});
```

Alternatywnie można ręcznie odnaleźć bezpośredni adres obrazka w kodzie źródłowym stroy.

Po otwarciu obrazu okazuje się, że został on zmodyfikowany — przedstawiona postać trzyma flagę z logiem Hack4Krak.

To jednak dopiero pierwszy etap zadania. Po dokładniejszym przyjrzeniu się szacie postaci można zauważyć ukrytą flagę z lekko zmodyfikowanymi kolorami. Zmieniając jasność, kontrast lub stosując prosty post-processing obrazu, można bez problemu odczytać jej treść.

## Informacje dodatkowe

*Nikt wciąż nie zna prawdziwej historii Kościoła Mariackiego...*
