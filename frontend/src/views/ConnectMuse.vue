<template>
  <div
    class="bg-gray-100 text-[#19596e] min-h-screen font-sans flex flex-col items-center pt-12 px-4 relative"
  >
    <!-- Title + Search -->
    <div class="w-full max-w-2xl flex justify-between items-center mb-6">
      <h1 class="text-3xl font-medium">Find Available Devices</h1>
      <button
        @click="searchDevices"
        class="bg-sky-400 text-[#19596e] font-medium px-4 py-2 rounded hover:bg-sky-500 transition"
      >
        Search
      </button>
    </div>

    <!-- Device List -->
    <div
      v-if="showDeviceList"
      class="w-full max-w-2xl bg-[#528aa3] text-white rounded-md p-4"
    >
      <div v-if="museDevices.length === 0" class="text-center py-4">
        No devices found.
      </div>
      <div
        v-for="(device, idx) in museDevices"
        :key="device.address || idx"
        class="flex justify-between font-bold text-lg mb-2 items-center"
      >
        <span>{{ device.name }}</span>
        <button
          :disabled="connecting || connected"
          @click="connectToDevice(device.address)"
          class="underline hover:text-gray-100 transition"
          :class="{ 'opacity-50': connecting || connected }"
        >
          {{
            connecting ? "Connecting..." : connected ? "Connected!" : "Connect"
          }}
        </button>
        <span class="ml-2">{{ connectStatus }}</span>
      </div>
    </div>

    <!-- Back and Next Buttons -->
    <div class="absolute bottom-6 left-6">
      <button
        @click="goBack"
        class="bg-gray-300 text-[#19596e] px-6 py-3 rounded-lg hover:bg-gray-400 transition"
      >
        Back
      </button>
    </div>

    <div class="absolute bottom-6 right-6">
      <button
        @click="goNext"
        class="bg-[#19596e] text-white px-6 py-3 rounded-lg hover:bg-gray-400 transition"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { fetchDevices, connectMuse } from "../api.js";
const showDeviceList = ref(true);
const connecting = ref(false);
const connected = ref(false);
const connectStatus = ref("");
const router = useRouter();
const museDevices = ref([]);

async function searchDevices() {
  showDeviceList.value = true;
  connectStatus.value = "";
  connecting.value = false;
  connected.value = false;
  try {
    const response = await fetchDevices();
    museDevices.value = response.data;
  } catch (error) {
    console.log("Failed to fetch devices: ", error);
  }
}

async function connectToDevice(address) {
  connectStatus.value = "Connecting...";
  connecting.value = true;
  try {
    const response = await connectMuse(address);
    console.log(response);
    if (response.data == "Streaming"){
      connectStatus.value = "Connected!";
      connected.value = true; 
      connecting.value = false;
    }
    else {
      connectStatus.value = "Not Connected";
      connected.value = false;
    }

  } catch (error) {
    console.log(error);
  }
}

function goBack() {
  router.push({ name: "Home" });
}

function goNext() {
  //if (connected.value == true){
  router.push({ name: "MuseData" });
  //}
}
</script>

<!-- Tailwind CSS is assumed to be globally included in the project -->
