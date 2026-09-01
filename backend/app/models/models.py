import enum
from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, Float, String, Boolean, DateTime, Date, ForeignKey, Text, Enum, Index
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class GoalPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class GoalStatus(str, enum.Enum):
    in_progress = "in_progress"
    achieved = "achieved"
    behind = "behind"


class RiskLevel(str, enum.Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class LiteracyLevel(str, enum.Enum):
    beginner = "beginner"
    basic = "basic"
    intermediate = "intermediate"
    advanced = "advanced"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    age = Column(Integer, nullable=True)
    occupation = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("FinancialProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("FinancialGoal", back_populates="user", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")
    insurances = relationship("Insurance", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    literacy_attempts = relationship("LiteracyAttempt", back_populates="user", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="user", cascade="all, delete-orphan")
    behavior_analyses = relationship("BehaviorAnalysis", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    education_level = Column(String(50), nullable=True)
    monthly_income = Column(Float, default=0.0)
    monthly_expenses = Column(Float, default=0.0)
    current_savings = Column(Float, default=0.0)
    monthly_investment_contribution = Column(Float, default=0.0)
    emergency_fund = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    date = Column(Date, nullable=False, default=date.today)
    category = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    description = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "date"),
    )


class FinancialGoal(Base):
    __tablename__ = "financial_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(120), nullable=False)
    goal_type = Column(String(50), nullable=False, default="custom")
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(Date, nullable=False)
    priority = Column(Enum(GoalPriority), default=GoalPriority.medium)
    status = Column(Enum(GoalStatus), default=GoalStatus.in_progress)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="goals")


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    loan_type = Column(String(50), nullable=False)
    principal_amount = Column(Float, nullable=False)
    outstanding_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    emi = Column(Float, nullable=False)
    start_date = Column(Date, nullable=True)
    tenure_months = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="loans")


class Insurance(Base):
    __tablename__ = "insurances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    insurance_type = Column(String(50), nullable=False)  # life, health, vehicle, home, other
    provider = Column(String(120), nullable=True)
    coverage_amount = Column(Float, nullable=False)
    premium_amount = Column(Float, nullable=False)
    premium_frequency = Column(String(20), default="yearly")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="insurances")


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    investment_type = Column(String(50), nullable=False)  # stocks, mutual_funds, fd, ppf, gold, crypto, other
    name = Column(String(120), nullable=True)
    invested_amount = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    start_date = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="investments")


class LiteracyQuestion(Base):
    __tablename__ = "literacy_questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON-encoded list
    correct_answer = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    topic = Column(String(50), nullable=False)


class LiteracyAttempt(Base):
    __tablename__ = "literacy_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    score_percentage = Column(Float, nullable=False)
    level = Column(Enum(LiteracyLevel), nullable=False)
    answers = Column(Text, nullable=True)  # JSON-encoded {question_id: answer}
    total_questions = Column(Integer, nullable=False)
    correct_count = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="literacy_attempts")


class RiskQuestion(Base):
    __tablename__ = "risk_questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    options = Column(Text, nullable=False)  # JSON-encoded list of {text, score}
    factor = Column(String(50), nullable=False)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    total_score = Column(Float, nullable=False)
    risk_level = Column(Enum(RiskLevel), nullable=False)
    answers = Column(Text, nullable=True)  # JSON-encoded

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="risk_assessments")


class BehaviorAnalysis(Base):
    __tablename__ = "behavior_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    avg_monthly_spending = Column(Float, default=0.0)
    spending_volatility = Column(Float, default=0.0)
    savings_consistency = Column(Float, default=0.0)
    discretionary_ratio = Column(Float, default=0.0)
    essential_ratio = Column(Float, default=0.0)
    investment_consistency = Column(Float, default=0.0)
    debt_burden = Column(Float, default=0.0)
    savings_rate = Column(Float, default=0.0)
    recurring_expense_ratio = Column(Float, default=0.0)
    category_concentration = Column(Float, default=0.0)

    cluster_label = Column(String(50), nullable=True)
    cluster_id = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="behavior_analyses")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # savings, investment, insurance, credit, goal
    recommendation = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False)  # high, medium, low
    reason = Column(Text, nullable=False)
    supporting_metrics = Column(Text, nullable=True)  # JSON-encoded
    expected_benefit = Column(Text, nullable=True)
    action = Column(Text, nullable=False)
    explanation_type = Column(String(30), default="rule_based")  # rule_based, ml_based, hybrid
    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recommendations")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    type = Column(String(50), nullable=False)  # budget_exceeded, savings_goal, emi_reminder, goal_reminder, unusual_spending
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    severity = Column(String(20), default="info")  # info, warning, critical

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
