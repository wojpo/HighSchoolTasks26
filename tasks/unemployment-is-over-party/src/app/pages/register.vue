<script setup>
const username = ref('')
const password = ref('')
const error = ref('')

const register = async () => {
  try {
    const res = await $fetch('/api/auth/register', {
      method: 'POST',
      body: { username: username.value, password: password.value }
    })
    if (res.success) {
      window.location.href = '/ticket'
    }
  } catch (err) {
    error.value = err.data?.message || 'Błąd rejestracji'
  }
}
</script>

<template>
  <div class="max-w-md mx-auto bg-white p-8 rounded-xl shadow-sm border border-slate-200 mt-10">
    <h2 class="text-2xl font-bold text-blue-800 mb-6 text-center">
      Rejestracja w systemie
    </h2>

    <form
      class="space-y-4"
      @submit.prevent="register"
    >
      <div
        v-if="error"
        class="bg-red-50 text-red-600 p-3 rounded-md text-sm border border-red-200"
      >
        {{ error }}
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Nazwa użytkownika</label>
        <input
          v-model="username"
          type="text"
          required
          class="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-700 mb-1">Hasło</label>
        <input
          v-model="password"
          type="password"
          required
          class="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
      </div>

      <button
        type="submit"
        class="w-full bg-blue-600 text-white font-medium py-2 px-4 rounded-md hover:bg-blue-700 transition"
      >
        Utwórz konto
      </button>

      <p class="text-center text-sm text-slate-600 mt-4">
        Masz już konto? <NuxtLink
          to="/login"
          class="text-blue-600 hover:underline"
        >Zaloguj się</NuxtLink>
      </p>
    </form>
  </div>
</template>
