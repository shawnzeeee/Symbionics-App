<template>
  <div class="bg-gray-100 text-white min-h-screen font-sans flex flex-col items-center px-4 relative">
    <!-- Title -->
    <h1 class="text-2xl md:text-3xl font-medium text-center text-[#19596e] mt-12">
      Electrode Calibration: Place Muse on forehead
    </h1>

    <!-- Electrode Checker Box -->
    <div class="bg-[#528aa3] p-8 rounded-md w-full max-w-md space-y-6 text-lg mt-12">
      <div v-for="(active, idx) in electrodes" :key="idx" class="flex justify-between items-center">
        <span>Electrode {{ idx + 1 }}</span>
        <div :class="['w-16 h-6 rounded', active ? 'bg-green-400' : 'bg-gray-300']"></div>
      </div>
    </div>

    <!-- Back Button -->
    <div class="absolute bottom-6 left-6">
      <button 
        @click="goBack"
        class="bg-sky-400 text-[#19596e] px-6 py-2 rounded hover:bg-sky-500 transition"
      >
        Back
      </button>
    </div>

    <!-- Next Button -->
    <div class="absolute bottom-6 right-6">
      <button 
        @click="goNext"
        class="bg-[#19596e] text-white px-6 py-2 rounded hover:bg-[#144452] transition"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const electrodes = ref([false, false, false, false])
const router = useRouter()

onMounted(() => {
  electrodes.value.forEach((_, idx) => {
    setTimeout(() => {
      electrodes.value[idx] = true
    }, idx * 700)
  })
})

function goBack() {
  router.push({ name: 'ConnectMuse' })
}

function goNext() {
  router.push({ path: 'Calibration' })
}
</script>

<!-- Tailwind CSS is assumed to be globally included in the project -->
