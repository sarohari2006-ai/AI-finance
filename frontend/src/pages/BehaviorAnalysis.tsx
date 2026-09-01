import { useEffect, useState } from "react";
import { behaviorApi } from "../services/endpoints";
import type { BehaviorAnalysis as BehaviorAnalysisType } from "../types";
import { Card, CardHeader, PageLoading, ErrorState, Badge, ProgressBar } from "../components/ui";
import { getErrorMessage } from "../services/api";

const METRICS: Array<{ key: keyof BehaviorAnalysisType; label: string; asPercent: boolean; goodDirection: "high" | "low" }> = [
  { key: "savings_rate", label: "Savings Rate", asPercent: true, goodDirection: "high" },
  { key: "discretionary_ratio", label: "Discretionary Spending Ratio", asPercent: true, goodDirection: "low" },
  { key: "essential_ratio", label: "Essential Spending Ratio", asPercent: true, goodDirection: "high" },
  { key: "savings_consistency", label: "Savings Consistency", asPercent: true, goodDirection: "high" },
  { key: "spending_volatility", label: "Spending Volatility", asPercent: true, goodDirection: "low" },
  { key: "debt_burden", label: "Debt Burden", asPercent: true, goodDirection: "low" },
  { key: "investment_consistency", label: "Investment Consistency", asPercent: true, goodDirection: "high" },
  { key: "recurring_expense_ratio", label: "Recurring Expense Ratio", asPercent: true, goodDirection: "low" },
  { key: "category_concentration", label: "Category Concentration", asPercent: true, goodDirection: "low" },
];

const ARCHETYPE_DESCRIPTIONS: Record<string, string> = {
  "Disciplined Saver": "You consistently save a healthy share of your income with controlled discretionary spending.",
  "High Discretionary Spender": "A large portion of your spending goes to non-essential categories like shopping and entertainment.",
  "Inconsistent Saver": "Your savings behavior varies significantly month to month.",
  "Debt-Heavy": "A significant share of your income goes toward debt repayment.",
  "Balanced Planner": "You maintain a healthy balance across spending, saving, and investing.",
};

export default function BehaviorAnalysis() {
  const [data, setData] = useState<BehaviorAnalysisType | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    behaviorApi.get().then(setData).catch((err) => setError(getErrorMessage(err))).finally(() => setLoading(false));
  }, []);

  if (loading) return <PageLoading />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink-900">Behavioral Analysis</h1>
        <p className="text-sm text-ink-500 mt-1">
          Derived from your transaction history using feature engineering and K-Means clustering against reference financial-behavior archetypes.
        </p>
      </div>

      <Card>
        <div className="flex items-center gap-3 mb-2">
          <span className="text-2xl">🧠</span>
          <div>
            <p className="text-xs text-ink-500 uppercase tracking-wide">Behavior Profile</p>
            <Badge tone="brand">{data.cluster_label}</Badge>
          </div>
        </div>
        <p className="text-sm text-ink-700 mt-3">{ARCHETYPE_DESCRIPTIONS[data.cluster_label || ""] || ""}</p>
      </Card>

      <Card>
        <CardHeader title="Why this profile?" subtitle="The underlying factors behind your classification" />
        <ul className="space-y-2">
          {data.insights?.map((insight, idx) => (
            <li key={idx} className="text-sm text-ink-700 flex gap-2">
              <span className="text-brand-600">•</span> {insight}
            </li>
          ))}
        </ul>
      </Card>

      <Card>
        <CardHeader title="Behavioral Metrics" subtitle="Feature values computed from your transaction and financial data" />
        <div className="grid sm:grid-cols-2 gap-5">
          {METRICS.map((m) => {
            const raw = data[m.key] as number;
            const pct = m.asPercent ? raw * 100 : raw;
            const isGood = m.goodDirection === "high" ? pct >= 50 : pct <= 50;
            return (
              <div key={m.key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-ink-700">{m.label}</span>
                  <span className="font-medium text-ink-900">{pct.toFixed(1)}%</span>
                </div>
                <ProgressBar value={pct} tone={isGood ? "success" : "warning"} />
              </div>
            );
          })}
        </div>
      </Card>

      <Card>
        <CardHeader title="Average Monthly Spending" />
        <p className="text-2xl font-bold text-ink-900">₹{data.avg_monthly_spending.toLocaleString("en-IN")}</p>
      </Card>
    </div>
  );
}
