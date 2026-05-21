<script setup>
import { useAuthState } from '~/composables/useAuthState'
import { useRoute, useRequestHeaders } from '#app'

const route = useRoute()
const ticketId = route.params.id

const headers = useRequestHeaders(['cookie'])
const { data: userResponse } = await useAsyncData('user', () => $fetch('/api/auth/me', { headers }))

const isAdmin = computed(() => {
  return !!userResponse.value?.user?.is_admin
})

const currentUsername = computed(() => userResponse.value?.user?.username)

const authState = useAuthState()

// THE VULNERABILITY SOURCE!
// During SSR, the bot visits this page. The bot sets the CURRENT USER for this ticket
// to its OWN username. Because authState is a module-level Map, this leaks to the user!
if (ticketId && currentUsername.value) {
  authState.setCurrentUser(ticketId, currentUsername.value)
}

const ticket = ref(null)
const isClosed = ref(false)
const message = ref('')

const fetchTicket = async () => {
  try {
    const res = await $fetch(`/api/ticket/${ticketId}`)
    ticket.value = res.ticket
    isClosed.value = res.ticket.is_closed || false
  } catch {
    message.value = 'Nie znaleziono zgłoszeń'
  }
}

onMounted(() => {
  fetchTicket()
})

const acceptTicket = async () => {
  try {
    const res = await $fetch('/api/ticket/accept', {
      method: 'POST',
      body: { ticket_id: ticketId }
    })
    if (res.success) {
      message.value = 'Zaakceptowano'
      fetchTicket()
    }
  } catch (err) {
    message.value = 'Błąd: ' + (err.data?.message || err.message)
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-sm border border-red-200">
    <div class="bg-red-600 text-white px-4 py-2 rounded-t-lg -mx-8 -mt-8 mb-6 font-bold flex justify-between items-center">
      <span>Panel Administracyjny - Bot Weryfikujący</span>
      <span class="text-xs bg-red-800 px-2 py-1 rounded">Wymagane uprawnienia</span>
    </div>

    <div
      v-if="!isAdmin"
      class="text-red-600 p-4 bg-red-50 rounded"
    >
      Odmowa dostępu. Zaloguj się jako administrator.
    </div>
    <div v-else>
      <div
        v-if="message"
        class="bg-slate-100 p-3 rounded mb-4 font-mono text-sm"
      >
        {{ message }}
      </div>

      <div v-if="ticket">
        <p class="mb-2">
          <strong>Zgłoszenie:</strong> {{ ticket.id }}
        </p>
        <p class="mb-4">
          <strong>Status:</strong>
          <span v-if="ticket.is_accepted">Zaakceptowane</span>
          <span v-else-if="isClosed">Zamknięte/Odrzucone</span>
          <span v-else>Oczekujące</span>
        </p>

        <button
          v-if="!ticket.is_accepted && !isClosed"
          class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
          @click="acceptTicket"
        >
          ZAAKCEPTUJ ZGŁOSZENIE
        </button>
      </div>
    </div>
  </div>
</template>
