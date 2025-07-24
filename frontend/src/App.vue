<template>
  <div id="app">
    <DevicesList />
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router";
import DevicesList from "./components/DevicesList.vue";

import { getHello } from "./api";

async function fetchHello() {
  try {
    const data = await getHello();
    alert(data.message);
  } catch (error) {
    alert("Error" + error.message);
  }
}
</script>

<style scoped>
/* You can add custom styles here if needed */
</style>
