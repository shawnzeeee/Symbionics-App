<template>
  <div class="bg-gray-100 text-[#19596e] min-h-screen font-sans relative flex flex-col items-center justify-center px-4">
    <!-- STEP 1: Start Calibration -->
    <div v-if="step === 1" class="flex flex-col items-center">
      <h1 class="text-2xl font-semibold mb-8">Calibration of Muse device</h1>
      <button 
        @click="nextStep" 
        class="bg-[#528aa3] text-white px-10 py-6 rounded-md text-lg text-center"
      >
        Press to start<br>3 min calibration video
      </button>
    </div>

    <!-- STEP 2: Calibration Video -->
    <div v-if="step === 2" class="flex flex-col items-center">
      <h1 class="text-2xl font-semibold mb-8">Calibration of Muse device</h1>
      <div class="bg-[#528aa3] text-white px-10 py-6 rounded-md text-lg text-center">
        *Insert python script video here*
      </div>
      <button 
        @click="nextStep" 
        class="mt-8 bg-sky-400 text-[#19596e] px-6 py-2 rounded hover:bg-sky-500 transition">
        Continue
      </button>
    </div>

    <!-- STEP 3: Enter File Name -->
    <div v-if="step === 3" class="flex flex-col items-center">
      <h1 class="text-2xl font-semibold mb-8">Calibration of Muse device</h1>
      <div class="bg-[#528aa3] text-white p-6 rounded-md text-center w-72">
        <label class="block mb-4">Enter file name for EEG data:</label>
        <input v-model="filename" type="text" placeholder="e.g., trial1.csv"
               class="w-full text-[#19596e] px-3 py-2 rounded" />
      </div>
      <button 
        @click="saveFile" 
        class="mt-6 bg-sky-400 text-[#19596e] px-6 py-2 rounded hover:bg-sky-500 transition">
        Save
      </button>
    </div>

    <!-- STEP 4: Confirmation -->
    <div v-if="step === 4" class="flex flex-col items-center">
      <h1 class="text-2xl font-semibold mb-8">Calibration of Muse device</h1>
      <div class="bg-[#528aa3] text-white px-12 py-6 rounded-md text-xl">
        Data file saved!
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

    <!-- Return to Muse Data Screen Button -->
    <div class="absolute bottom-6 right-6">
      <button 
        @click="goToMuseData" 
        class="bg-[#19596e] text-white px-6 py-2 rounded hover:bg-[#144452] transition"
      >
        Return to Muse Data Screen
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const step = ref(1)
const filename = ref('')
const router = useRouter()

function nextStep() {
  if (step.value < 4) step.value++
}

function saveFile() {
  if (!filename.value) {
    alert('Please enter a file name.')
    return
  }
  // Placeholder save logic — replace with actual file save
  console.log('Saving EEG data as:', filename.value)
  step.value = 4
}

function goBack() {
  if (step.value > 1) {
    step.value--
  } else {
    router.push({ name: 'CheckElectrodes' })
  }
}

function goToMuseData() {
  router.push({ name: 'MuseData' })
}
</script>

<!-- Tailwind CSS is assumed to be globally included in the project -->
