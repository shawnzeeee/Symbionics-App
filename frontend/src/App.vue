<template>
    <div id="app">
      <!-- Add router-view for Vue Router -->
      <router-view />
    </div>
  
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'

import { getHello } from "../api";

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
