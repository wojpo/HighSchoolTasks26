## Opis

To zadanie polega na zidentyfikowaniu i wykorzystaniu błędu w systemie cacheowania pseudonimu aktualnego użytkownika.
W ramach tego systemu w composable `useAuthState.ts`:
```ts
// VULNERABILITY: Module-level state leak!
// This object is shared across all concurrent requests in the Node process.
const activeUsersObj: Ref<Record<string, string>> = ref({})

export const useAuthState = () => {
    const state = useState<Record<string, string>>('leaked_users_state', () => activeUsersObj)

    const setCurrentUser = (solverId: string, username: string) => {
        state.value[solverId] = username
        activeUsersObj.value[solverId] = username
    }

    const getCurrentUser = (solverId: string) => {
        return state.value[solverId] || null
    }

    return {
        setCurrentUser,
        getCurrentUser
    }
}
```

Przez zastosowanie ref na poziomie modułu, obiekt `activeUsersObj` jest współdzielony pomiędzy wszystkimi równoczesnymi requestami w Nuxtcie.
Oznacza to, że jeśli jeden użytkownik ustawi swój pseudonim, to każdy inny użytkownik, który wykona request w tym samym czasie, może odczytać ten pseudonim jako swój aktualny pseudonim.
W przypadku tego zadania użyta była mapa przechowują pary użytkownika oraz id rozwiązującego, aby zapewnić możliwość rozwiązania zadania przez wielu użytkowników jednocześnie.

## Rozwiązanie

Aby rozwiązać zadanie, należy wykonać następujące kroki:
1. Założyć konto na stronie `unemployment-is-over-party.hack4krak.pl` i zalogować się.
2. Utworzyć aplikacje do pracy.
3. Otworzyć stronę `/change-password` i wprowadzić nowe hasło.
4. Odświeżyć stronę i skopiować nazwę użytkownika administratora.
5. Wylogować się ze strony, zalogować na konto administratora i przejść do panelu administracyjnego.
6. Zaakceptować zgłoszenie aplikacji do pracy.
7. Zalogować się ponownie na swoje konto i otworzyć stronę `/ticket`, gdzie w wiadomości od administratora znajdziesz flagę.