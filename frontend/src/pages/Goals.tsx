import { useEffect, useState } from "react";
import { goalsApi } from "../services/endpoints";
import type { Goal } from "../types";
import { Card, CardHeader, Button, Input, Select, PageLoading, EmptyState, Badge, ProgressBar } from "../components/ui";
import { useToast } from "../hooks/useToast";
import { getErrorMessage } from "../services/api";

const GOAL_TYPES = ["emergency_fund", "education", "home_purchase", "car", "retirement", "debt_reduction", "custom"];

const emptyForm = {
  name: "",
  goal_type: "custom",
  target_amount: "",
  current_amount: "0",
  target_date: "",
  priority: "medium",
};

export default function Goals() {
  const { showToast } = useToast();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);

  const load = () => {
    setLoading(true);
    goalsApi.list().then(setGoals).catch((err) => showToast(getErrorMessage(err), "error")).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await goalsApi.create({
        name: form.name,
        goal_type: form.goal_type,
        target_amount: Number(form.target_amount),
        current_amount: Number(form.current_amount) || 0,
        target_date: form.target_date,
        priority: form.priority,
      });
      showToast("Goal created", "success");
      setForm(emptyForm);
      setShowForm(false);
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this goal?")) return;
    try {
      await goalsApi.remove(id);
      showToast("Goal deleted", "success");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const handleContribute = async (goal: Goal) => {
    const amountStr = prompt(`Add contribution to "${goal.name}" (₹)`);
    if (!amountStr) return;
    const amount = Number(amountStr);
    if (!amount || amount <= 0) return;
    try {
      await goalsApi.update(goal.id, { current_amount: goal.current_amount + amount });
      showToast("Contribution added", "success");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  if (loading) return <PageLoading />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink-900">Financial Goals</h1>
          <p className="text-sm text-ink-500 mt-1">Set targets and track your progress toward them.</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? "Close" : "+ Add Goal"}</Button>
      </div>

      {showForm && (
        <Card>
          <CardHeader title="New Goal" />
          <form onSubmit={handleSubmit} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 items-end">
            <Input label="Goal name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <Select label="Type" value={form.goal_type} onChange={(e) => setForm({ ...form, goal_type: e.target.value })}>
              {GOAL_TYPES.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
            </Select>
            <Select label="Priority" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </Select>
            <Input label="Target amount (₹)" type="number" min={1} required value={form.target_amount} onChange={(e) => setForm({ ...form, target_amount: e.target.value })} />
            <Input label="Current amount (₹)" type="number" min={0} value={form.current_amount} onChange={(e) => setForm({ ...form, current_amount: e.target.value })} />
            <Input label="Target date" type="date" required value={form.target_date} onChange={(e) => setForm({ ...form, target_date: e.target.value })} />
            <Button type="submit" className="lg:col-span-3">Create Goal</Button>
          </form>
        </Card>
      )}

      {goals.length === 0 ? (
        <Card><EmptyState title="No goals yet" description="Create your first financial goal to start tracking progress." /></Card>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {goals.map((g) => (
            <Card key={g.id}>
              <div className="flex items-start justify-between mb-1">
                <div>
                  <p className="font-semibold text-ink-900">{g.name}</p>
                  <p className="text-xs text-ink-500 capitalize">{g.goal_type.replace("_", " ")} • {g.priority} priority</p>
                </div>
                <Badge tone={g.status === "achieved" ? "success" : "neutral"}>{g.status.replace("_", " ")}</Badge>
              </div>
              <div className="my-3">
                <ProgressBar value={g.progress_percentage} tone={g.progress_percentage >= 75 ? "success" : "brand"} />
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-ink-500 mb-3">
                <div>Target: <span className="font-medium text-ink-900">₹{g.target_amount.toLocaleString("en-IN")}</span></div>
                <div>Current: <span className="font-medium text-ink-900">₹{g.current_amount.toLocaleString("en-IN")}</span></div>
                <div>Remaining: <span className="font-medium text-ink-900">₹{g.remaining_amount.toLocaleString("en-IN")}</span></div>
                <div>Target date: <span className="font-medium text-ink-900">{g.target_date}</span></div>
              </div>
              <p className="text-xs bg-brand-50 text-brand-700 rounded-md px-3 py-2 mb-3">
                Recommended contribution: ₹{g.recommended_monthly_contribution.toLocaleString("en-IN")}/month
              </p>
              <div className="flex gap-3">
                <button onClick={() => handleContribute(g)} className="text-xs text-brand-600 font-medium hover:underline">+ Add contribution</button>
                <button onClick={() => handleDelete(g.id)} className="text-xs text-red-600 font-medium hover:underline">Delete</button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
