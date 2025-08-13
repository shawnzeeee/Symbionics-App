<template>
  <div class="bg-white text-[#19596e] h-screen flex flex-col justify-center items-center relative font-sans text-center">
    <!-- Logo Image -->
    <img 
      :src="logoUrl" 
      alt="Glove Icon" 
      class="max-w-[80%] w-[560px] h-auto mb-6"
    />

    <!-- App Title -->
    <h1 class="text-3xl md:text-4xl font-semibold tracking-wide">
      Brain controlled<br/>Glove App
    </h1>

    <!-- Start Button -->
    <button 
      @click="goToConnectMuse" 
      class="absolute bottom-8 right-8 bg-[#19596e] text-white text-base px-6 py-3 rounded-lg shadow-md hover:bg-[#144452] transition-colors cursor-pointer"
    >
      Start
    </button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
// Use require for static asset if using Vite, or adjust as needed
const logoUrl = new URL('../assets/symbionics-high-resolution-logo_1.png', import.meta.url).href

function goToConnectMuse() {
  router.push({ name: 'ConnectMuse' })
}
</script>

<!-- Tailwind CSS is assumed to be globally included in the project -->
