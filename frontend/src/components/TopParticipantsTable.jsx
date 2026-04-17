import { useEffect, useMemo, useRef, useState } from "react";
import { formatNumber } from "../utils/numberFormat";
import { formatPercent } from "../utils/percentFormat";

export default function TopParticipantsTable({ participants, enriching = false }) {
  const selectableIds = useMemo(
    () => participants.map((item, index) => `${index}:${item.name || "-"}`),
    [participants],
  );

  const [selectedParticipants, setSelectedParticipants] = useState(new Set());
  const selectAllRef = useRef(null);

  useEffect(() => {
    setSelectedParticipants(new Set(selectableIds));
  }, [selectableIds]);

  const selectedCount = selectedParticipants.size;
  const totalCount = selectableIds.length;
  const isAllSelected = totalCount > 0 && selectedCount === totalCount;
  const isPartiallySelected = selectedCount > 0 && selectedCount < totalCount;

  useEffect(() => {
    if (!selectAllRef.current) {
      return;
    }
    selectAllRef.current.indeterminate = isPartiallySelected;
  }, [isPartiallySelected]);

  const selectedTotals = useMemo(() => {
    return participants.reduce(
      (acc, item, index) => {
        const rowId = `${index}:${item.name || "-"}`;
        if (!selectedParticipants.has(rowId)) {
          return acc;
        }

        const ratio = Number(item.percentage || 0);
        acc.totalSelectedRatio += Number.isFinite(ratio) ? ratio : 0;

        if (item.deltaShares == null) {
          return acc;
        }

        const delta = Number(item.deltaShares);
        if (Number.isFinite(delta)) {
          acc.totalNetFlow += delta;
        }
        return acc;
      },
      {
        totalNetFlow: 0,
        totalSelectedRatio: 0,
      },
    );
  }, [participants, selectedParticipants]);

  const netFlowClass =
    selectedTotals.totalNetFlow > 0
      ? "text-emerald-600 bg-emerald-50"
      : selectedTotals.totalNetFlow < 0
      ? "text-red-600 bg-red-50"
      : "text-slate-700 bg-slate-100";

  const toggleParticipant = (rowId) => {
    setSelectedParticipants((prev) => {
      const next = new Set(prev);
      if (next.has(rowId)) {
        next.delete(rowId);
      } else {
        next.add(rowId);
      }
      return next;
    });
  };

  const handleToggleAll = () => {
    if (isAllSelected) {
      setSelectedParticipants(new Set());
      return;
    }
    setSelectedParticipants(new Set(selectableIds));
  };

  return (
    <div className="overflow-x-auto rounded-xl bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-800">前二十大券商明細</h2>
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
      <table className="min-w-full border-collapse text-sm text-slate-700">
        <thead>
          <tr>
            <th className="border-b px-4 py-2 text-center">
              <input
                ref={selectAllRef}
                type="checkbox"
                checked={isAllSelected}
                onChange={handleToggleAll}
                aria-label="全選或全不選券商"
              />
            </th>
            <th className="border-b px-4 py-2 text-left">名稱</th>
            <th className="border-b px-4 py-2 text-right">持股</th>
            <th className="border-b px-4 py-2 text-right">佔比(%)</th>
            <th className="border-b px-4 py-2 text-right">變化數量</th>
          </tr>
        </thead>
        <tbody>
          {participants.map((item, index) => {
            const rowId = `${index}:${item.name || "-"}`;
            const isSelected = selectedParticipants.has(rowId);
            const deltaShares = item.deltaShares;
            const deltaLabel = (enriching && deltaShares == null)
              ? "..."
              : deltaShares === undefined
              ? "..."
              : deltaShares === null
              ? "N/A"
              : deltaShares > 0
              ? `+${formatNumber(deltaShares)}`
              : formatNumber(deltaShares);
            const deltaClass =
              deltaShares > 0
                ? "text-emerald-500 bg-emerald-50"
                : deltaShares < 0
                ? "text-red-500 bg-red-50"
                : "text-gray-600";

            return (
              <tr key={index} className={index % 2 === 0 ? "bg-slate-50" : ""}>
                <td className="border-b px-4 py-2 text-center">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleParticipant(rowId)}
                    aria-label={`選擇 ${item.name || "券商"}`}
                  />
                </td>
                <td className="border-b px-4 py-2">{item.name || "-"}</td>
                <td className="border-b px-4 py-2 text-right">{formatNumber(item.share)}</td>
                <td className="border-b px-4 py-2 text-right">{formatPercent(item.percentage)}</td>
                <td className={`border-b px-4 py-2 text-right ${deltaClass}`}>
                  {deltaLabel}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
