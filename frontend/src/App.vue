<template>
  <div
    class="min-h-screen bg-gradient-to-br from-blue-50 to-white flex flex-col items-center justify-center px-4 py-12"
  >
    <div class="max-w-2xl w-full bg-white rounded-xl shadow-lg p-8">
      <h1 class="text-4xl font-bold text-blue-700 mb-4 text-center">
        About Symbionics
      </h1>
      <p class="text-lg text-gray-700 mb-6 text-center">
        <span class="font-semibold">Symbionics</span> is a pioneering BCI
        (Brain-Computer Interface) company dedicated to bridging the gap between
        human cognition and technology. Our mission is to empower individuals
        and organizations with seamless neural interfaces, enabling new
        possibilities in communication, control, and accessibility.
      </p>
      <div class="mb-6">
        <h2 class="text-2xl font-semibold text-blue-600 mb-2">Our Vision</h2>
        <p class="text-gray-600">
          We envision a world where the boundaries between mind and machine are
          dissolved, unlocking human potential and enhancing quality of life
          through safe, ethical, and innovative BCI solutions.
        </p>
      </div>
      <div>
        <h2 class="text-2xl font-semibold text-blue-600 mb-2">What We Do</h2>
        <ul class="list-disc list-inside text-gray-600">
          <li>Develop advanced neural interface technologies</li>
          <li>Collaborate with healthcare, research, and tech partners</li>
          <li>Promote accessibility and inclusivity through BCI</li>
          <li>Drive ethical standards in neurotechnology</li>
        </ul>
      </div>
    </div>
    <button @click="fetchHello">Get Hello</button>
    <footer class="mt-8 text-gray-400 text-sm">
      &copy; 2025 Symbionics. All rights reserved.
    </footer>
  </div>
</template>

<script setup>
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
