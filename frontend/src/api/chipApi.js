import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  timeout: 30000,
});

export async function fetchChips(stockCode, date) {
  const response = await apiClient.get("/chips", {
    params: { stock_code: stockCode, date },
  });
  return response.data;
}
