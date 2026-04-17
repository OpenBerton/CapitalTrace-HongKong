import PropTypes from "prop-types";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

function parseIsoDate(value) {
  if (!value) {
    return null;
  }
  const [year, month, day] = value.split("-").map(Number);
  if (!year || !month || !day) {
    return null;
  }
  return new Date(year, month - 1, day);
}

function formatIsoDate(dateObj) {
  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, "0");
  const day = String(dateObj.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export default function SearchBar({
  stockCode,
  date,
  tradingDays,
  tradingDaysLoading,
  onStockCodeChange,
  onDateChange,
  onSearch,
  loading,
  validationError,
}) {
  const selectableDates = tradingDays
    .map((tradingDay) => parseIsoDate(tradingDay))
    .filter((item) => item);

  const maxSelectableDate = selectableDates.length > 0
    ? selectableDates[selectableDates.length - 1]
    : null;

  const selectableDateSet = new Set(
    selectableDates.map((item) => formatIsoDate(item)),
  );

  const selectedDate = parseIsoDate(date);

  const isSelectableTradingDay = (dateObj) => {
    const isoDate = formatIsoDate(dateObj);
    return selectableDateSet.has(isoDate);
  };

  return (
    <div className="space-y-4 p-4 rounded-xl bg-white shadow-sm">
      <div className="grid gap-4 md:grid-cols-3">
        <label className="space-y-1">
          <span className="text-sm font-medium text-slate-700">股票代號</span>
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none"
            value={stockCode}
            onChange={(event) => onStockCodeChange(event.target.value)}
            placeholder="例如 00700"
            inputMode="numeric"
          />
        </label>
        <label className="space-y-1">
          <span className="text-sm font-medium text-slate-700">查詢日期</span>
          <DatePicker
            selected={selectedDate}
            onChange={(pickedDate) => onDateChange(pickedDate ? formatIsoDate(pickedDate) : "")}
            filterDate={isSelectableTradingDay}
            includeDates={selectableDates}
            maxDate={maxSelectableDate}
            dateFormat="yyyy-MM-dd"
            placeholderText={tradingDaysLoading ? "交易日載入中..." : "請選擇交易日"}
            disabled={tradingDaysLoading || tradingDays.length === 0}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-sky-500 focus:outline-none"
          />
        </label>
        <div className="flex items-end">
          <button
            type="button"
            onClick={onSearch}
            disabled={loading || tradingDaysLoading || tradingDays.length === 0}
            className="w-full rounded-lg bg-sky-600 px-4 py-3 text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {loading ? "查詢中..." : "查詢籌碼"}
          </button>
        </div>
      </div>
      {validationError && (
        <div className="rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-amber-800">
          {validationError}
        </div>
      )}
    </div>
  );
}

SearchBar.propTypes = {
  stockCode: PropTypes.string.isRequired,
  date: PropTypes.string.isRequired,
  tradingDays: PropTypes.arrayOf(PropTypes.string),
  tradingDaysLoading: PropTypes.bool,
  onStockCodeChange: PropTypes.func.isRequired,
  onDateChange: PropTypes.func.isRequired,
  onSearch: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  validationError: PropTypes.string,
};

SearchBar.defaultProps = {
  tradingDays: [],
  tradingDaysLoading: false,
  loading: false,
  validationError: "",
};
