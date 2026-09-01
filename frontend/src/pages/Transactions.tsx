import { useEffect, useState } from "react";
import { transactionsApi } from "../services/endpoints";
import type { Transaction } from "../types";
import { Card, CardHeader, Button, Input, Select, PageLoading, EmptyState, Badge } from "../components/ui";
import { useToast } from "../hooks/useToast";
import { getErrorMessage } from "../services/api";

const CATEGORIES = ["food", "shopping", "transport", "entertainment", "utilities", "rent", "healthcare", "education", "subscriptions", "travel", "salary", "other"];

const emptyForm = {
  date: new Date().toISOString().slice(0, 10),
  category: "food",
  amount: "",
  type: "expense" as "income" | "expense",
  description: "",
};

export default function Transactions() {
  const { showToast } = useToast();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState(emptyForm);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [filterCategory, setFilterCategory] = useState("");
  const [filterType, setFilterType] = useState("");

  const load = () => {
    setLoading(true);
    transactionsApi
      .list({ category: filterCategory || undefined, type: filterType || undefined })
      .then(setTransactions)
      .catch((err) => showToast(getErrorMessage(err), "error"))
      .finally(() => setLoading(false));
  };

  useEffect(load, [filterCategory, filterType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        date: form.date,
        category: form.category,
        amount: Number(form.amount),
        type: form.type,
        description: form.description || undefined,
      };
      if (editingId) {
        await transactionsApi.update(editingId, payload);
        showToast("Transaction updated", "success");
      } else {
        await transactionsApi.create(payload);
        showToast("Transaction added", "success");
      }
      setForm(emptyForm);
      setShowForm(false);
      setEditingId(null);
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const handleEdit = (t: Transaction) => {
    setForm({ date: t.date, category: t.category, amount: String(t.amount), type: t.type, description: t.description || "" });
    setEditingId(t.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this transaction?")) return;
    try {
      await transactionsApi.remove(id);
      showToast("Transaction deleted", "success");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  };

  const totalIncome = transactions.filter((t) => t.type === "income").reduce((s, t) => s + t.amount, 0);
  const totalExpense = transactions.filter((t) => t.type === "expense").reduce((s, t) => s + t.amount, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink-900">Transactions</h1>
          <p className="text-sm text-ink-500 mt-1">Track your income and expenses.</p>
        </div>
        <Button onClick={() => { setShowForm(!showForm); setEditingId(null); setForm(emptyForm); }}>
          {showForm ? "Close" : "+ Add Transaction"}
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <Card><p className="text-xs text-ink-500 uppercase">Total Income</p><p className="text-xl font-bold text-emerald-600 mt-1">₹{totalIncome.toLocaleString("en-IN")}</p></Card>
        <Card><p className="text-xs text-ink-500 uppercase">Total Expenses</p><p className="text-xl font-bold text-red-600 mt-1">₹{totalExpense.toLocaleString("en-IN")}</p></Card>
        <Card><p className="text-xs text-ink-500 uppercase">Net</p><p className="text-xl font-bold text-ink-900 mt-1">₹{(totalIncome - totalExpense).toLocaleString("en-IN")}</p></Card>
      </div>

      {showForm && (
        <Card>
          <CardHeader title={editingId ? "Edit Transaction" : "Add Transaction"} />
          <form onSubmit={handleSubmit} className="grid sm:grid-cols-2 lg:grid-cols-5 gap-3 items-end">
            <Input label="Date" type="date" required value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
            <Select label="Type" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value as "income" | "expense" })}>
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </Select>
            <Select label="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </Select>
            <Input label="Amount (₹)" type="number" min={0.01} step="0.01" required value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
            <Input label="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            <Button type="submit" className="lg:col-span-5 sm:col-span-2">{editingId ? "Update" : "Add"} Transaction</Button>
          </form>
        </Card>
      )}

      <Card>
        <div className="flex flex-wrap gap-3 mb-4">
          <Select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="w-40">
            <option value="">All types</option>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </Select>
          <Select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)} className="w-40">
            <option value="">All categories</option>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </Select>
        </div>

        {loading ? (
          <PageLoading />
        ) : transactions.length === 0 ? (
          <EmptyState title="No transactions found" description="Add your first transaction to start tracking." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-ink-500 uppercase border-b border-ink-100">
                  <th className="py-2 pr-4">Date</th>
                  <th className="py-2 pr-4">Category</th>
                  <th className="py-2 pr-4">Description</th>
                  <th className="py-2 pr-4">Type</th>
                  <th className="py-2 pr-4 text-right">Amount</th>
                  <th className="py-2 pr-4"></th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((t) => (
                  <tr key={t.id} className="border-b border-ink-100 last:border-0 hover:bg-ink-50/50">
                    <td className="py-2.5 pr-4 text-ink-700">{t.date}</td>
                    <td className="py-2.5 pr-4 capitalize text-ink-700">{t.category}</td>
                    <td className="py-2.5 pr-4 text-ink-500">{t.description || "—"}</td>
                    <td className="py-2.5 pr-4"><Badge tone={t.type === "income" ? "success" : "neutral"}>{t.type}</Badge></td>
                    <td className={`py-2.5 pr-4 text-right font-medium ${t.type === "income" ? "text-emerald-600" : "text-ink-900"}`}>
                      {t.type === "income" ? "+" : "-"}₹{t.amount.toLocaleString("en-IN")}
                    </td>
                    <td className="py-2.5 pr-4 text-right whitespace-nowrap">
                      <button onClick={() => handleEdit(t)} className="text-xs text-brand-600 hover:underline mr-3">Edit</button>
                      <button onClick={() => handleDelete(t.id)} className="text-xs text-red-600 hover:underline">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
