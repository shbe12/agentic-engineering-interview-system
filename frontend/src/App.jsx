import { useState } from "react";
import "./App.css";
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
    <div className="app">
      <h1>AI Mock Interview Agent</h1>

      {step === STEPS.UPLOAD && <ResumeUpload onUploaded={handleUploaded} />}

      {step === STEPS.READY && candidate && (
        <div className="ready-panel">
          <h2>Hi {candidate.resume_sections.name || "there"} 👋</h2>
          <p>
            Field detected: <strong>{candidate.field}</strong>
          </p>
          <button onClick={handleStart} disabled={starting}>
            {starting ? "Starting…" : "Begin interview"}
          </button>
          {error && <p className="error">{error}</p>}
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
