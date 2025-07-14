const API_BASE_URL = "http://localhost:8000/api";

export async function getHello() {
  const response = await fetch(`${API_BASE_URL}/hello`);
  if (!response.ok) {
    throw new Error("Failed to fetch hello message");
  }
  return response.json();
}

export async function getDevices(){
  const response = await fetch(`${API_BASE_URL}/devices`);
  if (!response.ok){
    throw new Error("Failed to fetch devices");
  }
  return response.json();
}

// Add more API functions here as needed
