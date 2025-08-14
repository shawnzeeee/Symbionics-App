<template>
  <div class="min-h-screen flex bg-gray-100 relative">
    <!-- Left side: Electrodes centered vertically -->
    <div class="ml-12 flex-shrink-0 flex items-center justify-between w-1/2">
      <Electrodes v-if="showElectrodes" />
      <div class="flex flex-col items-center justify-center">
        <span class="text-5xl font-bold drop-shadow text-[#075776]">
          {{ progressHeight > 50 ? 'CLOSE' : 'OPEN' }}
        </span>
      </div>
    </div>

    <!-- Right side: Calibration content -->
    <div class="flex flex-col items-center flex w-1/2">
      <h1 class="text-4xl text-[#075776] mt-10">Calibrate the model</h1>

      <!-- Meter -->
      <div class="relative flex items-center justify-center mt-10">
        <!-- Bar + outside labels -->
        <div class="flex flex-col items-center">
          <span class="text-[#075776] text-base font-semibold drop-shadow mb-1">Close</span>
          <div class="relative w-32 h-[500px] bg-[#4c89a3] overflow-hidden">
            <div
              class="absolute left-0 w-full bg-[#58c2ff] transition-all duration-300 z-0 rounded"
              :style="{ bottom: '0px', height: progressHeight + '%' }"
            ></div>
            <div
              class="absolute inset-x-0 top-1/2 -translate-y-1/2 h-px bg-white/80 z-10 pointer-events-none"
              aria-hidden="true"
            ></div>
          </div>
          <span class="text-[#075776] text-base font-semibold drop-shadow mt-1">Open</span>
        </div>
        

        <!-- Control Buttons -->
        <div class="flex flex-col justify-between h-[500px] ml-4 z-10">
          <!-- Close sensitivity -->
          <div class="flex flex-col gap-2">
            <span class="text-[#19596e] text-sm">Close sensitivity</span>
            <div class="flex items-center gap-2">
              <button
                @click="decreaseTop"
                :disabled="attention_adder <= 1"
                class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >-</button>
              <button
                @click="increaseTop"
                :disabled="attention_adder >= 40"
                class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >+</button>
            </div>
            <div class="bg-white rounded px-3 py-1 shadow text-[#19596e]">
              Value: <b>{{ attention_adder }}</b>
            </div>
          </div>

          <!-- Open sensitivity -->
          <div class="flex flex-col gap-2">
            <span class="text-[#19596e] text-sm">Open sensitivity</span>
            <div class="flex items-center gap-2">
              <button
                @click="decreaseBottom"
                :disabled="attention_subtractor <= 1"
                class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >-</button>
              <button
                @click="increaseBottom"
                :disabled="attention_subtractor >= 40"
                class="w-10 h-10 bg-[#58c2ff] text-white text-2xl flex items-center justify-center cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >+</button>
            </div>
            <div class="bg-white rounded px-3 py-1 shadow text-[#19596e]">
              Value: <b>{{ attention_subtractor }}</b>
            </div>
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
      <div class="absolute bottom-5 right-5 flex flex-col items-end space-y-3 z-10">
        <button
          @click="saveSettings()"
          class="bg-white text-[#19596e] border border-[#19596e] px-6 py-2 text-lg rounded hover:bg-gray-100 transition cursor-pointer"
        >
          Save Settings
        </button>
        <button
          @click="loadModel"
          class="bg-[#19596e] text-white px-6 py-2 text-lg rounded hover:bg-[#144452] transition cursor-pointer"
        >
          Load to Glove
        </button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { useRouter, useRoute } from "vue-router";
