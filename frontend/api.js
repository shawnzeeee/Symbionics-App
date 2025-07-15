import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

export async function getHello() {
  const response = await axios.get(`${API_BASE_URL}/hello`);
  return response.data;
}

export async function fetchDevices() {
  const response = await axios.get(`${API_BASE_URL}/devices`);
  return response.data;
}
