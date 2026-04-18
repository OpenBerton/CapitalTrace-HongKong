import SearchBar from "../components/SearchBar";
import LoadingSpinner from "../components/LoadingSpinner";
import HoldingDistributionChart from "../components/HoldingDistributionChart";
import TopParticipantsTable from "../components/TopParticipantsTable";
import useFetchChips from "../hooks/useFetchChips";
import useChipQueryForm from "../hooks/useChipQueryForm";
import useTradingDays from "../hooks/useTradingDays";

export default function Dashboard() {
  const {
    stockCode,
    date,
    validationError,
    isInputComplete,
    setStockCode,
    setDate,
    validateInputs,
  } = useChipQueryForm();
  const {
    validTradingDays,
    tradingDaysLoading,
    tradingDaysError,
  } = useTradingDays(setDate);
  const { data, loading, enriching, error, fetchData } = useFetchChips();

  const handleSearch = () => {
    const trimmedStockCode = stockCode.trim();
    const trimmedDate = date.trim();

    if (!validateInputs(trimmedStockCode, trimmedDate, validTradingDays)) {
      return;
    }

    fetchData(trimmedStockCode, trimmedDate);
  };

  const displayError = tradingDaysError || validationError;


  return (
    <div className="mx-auto max-w-6xl space-y-6 p-4 md:p-8">
      <header className="rounded-xl bg-slate-900 p-6 text-white shadow-lg">
        <h1 className="text-3xl font-bold">港股 CCASS 主力籌碼即時分析</h1>
        <p className="mt-2 text-slate-300">輸入股票代號與日期，即時抓取 CCASS 籌碼分佈並呈現前二十大券商集中度。</p>
      </header>
      <SearchBar
        stockCode={stockCode}
        date={date}
        tradingDays={validTradingDays}
        tradingDaysLoading={tradingDaysLoading}
        onStockCodeChange={setStockCode}
        onDateChange={setDate}
        onSearch={handleSearch}
        loading={loading}
        validationError={displayError}
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
                <span>交收對齊</span>
                <span className="font-medium">查詢交易日：{data.date} / 對應 CCASS 交收日：{data.ccass_settlement_date}</span>
              </div>
              <div className="flex justify-between">
                <span>收盤價</span>
                <span className="font-medium">
                  {data.closePrice != null
                    ? `HKD ${Number(data.closePrice).toFixed(2)}`
                    : enriching
                    ? "更新中..."
                    : "無資料"}
                </span>
              </div>
              <div className="flex justify-between">
                <span>前二十大集中度</span>
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
          <TopParticipantsTable participants={data.top_participants} enriching={enriching} />
        </div>
      )}
    </div>
  );
}
