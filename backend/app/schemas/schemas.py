from datetime import date, datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Auth ----------

class UserRegister(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    age: Optional[int] = Field(default=None, ge=0, le=120)
    occupation: Optional[str] = Field(default=None, max_length=120)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    age: Optional[int] = None
    occupation: Optional[str] = None
    created_at: datetime


# ---------- Financial Profile ----------

class FinancialProfileBase(BaseModel):
    education_level: Optional[str] = None
    monthly_income: float = Field(default=0.0, ge=0)
    monthly_expenses: float = Field(default=0.0, ge=0)
    current_savings: float = Field(default=0.0, ge=0)
    monthly_investment_contribution: float = Field(default=0.0, ge=0)
    emergency_fund: float = Field(default=0.0, ge=0)


class FinancialProfileUpdate(FinancialProfileBase):
    pass


class FinancialProfileOut(FinancialProfileBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    updated_at: datetime


# ---------- Transactions ----------

class TransactionBase(BaseModel):
    date: date
    category: str
    amount: float = Field(gt=0)
    type: str  # income | expense
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    category: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[str] = None
    description: Optional[str] = None


class TransactionOut(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime


# ---------- Goals ----------

class GoalBase(BaseModel):
    name: str
    goal_type: str = "custom"
    target_amount: float = Field(gt=0)
    current_amount: float = Field(default=0.0, ge=0)
    target_date: date
    priority: str = "medium"


class GoalCreate(GoalBase):
    pass


class GoalUpdate(BaseModel):
    name: Optional[str] = None
    goal_type: Optional[str] = None
    target_amount: Optional[float] = Field(default=None, gt=0)
    current_amount: Optional[float] = Field(default=None, ge=0)
    target_date: Optional[date] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class GoalOut(GoalBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    status: str
    progress_percentage: float
    remaining_amount: float
    recommended_monthly_contribution: float


# ---------- Loans ----------

class LoanBase(BaseModel):
    loan_type: str
    principal_amount: float = Field(gt=0)
    outstanding_amount: float = Field(ge=0)
    interest_rate: float = Field(ge=0)
    emi: float = Field(ge=0)
    start_date: Optional[date] = None
    tenure_months: Optional[int] = None


class LoanCreate(LoanBase):
    pass


class LoanOut(LoanBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


# ---------- Insurance ----------

class InsuranceBase(BaseModel):
    insurance_type: str
    provider: Optional[str] = None
    coverage_amount: float = Field(gt=0)
    premium_amount: float = Field(ge=0)
    premium_frequency: str = "yearly"
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class InsuranceCreate(InsuranceBase):
    pass


class InsuranceOut(InsuranceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int


# ---------- Investments ----------

class InvestmentBase(BaseModel):
    investment_type: str
    name: Optional[str] = None
    invested_amount: float = Field(ge=0)
    current_value: float = Field(ge=0)
    start_date: Optional[date] = None


class InvestmentCreate(InvestmentBase):
    pass


class InvestmentOut(InvestmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    returns_percentage: float


# ---------- Literacy ----------

class LiteracyQuestionOut(BaseModel):
    id: int
    question: str
    options: List[str]
    topic: str


class LiteracySubmit(BaseModel):
    answers: Dict[int, str]  # question_id -> selected option


class LiteracyResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    score_percentage: float
    level: str
    total_questions: int
    correct_count: int
    created_at: datetime
    breakdown: Optional[List[Dict[str, Any]]] = None


# ---------- Risk ----------

class RiskQuestionOut(BaseModel):
    id: int
    question: str
    options: List[Dict[str, Any]]
    factor: str


class RiskSubmit(BaseModel):
    answers: Dict[int, int]  # question_id -> selected option index


class RiskResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    total_score: float
    risk_level: str
    created_at: datetime


# ---------- Behavior ----------

class BehaviorAnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    avg_monthly_spending: float
    spending_volatility: float
    savings_consistency: float
    discretionary_ratio: float
    essential_ratio: float
    investment_consistency: float
    debt_burden: float
    savings_rate: float
    recurring_expense_ratio: float
    category_concentration: float
    cluster_label: Optional[str] = None
    created_at: datetime
    insights: Optional[List[str]] = None


# ---------- Financial Health ----------

class FinancialHealthOut(BaseModel):
    score: float
    category: str
    components: Dict[str, float]
    explanation: Dict[str, str]


# ---------- Recommendations ----------

class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    category: str
    recommendation: str
    priority: str
    reason: str
    supporting_metrics: Optional[Dict[str, Any]] = None
    expected_benefit: Optional[str] = None
    action: str
    explanation_type: str
    is_read: bool
    created_at: datetime


# ---------- Notifications ----------

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    severity: str
    created_at: datetime


# ---------- Dashboard ----------

class DashboardOut(BaseModel):
    financial_health: FinancialHealthOut
    monthly_income: float
    monthly_expenses: float
    monthly_savings: float
    savings_rate: float
    spending_by_category: Dict[str, float]
    income_vs_expense_trend: List[Dict[str, Any]]
    savings_trend: List[Dict[str, Any]]
    investment_trend: List[Dict[str, Any]]
    goals: List[GoalOut]
    top_recommendations: List[RecommendationOut]
    behavior_profile: Optional[BehaviorAnalysisOut] = None
    risk_level: Optional[str] = None
    literacy_level: Optional[str] = None
    alerts: List[NotificationOut]
