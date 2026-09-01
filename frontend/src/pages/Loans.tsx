import { useEffect, useState } from "react";
import { loansApi } from "../services/endpoints";
import type { Loan } from "../types";
import { Card, CardHeader, Button, Input, Select, PageLoading, EmptyState, Badge } from "../components/ui";
import { useToast } from "../hooks/useToast";
import { getErrorMessage } from "../services/api";

const LOAN_TYPES = ["home_loan", "car_loan", "personal_loan", "education_loan", "credit_card", "other"];

const emptyForm = {
  loan_type: "personal_loan",
  principal_amount: "",
  outstanding_amount: "",
  interest_rate: "",
  emi: "",
  start_date: "",
  tenure_months: "",
};

export default function Loans() {
  const { showToast } = useToast();
  const [loans, setLoans] = useState<Loan[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);

  const load = () => {
    setLoading(true);
    loansApi.list().then(setLoans).catch((err) => showToast(getErrorMessage(err), "error")).finally(() => setLoading(false));
  };
  useEffect(load, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await loansApi.create({
        loan_type: form.loan_type,
        principal_amount: Number(form.principal_amount),
        outstanding_amount: Number(form.outstanding_amount),
        interest_rate: Number(form.interest_rate),
        emi: Number(form.emi),
        start_date: form.start_date || undefined,
        tenure_months: form.tenure_months ? Number(form.tenure_months) : undefined,
      });
      showToast("Loan added", "success");
      setForm(emptyForm);
      setShowForm(false);
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this loan record?")) return;
    try {
      await loansApi.remove(id);
      showToast("Loan deleted", "success");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const totalEmi = loans.reduce((s, l) => s + l.emi, 0);
  const totalOutstanding = loans.reduce((s, l) => s + l.outstanding_amount, 0);

  if (loading) return <PageLoading />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink-900">Loans & Credit</h1>
          <p className="text-sm text-ink-500 mt-1">Track your outstanding loans and EMI obligations.</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? "Close" : "+ Add Loan"}</Button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Card><p className="text-xs text-ink-500 uppercase">Total Monthly EMI</p><p className="text-xl font-bold text-ink-900 mt-1">₹{totalEmi.toLocaleString("en-IN")}</p></Card>
        <Card><p className="text-xs text-ink-500 uppercase">Total Outstanding</p><p className="text-xl font-bold text-ink-900 mt-1">₹{totalOutstanding.toLocaleString("en-IN")}</p></Card>
      </div>

      {showForm && (
        <Card>
          <CardHeader title="New Loan" />
          <form onSubmit={handleSubmit} className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 items-end">
            <Select label="Loan type" value={form.loan_type} onChange={(e) => setForm({ ...form, loan_type: e.target.value })}>
              {LOAN_TYPES.map((t) => <option key={t} value={t}>{t.replace("_", " ")}</option>)}
            </Select>
            <Input label="Principal amount (₹)" type="number" min={0} required value={form.principal_amount} onChange={(e) => setForm({ ...form, principal_amount: e.target.value })} />
            <Input label="Outstanding amount (₹)" type="number" min={0} required value={form.outstanding_amount} onChange={(e) => setForm({ ...form, outstanding_amount: e.target.value })} />
            <Input label="Interest rate (% p.a.)" type="number" min={0} step="0.1" required value={form.interest_rate} onChange={(e) => setForm({ ...form, interest_rate: e.target.value })} />
            <Input label="Monthly EMI (₹)" type="number" min={0} required value={form.emi} onChange={(e) => setForm({ ...form, emi: e.target.value })} />
            <Input label="Tenure (months)" type="number" min={0} value={form.tenure_months} onChange={(e) => setForm({ ...form, tenure_months: e.target.value })} />
            <Input label="Start date" type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
            <Button type="submit" className="lg:col-span-3">Add Loan</Button>
          </form>
        </Card>
      )}

      {loans.length === 0 ? (
        <Card><EmptyState title="No loans on file" description="Add a loan to track EMI and debt burden." /></Card>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {loans.map((l) => (
            <Card key={l.id}>
              <div className="flex items-start justify-between mb-2">
                <p className="font-semibold text-ink-900 capitalize">{l.loan_type.replace("_", " ")}</p>
                {l.interest_rate >= 12 && <Badge tone="warning">High interest</Badge>}
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs text-ink-500">
                <div>Principal: <span className="font-medium text-ink-900">₹{l.principal_amount.toLocaleString("en-IN")}</span></div>
                <div>Outstanding: <span className="font-medium text-ink-900">₹{l.outstanding_amount.toLocaleString("en-IN")}</span></div>
                <div>Interest rate: <span className="font-medium text-ink-900">{l.interest_rate}%</span></div>
                <div>EMI: <span className="font-medium text-ink-900">₹{l.emi.toLocaleString("en-IN")}/mo</span></div>
              </div>
              <button onClick={() => handleDelete(l.id)} className="text-xs text-red-600 font-medium hover:underline mt-3">Delete</button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
