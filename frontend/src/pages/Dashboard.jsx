import { useMemo, useState } from "react";
import SearchBar from "../components/SearchBar";
import LoadingSpinner from "../components/LoadingSpinner";
import HoldingDistributionChart from "../components/HoldingDistributionChart";
import TopParticipantsTable from "../components/TopParticipantsTable";
import useFetchChips from "../hooks/useFetchChips";

const STOCK_CODE_PATTERN = /^\d{1,6}$/;

export default function Dashboard() {
  const [stockCode, setStockCode] = useState("");
  const [date, setDate] = useState("");
  const [validationError, setValidationError] = useState("");
  const { data, loading, error, fetchData } = useFetchChips();

  const isInputComplete = useMemo(
    () => stockCode.trim().length > 0 && date.trim().length > 0,
    [stockCode, date],
  );

  const validateInputs = (code, queryDate) => {
    if (!code || !queryDate) {
      setValidationError("請輸入股票代號與查詢日期。");
      return false;
    }

    if (!STOCK_CODE_PATTERN.test(code)) {
      setValidationError("股票代號必須為 1 到 6 位數字，例如 00700。");
      return false;
    }

    setValidationError("");
    return true;
  };

  const handleSearch = () => {
    const trimmedStockCode = stockCode.trim();
    const trimmedDate = date.trim();

    if (!validateInputs(trimmedStockCode, trimmedDate)) {
      return;
    }

    fetchData(trimmedStockCode, trimmedDate);
  };


  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-8">
      <header className="rounded-xl bg-slate-900 p-6 text-white shadow-lg">
        <h1 className="text-3xl font-bold">港股 CCASS 主力籌碼即時分析</h1>
        <p className="mt-2 text-slate-300">輸入股票代號與日期，即時抓取 CCASS 籌碼分佈並呈現前十大券商集中度。</p>
      </header>
      <SearchBar
        stockCode={stockCode}
        date={date}
        onStockCodeChange={setStockCode}
        onDateChange={setDate}
        onSearch={handleSearch}
        loading={loading}
        validationError={validationError}
      />

      {!isInputComplete && (
        <div className="rounded-xl border border-sky-200 bg-sky-50 p-4 text-slate-700">
          請輸入股票代號與日期，然後按「查詢籌碼」。
        </div>
      )}

      {data && (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="rounded-xl bg-white p-4 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-800">查詢摘要</h2>
            <div className="mt-4 space-y-3 text-sm text-slate-700">
              <div className="flex justify-between">
                <span>股票代號</span>
                <span className="font-medium">{data.stock_code}</span>
              </div>
              <div className="flex justify-between">
                <span>查詢日期</span>
                <span className="font-medium">{data.date}</span>
              </div>
              <div className="flex justify-between">
                <span>前十大集中度</span>
                <span className="font-medium">{Number(data.total_top_share_ratio).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between">
                <span>資料欄位</span>
                <span className="font-medium truncate max-w-[10rem]">{data.raw_columns.join(" / ")}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {loading && <LoadingSpinner />}
      {error && (
        <div className="rounded-xl border border-rose-300 bg-rose-50 p-4 text-rose-700">{error}</div>
      )}

      {data && (
        <div className="grid gap-6 xl:grid-cols-2">
          <HoldingDistributionChart data={data.top_participants} />
          <TopParticipantsTable participants={data.top_participants} />
        </div>
      )}
    </div>
  );
}
