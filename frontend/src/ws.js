export async function createSignalQualitySocket(onMessage, fileName) {
  const socket = new WebSocket(
    `ws://localhost:8000/api/signal-quality?file_name=${encodeURIComponent(fileName)}`
  );
  socket.onmessage = (event) => {
    onMessage(JSON.parse(event.data));
  };
  return socket;
}
