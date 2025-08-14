<template>
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

</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { createSignalQualitySocket } from "../ws.js";
import { beginCalibration, disconnectMuse } from "../api.js";

// Each electrode: true = green, false = red
const electrodes = ref([false, false, false, false]);


let socket = null;

onMounted(async () => {
  // Only update from signal, no demo animation
  console.log("mounted")
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


</script>