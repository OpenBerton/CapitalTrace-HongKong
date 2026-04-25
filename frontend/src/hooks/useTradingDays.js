import { useEffect, useState } from "react";
import { fetchTradingDays } from "../api/chipApi";

function todayIso() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default function useTradingDays(onDateChange) {
  const [validTradingDays, setValidTradingDays] = useState([]);
  const [tradingDaysLoading, setTradingDaysLoading] = useState(true);
  const [tradingDaysError, setTradingDaysError] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadTradingDays() {
      setTradingDaysLoading(true);
      setTradingDaysError("");
      try {
        const days = await fetchTradingDays();
        if (!isMounted) {
          return;
        }
        const cappedDays = days.filter((item) => item <= todayIso());
        const selectableDays = cappedDays.length > 3 ? cappedDays.slice(0, -3) : [];
        setValidTradingDays(selectableDays);
        if (selectableDays.length > 0) {
          onDateChange((prevDate) => (
            selectableDays.includes(prevDate) ? prevDate : selectableDays[selectableDays.length - 1]
          ));
        }
      } catch {
        if (isMounted) {
          setTradingDaysError("交易日清單載入失敗，請稍後重試。");
          setValidTradingDays([]);
        }
      } finally {
        if (isMounted) {
          setTradingDaysLoading(false);
        }
      }
    }

    loadTradingDays();
    return () => {
      isMounted = false;
    };
  }, [onDateChange]);

  return {
    validTradingDays,
    tradingDaysLoading,
    tradingDaysError,
  };
}
