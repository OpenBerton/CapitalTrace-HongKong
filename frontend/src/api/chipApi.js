import axios from "axios";

const requestTimeout = Number(import.meta.env.VITE_API_TIMEOUT_MS || 60000);

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1",
  timeout: requestTimeout,
});

export async function fetchChips(stockCode, date) {
  const response = await apiClient.get("/chips", {
    params: { stock_code: stockCode, date },
  });
  return response.data;
}

export async function fetchChipsEnriched(stockCode, date) {
  const response = await apiClient.get("/chips/enriched", {
    params: { stock_code: stockCode, date },
  });
  return response.data;
}

export async function fetchTradingDays() {
  const response = await apiClient.get("/trading-days");
  return response.data;
}
