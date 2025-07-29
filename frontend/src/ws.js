export async function createSignalQualitySocket(onMessage) {
  const socket = new WebSocket("ws://localhost:8000/api/signal-quality");
  socket.onmessage = (event) => {
    onMessage(JSON.parse(event.data));
  };
  return socket;
}
// import axios from "axios";

// const API_BASE_URL = "http://localhost:8000/api";
// export async function createSignalQualitySocket() {
//   const response = await axios.get(`${API_BASE_URL}/end-stream`);
//   return response.data;
// }
