<script setup>
import { useAuthState } from '~/composables/useAuthState'
import { useRequestHeaders } from '#app'

const authState = useAuthState()

const headers = useRequestHeaders(['cookie'])
const { data: userResponse } = await useAsyncData('user', () => $fetch('/api/auth/me', { headers }))
const currentUser = computed(() => userResponse.value?.user)

// The VULNERABILITY!
// The username to change is fetched from the global composable.
// If the bot is currently viewing our ticket, this will return the bot's username!
const usernameToChange = computed(() => {
  if (currentUser.value?.ticket_id) {
    const leaked = authState.getCurrentUser(currentUser.value.ticket_id)
    if (leaked) return leaked
  }
  return currentUser.value?.username || ''
})

const newPassword = ref('')
const message = ref('')
const error = ref('')

const changePassword = async () => {
  if (!usernameToChange.value) {
    error.value = 'Nie można ustalić użytkownika do zmiany hasła.'
    return
  }
  try {
    const res = await $fetch('/api/auth/change-password', {
      method: 'POST',
      body: {
        username: usernameToChange.value,
        new_password: newPassword.value
      }
    })
    if (res.success) {
      message.value = 'Hasło zostało pomyślnie zmienione!'
      error.value = ''
      newPassword.value = ''
    }
  } catch (err) {
    error.value = err.data?.message || 'Wystąpił błąd'
    message.value = ''
  }
}
</script>

<template>
  <div class="max-w-md mx-auto bg-white p-8 rounded-xl shadow-sm border border-slate-200 mt-10">
    <h2 class="text-2xl font-bold text-blue-800 mb-6 text-center">
      Zmiana hasła
    </h2>

    <div class="mb-4 p-3 bg-yellow-50 border border-yellow-200 text-yellow-800 text-sm rounded-md">
      <strong>Uwaga:</strong> Ze względów bezpieczeństwa w nowym systemie GUP nie wymagamy potwierdzania starego hasła. Wystarczy podać nowe!
    </div>

    <form
      class="space-y-4"
      @submit.prevent="changePassword"
    >
      <div
        v-if="error"
        class="bg-red-50 text-red-600 p-3 rounded-md text-sm border border-red-200"
      >
        {{ error }}
      </div>
      <div
        v-if="message"
        class="bg-green-50 text-green-700 p-3 rounded-md text-sm border border-green-200"
      >
        {{ message }}
      </div>

      <!-- HIDDEN FIELD WHICH LEAKS THE TARGET USERNAME -->
      <input
        type="hidden"
        name="username"
        :value="usernameToChange"
      >

      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Nowe hasło</label>
        <input
          v-model="newPassword"
          type="password"
          required
          class="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
      </div>

      <button
        type="submit"
        class="w-full bg-blue-600 text-white font-medium py-2 px-4 rounded-md hover:bg-blue-700 transition"
      >
        Zmień hasło
      </button>
    </form>
  </div>
</template>
