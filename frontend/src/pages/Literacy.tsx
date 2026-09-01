import { useEffect, useState } from "react";
import { literacyApi } from "../services/endpoints";
import type { LiteracyQuestion, LiteracyResult } from "../types";
import { Card, CardHeader, Button, PageLoading, Badge, ErrorState } from "../components/ui";
import { useToast } from "../hooks/useToast";
import { getErrorMessage } from "../services/api";

const LEVEL_TONE: Record<string, "danger" | "warning" | "brand" | "success"> = {
  beginner: "danger",
  basic: "warning",
  intermediate: "brand",
  advanced: "success",
};

export default function Literacy() {
  const { showToast } = useToast();
  const [questions, setQuestions] = useState<LiteracyQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<number, string>>({});
  const [result, setResult] = useState<LiteracyResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([literacyApi.questions(), literacyApi.result().catch(() => null)])
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
      const res = await literacyApi.submit(answers);
      setResult(res);
      showToast("Assessment submitted", "success");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setSubmitting(false);
    }
  };

  const retake = () => {
    setResult(null);
    setAnswers({});
  };

  if (loading) return <PageLoading />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-ink-900">Financial Literacy Assessment</h1>
        <p className="text-sm text-ink-500 mt-1">Test your understanding of key financial concepts. Your level shapes how detailed future recommendations are.</p>
      </div>

      {result && !result.breakdown ? (
        <Card>
          <CardHeader title="Your Latest Result" />
          <div className="flex items-center gap-4">
            <p className="text-4xl font-extrabold text-ink-900">{result.score_percentage}%</p>
            <Badge tone={LEVEL_TONE[result.level]}>{result.level}</Badge>
          </div>
          <p className="text-sm text-ink-500 mt-2">{result.correct_count} of {result.total_questions} correct.</p>
          <Button className="mt-4" onClick={retake}>Retake Assessment</Button>
        </Card>
      ) : result?.breakdown ? (
        <Card>
          <CardHeader title="Assessment Results" action={<Button size="sm" onClick={retake}>Retake</Button>} />
          <div className="flex items-center gap-4 mb-5">
            <p className="text-4xl font-extrabold text-ink-900">{result.score_percentage}%</p>
            <Badge tone={LEVEL_TONE[result.level]}>{result.level}</Badge>
          </div>
          <div className="space-y-4">
            {result.breakdown.map((b, idx) => (
              <div key={b.question_id} className="border-b border-ink-100 pb-3 last:border-0">
                <p className="text-sm font-medium text-ink-900">{idx + 1}. {b.question}</p>
                <p className={`text-xs mt-1 ${b.is_correct ? "text-emerald-600" : "text-red-600"}`}>
                  Your answer: {b.your_answer} {b.is_correct ? "✓ Correct" : `✗ Correct answer: ${b.correct_answer}`}
                </p>
                <p className="text-xs text-ink-500 mt-1">{b.explanation}</p>
              </div>
            ))}
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {questions.map((q, idx) => (
            <Card key={q.id}>
              <p className="text-sm font-medium text-ink-900 mb-3">{idx + 1}. {q.question}</p>
              <div className="space-y-2">
                {q.options.map((opt) => (
                  <label key={opt} className="flex items-center gap-2 text-sm text-ink-700 cursor-pointer">
                    <input
                      type="radio"
                      name={`q-${q.id}`}
                      value={opt}
                      checked={answers[q.id] === opt}
                      onChange={() => setAnswers({ ...answers, [q.id]: opt })}
                      className="accent-brand-600"
                    />
                    {opt}
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
