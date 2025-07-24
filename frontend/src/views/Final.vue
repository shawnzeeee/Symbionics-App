<template>
  <div class="bg-gray-100 text-[#19596e] h-screen flex flex-col items-center justify-center font-sans relative">
    <!-- Final Message -->
    <h1 class="text-3xl font-semibold mb-6 text-center">You're all set!</h1>
    <div class="bg-[#528aa3] text-white px-10 py-6 rounded-md text-xl text-center">
      The Muse data has been loaded,<br> and calibration is complete.
    </div>

    <!-- Button Options -->
    <div class="absolute bottom-6 w-full flex justify-between px-6">
      <button 
        @click="goHome"
        class="bg-sky-400 text-[#19596e] px-6 py-2 rounded hover:bg-sky-500 transition">
        Back to Home
      </button>

      <button 
        @click="goToMuseData"
        class="bg-[#19596e] text-white px-6 py-2 rounded hover:bg-[#144452] transition">
        Load New Data
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

function goHome() {
  router.push({ name: 'Home' })
}

function goToMuseData() {
  router.push({ name: 'MuseData' })
}
</script>

<!-- Tailwind CSS is assumed to be globally included in the project -->
