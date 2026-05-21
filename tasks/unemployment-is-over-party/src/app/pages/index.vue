<script setup>
definePageMeta({
  title: 'Grodzki Urząd Pracy w Krakowie'
})
</script>

<template>
  <div class="space-y-8">
    <div class="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
      <h2 class="text-3xl font-bold text-blue-800 mb-4">
        Witaj w Grodzkim Urzędzie Pracy
      </h2>
      <p class="text-lg text-slate-600 leading-relaxed mb-6">
        Jesteśmy tutaj, aby pomóc Ci znaleźć idealną pracę. Nasz nowy system zgłoszeń rekrutacyjnych
        jest w pełni zautomatyzowany i obsługiwany przez najnowocześniejsze systemy AI (oraz naszych urzędników).
      </p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div class="p-6 bg-blue-50 rounded-lg border border-blue-100">
          <h3 class="text-xl font-semibold text-blue-700 mb-3">
            Dla Poszukujących Pracy
          </h3>
          <p class="text-slate-600 mb-4">
            Zarejestruj się, utwórz swój profil i złóż zgłoszenie aplikacyjne. Nasz zespół rozpatrzy Twoje zgłoszenie w przeciągu zaledwie 1 minuty!
          </p>
          <NuxtLink
            to="/register"
            class="inline-block bg-blue-600 text-white font-medium px-4 py-2 rounded shadow hover:bg-blue-700 transition"
          >Rozpocznij</NuxtLink>
        </div>
        <div class="p-6 bg-slate-50 rounded-lg border border-slate-200">
          <h3 class="text-xl font-semibold text-slate-700 mb-3">
            Dla Pracodawców
          </h3>
          <p class="text-slate-600 mb-4">
            Wkrótce dodamy moduł dla pracodawców. Obecnie skupiamy się na pomocy bezrobotnym w znalezieniu zatrudnienia.
          </p>
          <span class="inline-block bg-slate-200 text-slate-500 font-medium px-4 py-2 rounded cursor-not-allowed">Wkrótce</span>
        </div>
      </div>
    </div>
  </div>
</template>
