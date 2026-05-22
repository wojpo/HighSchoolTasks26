## Opis

To było zadanie OSINT. Nie chodziło o jedno proste wyszukanie, tylko o połączenie kilku śladów: osoby, domeny, certyfikatów, starej strony, screena i commita.

AI mogło pomóc w analizie i skojarzeniach, np. przy odkryciu znaczenia screena albo wskazaniu, że hash wygląda jak commit. Nie musiało jednak samodzielnie znaleźć całej domeny ani przejść pełnej ścieżki. W OSINT najważniejsze jest korelowanie informacji i budowanie spójnego obrazu osoby lub projektu.

## Rozwiązanie

Najpierw należało ustalić, kim jest szukana osoba. Wskazówki prowadziły do nicku `Norbiros`: autora `emojitype`, moda do Minecrafta oraz osoby powiązanej z XXXI LO.

Potem warto było sprawdzić jego publiczne profile, głównie GitHuba i linki na innych platformach. W ten sposób można było dojść do domeny `norbiros.dev`.

### Certyfikaty

Następny krok to Certificate Transparency. Certyfikaty TLS są zapisywane w publicznych logach, więc przez narzędzia takie jak [crt.sh](https://crt.sh/) można znaleźć subdomeny, nawet jeśli nigdzie nie są podlinkowane.

Po sprawdzeniu `norbiros.dev` pojawiało się kilka stron bez większej treści, ale jedna była istotna:

```text
https://archiwum31.norbiros.dev/
```

Na tej stronie był screen z Discorda.

### Screen

Na screenie pojawiają się `Norbiros`, `Goteusz` i `Szczurekyt`. Rozmowa mówi o jednej opensourceowej bibliotece serwera Minecraft napisanego w Ruście oraz podaje hash commita:

```text
f226853a9f45d63559e433bc42f57be64b64646b
```

Po dalszym sprawdzeniu tych nicków i projektu można dojść do `CrabCraft` oraz repozytorium:

```text
https://github.com/CrabCraftDev/CrabNBT
```

Ostatecznie należało otworzyć commit:

```text
https://github.com/CrabCraftDev/CrabNBT/commit/f226853a9f45d63559e433bc42f57be64b64646b
```

Tam znajdowała się właściwa treść potrzebna do rozwiązania zadania.
