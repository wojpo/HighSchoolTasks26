<script setup>
import { useRequestHeaders } from '#app'

const headers = useRequestHeaders(['cookie'])
const { data: userResponse } = await useAsyncData('user', () => $fetch('/api/auth/me', { headers }))

const isAdmin = computed(() => {
  return !!userResponse.value?.user?.is_admin
})

const tickets = ref([])
const error = ref('')

const fetchTickets = async () => {
  if (!isAdmin.value) return
  try {
    const res = await $fetch('/api/admin/tickets')
    tickets.value = res.tickets
  } catch {
    error.value = 'Błąd pobierania zgłoszeń'
  }
}

onMounted(() => {
  fetchTickets()
})
</script>

<template>
  <div class="max-w-4xl mx-auto bg-white p-8 rounded-xl shadow-sm border border-red-200">
    <div class="bg-red-600 text-white px-4 py-2 rounded-t-lg -mx-8 -mt-8 mb-6 font-bold flex justify-between items-center">
      <span>Panel Administracyjny - Zarządzanie Zgłoszeniami</span>
      <span class="text-xs bg-red-800 px-2 py-1 rounded">Admin Only</span>
    </div>

    <div
      v-if="!isAdmin"
      class="text-red-600 p-4 bg-red-50 rounded"
    >
      Odmowa dostępu. Zaloguj się jako administrator.
    </div>
    <div v-else>
      <div
        v-if="error"
        class="bg-red-50 text-red-600 p-3 rounded mb-4"
      >
        {{ error }}
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full bg-white border border-slate-200 rounded-md">
          <thead class="bg-slate-100 border-b border-slate-200">
            <tr>
              <th class="py-3 px-4 text-left font-semibold text-slate-700">
                ID Zgłoszenia
              </th>
              <th class="py-3 px-4 text-left font-semibold text-slate-700">
                Użytkownik
              </th>
              <th class="py-3 px-4 text-left font-semibold text-slate-700">
                Status
              </th>
              <th class="py-3 px-4 text-left font-semibold text-slate-700">
                Akcje
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="ticket in tickets"
              :key="ticket.id"
              class="border-b border-slate-100 hover:bg-slate-50 transition"
            >
              <td class="py-3 px-4 font-mono text-sm">
                {{ ticket.id.substring(0, 12) }}...
              </td>
              <td class="py-3 px-4 font-medium">
                {{ ticket.username || 'Brak' }}
              </td>
              <td class="py-3 px-4">
                <span
                  v-if="ticket.is_accepted"
                  class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs"
                >Zaakceptowane</span>
                <span
                  v-else
                  class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs"
                >Otwarte</span>
              </td>
              <td class="py-3 px-4">
                <NuxtLink
                  :to="`/admin/ticket/${ticket.id}`"
                  class="text-blue-600 hover:text-blue-800 hover:underline text-sm font-medium"
                >
                  Szczegóły
                </NuxtLink>
              </td>
            </tr>
            <tr v-if="tickets.length === 0">
              <td
                colspan="4"
                class="py-6 text-center text-slate-500"
              >
                Brak zgłoszeń w systemie.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
