import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useState } from "react";
import clsx from "clsx";
import { useAuth } from "../hooks/useAuth";

const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/profile", label: "Financial Profile", icon: "👤" },
  { to: "/transactions", label: "Transactions", icon: "💳" },
  { to: "/goals", label: "Financial Goals", icon: "🎯" },
  { to: "/loans", label: "Loans / Credit", icon: "🏦" },
  { to: "/insurance", label: "Insurance", icon: "🛡️" },
  { to: "/investments", label: "Investments", icon: "📈" },
  { to: "/behavior", label: "Behavioral Analysis", icon: "🧠" },
  { to: "/literacy", label: "Financial Literacy", icon: "📚" },
  { to: "/risk", label: "Risk Assessment", icon: "⚖️" },
  { to: "/recommendations", label: "AI Recommendations", icon: "✨" },
  { to: "/notifications", label: "Notifications", icon: "🔔" },
  { to: "/settings", label: "Profile / Settings", icon: "⚙️" },
];

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex bg-ink-100">
      {/* Sidebar */}
      <aside
        className={clsx(
          "fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-ink-100 flex flex-col transition-transform lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="h-16 flex items-center gap-2 px-5 border-b border-ink-100">
          <span className="text-xl">💰</span>
          <span className="font-bold text-ink-900 text-sm leading-tight">
            AI Financial<br />Advisor
          </span>
        </div>
        <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                  isActive ? "bg-brand-50 text-brand-700" : "text-ink-700 hover:bg-ink-100"
                )
              }
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-ink-100">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-ink-700 hover:bg-ink-100"
          >
            <span>🚪</span> Logout
          </button>
        </div>
      </aside>

      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/30 z-30 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-ink-100 flex items-center justify-between px-4 lg:px-8 sticky top-0 z-20">
          <button className="lg:hidden text-ink-700" onClick={() => setSidebarOpen(true)}>
            ☰
          </button>
          <div className="hidden lg:block" />
          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium text-ink-900">{user?.name}</p>
              <p className="text-xs text-ink-500">{user?.occupation || "Member"}</p>
            </div>
            <div className="w-9 h-9 rounded-full bg-brand-600 text-white flex items-center justify-center font-semibold text-sm">
              {user?.name?.charAt(0).toUpperCase()}
            </div>
          </div>
        </header>
        <main className="flex-1 p-4 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
