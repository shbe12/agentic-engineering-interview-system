import { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import ReportView from "./components/ReportView";
import ResumeUpload from "./components/ResumeUpload";
import { startInterview } from "./api/client";

const STEPS = { UPLOAD: "upload", READY: "ready", CHAT: "chat", REPORT: "report" };

export default function App() {
  const [step, setStep] = useState(STEPS.UPLOAD);
  const [candidate, setCandidate] = useState(null);
  const [session, setSession] = useState(null);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState(null);

  function handleUploaded(result) {
    setCandidate(result);
    setStep(STEPS.READY);
  }

  async function handleStart() {
    setStarting(true);
    setError(null);
    try {
      const result = await startInterview(candidate.candidate_id);
      setSession(result);
      setStep(STEPS.CHAT);
    } catch (err) {
      setError(err.message);
    } finally {
      setStarting(false);
    }
  }

  function handleCompleted() {
    setStep(STEPS.REPORT);
  }

  return (
    <div className="mx-auto max-w-2xl px-5 py-8 text-left">
      <h1 className="mb-6 text-2xl font-semibold text-[var(--text-h)]">AI Mock Interview Agent</h1>

      {step === STEPS.UPLOAD && <ResumeUpload onUploaded={handleUploaded} />}

      {step === STEPS.READY && candidate && (
        <div className="flex flex-col items-start gap-3">
          <h2 className="text-lg font-medium text-[var(--text-h)]">
            Hi {candidate.resume_sections.name || "there"} 👋
          </h2>
          <p>
            Field detected: <strong>{candidate.field}</strong>
          </p>
          <button
            onClick={handleStart}
            disabled={starting}
            className="rounded-md bg-[var(--accent)] px-4 py-2 font-medium text-white disabled:opacity-50"
          >
            {starting ? "Starting…" : "Begin interview"}
          </button>
          {error && <p className="text-red-500">{error}</p>}
        </div>
      )}

      {step === STEPS.CHAT && session && (
        <ChatWindow
          sessionId={session.session_id}
          initialPhase={session.phase}
          initialMessage={session.message}
          onCompleted={handleCompleted}
        />
      )}

      {step === STEPS.REPORT && session && <ReportView sessionId={session.session_id} />}
    </div>
  );
}
