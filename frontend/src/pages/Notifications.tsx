import { useEffect, useState } from "react";
import { notificationsApi } from "../services/endpoints";
import type { Notification } from "../types";
import { Card, PageLoading, ErrorState, EmptyState, Badge } from "../components/ui";
import { getErrorMessage } from "../services/api";

const TYPE_ICON: Record<string, string> = {
  budget_exceeded: "⚠️",
  emi_reminder: "🏦",
  goal_reminder: "🎯",
  unusual_spending: "📊",
  savings_goal: "🎉",
};

export default function Notifications() {
  const [items, setItems] = useState<Notification[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    notificationsApi.list().then(setItems).catch((err) => setError(getErrorMessage(err))).finally(() => setLoading(false));
  }, []);

  const markRead = async (id: number) => {
    try {
      await notificationsApi.markRead(id);
      setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch {
      // non-critical
    }
  };

  if (loading) return <PageLoading />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink-900">Notifications</h1>
        <p className="text-sm text-ink-500 mt-1">Alerts and reminders based on your financial activity.</p>
      </div>

      {items.length === 0 ? (
        <Card><EmptyState title="No notifications" description="You're all caught up." /></Card>
      ) : (
        <div className="space-y-2">
          {items.map((n) => (
            <Card key={n.id} className={n.is_read ? "opacity-60" : ""} onClick={() => !n.is_read && markRead(n.id)}>
              <div className="flex items-start gap-3">
                <span className="text-xl">{TYPE_ICON[n.type] || "🔔"}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-ink-900 text-sm">{n.title}</p>
                    <Badge tone={n.severity === "critical" ? "danger" : n.severity === "warning" ? "warning" : "neutral"}>{n.severity}</Badge>
                  </div>
                  <p className="text-sm text-ink-500 mt-1">{n.message}</p>
                  <p className="text-xs text-ink-500 mt-1">{new Date(n.created_at).toLocaleString()}</p>
                </div>
                {!n.is_read && (
                  <button onClick={() => markRead(n.id)} className="text-xs text-brand-600 hover:underline whitespace-nowrap">
                    Mark read
                  </button>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
