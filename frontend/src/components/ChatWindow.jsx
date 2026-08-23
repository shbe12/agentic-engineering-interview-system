import { useEffect, useRef, useState } from "react";
import { sendMessage, sendVoiceMessage, speak } from "../api/client";
import PhaseIndicator from "./PhaseIndicator";
import VoiceRecorder from "./VoiceRecorder";

export default function ChatWindow({ sessionId, initialPhase, initialMessage, onCompleted }) {
  const [messages, setMessages] = useState([
    { role: "interviewer", content: initialMessage },
  ]);
  const [phase, setPhase] = useState(initialPhase);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [voiceOn, setVoiceOn] = useState(true);
  const [anxietyNote, setAnxietyNote] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (voiceOn) playReply(initialMessage);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function playReply(text) {
    try {
      const blob = await speak(text);
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
    } catch {
      // TTS is best-effort; text is already shown either way.
    }
  }

  function afterReply(result) {
    setMessages((prev) => [...prev, { role: "interviewer", content: result.reply }]);
    setPhase(result.phase);
    if (voiceOn) playReply(result.reply);
    if (result.status === "completed") onCompleted(sessionId);
  }

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim() || sending) return;
    const content = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "candidate", content }]);
    setSending(true);
    try {
      const result = await sendMessage(sessionId, content);
      afterReply(result);
    } finally {
      setSending(false);
    }
  }

  async function handleVoice(blob) {
    setSending(true);
    setMessages((prev) => [...prev, { role: "candidate", content: "🎙 (voice answer)" }]);
    try {
      const result = await sendVoiceMessage(sessionId, blob);
      if (result.anxiety_detected) {
        setAnxietyNote(result.reassurance_note);
      } else {
        setAnxietyNote(null);
      }
      afterReply(result);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="chat-window">
      <PhaseIndicator phase={phase} />
      <label className="voice-toggle">
        <input type="checkbox" checked={voiceOn} onChange={(e) => setVoiceOn(e.target.checked)} />
        Play interviewer voice
      </label>
      {anxietyNote && <div className="anxiety-banner">{anxietyNote}</div>}
      <div className="transcript">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <span className="role">{m.role === "interviewer" ? "Interviewer" : "You"}</span>
            <p>{m.content}</p>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSend} className="composer">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your answer…"
          disabled={sending}
        />
        <button type="submit" disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
      <VoiceRecorder onRecorded={handleVoice} disabled={sending} />
    </div>
  );
}
