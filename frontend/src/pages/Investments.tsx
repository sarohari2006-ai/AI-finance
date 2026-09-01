import { useEffect, useState } from "react";
import { investmentsApi } from "../services/endpoints";
import type { Investment } from "../types";
import { Card, CardHeader, Button, Input, Select, PageLoading, EmptyState, Badge } from "../components/ui";
import { useToast } from "../hooks/useToast";
import { getErrorMessage } from "../services/api";

const TYPES = ["stocks", "mutual_funds", "fd", "ppf", "gold", "crypto", "other"];

const emptyForm = {
  investment_type: "mutual_funds",
  name: "",
  invested_amount: "",
  current_value: "",
  start_date: "",
};

export default function Investments() {
  const { showToast } = useToast();
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);

  const load = () => {
    setLoading(true);
    investmentsApi.list().then(setInvestments).catch((err) => showToast(getErrorMessage(err), "error")).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await investmentsApi.create({
        investment_type: form.investment_type,
        name: form.name || undefined,
        invested_amount: Number(form.invested_amount),
        current_value: Number(form.current_value),
        start_date: form.start_date || undefined,
      });
      showToast("Investment added", "success");
      setForm(emptyForm);
      setShowForm(false);
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this investment?")) return;
    try {
      await investmentsApi.remove(id);
      showToast("Investment deleted", "success");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const totalInvested = investments.reduce((s, i) => s + i.invested_amount, 0);
  const totalCurrent = investments.reduce((s, i) => s + i.current_value, 0);
  const overallReturn = totalInvested > 0 ? ((totalCurrent - totalInvested) / totalInvested) * 100 : 0;

  if (loading) return <PageLoading />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink-900">Investments</h1>
          <p className="text-sm text-ink-500 mt-1">Educational tracking only — not a guarantee of future returns.</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? "Close" : "+ Add Investment"}</Button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card><p className="text-xs text-ink-500 uppercase">Invested</p><p className="text-xl font-bold text-ink-900 mt-1">₹{totalInvested.toLocaleString("en-IN")}</p></Card>
        <Card><p className="text-xs text-ink-500 uppercase">Current Value</p><p className="text-xl font-bold text-ink-900 mt-1">₹{totalCurrent.toLocaleString("en-IN")}</p></Card>
        <Card><p className="text-xs text-ink-500 uppercase">Overall Return</p><p className={`text-xl font-bold mt-1 ${overallReturn >= 0 ? "text-emerald-600" : "text-red-600"}`}>{overallReturn.toFixed(1)}%</p></Card>
      </div>

      {showForm && (
        <Card>
          <CardHeader title="New Investment" />
          <form onSubmit={handleSubmit} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 items-end">
            <Select label="Type" value={form.investment_type} onChange={(e) => setForm({ ...form, investment_type: e.target.value })}>
              {TYPES.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
            </Select>
            <Input label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
            <Input label="Start date" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
            <Input label="Invested amount (₹)" type="number" min={0} required value={form.invested_amount} onChange={(e) => setForm({ ...form, invested_amount: e.target.value })} />
            <Input label="Current value (₹)" type="number" min={0} required value={form.current_value} onChange={(e) => setForm({ ...form, current_value: e.target.value })} />
            <Button type="submit" className="lg:col-span-3">Add Investment</Button>
          </form>
        </Card>
      )}

      {investments.length === 0 ? (
        <Card><EmptyState title="No investments on file" description="Add an investment to track its performance." /></Card>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {investments.map((i) => (
            <Card key={i.id}>
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-semibold text-ink-900">{i.name || i.investment_type}</p>
                  <p className="text-xs text-ink-500 capitalize">{i.investment_type.replace("_", " ")}</p>
                </div>
                <Badge tone={i.returns_percentage >= 0 ? "success" : "danger"}>{i.returns_percentage >= 0 ? "+" : ""}{i.returns_percentage}%</Badge>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-ink-500">
                <div>Invested: <span className="font-medium text-ink-900">₹{i.invested_amount.toLocaleString("en-IN")}</span></div>
                <div>Current: <span className="font-medium text-ink-900">₹{i.current_value.toLocaleString("en-IN")}</span></div>
              </div>
              <button onClick={() => handleDelete(i.id)} className="text-xs text-red-600 font-medium hover:underline mt-3">Delete</button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
