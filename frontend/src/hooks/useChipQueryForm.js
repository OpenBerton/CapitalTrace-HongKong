import { useMemo, useState } from "react";

const STOCK_CODE_PATTERN = /^\d{1,6}$/;

export default function useChipQueryForm() {
  const [stockCode, setStockCode] = useState("");
  const [date, setDate] = useState("");
  const [validationError, setValidationError] = useState("");

  const isInputComplete = useMemo(
    () => stockCode.trim().length > 0 && date.trim().length > 0,
    [stockCode, date],
  );

  const validateInputs = (code, queryDate, validTradingDays) => {
    if (!code || !queryDate) {
      setValidationError("請輸入股票代號與查詢日期。");
      return false;
    }

    if (!STOCK_CODE_PATTERN.test(code)) {
      setValidationError("股票代號必須為 1 到 6 位數字，例如 00700。");
      return false;
    }

    if (validTradingDays.length > 0 && !validTradingDays.includes(queryDate)) {
      setValidationError("請選擇有效的港股交易日。");
      return false;
    }

    setValidationError("");
    return true;
  };

  return {
    stockCode,
    date,
    validationError,
    isInputComplete,
    setStockCode,
    setDate,
    setValidationError,
    validateInputs,
  };
}
