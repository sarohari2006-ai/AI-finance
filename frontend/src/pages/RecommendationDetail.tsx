import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { recommendationsApi } from "../services/endpoints";
import type { Recommendation } from "../types";
import { Card, CardHeader, PageLoading, ErrorState, PriorityBadge, Badge } from "../components/ui";
import { getErrorMessage } from "../services/api";

function formatMetricValue(v: unknown): string {
  if (typeof v === "number") return v.toLocaleString("en-IN", { maximumFractionDigits: 2 });
  if (Array.isArray(v)) return v.map((x) => (typeof x === "object" ? JSON.stringify(x) : String(x))).join(", ");
  if (typeof v === "object" && v !== null) return JSON.stringify(v);
  return String(v);
}

export default function RecommendationDetail() {
  const { id } = useParams();
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    recommendationsApi
      .get(Number(id))
      .then(setRec)
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <PageLoading />;
  if (error) return <ErrorState message={error} />;
  if (!rec) return null;

  return (
    <div className="space-y-6 max-w-2xl">
      <Link to="/recommendations" className="text-sm text-brand-600 hover:underline">← Back to recommendations</Link>

      <div>
        <div className="flex items-center gap-2 mb-2">
          <Badge>{rec.category}</Badge>
          <PriorityBadge priority={rec.priority} />
        </div>
        <h1 className="text-2xl font-bold text-ink-900">{rec.title}</h1>
      </div>

      <Card>
        <CardHeader title="Recommendation" />
        <p className="text-sm text-ink-700">{rec.recommendation}</p>
      </Card>

      <Card>
        <CardHeader title="Why am I seeing this?" subtitle={`Explanation type: ${rec.explanation_type.replace("_", " ")}`} />
        <p className="text-sm text-ink-700">{rec.reason}</p>
        {rec.supporting_metrics && Object.keys(rec.supporting_metrics).length > 0 && (
          <div className="mt-4 border-t border-ink-100 pt-4">
            <p className="text-xs font-medium text-ink-500 uppercase mb-2">Supporting Data</p>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              {Object.entries(rec.supporting_metrics)
                .filter(([k]) => !["id", "user_id"].includes(k))
                .map(([k, v]) => (
                  <div key={k}>
                    <dt className="text-xs text-ink-500 capitalize">{k.replace(/_/g, " ")}</dt>
                    <dd className="font-medium text-ink-900">{formatMetricValue(v)}</dd>
                  </div>
                ))}
            </dl>
          </div>
        )}
      </Card>

      {rec.expected_benefit && (
        <Card>
          <CardHeader title="Expected Benefit" />
          <p className="text-sm text-ink-700">{rec.expected_benefit}</p>
        </Card>
      )}

      <Card>
        <CardHeader title="Recommended Action" />
        <p className="text-sm text-ink-700">{rec.action}</p>
      </Card>

      <p className="text-xs text-ink-500 border-t border-ink-100 pt-4">
        This is educational and personalized guidance based on the information you've provided. It does not
        constitute professional financial, investment, insurance, tax, or legal advice.
      </p>
    </div>
  );
}
