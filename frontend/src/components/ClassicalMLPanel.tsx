"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ClassicalChart } from "@/lib/types";

type Props = {
  charts: ClassicalChart[];
};

export function ClassicalMLPanel({ charts }: Props) {
  if (charts.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        No classical ML charts yet. Log learning curves, ROC, confusion matrix, or
        feature importance via SDK <code className="text-cyan-500">add_classical_chart</code>.
      </p>
    );
  }

  return (
    <div className="grid gap-6">
      {charts.map((chart) => (
        <div
          key={chart.id}
          className="rounded-lg border border-slate-800 bg-slate-900/40 p-4"
        >
          <h3 className="mb-3 text-sm font-medium text-slate-300">
            {chart.title ?? chart.chart_type.replace(/_/g, " ")}
            <span className="ml-2 font-mono text-xs text-slate-500">
              {chart.chart_type}
            </span>
          </h3>
          {chart.chart_type === "learning_curve" && (
            <LearningCurveChart data={chart.data} />
          )}
          {chart.chart_type === "roc" && <RocChart data={chart.data} />}
          {chart.chart_type === "confusion_matrix" && (
            <ConfusionMatrix data={chart.data} />
          )}
          {chart.chart_type === "feature_importance" && (
            <FeatureImportanceChart data={chart.data} />
          )}
        </div>
      ))}
    </div>
  );
}

function LearningCurveChart({ data }: { data: Record<string, unknown> }) {
  const sizes = data.train_sizes as number[];
  const train = data.train_scores as number[];
  const val = data.val_scores as number[];
  const rows = sizes.map((size, i) => ({
    size,
    train: train[i],
    val: val[i],
  }));

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={rows}>
          <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
          <XAxis dataKey="size" stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 1]} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
          <Legend />
          <Line type="monotone" dataKey="train" stroke="#22d3ee" strokeWidth={2} dot={{ r: 3 }} />
          <Line type="monotone" dataKey="val" stroke="#a78bfa" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function RocChart({ data }: { data: Record<string, unknown> }) {
  const fpr = data.fpr as number[];
  const tpr = data.tpr as number[];
  const auc = data.auc as number | undefined;
  const rows = fpr.map((x, i) => ({ fpr: x, tpr: tpr[i] }));

  return (
    <div className="h-64">
      {auc != null && (
        <p className="mb-2 font-mono text-xs text-slate-400">AUC = {auc.toFixed(3)}</p>
      )}
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={rows}>
          <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
          <XAxis dataKey="fpr" stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 1]} />
          <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={[0, 1]} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
          <Line type="monotone" dataKey="tpr" stroke="#34d399" strokeWidth={2} dot={{ r: 2 }} name="ROC" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function ConfusionMatrix({ data }: { data: Record<string, unknown> }) {
  const labels = data.labels as string[];
  const matrix = data.matrix as number[][];
  const max = Math.max(...matrix.flat(), 1);

  return (
    <div className="overflow-x-auto">
      <table className="border-collapse text-sm">
        <thead>
          <tr>
            <th className="p-2 text-slate-500" />
            {labels.map((l) => (
              <th key={l} className="p-2 text-slate-400">
                pred {l}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={labels[i]}>
              <th className="p-2 text-left text-slate-400">true {labels[i]}</th>
              {row.map((cell, j) => {
                const intensity = cell / max;
                return (
                  <td
                    key={`${i}-${j}`}
                    className="p-2 text-center font-mono"
                    style={{
                      background: `rgba(34, 211, 238, ${0.15 + intensity * 0.65})`,
                    }}
                  >
                    {cell}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function FeatureImportanceChart({ data }: { data: Record<string, unknown> }) {
  const features = data.features as string[];
  const importances = data.importances as number[];
  const rows = features.map((name, i) => ({
    name,
    importance: importances[i],
  }));

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={rows} layout="vertical" margin={{ left: 24 }}>
          <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
          <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
          <YAxis type="category" dataKey="name" stroke="#64748b" tick={{ fontSize: 11 }} width={80} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
          <Bar dataKey="importance" fill="#fbbf24" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
