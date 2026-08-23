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

  if (error) return <p className="error">Could not load report: {error}</p>;
  if (!report) return <p>Generating your final report…</p>;

  return (
    <div className="report-view">
      <h2>Final report</h2>
      <p className="summary">{report.summary}</p>
      <table className="scores">
        <tbody>
          {Object.entries(report.per_phase_scores).map(([phase, score]) => (
            <tr key={phase}>
              <td>{PHASE_LABELS[phase] ?? `Phase ${phase}`}</td>
              <td>{score === null || score === undefined ? "—" : `${score}/100`}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
