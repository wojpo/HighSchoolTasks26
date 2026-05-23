## Opis

W tym zadaniu wykorzystywano [cookie](https://pl.wikipedia.org/wiki/HTTP_cookie) do przechowywania informacji o sesji użytkownika, co samo w sobie jest standardowym rozwiązaniem stosowanym w aplikacjach webowych. Problemem okazał się jednak sposób jego implementacji.

Zamiast bezpiecznego mechanizmu, takiego jak losowy identyfikator sesji generowany po stronie serwera lub podpisany token (np. JWT), ciasteczko zawierało [obiekt JSON](https://www.w3schools.com/js/js_json_objects.asp) zakodowany przy użyciu [Base64](https://pl.wikipedia.org/wiki/Base64).

W praktyce oznaczało to, że użytkownik mógł:

- odczytać zawartość ciasteczka poprzez jego zdekodowanie,
- dowolnie modyfikować przechowywane dane (np. role, uprawnienia lub identyfikator użytkownika),
- ponownie zakodować zmienione dane i przesłać je do serwera.

Serwer bezkrytycznie ufał zawartości otrzymanego cookie i nie przeprowadzał żadnej dodatkowej weryfikacji. W efekcie mechanizm kontroli dostępu był faktycznie realizowany po stronie klienta.

Jest to klasyczny przykład błędu projektowego prowadzącego do łatwej eskalacji uprawnień oraz obejścia mechanizmów autoryzacji.

## Rozwiązanie

Po zalogowaniu się do systemu przy użyciu danych logowania z zadania otrzymujemy następujące cookie:

```eyJ1c2VybmFtZSI6ImthbmFyenljYV9oYWxpbmEiLCJpc0FkbWluIjpmYWxzZX0%3D```

Ze względu na standardy przesyłania danych w sieci (HTTP) cookie jest kodowane w 
formacie URL, co oznacza że znak `=` jest przedstawiony jako `%3D`

Po odkodowaniu URL otrzymujemy:

```eyJ1c2VybmFtZSI6ImthbmFyenljYV9oYWxpbmEiLCJpc0FkbWluIjpmYWxzZX0=```

Następnie dekodujemy ten tekst za pomocą [Base64](https://en.wikipedia.org/wiki/Base64), co daje nam obiekt JSON:

```json
{"username":"kanarzyca_halina","isAdmin":false}
```

Teraz wystarczy zmienić wartość pola `isAdmin` na `true` i ponownie zakodować 
dane w Base64 (w większości przeglądarek nie trzeba ponownie kodować URL)

```eyJ1c2VybmFtZSI6ImthbmFyenljYV9oYWxpbmEiLCJpc0FkbWluIjp0cnVlfQ==```

Po odświeżeniu strony z tym zmodyfikowanym cookie uzyskujemy dostęp do panelu 
administratora, gdzie znajduje się flaga zadania (na flagę należało zaczekać minutę
lub edytować plik JS).