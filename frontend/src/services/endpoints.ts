import { api } from "./api";
import type {
  AuthResponse, User, FinancialProfile, Transaction, Goal, Loan, InsurancePolicy,
  Investment, LiteracyQuestion, LiteracyResult, RiskQuestion, RiskResult,
  BehaviorAnalysis, FinancialHealth, Recommendation, Notification, Dashboard,
} from "../types";

// ---------- Auth ----------
export const authApi = {
  register: (data: { name: string; email: string; password: string; age?: number; occupation?: string }) =>
    api.post<AuthResponse>("/auth/register", data).then((r) => r.data),
  login: (data: { email: string; password: string }) =>
    api.post<AuthResponse>("/auth/login", data).then((r) => r.data),
  me: () => api.get<User>("/auth/me").then((r) => r.data),
};

// ---------- Profile ----------
export const profileApi = {
  get: () => api.get<FinancialProfile>("/profile").then((r) => r.data),
  update: (data: Partial<FinancialProfile>) => api.put<FinancialProfile>("/profile", data).then((r) => r.data),
};

// ---------- Transactions ----------
export const transactionsApi = {
  list: (params?: { category?: string; type?: string; start_date?: string; end_date?: string }) =>
    api.get<Transaction[]>("/transactions", { params }).then((r) => r.data),
  create: (data: Omit<Transaction, "id" | "user_id" | "created_at">) =>
    api.post<Transaction>("/transactions", data).then((r) => r.data),
  update: (id: number, data: Partial<Transaction>) =>
    api.put<Transaction>(`/transactions/${id}`, data).then((r) => r.data),
  remove: (id: number) => api.delete(`/transactions/${id}`),
};

// ---------- Goals ----------
export const goalsApi = {
  list: () => api.get<Goal[]>("/goals").then((r) => r.data),
  create: (data: { name: string; goal_type: string; target_amount: number; current_amount: number; target_date: string; priority: string }) =>
    api.post<Goal>("/goals", data).then((r) => r.data),
  update: (id: number, data: Partial<Goal>) => api.put<Goal>(`/goals/${id}`, data).then((r) => r.data),
  remove: (id: number) => api.delete(`/goals/${id}`),
};

// ---------- Loans ----------
export const loansApi = {
  list: () => api.get<Loan[]>("/loans").then((r) => r.data),
  create: (data: Omit<Loan, "id" | "user_id">) => api.post<Loan>("/loans", data).then((r) => r.data),
  remove: (id: number) => api.delete(`/loans/${id}`),
};

// ---------- Insurance ----------
export const insuranceApi = {
  list: () => api.get<InsurancePolicy[]>("/insurance").then((r) => r.data),
  create: (data: Omit<InsurancePolicy, "id" | "user_id">) => api.post<InsurancePolicy>("/insurance", data).then((r) => r.data),
  remove: (id: number) => api.delete(`/insurance/${id}`),
};

// ---------- Investments ----------
export const investmentsApi = {
  list: () => api.get<Investment[]>("/investments").then((r) => r.data),
  create: (data: { investment_type: string; name?: string; invested_amount: number; current_value: number; start_date?: string }) =>
    api.post<Investment>("/investments", data).then((r) => r.data),
  remove: (id: number) => api.delete(`/investments/${id}`),
};

// ---------- Literacy ----------
export const literacyApi = {
  questions: () => api.get<LiteracyQuestion[]>("/literacy/questions").then((r) => r.data),
  submit: (answers: Record<number, string>) => api.post<LiteracyResult>("/literacy/submit", { answers }).then((r) => r.data),
  result: () => api.get<LiteracyResult>("/literacy/result").then((r) => r.data),
};

// ---------- Risk ----------
export const riskApi = {
  questions: () => api.get<RiskQuestion[]>("/risk/questions").then((r) => r.data),
  submit: (answers: Record<number, number>) => api.post<RiskResult>("/risk/submit", { answers }).then((r) => r.data),
  result: () => api.get<RiskResult>("/risk/result").then((r) => r.data),
};

// ---------- Behavior ----------
export const behaviorApi = {
  get: () => api.get<BehaviorAnalysis>("/behavior-analysis").then((r) => r.data),
};

// ---------- Financial Health ----------
export const financialHealthApi = {
  get: () => api.get<FinancialHealth>("/financial-health").then((r) => r.data),
};

// ---------- Recommendations ----------
export const recommendationsApi = {
  list: () => api.get<Recommendation[]>("/recommendations").then((r) => r.data),
  get: (id: number) => api.get<Recommendation>(`/recommendations/${id}`).then((r) => r.data),
};

// ---------- Notifications ----------
export const notificationsApi = {
  list: () => api.get<Notification[]>("/notifications").then((r) => r.data),
  markRead: (id: number) => api.put<Notification>(`/notifications/${id}/read`).then((r) => r.data),
};

// ---------- Dashboard ----------
export const dashboardApi = {
  get: () => api.get<Dashboard>("/dashboard").then((r) => r.data),
};
