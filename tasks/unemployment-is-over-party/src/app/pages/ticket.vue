<script setup>
const ticket = ref(null)
const messages = ref([])
const error = ref('')
const replyContent = ref('')
const isClosed = ref(false)
const isLoading = ref(true)

const fetchTicket = async () => {
  try {
    const res = await $fetch('/api/ticket/current')
    ticket.value = res.ticket
    messages.value = res.messages
    isClosed.value = res.ticket?.is_closed
  } catch {
    error.value = 'Nie udało się pobrać zgłoszenia'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchTicket()
  setInterval(() => {
    if (!isLoading.value) fetchTicket()
  }, 3000)
})

const submitApplication = async () => {
  try {
    await $fetch('/api/ticket/submit', { method: 'POST' })
    error.value = ''
    fetchTicket()
  } catch (err) {
    error.value = err.data?.message || 'Błąd'
  }
}

const sendReply = async () => {
  try {
    await $fetch('/api/ticket/reply', {
      method: 'POST',
      body: { content: replyContent.value }
    })
    replyContent.value = ''
    fetchTicket()
  } catch (err) {
    error.value = err.data?.message || 'Błąd'
  }
}

const clearTicket = async () => {
  try {
    await $fetch('/api/ticket/clear', { method: 'POST' })
    ticket.value = null
    isClosed.value = false
    messages.value = []
  } catch (err) {
    error.value = err.data?.message || 'Błąd przy zamykaniu zgłoszenia'
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-sm border border-slate-200">
    <h2 class="text-3xl font-bold text-blue-800 mb-6">
      Twoje zgłoszenie o pracę
    </h2>

    <div
      v-if="error"
      class="bg-red-50 text-red-600 p-4 rounded-md mb-6 border border-red-200"
    >
      {{ error }}
    </div>

    <div
      v-if="isLoading"
      class="text-center p-8 text-slate-500"
    >
      Ładowanie...
    </div>

    <div
      v-else-if="!ticket"
      class="text-center p-8 border-2 border-dashed border-slate-300 rounded-lg"
    >
      <p class="text-slate-600 mb-4">
        Nie masz jeszcze żadnego otwartego zgłoszenia lub poprzednie zostało zamknięte.
      </p>
      <button
        class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition shadow-md w-full"
        @click="submitApplication"
      >
        Złóż wniosek do rozpatrzenia
      </button>
    </div>

    <div
      v-else
      class="space-y-6"
    >
      <div class="flex justify-between items-center border-b pb-4">
        <span class="text-slate-500">ID Zgłoszenia:</span>
        <span class="font-mono text-sm bg-slate-100 px-2 py-1 rounded">{{ ticket.id }}</span>
      </div>

      <div class="flex justify-between items-center border-b pb-4">
        <span class="text-slate-500">Status aplikacji:</span>
        <span
          v-if="ticket.is_accepted"
          class="text-green-600 font-bold bg-green-50 px-3 py-1 rounded border border-green-200"
        >ZAAKCEPTOWANE</span>
        <span
          v-else-if="isClosed"
          class="text-red-600 font-bold bg-red-50 px-3 py-1 rounded border border-red-200"
        >ZAMKNIĘTE / ODRZUCONE</span>
        <span
          v-else
          class="text-slate-600 font-bold bg-slate-50 px-3 py-1 rounded border border-slate-200"
        >W TRAKCIE ROZPATRYWANIA</span>
      </div>

      <div
        v-if="messages.length > 0"
        class="mt-8 border rounded-lg bg-slate-50 flex flex-col h-96"
      >
        <div class="flex-grow p-4 overflow-y-auto space-y-4">
          <div
            v-for="msg in messages"
            :key="msg.id"
            :class="['flex', msg.sender === 'user' ? 'justify-end' : 'justify-start']"
          >
            <div :class="['max-w-[70%] rounded-lg p-3', msg.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-white border text-slate-800']">
              <p class="text-xs opacity-75 mb-1">
                {{ msg.sender === 'user' ? 'Ty' : '~Administracja' }}
              </p>
              <p>{{ msg.content }}</p>
            </div>
          </div>
        </div>

        <div
          v-if="!ticket.is_accepted && !isClosed"
          class="p-4 bg-white border-t rounded-b-lg"
        >
          <form
            class="flex gap-2"
            @submit.prevent="sendReply"
          >
            <input
              v-model="replyContent"
              type="text"
              placeholder="Wpisz odpowiedź..."
              class="flex-grow px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
            <button
              type="submit"
              class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Wyślij
            </button>
          </form>
        </div>

        <div
          v-else-if="isClosed"
          class="p-4 bg-red-50 border-t rounded-b-lg text-center"
        >
          <p class="text-red-700 mb-3 font-medium">
            To zgłoszenie zostało zamknięte. Nie możesz już na nie odpowiadać.
          </p>
          <button
            class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-6 rounded-md transition shadow-sm"
            @click="clearTicket"
          >
            Zamknij widok i złóż nowy wniosek
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
