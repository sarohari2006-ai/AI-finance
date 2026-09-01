import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { Button, ErrorState, Input } from "../components/ui";
import { getErrorMessage } from "../services/api";

export default function Login() {
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const fillDemo = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword("password123");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-ink-100 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-ink-100 p-8">
        <div className="text-center mb-6">
          <div className="text-3xl mb-2">💰</div>
          <h1 className="text-xl font-bold text-ink-900">Welcome back</h1>
          <p className="text-sm text-ink-500 mt-1">Log in to your financial advisory dashboard</p>
        </div>

        {error && <div className="mb-4"><ErrorState message={error} /></div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
          <Input label="Password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "Logging in..." : "Log in"}
          </Button>
        </form>

        <div className="mt-6 pt-5 border-t border-ink-100">
          <p className="text-xs font-medium text-ink-500 mb-2">Try a demo account (password: password123)</p>
          <div className="flex flex-wrap gap-2">
            {["asha@example.com", "rohan@example.com", "priya@example.com"].map((e) => (
              <button
                key={e}
                type="button"
                onClick={() => fillDemo(e)}
                className="text-xs px-2.5 py-1 rounded-full bg-ink-100 text-ink-700 hover:bg-ink-200"
              >
                {e}
              </button>
            ))}
          </div>
        </div>

        <p className="text-center text-sm text-ink-500 mt-6">
          Don't have an account?{" "}
          <Link to="/register" className="text-brand-600 font-medium hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
