import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { profileApi } from "../services/endpoints";
import { Button, ErrorState, Input, Select } from "../components/ui";
import { getErrorMessage } from "../services/api";

export default function Onboarding() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    education_level: "undergraduate",
    monthly_income: "",
    monthly_expenses: "",
    current_savings: "",
    monthly_investment_contribution: "",
    emergency_fund: "",
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await profileApi.update({
        education_level: form.education_level,
        monthly_income: Number(form.monthly_income) || 0,
        monthly_expenses: Number(form.monthly_expenses) || 0,
        current_savings: Number(form.current_savings) || 0,
        monthly_investment_contribution: Number(form.monthly_investment_contribution) || 0,
        emergency_fund: Number(form.emergency_fund) || 0,
      });
      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink-100 px-4 py-10">
      <div className="w-full max-w-lg bg-white rounded-2xl shadow-sm border border-ink-100 p-8">
        <h1 className="text-xl font-bold text-ink-900">Let's set up your financial profile</h1>
        <p className="text-sm text-ink-500 mt-1 mb-6">
          This helps us personalize your dashboard and recommendations. You can update this anytime.
        </p>

        {error && <div className="mb-4"><ErrorState message={error} /></div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Education level"
            value={form.education_level}
            onChange={(e) => setForm({ ...form, education_level: e.target.value })}
          >
            <option value="high_school">High School</option>
            <option value="undergraduate">Undergraduate</option>
            <option value="postgraduate">Postgraduate</option>
            <option value="other">Other</option>
          </Select>

          <div className="grid grid-cols-2 gap-3">
            <Input label="Monthly income (₹)" type="number" min={0} required value={form.monthly_income} onChange={(e) => setForm({ ...form, monthly_income: e.target.value })} />
            <Input label="Monthly expenses (₹)" type="number" min={0} required value={form.monthly_expenses} onChange={(e) => setForm({ ...form, monthly_expenses: e.target.value })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Current savings (₹)" type="number" min={0} value={form.current_savings} onChange={(e) => setForm({ ...form, current_savings: e.target.value })} />
            <Input label="Emergency fund (₹)" type="number" min={0} value={form.emergency_fund} onChange={(e) => setForm({ ...form, emergency_fund: e.target.value })} />
          </div>
          <Input
            label="Monthly investment contribution (₹)"
            type="number"
            min={0}
            value={form.monthly_investment_contribution}
            onChange={(e) => setForm({ ...form, monthly_investment_contribution: e.target.value })}
          />

          <div className="flex gap-3 pt-2">
            <Button type="submit" disabled={saving} className="flex-1">
              {saving ? "Saving..." : "Continue to dashboard"}
            </Button>
            <Button type="button" variant="ghost" onClick={() => navigate("/dashboard")}>
              Skip for now
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
