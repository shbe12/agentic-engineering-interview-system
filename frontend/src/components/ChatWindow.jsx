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
    <div>
      <PhaseIndicator phase={phase} />
      <label className="mb-3 flex items-center gap-1.5 text-sm">
        <input type="checkbox" checked={voiceOn} onChange={(e) => setVoiceOn(e.target.checked)} />
        Play interviewer voice
      </label>
      {anxietyNote && (
        <div className="mb-3 rounded-md border border-amber-600 bg-amber-950/40 px-3 py-2 text-sm">
          {anxietyNote}
        </div>
      )}
      <div className="mb-3 flex max-h-[55vh] flex-col gap-2.5 overflow-y-auto px-1 py-2">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[85%] rounded-lg px-3 py-2 ${
              m.role === "interviewer"
                ? "self-start bg-[var(--accent-bg)]"
                : "self-end bg-[var(--social-bg)]"
            }`}
          >
            <span className="block text-xs opacity-60">
              {m.role === "interviewer" ? "Interviewer" : "You"}
            </span>
            <p className="m-0 whitespace-pre-wrap">{m.content}</p>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSend} className="mb-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your answer…"
          disabled={sending}
          className="flex-1 rounded-md border border-[var(--border)] bg-transparent px-2.5 py-2"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="rounded-md bg-[var(--accent)] px-4 py-2 font-medium text-white disabled:opacity-50"
        >
          Send
        </button>
      </form>
      <VoiceRecorder onRecorded={handleVoice} disabled={sending} />
    </div>
  );
}
