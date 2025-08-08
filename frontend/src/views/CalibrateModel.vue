<template>
  <div class="min-h-screen flex flex-col items-center bg-gray-100 relative">
    <h1 class="text-4xl text-[#075776] mt-10">Calibrate the model</h1>
    <div class="relative flex items-center justify-center mt-10">
      <!-- Blue Column -->
      <div class="relative w-32 h-[500px] bg-[#4c89a3] overflow-hidden">
        <!-- Dynamic Loading Bar -->
        <div
          class="absolute left-0 w-full bg-[#58c2ff] transition-all duration-300 z-0 rounded"
          :style="{ bottom: '0px', height: progressHeight + '%' }"
        ></div>
      </div>

      <!-- Control Buttons -->
      <div class="flex flex-col justify-between h-[500px] ml-4 z-10">
        <div class="flex flex-col gap-2">
          <button @click="increaseTop" class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center">+</button>
          <button @click="decreaseTop" class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center">-</button>
        </div>
        <div class="flex flex-col gap-2">
          <button @click="increaseBottom" class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center">+</button>
          <button @click="decreaseBottom" class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center">-</button>
        </div>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <button @click="goBack" class="absolute bottom-5 left-5 bg-[#58c2ff] text-white px-4 py-2 text-lg rounded z-10">Back</button>
    <button @click="loadModel" class="absolute bottom-5 right-5 bg-[#19596e] text-white px-6 py-2 text-lg rounded hover:bg-[#144452] transition z-10">Load</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, onMounted } from 'vue';

const router = useRouter();
const progressHeight = ref(0); // 0 to 100

function increaseTop() {
  console.log('Increase Top');
}

function decreaseTop() {
  console.log('Decrease Top');
}

function increaseBottom() {
  console.log('Increase Bottom');
}

function decreaseBottom() {
  console.log('Decrease Bottom');
}

function goBack() {
  router.back();
}

function loadModel() {
  console.log('Load model');
  // Add your model loading logic here
}

// Simulated backend update loop
onMounted(() => {
  setInterval(async () => {
    try {
      // Replace with actual fetch logic
      const simulatedValue = Math.floor(Math.random() * 101); // 0–100
      progressHeight.value = simulatedValue;
    } catch (err) {
      console.error('Failed to fetch progress:', err);
    }
  }, 1000); // Poll every 1 second
});
</script>

<style scoped>
/* No scoped styles needed since TailwindCSS is used */
</style>
