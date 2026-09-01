import { useEffect, useState } from "react";
import { riskApi } from "../services/endpoints";
import type { RiskQuestion, RiskResult } from "../types";
import { Card, CardHeader, Button, PageLoading, Badge, ErrorState } from "../components/ui";
import { useToast } from "../hooks/useToast";
import { getErrorMessage } from "../services/api";

const LEVEL_TONE: Record<string, "success" | "warning" | "brand"> = {
  low: "success",
  moderate: "brand",
  high: "warning",
};

export default function RiskAssessment() {
  const { showToast } = useToast();
  const [questions, setQuestions] = useState<RiskQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [result, setResult] = useState<RiskResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [retaking, setRetaking] = useState(false);

  useEffect(() => {
    Promise.all([riskApi.questions(), riskApi.result().catch(() => null)])
      .then(([qs, res]) => {
        setQuestions(qs);
        if (res) setResult(res);
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = async () => {
    if (Object.keys(answers).length < questions.length) {
      showToast("Please answer all questions before submitting.", "error");
      return;
    }
    setSubmitting(true);
    try {
      const res = await riskApi.submit(answers);
      setResult(res);
      setRetaking(false);
      showToast("Risk assessment submitted", "success");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <PageLoading />;
  if (error) return <ErrorState message={error} />;

  const showQuiz = !result || retaking;

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-ink-900">Risk Tolerance Assessment</h1>
        <p className="text-sm text-ink-500 mt-1">This shapes the investment guidance you receive. It is educational, not personalized financial advice.</p>
      </div>

      {result && !retaking && (
        <Card>
          <CardHeader title="Your Risk Profile" action={<Button size="sm" onClick={() => setRetaking(true)}>Retake</Button>} />
          <Badge tone={LEVEL_TONE[result.risk_level]}>{result.risk_level} risk tolerance</Badge>
          <p className="text-sm text-ink-500 mt-3">
            Total score: {result.total_score}. This reflects your investment experience, income stability, emergency savings,
            time horizon, and comfort with market fluctuations.
          </p>
        </Card>
      )}

      {showQuiz && (
        <div className="space-y-4">
          {questions.map((q, idx) => (
            <Card key={q.id}>
              <p className="text-sm font-medium text-ink-900 mb-3">{idx + 1}. {q.question}</p>
              <div className="space-y-2">
                {q.options.map((opt, optIdx) => (
                  <label key={optIdx} className="flex items-center gap-2 text-sm text-ink-700 cursor-pointer">
                    <input
                      type="radio"
                      name={`rq-${q.id}`}
                      checked={answers[q.id] === optIdx}
                      onChange={() => setAnswers({ ...answers, [q.id]: optIdx })}
                      className="accent-brand-600"
                    />
                    {opt.text}
                  </label>
                ))}
              </div>
            </Card>
          ))}
          <Button onClick={handleSubmit} disabled={submitting}>{submitting ? "Submitting..." : "Submit Assessment"}</Button>
        </div>
      )}
    </div>
  );
}
