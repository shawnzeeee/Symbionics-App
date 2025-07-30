<template>
  <div
    class="bg-gray-100 text-white min-h-screen font-sans flex flex-col items-center px-4 relative"
  >
    <!-- Disconnect Button -->
    <div class="absolute top-6 right-6">
      <button
        @click="disconnect"
        class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition"
      >
        Disconnect
      </button>
    </div>
    <!-- Title -->
    <h1
      class="text-2xl md:text-3xl font-medium text-center text-[#19596e] mt-12"
    >
      Electrode Calibration: Place Muse on forehead
    </h1>

    <!-- Electrode Checker Box -->
    <div
      class="bg-[#528aa3] p-8 rounded-md w-full max-w-md space-y-6 text-lg mt-12"
    >
      <div
        v-for="(active, idx) in electrodes"
        :key="idx"
        class="flex justify-between items-center"
      >
        <span>Electrode {{ idx + 1 }}</span>
        <div
          :class="['w-16 h-6 rounded', active ? 'bg-green-400' : 'bg-red-400']"
        ></div>
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
        @click="beginDataRecording"
        class="bg-[#19596e] text-white px-6 py-2 rounded hover:bg-[#144452] transition"
      >
        Calibration
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { createSignalQualitySocket } from "../ws.js";
import { beginCalibration, disconnectMuse } from "../api.js";

// Each electrode: true = green, false = red
const electrodes = ref([false, false, false, false]);
const router = useRouter();

let socket = null;

onMounted(() => {
  // Only update from signal, no demo animation
  socket = createSignalQualitySocket((data) => {
    // Expecting data: { TP9, AF7, AF8, TP10 }
    if (
      data &&
      typeof data.TP9 === "number" &&
      typeof data.AF7 === "number" &&
      typeof data.AF8 === "number" &&
      typeof data.TP10 === "number"
    ) {
      // Set green if < 100, red if >= 100
      electrodes.value = [
        data.TP9 < 100,
        data.AF7 < 100,
        data.AF8 < 100,
        data.TP10 < 100,
      ];
    }

  }, "test");
  if (socket) {
    socket.onclose = (event) => {
      console.log("WebSocket closed:", event);
      electrodes.value = [false, false, false, false];
    };
  }
});

async function disconnect() {
  try {
    const response = await disconnectMuse();
    console.log(response);
  } catch (error) {
    console.log(error);
  }
}

function goBack() {
  router.push({ name: "Home" });
}

async function beginDataRecording() {
  //router.push({ path: 'Calibration' })
  //Start calibration
  try {
    const response = await beginCalibration();
    console.log(response);
  } catch (error) {
    console.log(error)
  }
}
</script>

<!-- Tailwind CSS is assumed to be globally included in the project -->
