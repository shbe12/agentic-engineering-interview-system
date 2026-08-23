const PHASE_LABELS = {
  1: "Background",
  2: "Technical deep-dive — project 1",
  3: "Technical deep-dive — project 2",
  4: "Factual ML questions",
  5: "Behavioral",
};

export default function PhaseIndicator({ phase }) {
  return (
    <div className="phase-indicator">
      {[1, 2, 3, 4, 5].map((p) => (
        <div key={p} className={`phase-step ${p === phase ? "active" : p < phase ? "done" : ""}`}>
          <span className="phase-number">{p}</span>
          <span className="phase-label">{PHASE_LABELS[p]}</span>
        </div>
      ))}
    </div>
  );
}
