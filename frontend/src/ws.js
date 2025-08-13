export async function createSignalQualitySocket(onMessage, fileName) {
  const socket = new WebSocket(
    `ws://localhost:8000/api/signal-quality?file_name=${encodeURIComponent(fileName)}`
  );
  socket.onmessage = (event) => {
    onMessage(JSON.parse(event.data));
  };
  return socket;
}

export function createAttentionThresholdSocket(onMessage) {
  const socket = new WebSocket(`ws://localhost:8000/api/attention-threshold`);
  socket.onmessage = (event) => {
    onMessage(JSON.parse(event.data));
  };
  return socket;
}
