import { formatNumber } from "../utils/numberFormat";
import { formatPercent } from "../utils/percentFormat";

export default function TopParticipantsTable({ participants }) {
  return (
    <div className="overflow-x-auto rounded-xl bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-800">前十大券商明細</h2>
      <table className="min-w-full border-collapse text-sm text-slate-700">
        <thead>
          <tr>
            <th className="border-b px-4 py-2 text-left">名稱</th>
            <th className="border-b px-4 py-2 text-right">持股</th>
            <th className="border-b px-4 py-2 text-right">佔比(%)</th>
          </tr>
        </thead>
        <tbody>
          {participants.map((item, index) => (
            <tr key={index} className={index % 2 === 0 ? "bg-slate-50" : ""}>
              <td className="border-b px-4 py-2">{item.name || "-"}</td>
              <td className="border-b px-4 py-2 text-right">{formatNumber(item.share)}</td>
              <td className="border-b px-4 py-2 text-right">{formatPercent(item.percentage)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
