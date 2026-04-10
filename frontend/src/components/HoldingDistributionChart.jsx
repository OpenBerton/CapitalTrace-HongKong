import { BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function HoldingDistributionChart({ data }) {
  return (
    <div className="h-96 rounded-xl bg-white p-4 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-800">前十大券商持股分布</h2>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={(value) => `${value}%`} />
          <Tooltip
            formatter={(value) => [`${Number(value).toFixed(2)}%`, "佔比"]}
            labelFormatter={(label) => `券商：${label}`}
          />
          <Bar dataKey="percentage" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
