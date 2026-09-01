import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-50 to-white">
      <header className="max-w-6xl mx-auto flex items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2 font-bold text-ink-900">
          <span className="text-2xl">💰</span> AI Financial Advisor
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="px-4 py-2 text-sm font-medium text-ink-700 hover:text-ink-900">
            Log in
          </Link>
          <Link to="/register" className="px-4 py-2 text-sm font-medium bg-brand-600 text-white rounded-lg hover:bg-brand-700">
            Get Started
          </Link>
        </div>
      </header>

      <section className="max-w-4xl mx-auto text-center px-6 pt-16 pb-20">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-ink-900 tracking-tight">
          Financial guidance that's <span className="text-brand-600">personal, clear, and explainable</span>
        </h1>
        <p className="mt-5 text-lg text-ink-500 max-w-2xl mx-auto">
          Track your income, spending, goals and investments — and get personalized recommendations
          that show exactly why they were made, based on your own numbers.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Link to="/register" className="px-6 py-3 bg-brand-600 text-white rounded-lg font-semibold hover:bg-brand-700">
            Create your free account
          </Link>
          <Link to="/login" className="px-6 py-3 bg-white border border-ink-200 text-ink-700 rounded-lg font-semibold hover:bg-ink-50">
            I already have an account
          </Link>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-6 pb-24 grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          { icon: "🎯", title: "Goal Tracking", desc: "Set savings, home, education, or retirement goals and track real progress." },
          { icon: "🧠", title: "Behavioral Insights", desc: "Understand your spending patterns and behavioral archetype." },
          { icon: "✨", title: "Explainable AI", desc: "Every recommendation shows the exact numbers behind it." },
          { icon: "📊", title: "Financial Health Score", desc: "A transparent 0-100 score built from your savings, debt, and goals." },
        ].map((f) => (
          <div key={f.title} className="bg-white rounded-xl border border-ink-100 p-5 shadow-sm">
            <div className="text-2xl">{f.icon}</div>
            <h3 className="mt-3 font-semibold text-ink-900">{f.title}</h3>
            <p className="mt-1 text-sm text-ink-500">{f.desc}</p>
          </div>
        ))}
      </section>

      <footer className="max-w-6xl mx-auto px-6 pb-10">
        <p className="text-xs text-ink-500 border-t border-ink-100 pt-6">
          This system provides educational and personalized financial guidance based on the information
          provided by the user. It does not constitute professional financial, investment, insurance, tax,
          or legal advice.
        </p>
      </footer>
    </div>
  );
}
