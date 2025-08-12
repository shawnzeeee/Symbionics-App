<template>
  <div class="min-h-screen flex flex-col items-center bg-gray-100 relative">
    <h1 class="text-4xl text-[#075776] mt-10">Calibrate the model</h1>
    <!-- Meter -->
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
          <span class="text-[#19596e] text-sm">Adder</span>
          <button @click="increaseTop" class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center">
            +
          </button>
          <button @click="decreaseTop" class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center"
          >
            -
          </button>
          <span class="mt-1 text-[#19596e] text-sm">= {{ attention_adder }}</span>

        </div>
        <div class="flex flex-col gap-2">
          <span class="text-[#19596e] text-sm">Subtractor</span>
          <button @click="increaseBottom" class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center"
          >
            +
          </button>
          <button @click="decreaseBottom" class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center"
          >
            -
          </button>
          <span class="mt-1 text-[#19596e] text-sm">= {{ attention_subtractor }}</span>
        </div>
      </div>
    </div>
    
    <!-- Live readouts -->
    <div class="mt-6 flex gap-4 text-[#19596e]">
      <div class="bg-white rounded px-3 py-2 shadow">Threshold: <b>{{ threshold }}</b></div>
      <div class="bg-white rounded px-3 py-2 shadow">Adder: <b>{{ attention_adder }}</b></div>
      <div class="bg-white rounded px-3 py-2 shadow">Subtractor: <b>{{ attention_subtractor }}</b></div>
    </div>
    
    <!-- Navigation Buttons -->
    <button
      @click="goBack"
      class="absolute bottom-5 left-5 bg-[#58c2ff] text-white px-4 py-2 text-lg rounded z-10"
    >
      Back
    </button>
    <button
      @click="loadModel"
      class="absolute bottom-5 right-5 bg-[#19596e] text-white px-6 py-2 text-lg rounded hover:bg-[#144452] transition z-10"
    >
      Load
    </button>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router";
import { ref, onMounted } from "vue";
import { createAttentionThresholdSocket } from "../ws.js";
import { trainSVM, beginPylslStream, loadFileToGlove } from "../api.js";

const router = useRouter();
const progressHeight = ref(0); // 0 to 100
const SCALE_MIN = 0;
const SCALE_MAX = 220;
const clamp = (n, a, b) => Math.max(a, Math.min(b, n));

const route = useRoute();
const selectedFile = ref(route.params.filename);
const attention_adder = ref(15);
const attention_subtractor = ref(15);

let socket = null;

function increaseTop() {
  attention_adder.value++;
  sendAttentionValues();
}

function decreaseTop() {
  attention_adder.value--;
  sendAttentionValues();
}

function increaseBottom() {
  attention_subtractor.value++;
  sendAttentionValues();
}

function decreaseBottom() {
  attention_subtractor.value--;
  sendAttentionValues();
}

function sendAttentionValues() {
  if (socket && socket.readyState === 1) {
    socket.send(
      JSON.stringify({
        attention_adder: attention_adder.value,
        attention_subtractor: attention_subtractor.value,
      })
    );
  }
}

function goBack() {
  //add thread closing logic here
  router.back();
}

//helper function to convert 0-220 to 0-100 for display on the bar
function getDataNumber(msg) {
  let payload = msg;
  if (typeof msg === "string") {
    try { payload = JSON.parse(msg); } catch {}
  }

  // e.g., { gesture: 'O', attention_threshold: 35 }
  const raw =
    typeof payload === "number" ? payload :
    payload?.attention_threshold ?? payload?.progress ?? payload?.value ?? 0;

  const val = clamp(Number(raw), SCALE_MIN, SCALE_MAX);     // 0..220
  const pct = ((val - SCALE_MIN) / (SCALE_MAX - SCALE_MIN)) * 100; // 0..100
  progressHeight.value = Math.round(pct);
}

async function loadModel() {
  //add thread closing logic here too

  console.log("sending csv file to pi: ", selectedFile.value);
  try{
    const response = await loadFileToGlove(selectedFile.value)
    console.log(response)
    if (response.success == true){
      router.push({ path: "Final" });
    }
  }catch(error){
    console.log(error)
  }
}

onMounted(async () => {
  console.log("Selected file:", selectedFile.value);
  try {
    console.log("training SVM");
    const training_response = await trainSVM(selectedFile.value);
    console.log("trainSVM:", training_response);

    console.log("beginning pylsl");
    const stream_response =await beginPylslStream(selectedFile.value);
    console.log("beginPylslStream:", stream_response);

    socket = createAttentionThresholdSocket((data) => {
      console.log(data);
      console.log(getDataNumber(data))
    });

    if (socket) {
      socket.onclose = (event) => {
        console.log("WebSocket closed:", event);
      };
    }
  } catch (error) {
    console.log(error);
  }

  //Train SVM
  //Wait for response
  //Open websocket and read the real time classification

  // socket = await createAttentionThresholdSocket((data) => {
  //   progressHeight.value = data
  // }, selectedFile.value)w
});
</script>

<style scoped>
/* No scoped styles needed since TailwindCSS is used */
</style>
