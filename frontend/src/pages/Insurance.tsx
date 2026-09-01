import { useEffect, useState } from "react";
import { insuranceApi } from "../services/endpoints";
import type { InsurancePolicy } from "../types";
import { Card, CardHeader, Button, Input, Select, PageLoading, EmptyState } from "../components/ui";
import { useToast } from "../hooks/useToast";
import { getErrorMessage } from "../services/api";

const TYPES = ["health", "life", "vehicle", "home", "other"];

const emptyForm = {
  insurance_type: "health",
  provider: "",
  coverage_amount: "",
  premium_amount: "",
  premium_frequency: "yearly",
  start_date: "",
  end_date: "",
};

export default function Insurance() {
  const { showToast } = useToast();
  const [policies, setPolicies] = useState<InsurancePolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);

  const load = () => {
    setLoading(true);
    insuranceApi.list().then(setPolicies).catch((err) => showToast(getErrorMessage(err), "error")).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await insuranceApi.create({
        insurance_type: form.insurance_type,
        provider: form.provider || undefined,
        coverage_amount: Number(form.coverage_amount),
        premium_amount: Number(form.premium_amount),
        premium_frequency: form.premium_frequency,
        start_date: form.start_date || undefined,
        end_date: form.end_date || undefined,
      });
      showToast("Insurance policy added", "success");
      setForm(emptyForm);
      setShowForm(false);
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this policy?")) return;
    try {
      await insuranceApi.remove(id);
      showToast("Policy deleted", "success");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  if (loading) return <PageLoading />;

  const hasHealth = policies.some((p) => p.insurance_type === "health");
  const hasLife = policies.some((p) => p.insurance_type === "life");

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink-900">Insurance</h1>
          <p className="text-sm text-ink-500 mt-1">Track your coverage. Educational guidance only — not professional insurance advice.</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? "Close" : "+ Add Policy"}</Button>
      </div>

      {(!hasHealth || !hasLife) && (
        <div className="rounded-lg bg-amber-50 border border-amber-200 text-amber-800 text-sm px-4 py-3">
          {!hasHealth && "No health insurance on file. "}{!hasLife && "No life insurance on file. "}
          Consider reviewing your coverage — see AI Recommendations for details.
        </div>
      )}

      {showForm && (
        <Card>
          <CardHeader title="New Insurance Policy" />
          <form onSubmit={handleSubmit} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 items-end">
            <Select label="Type" value={form.insurance_type} onChange={(e) => setForm({ ...form, insurance_type: e.target.value })}>
              {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </Select>
            <Input label="Provider" value={form.provider} onChange={(e) => setForm({ ...form, provider: e.target.value })} />
            <Select label="Premium frequency" value={form.premium_frequency} onChange={(e) => setForm({ ...form, premium_frequency: e.target.value })}>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </Select>
            <Input label="Coverage amount (₹)" type="number" min={0} required value={form.coverage_amount} onChange={(e) => setForm({ ...form, coverage_amount: e.target.value })} />
            <Input label="Premium amount (₹)" type="number" min={0} required value={form.premium_amount} onChange={(e) => setForm({ ...form, premium_amount: e.target.value })} />
            <Input label="Start date" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
            <Button type="submit" className="lg:col-span-3">Add Policy</Button>
          </form>
        </Card>
      )}

      {policies.length === 0 ? (
        <Card><EmptyState title="No insurance policies on file" /></Card>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {policies.map((p) => (
            <Card key={p.id}>
              <p className="font-semibold text-ink-900 capitalize">{p.insurance_type} insurance</p>
              <p className="text-xs text-ink-500 mb-2">{p.provider || "No provider listed"}</p>
              <div className="grid grid-cols-2 gap-2 text-xs text-ink-500">
                <div>Coverage: <span className="font-medium text-ink-900">₹{p.coverage_amount.toLocaleString("en-IN")}</span></div>
                <div>Premium: <span className="font-medium text-ink-900">₹{p.premium_amount.toLocaleString("en-IN")}/{p.premium_frequency}</span></div>
              </div>
              <button onClick={() => handleDelete(p.id)} className="text-xs text-red-600 font-medium hover:underline mt-3">Delete</button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
