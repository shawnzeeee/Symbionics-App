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
          <button
            @click="increaseTop"
            class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center"
          >
            +
          </button>
          <button
            @click="decreaseTop"
            class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center"
          >
            -
          </button>
        </div>
        <div class="flex flex-col gap-2">
          <button
            @click="increaseBottom"
            class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center"
          >
            +
          </button>
          <button
            @click="decreaseBottom"
            class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center"
          >
            -
          </button>
        </div>
      </div>
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
import { trainSVM, beginPylslStream } from "../api.js";

const router = useRouter();
const progressHeight = ref(0); // 0 to 100
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
  router.back();
}

async function loadModel() {
  console.log(selectedFile.value);
  // try{
  //   const response = await loadFileToGlove(selectedFile.value)
  //   console.log(response)
  //   if (response.success == true){
  //     router.push({ path: "Final" });
  //   }
  // }catch(error){
  //   console.log(error)
  // }
}

onMounted(async () => {
  console.log("Selected file:", selectedFile.value);
  try {
    const training_response = await trainSVM(selectedFile.value);
    await beginPylslStream(selectedFile.value);
    socket = createAttentionThresholdSocket((data) => {
      console.log(data);
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
  // }, selectedFile.value)
});
</script>

<style scoped>
/* No scoped styles needed since TailwindCSS is used */
</style>
