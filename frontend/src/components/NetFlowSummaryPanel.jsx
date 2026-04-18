import { formatNumber } from "../utils/numberFormat";
import { formatPercent } from "../utils/percentFormat";

export default function NetFlowSummaryPanel({ selectedTotals, selectedCount, totalCount, netFlowClass }) {
  return (
    <div className="mb-4 rounded-lg border border-slate-200 p-4 shadow-sm">
      <div className="text-sm text-slate-600">自訂機構淨流入/流出總結</div>
      <div className="mt-2 flex flex-wrap items-center gap-3">
        <span className={`rounded-md px-3 py-2 text-sm font-semibold ${netFlowClass}`}>
          選定機構淨流入總計：
          {selectedTotals.totalNetFlow > 0 ? "+" : ""}
          {formatNumber(selectedTotals.totalNetFlow)} 股
        </span>
        <span className="rounded-md bg-slate-100 px-3 py-2 text-sm font-medium text-slate-700">
          選定機構佔比合計：{formatPercent(selectedTotals.totalSelectedRatio)}
        </span>
        <span className="text-sm text-slate-500">已選 {selectedCount} / {totalCount}</span>
      </div>
    </div>
  );
}
