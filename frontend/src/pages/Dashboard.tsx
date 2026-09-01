import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { dashboardApi } from "../services/endpoints";
import type { Dashboard as DashboardType } from "../types";
import { Card, CardHeader, PageLoading, ErrorState, ProgressBar, Badge, PriorityBadge, EmptyState } from "../components/ui";
import { getErrorMessage } from "../services/api";

const CATEGORY_COLORS = ["#2f8271", "#4d9f88", "#7cbfa9", "#aad7c8", "#22685b", "#1c534a", "#d5ebe3", "#153833", "#64748b", "#94a3b8"];

function formatCurrency(v: number) {
  return `₹${v.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

function healthTone(category: string): "success" | "brand" | "warning" | "danger" {
  if (category === "Strong") return "success";
  if (category === "Good") return "brand";
  if (category === "Fair") return "warning";
  return "danger";
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardType | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardApi
      .get()
      .then(setData)
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <PageLoading />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  const pieData = Object.entries(data.spending_by_category).map(([name, value]) => ({ name, value }));
  const health = data.financial_health;
  const tone = healthTone(health.category);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink-900">Your Financial Dashboard</h1>
        <p className="text-sm text-ink-500 mt-1">A complete view of your money, goals, and personalized guidance.</p>
      </div>

      {/* Top section: health + key metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <Card className="lg:col-span-1 flex flex-col items-center justify-center text-center">
          <p className="text-xs font-medium text-ink-500 uppercase tracking-wide">Financial Health Score</p>
          <p className="text-4xl font-extrabold text-ink-900 mt-2">{health.score}</p>
          <div className="mt-2"><Badge tone={tone}>{health.category}</Badge></div>
        </Card>
        <Card>
          <p className="text-xs font-medium text-ink-500 uppercase tracking-wide">Monthly Income</p>
          <p className="text-2xl font-bold text-ink-900 mt-2">{formatCurrency(data.monthly_income)}</p>
        </Card>
        <Card>
          <p className="text-xs font-medium text-ink-500 uppercase tracking-wide">Monthly Expenses</p>
          <p className="text-2xl font-bold text-ink-900 mt-2">{formatCurrency(data.monthly_expenses)}</p>
        </Card>
        <Card>
          <p className="text-xs font-medium text-ink-500 uppercase tracking-wide">Savings Rate</p>
          <p className="text-2xl font-bold text-ink-900 mt-2">{data.savings_rate.toFixed(1)}%</p>
          <p className="text-xs text-ink-500 mt-1">Savings: {formatCurrency(data.monthly_savings)}/mo</p>
        </Card>
      </div>

      {/* Financial health breakdown */}
      <Card>
        <CardHeader title="Financial Health Breakdown" subtitle="Transparent scoring across 7 weighted components" />
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-4">
          {Object.entries(health.components).map(([key, value]) => (
            <div key={key}>
              <p className="text-xs text-ink-500 capitalize mb-1">{key.replace(/_/g, " ")}</p>
              <p className="text-sm font-semibold text-ink-900 mb-1">{value}</p>
              <ProgressBar value={value} tone={value >= 70 ? "success" : value >= 40 ? "warning" : "danger"} />
            </div>
          ))}
        </div>
      </Card>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader title="Income vs Expenses" subtitle="Last 6 months" />
          {data.income_vs_expense_trend.length === 0 ? (
            <EmptyState title="No transaction history yet" description="Add transactions to see trends here." />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.income_vs_expense_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                <Legend />
                <Bar dataKey="income" fill="#2f8271" radius={[4, 4, 0, 0]} name="Income" />
                <Bar dataKey="expense" fill="#f59e0b" radius={[4, 4, 0, 0]} name="Expense" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <CardHeader title="Spending by Category" />
          {pieData.length === 0 ? (
            <EmptyState title="No spending data yet" description="Add expense transactions to see the breakdown." />
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={(d) => d.name}>
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <CardHeader title="Savings Trend" subtitle="Monthly net savings" />
          {data.savings_trend.length === 0 ? (
            <EmptyState title="No savings data yet" />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={data.savings_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                <Area type="monotone" dataKey="savings" stroke="#2f8271" fill="#d5ebe3" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card>
          <CardHeader title="Investment Growth" subtitle="Cumulative invested value over time" />
          {data.investment_trend.length === 0 ? (
            <EmptyState title="No investments recorded yet" description="Add an investment to track its growth here." />
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={data.investment_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                <Area type="monotone" dataKey="cumulative_value" stroke="#22685b" fill="#aad7c8" />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </Card>
      </div>

      {/* Goals */}
      <Card>
        <CardHeader title="Financial Goals" action={<Link to="/goals" className="text-sm text-brand-600 font-medium hover:underline">Manage goals →</Link>} />
        {data.goals.length === 0 ? (
          <EmptyState title="No goals yet" description="Set a savings, home, or retirement goal to start tracking progress." action={<Link to="/goals" className="text-sm text-brand-600 font-medium hover:underline">Create a goal</Link>} />
        ) : (
          <div className="grid sm:grid-cols-2 gap-4">
            {data.goals.slice(0, 4).map((g) => (
              <div key={g.id} className="border border-ink-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium text-ink-900 text-sm">{g.name}</p>
                  <Badge tone={g.status === "achieved" ? "success" : "neutral"}>{g.status.replace("_", " ")}</Badge>
                </div>
                <ProgressBar value={g.progress_percentage} tone={g.progress_percentage >= 75 ? "success" : "brand"} />
                <div className="flex justify-between text-xs text-ink-500 mt-2">
                  <span>{formatCurrency(g.current_amount)} of {formatCurrency(g.target_amount)}</span>
                  <span>{g.progress_percentage.toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Recommendations */}
      <Card>
        <CardHeader title="AI Recommendations" subtitle="Personalized, explainable guidance based on your data" action={<Link to="/recommendations" className="text-sm text-brand-600 font-medium hover:underline">View all →</Link>} />
        {data.top_recommendations.length === 0 ? (
          <EmptyState title="No recommendations yet" description="Complete your profile to receive personalized guidance." />
        ) : (
          <div className="space-y-3">
            {data.top_recommendations.map((r) => (
              <Link
                key={r.id}
                to={`/recommendations/${r.id}`}
                className="block border border-ink-100 rounded-lg p-4 hover:border-brand-300 hover:bg-brand-50/30 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium text-ink-900 text-sm">{r.title}</p>
                    <p className="text-xs text-ink-500 mt-1">{r.recommendation}</p>
                  </div>
                  <PriorityBadge priority={r.priority} />
                </div>
              </Link>
            ))}
          </div>
        )}
      </Card>

      {/* Behavior + risk + literacy */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader title="Behavioral Profile" />
          {data.behavior_profile ? (
            <div>
              <Badge tone="brand">{data.behavior_profile.cluster_label}</Badge>
              <ul className="mt-3 space-y-1.5 text-xs text-ink-500">
                {data.behavior_profile.insights?.slice(0, 3).map((i, idx) => <li key={idx}>• {i}</li>)}
              </ul>
            </div>
          ) : (
            <EmptyState title="Not yet analyzed" description="Add transactions to see your behavioral archetype." />
          )}
        </Card>
        <Card>
          <CardHeader title="Risk Profile" />
          {data.risk_level ? (
            <Badge tone="brand">{data.risk_level} risk tolerance</Badge>
          ) : (
            <EmptyState title="Not assessed" action={<Link to="/risk" className="text-sm text-brand-600 font-medium hover:underline">Take assessment</Link>} />
          )}
        </Card>
        <Card>
          <CardHeader title="Financial Literacy" />
          {data.literacy_level ? (
            <Badge tone="brand">{data.literacy_level}</Badge>
          ) : (
            <EmptyState title="Not assessed" action={<Link to="/literacy" className="text-sm text-brand-600 font-medium hover:underline">Take quiz</Link>} />
          )}
        </Card>
      </div>

      {/* Alerts */}
      <Card>
        <CardHeader title="Alerts & Reminders" />
        {data.alerts.length === 0 ? (
          <EmptyState title="No active alerts" description="You're all caught up." />
        ) : (
          <div className="space-y-2">
            {data.alerts.map((a) => (
              <div key={a.id} className="flex items-start gap-3 text-sm border-b border-ink-100 last:border-0 pb-2 last:pb-0">
                <Badge tone={a.severity === "critical" ? "danger" : a.severity === "warning" ? "warning" : "neutral"}>{a.severity}</Badge>
                <div>
                  <p className="font-medium text-ink-900">{a.title}</p>
                  <p className="text-ink-500 text-xs">{a.message}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
