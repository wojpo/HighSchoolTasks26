## Opis

Serwer stawia 53-blokowy (X: -26 do 26) bedrockowy vault w odległości ~40 bloków na północ od spawnu (Z=25). Gracz nie może go obejść ani przez niego przejść normalnie. Dwie mechaniki:

- **Zewnętrzny przycisk** (Z=-13, przed południową ścianą) — dostępny normalnie w zasięgu 3 bloków
- **Wewnętrzny przycisk** (Z=-25, przy północnej wewnętrznej ścianie) — dostępny tylko po teleporcie

Scoreboard `quickHeist` śledzi stan gracza (dummy, startowo 0):
- 0 → start
- 1 → naciśnięto zewnętrzny przycisk
- 2 → naciśnięto wewnętrzny przycisk, czeka na powrót na zewnątrz
- 3 → ukończono

Repeating command block (Y=62, pod spawnem) co tick sprawdza: stan=2 AND gracz na zewnątrz → `/tell` flag → chain block ustawia stan=3.

## Rozwiązanie

1. Zbudować i uruchomić klienta z `src/client/` dla Minecraft `1.21.6` (Fabric, klawisz `K` = teleport 50 bloków do przodu).
2. Wejść na serwer — spawn przy Z=25 patrzący na północ.
3. Podejść do zewnętrznej południowej ściany (Z≈-10) i nacisnąć przycisk przy Z=-13.
4. Wrócić do pozycji spawnu (Z=25), patrzeć na północ, nacisnąć `K` — teleport ląduje przy Z=-25 (wewnątrz, przy przycisku wewnętrznym).
5. Nacisnąć przycisk wewnętrzny przy Z=-25 (można też zrobić krok na południe żeby był w zasięgu).
6. Odwrócić się (patrzeć na południe), nacisnąć `K` — teleport 50 bloków na południe wyprowadza z powrotem przy Z=25 (spawn, na zewnątrz).
7. Serwer (repeating CB) wykrywa stan=2 AND gracz na zewnątrz, wysyła `/tell` z flagą.

Flaga: `hack4KrakCTF{szybki_napad_na_bedrockowy_skarbiec}`
