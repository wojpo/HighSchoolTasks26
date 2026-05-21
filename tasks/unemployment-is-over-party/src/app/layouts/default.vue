<template>
  <div class="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-800">
    <!-- Navbar: Grodzki Urząd Pracy -->
    <Navbar />
    <main class="flex-grow max-w-6xl w-full mx-auto px-4 py-8">
      <slot />
    </main>

    <footer class="bg-blue-800 text-blue-200 text-center py-6 mt-auto">
      <p>&copy; 2026 Grodzki Urząd Pracy w Krakowie. Wszelkie prawa zastrzeżone.</p>
    </footer>
  </div>
</template>
