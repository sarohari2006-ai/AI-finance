"""
Notification service abstraction.

`NotificationChannel` is the interface a real push/email/SMS provider would
implement. In development (and for this academic project) we use
`InAppNotificationChannel`, which simply persists notifications to the
database for the frontend to poll/display. Swapping in a real provider
later only requires implementing `send()` — nothing else in the app needs
to change.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import List

from sqlalchemy.orm import Session

from app.models.models import Notification, User, Loan, FinancialGoal, GoalStatus


class NotificationChannel(ABC):
    @abstractmethod
    def send(self, db: Session, user: User, type_: str, title: str, message: str, severity: str = "info") -> Notification:
        ...


class InAppNotificationChannel(NotificationChannel):
    def send(self, db: Session, user: User, type_: str, title: str, message: str, severity: str = "info") -> Notification:
        notif = Notification(user_id=user.id, type=type_, title=title, message=message, severity=severity)
        db.add(notif)
        db.commit()
        db.refresh(notif)
        return notif


default_channel = InAppNotificationChannel()


def _already_alerted_today(db: Session, user: User, type_: str, title: str) -> bool:
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(hours=24)
    existing = (
        db.query(Notification)
        .filter(
            Notification.user_id == user.id,
            Notification.type == type_,
            Notification.title == title,
            Notification.created_at >= cutoff,
        )
        .first()
    )
    return existing is not None


def generate_alerts(db: Session, user: User, context: dict) -> List[Notification]:
    """Rule-based alert generation, run after the pipeline recomputes context.

    Deduplicated per 24h window per (type, title) so polling the notifications
    endpoint doesn't spam duplicate alerts.
    """
    alerts: List[Notification] = []

    def maybe_send(type_: str, title: str, message: str, severity: str):
        if not _already_alerted_today(db, user, type_, title):
            alerts.append(default_channel.send(db, user, type_, title, message, severity))

    if context["monthly_expenses"] > context["monthly_income"] > 0:
        maybe_send(
            "budget_exceeded", "Monthly Budget Exceeded",
            f"Your expenses (₹{context['monthly_expenses']:,.0f}) exceeded your income "
            f"(₹{context['monthly_income']:,.0f}) this period.",
            "critical",
        )

    if context["debt_to_income_pct"] > 40:
        maybe_send(
            "emi_reminder", "High EMI Burden",
            f"Your EMI payments are {context['debt_to_income_pct']:.0f}% of your income. "
            "Consider reviewing your loan obligations.",
            "warning",
        )

    for g in context.get("goals", []):
        if g["status"] != "achieved" and g["progress_percentage"] < 25:
            maybe_send(
                "goal_reminder", f"Goal Reminder: {g['name']}",
                f"You're at {g['progress_percentage']:.0f}% progress on '{g['name']}'. "
                f"Target date: {g['target_date']}.",
                "info",
            )

    if context["discretionary_ratio"] > 0.5:
        maybe_send(
            "unusual_spending", "High Discretionary Spending",
            f"Discretionary spending is {context['discretionary_ratio'] * 100:.0f}% of your expenses this period.",
            "warning",
        )

    return alerts
