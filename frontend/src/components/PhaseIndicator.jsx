const PHASE_LABELS = {
  1: "Background",
  2: "Technical deep-dive — project 1",
  3: "Technical deep-dive — project 2",
  4: "Factual ML questions",
  5: "Behavioral",
};

export default function PhaseIndicator({ phase }) {
  return (
    <div className="mb-3 flex flex-wrap gap-1">
      {[1, 2, 3, 4, 5].map((p) => (
        <div
          key={p}
          className={`flex-1 rounded-md px-1 py-1.5 text-center text-xs bg-[var(--accent-bg)] ${
            p === phase
              ? "opacity-100 outline outline-2 outline-[var(--accent)]"
              : p < phase
                ? "opacity-85"
                : "opacity-50"
          }`}
        >
          <span className="block font-bold">{p}</span>
          <span>{PHASE_LABELS[p]}</span>
        </div>
      ))}
    </div>
  );
}
