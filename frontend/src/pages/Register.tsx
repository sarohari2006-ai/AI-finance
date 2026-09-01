import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { Button, ErrorState, Input } from "../components/ui";
import { getErrorMessage } from "../services/api";

export default function Register() {
  const { register, isLoading } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", age: "", occupation: "" });
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (form.password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    try {
      await register({
        name: form.name,
        email: form.email,
        password: form.password,
        age: form.age ? Number(form.age) : undefined,
        occupation: form.occupation || undefined,
      });
      navigate("/onboarding");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink-100 px-4 py-10">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-ink-100 p-8">
        <div className="text-center mb-6">
          <div className="text-3xl mb-2">💰</div>
          <h1 className="text-xl font-bold text-ink-900">Create your account</h1>
          <p className="text-sm text-ink-500 mt-1">Start your personalized financial journey</p>
        </div>

        {error && <div className="mb-4"><ErrorState message={error} /></div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Full name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Input label="Email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <Input label="Password" type="password" required minLength={6} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <Input label="Age" type="number" min={0} max={120} value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} />
            <Input label="Occupation" value={form.occupation} onChange={(e) => setForm({ ...form, occupation: e.target.value })} />
          </div>
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Creating account..." : "Create account"}
          </Button>
        </form>

        <p className="text-center text-sm text-ink-500 mt-6">
          Already have an account?{" "}
          <Link to="/login" className="text-brand-600 font-medium hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
