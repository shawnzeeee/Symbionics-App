export function createSignalQualitySocket(onMessage){
  const socket = new WebSocket("ws://localhost:8000/ws/signal-quality");
  socket.onmessage = (event) => {
    onMessage(JSON.parse(event.data));
  };
  return socket;  
}