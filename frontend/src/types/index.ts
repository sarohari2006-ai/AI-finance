export interface User {
  id: number;
  name: string;
  email: string;
  age?: number | null;
  occupation?: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface FinancialProfile {
  id: number;
  user_id: number;
  education_level?: string | null;
  monthly_income: number;
  monthly_expenses: number;
  current_savings: number;
  monthly_investment_contribution: number;
  emergency_fund: number;
  updated_at: string;
}

export type TransactionType = "income" | "expense";

export interface Transaction {
  id: number;
  user_id: number;
  date: string;
  category: string;
  amount: number;
  type: TransactionType;
  description?: string | null;
  created_at: string;
}

export interface Goal {
  id: number;
  user_id: number;
  name: string;
  goal_type: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  priority: "low" | "medium" | "high";
  status: "in_progress" | "achieved" | "behind";
  progress_percentage: number;
  remaining_amount: number;
  recommended_monthly_contribution: number;
}

export interface Loan {
  id: number;
  user_id: number;
  loan_type: string;
  principal_amount: number;
  outstanding_amount: number;
  interest_rate: number;
  emi: number;
  start_date?: string | null;
  tenure_months?: number | null;
}

export interface InsurancePolicy {
  id: number;
  user_id: number;
  insurance_type: string;
  provider?: string | null;
  coverage_amount: number;
  premium_amount: number;
  premium_frequency: string;
  start_date?: string | null;
  end_date?: string | null;
}

export interface Investment {
  id: number;
  user_id: number;
  investment_type: string;
  name?: string | null;
  invested_amount: number;
  current_value: number;
  start_date?: string | null;
  returns_percentage: number;
}

export interface LiteracyQuestion {
  id: number;
  question: string;
  options: string[];
  topic: string;
}

export interface LiteracyResult {
  id: number;
  score_percentage: number;
  level: "beginner" | "basic" | "intermediate" | "advanced";
  total_questions: number;
  correct_count: number;
  created_at: string;
  breakdown?: Array<{
    question_id: number;
    question: string;
    your_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
  }>;
}

export interface RiskQuestion {
  id: number;
  question: string;
  options: Array<{ text: string; score: number }>;
  factor: string;
}

export interface RiskResult {
  id: number;
  total_score: number;
  risk_level: "low" | "moderate" | "high";
  created_at: string;
}

export interface BehaviorAnalysis {
  id: number;
  avg_monthly_spending: number;
  spending_volatility: number;
  savings_consistency: number;
  discretionary_ratio: number;
  essential_ratio: number;
  investment_consistency: number;
  debt_burden: number;
  savings_rate: number;
  recurring_expense_ratio: number;
  category_concentration: number;
  cluster_label?: string | null;
  created_at: string;
  insights?: string[];
}

export interface FinancialHealth {
  score: number;
  category: string;
  components: Record<string, number>;
  explanation: Record<string, string>;
}

export interface Recommendation {
  id: number;
  title: string;
  category: "savings" | "investment" | "insurance" | "credit" | "goal";
  recommendation: string;
  priority: "high" | "medium" | "low";
  reason: string;
  supporting_metrics?: Record<string, unknown> | null;
  expected_benefit?: string | null;
  action: string;
  explanation_type: string;
  is_read: boolean;
  created_at: string;
}

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  severity: "info" | "warning" | "critical";
  created_at: string;
}

export interface Dashboard {
  financial_health: FinancialHealth;
  monthly_income: number;
  monthly_expenses: number;
  monthly_savings: number;
  savings_rate: number;
  spending_by_category: Record<string, number>;
  income_vs_expense_trend: Array<{ month: string; income: number; expense: number; savings: number }>;
  savings_trend: Array<{ month: string; savings: number }>;
  investment_trend: Array<{ date: string | null; cumulative_value: number }>;
  goals: Goal[];
  top_recommendations: Recommendation[];
  behavior_profile?: BehaviorAnalysis | null;
  risk_level?: string | null;
  literacy_level?: string | null;
  alerts: Notification[];
}