import { ref, onMounted } from "vue";
import { createAttentionThresholdSocket } from "../ws.js";
import { trainSVM, beginPylslStreamNoFileWrite, loadFileToGlove, endMusePylslStream, updateCSV, fetchSensitivityValues} from "../api.js";
import { isNavigationFailure, NavigationFailureType } from 'vue-router';
import Electrodes from "../components/Electrodes.vue"
const router = useRouter();
const progressHeight = ref(0); // 0 to 100
const SCALE_MIN = 0;
const SCALE_MAX = 220;
const clamp = (n, a, b) => Math.max(a, Math.min(b, n));

const route = useRoute();
const selectedFile = ref(route.params.filename);
const attention_adder = ref(15);
const attention_subtractor = ref(15);

const showElectrodes = ref(false)
const isLoading = ref(true); // start in loading state

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

//variables to send to backend via websocket to change the script dynamically
function sendAttentionValues() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({
        attention_adder: attention_adder.value,
        attention_subtractor: attention_subtractor.value,
      })
    );
  }
}

function goBack() {
  //terminate muse and pylsl stream
  endMusePylslStream()
  router.back();
}

function saveSettings() {
  // use .value from refs
  const adder = Number(attention_adder.value);
  const subtractor = Number(attention_subtractor.value);
  const fname = String(selectedFile.value || "");

  updateCSV(fname, adder, subtractor);
  console.log("csv updated with", attention_adder.value, " and ", attention_subtractor.value)
}


//helper function to convert 0-220 to 0-100 for display on the bar
const threshold = ref(0); // <-- add this

function getDataNumber(msg) {
  let payload = msg;
  if (typeof msg === "string") {
    try { payload = JSON.parse(msg); } catch {}
  }

  // If server sends a threshold, keep the live readout in sync
  if (payload && payload.attention_threshold != null) {
    threshold.value = Number(payload.attention_threshold);
  }

  const raw =
    typeof payload === "number" ? payload :
    payload?.attention_threshold ?? payload?.progress ?? payload?.value ?? 0;

  const val = clamp(Number(raw), SCALE_MIN, SCALE_MAX);     // 0..220
  const pct = ((val - SCALE_MIN) / (SCALE_MAX - SCALE_MIN)) * 100; // 0..100
  progressHeight.value = Math.round(pct);
  //console.log(Math.round(pct));
}

async function loadModel() {
  //terminate the muselsl and pyslsl stream
  endMusePylslStream()
  console.log("sending csv file to pi: ", selectedFile.value);
  // router.push({ name: 'Final' })
  try{
    const response = await loadFileToGlove(selectedFile.value)
    console.log(response)
    if (response.success == true){
      router.push({ name: 'Final' });
    }
  }catch(error){
    console.log(error)
  }
}

onMounted(async () => {
  console.log("Selected file:", selectedFile.value);
  try{
    const fetch_sensitivity_response = await fetchSensitivityValues(selectedFile.value)
      if (fetch_sensitivity_response){
        attention_adder.value = fetch_sensitivity_response.data.attention_adder
        attention_subtractor.value = fetch_sensitivity_response.data.attention_subtractor
      }
  }
  catch (error){
    console.log(error);
  }
  try {
    const training_response = await trainSVM(selectedFile.value);
    console.log("trainSVM:", training_response);

    const stream_response =await beginPylslStreamNoFileWrite(selectedFile.value);
    console.log("beginPylslStreamNoFileWrite:", stream_response);
    isLoading.value = false;

    showElectrodes.value = true
    socket = createAttentionThresholdSocket((data) => {
      //console.log("WS message: ", data);

      //this function converts WS message data to int and sets the height of the bar in the html
      getDataNumber(data)
    });

    
  if (socket) {
    // If it’s already open (hot-reload cases), send once
    if (socket.readyState === WebSocket.OPEN) {
      sendAttentionValues();
    } else {
      socket.addEventListener("open", () => {
        console.log("WS open");
        sendAttentionValues(); // <-- initial state push
      });
    }
    socket.addEventListener("close", (event) => {
      console.log("WebSocket closed:", event);
    });
    socket.addEventListener("error", (e) => {
      console.error("WebSocket error:", e);
    });
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
