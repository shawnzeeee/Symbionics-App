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
        :key="device.id"
        class="flex items-center justify-between py-2 border-b"
      >
        <span>{{ device.name }}</span>
        <button
          class="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
          @click="connectToDevice(device)"
        >
          Connect
        </button>
      </li>
    </ul>
    <div v-if="devices.length === 0 && !loading" class="text-gray-500 mt-4">
      No devices found.
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { fetchDevices } from "../../api.js";
const devices = ref([]);
const loading = ref(false);

// Dummy function to simulate fetching devices
async function getListOfDevices() {
  loading.value = true;
  try {
    const response = await fetchDevices();
    console.log("Fetched devices:", response); // Print the response to the console
    devices.value = response;
  } catch (error) {
    alert("Failed to fetch devices: " + error.message);
    devices.value = [];
  } finally {
    loading.value = false;
  }
}

function refreshDevices() {
  fetchDevices();
}

function connectToDevice(device) {
  // Replace with actual connect logic
  alert(`Connecting to ${device.name}...`);
}

// Fetch devices on mount
getListOfDevices();
</script>

<style scoped>
/* ...existing code... */
</style>
