<template>
  <div
    class="bg-gray-100 text-[#19596e] min-h-screen flex flex-col items-center justify-center font-sans relative px-4"
  >
    <!-- STEP 1: File Selection -->
    <div v-if="step === 1" class="flex flex-col items-center">
      <h1 class="text-2xl md:text-3xl font-medium text-center mb-8">
        Select Muse data to load to Glove
      </h1>
      <div class="flex gap-8 justify-center w-full max-w-4xl">
        <!-- File List -->
        <div
          class="bg-[#528aa3] text-white rounded-md p-6 w-64 flex flex-col gap-4 text-lg font-normal"
        >
          <div
            v-for="file in files"
            :key="file"
            class="cursor-pointer hover:underline"
            :class="{ 'font-bold underline': selectedFile === file }"
            @click="selectFile(file)"
          >
            {{ file }}
          </div>
        </div>

        <!-- Load/New Buttons -->
        <div class="flex flex-col justify-center gap-6">
          <button
            @click="loadFile"
            class="bg-sky-400 text-[#19596e] px-6 py-3 rounded hover:bg-sky-500 transition"
          >
            Load
          </button>
          <button
            @click="goToNew"
            class="bg-sky-400 text-[#19596e] px-6 py-3 rounded hover:bg-sky-500 transition"
          >
            New
          </button>
        </div>
      </div>
    </div>

    <!-- STEP 2: Loading -->
    <div
      v-if="step === 2"
      class="flex flex-col items-center justify-center text-center"
    >
      <h2 class="text-xl md:text-2xl font-medium">
        Loading screen here maybe<br />while waiting for the Pi to confirm data
        is sent
      </h2>
    </div>

    <!-- STEP 3: Success -->
    <div
      v-if="step === 3"
      class="flex flex-col items-center justify-center text-center"
    >
      <h1 class="text-2xl md:text-3xl font-medium mb-8">
        Select Muse data to load to Glove
      </h1>
      <div class="bg-[#528aa3] text-white px-12 py-6 rounded-md text-xl">
        Data successfully sent
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

    <!-- Next Button for Step 3 -->
    <div v-if="step === 3" class="absolute bottom-6 right-6">
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
import { ref } from "vue";
import { useRouter } from "vue-router";
import { onMounted } from "vue";


const step = ref(1);
const files = ref([]);
const selectedFile = ref(null);
const router = useRouter();

function selectFile(file) {
  selectedFile.value = file;
}

function loadFile() {
  if (!selectedFile.value) {
    alert("Please select a file to load.");
    return;
  }
  step.value = 2;
  setTimeout(() => {
    step.value = 3;
  }, 2000);
}

function goToNew() {
  router.push({ name: "Calibration" });
}

function goBack() {
  router.push({ name: "ConnectMuse" });
}

function goNext() {
  router.push({ path: "Final" });
}

onMounted(async () => {
  try {
    const response = await fetch("http://localhost:8000/api/list-csv");
    const data = await response.json();
    files.value = data.files;
    console.log(data)
  } catch (err) {
    console.error("Failed to load files:", err);
  }
});

</script>

<!-- Tailwind CSS is assumed to be globally included in the project -->
