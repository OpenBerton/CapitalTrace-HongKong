import { useCallback, useRef, useState } from "react";
import { fetchChips, fetchChipsEnriched } from "../api/chipApi";

export default function useFetchChips() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [enriching, setEnriching] = useState(false);
  const [error, setError] = useState(null);
  const requestIdRef = useRef(0);

  const fetchData = useCallback(async (stockCode, date) => {
    const requestId = requestIdRef.current + 1;
    requestIdRef.current = requestId;

    setLoading(true);
    setEnriching(false);
    setError(null);
    try {
      const quickResult = await fetchChips(stockCode, date);
      if (requestId !== requestIdRef.current) {
        return;
      }

      setData(quickResult);
      setLoading(false);
      setEnriching(true);

      try {
        const enrichedResult = await fetchChipsEnriched(stockCode, date);
        if (requestId === requestIdRef.current) {
          setData(enrichedResult);
        }
      } catch (enrichErr) {
        if (requestId === requestIdRef.current) {
          // Keep quick result on screen; enrichment failure should not block the main view.
          console.warn("Enrichment fetch failed", enrichErr);
        }
      } finally {
        if (requestId === requestIdRef.current) {
          setEnriching(false);
        }
      }
    } catch (err) {
      if (requestId !== requestIdRef.current) {
        return;
      }
      if (err.code === "ECONNABORTED") {
        setError("查詢逾時（前端等待上限已到），請稍後重試或縮小查詢範圍。");
      } else {
        setError(err.response?.data?.detail || err.message || "查詢失敗，請稍後重試。");
      }
      setData(null);
    } finally {
      if (requestId === requestIdRef.current) {
        setLoading(false);
      }
    }
  }, []);

  return { data, loading, enriching, error, fetchData };
}
