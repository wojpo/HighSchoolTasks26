## Opis

Zadanie uruchamia małego Linuxa w przeglądarce przez `v86` i pokazuje, że `/proc` nie jest zwykłym katalogiem z plikami, tylko widokiem na działające procesy systemu.

Flaga znajduje się w `/root/flag.txt` i ma uprawnienia `400`, więc użytkownik `ctf` nie może jej odczytać bezpośrednio. W tle działa jednak proces `maintenance-daemon`, który dostał kopię flagi w zmiennej środowiskowej.

Środowisko procesu jest widoczne w `/proc/<pid>/environ`.

## Rozwiązanie

Przykładowe rozwiązanie:

1. Uruchamiamy emulator na stronie i czekamy na shell użytkownika `ctf`.
2. Sprawdzamy procesy, np. `ps`.
3. Znajdujemy proces `maintenance-daemon`.
4. Odczytujemy jego środowisko: `cat /proc/<pid>/environ`.
5. Ponieważ wartości są rozdzielone bajtem `NUL`, wygodnie użyć `tr '\0' '\n'`.

Przykład:

```bash
ps
cat /proc/7/environ | tr '\0' '\n'
```

Flaga:

```text
hack4KrakCTF{pr0c_fd_1s_a_w1nd0w}
```
