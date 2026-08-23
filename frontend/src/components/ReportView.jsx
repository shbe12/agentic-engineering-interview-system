import { useEffect, useState } from "react";
import { getReport } from "../api/client";

const PHASE_LABELS = {
  1: "Background",
  2: "Technical deep-dive — project 1",
  3: "Technical deep-dive — project 2",
  4: "Factual ML questions",
  5: "Behavioral",
};

export default function ReportView({ sessionId }) {
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    let attempts = 0;

    async function poll() {
      try {
        const data = await getReport(sessionId);
        if (!cancelled) setReport(data);
      } catch (err) {
        attempts += 1;
        if (attempts < 10) {
          setTimeout(poll, 1500); // report generation runs right after the last message
        } else if (!cancelled) {
          setError(err.message);
        }
      }
    }
    poll();
    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  if (error) return <p className="text-red-500">Could not load report: {error}</p>;
  if (!report) return <p>Generating your final report…</p>;

  return (
    <div>
      <h2 className="mb-2 text-lg font-medium text-[var(--text-h)]">Final report</h2>
      <p className="leading-relaxed">{report.summary}</p>
      <table className="mt-4 w-full border-collapse">
        <tbody>
          {Object.entries(report.per_phase_scores).map(([phase, score]) => (
            <tr key={phase}>
              <td className="border-b border-[var(--border)] py-2">
                {PHASE_LABELS[phase] ?? `Phase ${phase}`}
              </td>
              <td className="border-b border-[var(--border)] py-2">
                {score === null || score === undefined ? "—" : `${score}/100`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
