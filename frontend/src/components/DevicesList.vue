<template>
  <div class="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold mb-4">Available Devices</h2>
    <button
      class="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      @click="refreshDevices"
      :disabled="loading"
    >
      {{ loading ? "Refreshing..." : "Refresh" }}
    </button>
    <ul>
      <li
        v-for="device in devices"
        :key="device.address"
        class="flex items-center justify-between py-2 border-b"
      >
        <span>{{ device.name }}</span>
        <button
          class="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 mr-2"
          @click="connectToDevice(device)"
        >
          Connect
        </button>
        <button
          class="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
          @click="disconnectFromDevice()"
        >
          Disconnect
        </button>
      </li>
    </ul>
    <div v-if="devices.length === 0 && !loading" class="text-gray-500 mt-4">
      No devices found.
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { fetchDevices, connectMuse, disconnectMuse } from "../api.js";
const devices = ref([{ name: "Muse-1234", address: "00:55:DA:B0:1E:78" }]);
const loading = ref(false);

// Dummy function to simulate fetching devices
async function getListOfDevices() {
  loading.value = true;
  try {
    const response = await fetchDevices();
    devices.value = response.data;
    console.log("Fetched devices:", devices);
  } catch (error) {
    alert("Failed to fetch devices: " + error.message);
    devices.value = [];
  } finally {
    loading.value = false;
  }
}

function refreshDevices() {
  getListOfDevices();
}

//Implement functionality to allow ONLY ONE connection at a time
async function connectToDevice(device) {
  try {
    const response = await connectMuse(device.address);
    console.log(response.data);
  } catch (error) {
    alert("Failed to connect to device: " + error.message);
  }
}

async function disconnectFromDevice() {
  try {
    const response = await disconnectMuse();
    console.log(response);
  } catch (error) {
    alert("Failed to disconnect from device: " + error.message);
  }
}
</script>

<style scoped>
/* ...existing code... */
</style>
