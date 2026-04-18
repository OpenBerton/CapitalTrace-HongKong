import { formatNumber } from "../utils/numberFormat";
import { formatPercent } from "../utils/percentFormat";
import useParticipantSelection from "../hooks/useParticipantSelection";
import NetFlowSummaryPanel from "./NetFlowSummaryPanel";

export default function TopParticipantsTable({ participants, enriching = false }) {
  const {
    buildRowId,
    selectedParticipants,
    selectedCount,
    totalCount,
    isAllSelected,
    selectedTotals,
    netFlowClass,
    selectAllRef,
    toggleParticipant,
    handleToggleAll,
  } = useParticipantSelection(participants);

  return (
    <div className="overflow-x-auto rounded-xl bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-800">前二十大券商明細</h2>
      <NetFlowSummaryPanel
        selectedTotals={selectedTotals}
        selectedCount={selectedCount}
        totalCount={totalCount}
        netFlowClass={netFlowClass}
      />
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
            const rowId = buildRowId(item, index);
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
