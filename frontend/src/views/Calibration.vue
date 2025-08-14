<template>
  <div
    class="bg-gray-100 text-[#19596e] min-h-screen font-sans relative flex flex-col items-center justify-center px-4"
  >
    <!-- STEP 1: Enter File Name -->
    <div v-if="step === 1" class="flex flex-col items-center">
      <h1 class="text-2xl font-semibold mb-8">Calibration of Muse device</h1>
      <div class="bg-[#528aa3] text-white p-6 rounded-md text-center w-72">
        <label class="block mb-4">Enter file name for EEG data:</label>
        <input
          v-model="filename"
          type="text"
          placeholder="e.g., trial1.csv"
          class="w-full text-[#19596e] bg-white px-3 py-2 rounded"
        />
      </div>
      <button
        @click="beginDataCollection"
        class="mt-6 bg-[#19596e] text-white px-6 py-2 rounded hover:bg-sky-500 transition cursor-pointer"
      >
        Start Calibration
      </button>
    </div>

    <!-- Back Button -->
    <div class="absolute bottom-6 left-6">
      <button
        @click="goBack"
        class="bg-sky-400 text-[#19596e] px-6 py-2 rounded hover:bg-sky-500 transition cursor-pointer"
      >
        Back
      </button>
    </div>

    <!-- Return to Muse Data Screen Button -->
    <div class="absolute bottom-6 right-6">
      <button
        @click="goToMuseData"
        class="bg-[#19596e] text-white px-6 py-2 rounded hover:bg-[#144452] transition cursor-pointer"
      >
        Return to Muse Data Screen
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { beginPylslStream } from "../api.js";

const step = ref(1);
const filename = ref("");
const router = useRouter();

function nextStep() {
  if (step.value < 4) step.value++;
}

async function beginDataCollection() {
  try {
    await beginPylslStream(filename.value);
    router.push({ name: "CheckElectrodes" });
  } catch (error) {
    console.log(error);
  }
}

function saveFile() {
  if (!filename.value) {
    alert("Please enter a file name.");
    return;
  }
  // Placeholder save logic — replace with actual file save
  console.log("Saving EEG data as:", filename.value);
  step.value = 2;
}

function goBack() {
  if (step.value > 1) {
    step.value--;
  } else {
    router.push({ name: "MuseData" });
  }
}

function goToMuseData() {
  router.push({ name: "MuseData" });
}
</script>

<!-- Tailwind CSS is assumed to be globally included in the project -->
