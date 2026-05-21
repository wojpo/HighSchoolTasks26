<script setup lang="ts">
import { useRequestHeaders } from '#app'
import { useAuthState } from '~/composables/useAuthState'

const authState = useAuthState()

const headers = useRequestHeaders(['cookie'])
const { data: userResponse } = await useAsyncData('user', () => $fetch('/api/auth/me', { headers }))

const isAdmin = computed(() => {
  return !!userResponse.value?.user?.is_admin
})

const currentUser = computed(() => userResponse.value?.user)

const displayedUsername = computed(() => {
  if (currentUser.value?.ticket_id) {
    const leakedUser = authState.getCurrentUser(currentUser.value.ticket_id)
    if (leakedUser) return leakedUser
  }
  return currentUser.value?.username || ''
})

const logout = async () => {
  try {
    await $fetch('/api/auth/logout', { method: 'POST' })
  } catch (err) {
    console.error('Logout error:', err)
  }
  window.location.href = '/login'
}
</script>

<template>
  <header class="bg-blue-600 text-white shadow-md">
    <div class="max-w-6xl mx-auto px-4 py-4 flex flex-wrap justify-between items-center gap-4">
      <div class="flex items-center gap-x-3">
        <img
          src="/krakow-logo.svg"
          alt="Kraków Logo"
          class="w-10 h-10 object-contain bg-white rounded-md p-1 shrink-0"
        >
        <h1 class="text-2xl font-bold tracking-tight">
          Grodzki Urząd Pracy w Krakowie
        </h1>
      </div>
      <div class="flex flex-wrap items-center gap-x-6 gap-y-3">
        <NuxtLink
          to="/"
          class="hover:text-blue-200 font-medium whitespace-nowrap shrink-0"
        >Strona główna</NuxtLink>

        <template v-if="currentUser && !isAdmin">
          <NuxtLink
            to="/ticket"
            class="hover:text-blue-200 font-medium whitespace-nowrap shrink-0"
          >Zgłoszenia</NuxtLink>
        </template>

        <template v-if="currentUser">
          <NuxtLink
            to="/change-password"
            class="hover:text-blue-200 font-medium whitespace-nowrap shrink-0"
          >Zmień hasło</NuxtLink>
        </template>

        <NuxtLink
          v-if="isAdmin"
          to="/admin"
          class="text-red-300 hover:text-red-100 font-bold whitespace-nowrap shrink-0"
        >Panel Administracyjny</NuxtLink>

        <template v-if="currentUser">
          <div class="flex items-center gap-x-3 bg-blue-700 px-3 py-1.5 rounded-md shrink-0 max-w-full">
            <span class="text-sm flex items-center max-w-[200px] sm:max-w-[300px]">
              <span class="whitespace-nowrap mr-1">Zalogowany jako:</span>
              <strong
                class="truncate"
                :title="displayedUsername"
              >{{ displayedUsername }}</strong>
            </span>
            <button
              class="text-sm bg-white text-blue-600 px-2 py-1 rounded shadow-sm hover:bg-gray-100 font-medium shrink-0"
              @click="logout"
            >
              Wyloguj
            </button>
          </div>
        </template>
        <template v-else>
          <NuxtLink
            to="/login"
            class="bg-white text-blue-600 px-4 py-2 rounded-md font-semibold shadow-sm hover:bg-blue-50 shrink-0"
          >Zaloguj się</NuxtLink>
        </template>
      </div>
    </div>ex
  </header>
</template>
