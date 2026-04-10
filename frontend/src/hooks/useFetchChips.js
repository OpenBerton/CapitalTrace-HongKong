import { useCallback, useState } from "react";
import { fetchChips } from "../api/chipApi";

export default function useFetchChips() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async (stockCode, date) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchChips(stockCode, date);
      setData(result);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "查詢失敗，請稍後重試。");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, fetchData };
}
