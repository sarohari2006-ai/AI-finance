import { useEffect, useState } from "react";
import { profileApi } from "../services/endpoints";
import type { FinancialProfile } from "../types";
import { Card, CardHeader, Button, Input, Select, PageLoading, ErrorState } from "../components/ui";
import { useToast } from "../hooks/useToast";
import { getErrorMessage } from "../services/api";
import { useAuth } from "../hooks/useAuth";

export default function Profile() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [, setProfile] = useState<FinancialProfile | null>(null);
  const [form, setForm] = useState({
    education_level: "",
    monthly_income: "",
    monthly_expenses: "",
    current_savings: "",
    monthly_investment_contribution: "",
    emergency_fund: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    profileApi
      .get()
      .then((p) => {
        setProfile(p);
        setForm({
          education_level: p.education_level || "undergraduate",
          monthly_income: String(p.monthly_income ?? ""),
          monthly_expenses: String(p.monthly_expenses ?? ""),
          current_savings: String(p.current_savings ?? ""),
          monthly_investment_contribution: String(p.monthly_investment_contribution ?? ""),
          emergency_fund: String(p.emergency_fund ?? ""),
        });
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const updated = await profileApi.update({
        education_level: form.education_level,
        monthly_income: Number(form.monthly_income) || 0,
        monthly_expenses: Number(form.monthly_expenses) || 0,
        current_savings: Number(form.current_savings) || 0,
        monthly_investment_contribution: Number(form.monthly_investment_contribution) || 0,
        emergency_fund: Number(form.emergency_fund) || 0,
      });
      setProfile(updated);
      showToast("Financial profile updated", "success");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <PageLoading />;

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-ink-900">Financial Profile</h1>
        <p className="text-sm text-ink-500 mt-1">Keep this up to date for accurate recommendations.</p>
      </div>

      {error && <ErrorState message={error} />}

      <Card>
        <CardHeader title="Personal Information" />
        <div className="grid sm:grid-cols-2 gap-4">
          <Input label="Name" value={user?.name || ""} disabled />
          <Input label="Age" value={user?.age?.toString() || ""} disabled />
          <Input label="Occupation" value={user?.occupation || ""} disabled className="sm:col-span-2" />
        </div>
        <p className="text-xs text-ink-500 mt-2">Update personal details in Settings.</p>
      </Card>

      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader title="Financial Information" subtitle="Used to calculate savings rate, health score, and recommendations" />
          <div className="grid sm:grid-cols-2 gap-4">
            <Select label="Education level" value={form.education_level} onChange={(e) => setForm({ ...form, education_level: e.target.value })}>
              <option value="high_school">High School</option>
              <option value="undergraduate">Undergraduate</option>
              <option value="postgraduate">Postgraduate</option>
              <option value="other">Other</option>
            </Select>
            <div />
            <Input label="Monthly income (₹)" type="number" min={0} value={form.monthly_income} onChange={(e) => setForm({ ...form, monthly_income: e.target.value })} />
            <Input label="Monthly expenses (₹)" type="number" min={0} value={form.monthly_expenses} onChange={(e) => setForm({ ...form, monthly_expenses: e.target.value })} />
            <Input label="Current savings (₹)" type="number" min={0} value={form.current_savings} onChange={(e) => setForm({ ...form, current_savings: e.target.value })} />
            <Input label="Emergency fund (₹)" type="number" min={0} value={form.emergency_fund} onChange={(e) => setForm({ ...form, emergency_fund: e.target.value })} />
            <Input label="Monthly investment contribution (₹)" type="number" min={0} value={form.monthly_investment_contribution} onChange={(e) => setForm({ ...form, monthly_investment_contribution: e.target.value })} />
          </div>
          <div className="mt-5">
            <Button type="submit" disabled={saving}>{saving ? "Saving..." : "Save changes"}</Button>
          </div>
        </Card>
      </form>
    </div>
  );
}
