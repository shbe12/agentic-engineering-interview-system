const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function asJson(res) {
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  return res.json();
}

export async function uploadResume(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/resume/upload`, { method: "POST", body: form });
  return asJson(res);
}

export async function startInterview(candidateId) {
  const res = await fetch(`${BASE_URL}/interview/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ candidate_id: candidateId }),
  });
  return asJson(res);
}

export async function sendMessage(sessionId, content) {
  const res = await fetch(`${BASE_URL}/interview/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, content }),
  });
  return asJson(res);
}

export async function sendVoiceMessage(sessionId, blob) {
  const form = new FormData();
  form.append("file", blob, "answer.webm");
  const res = await fetch(
    `${BASE_URL}/interview/voice?session_id=${encodeURIComponent(sessionId)}`,
    { method: "POST", body: form }
  );
  return asJson(res);
}

export async function speak(text) {
  const res = await fetch(`${BASE_URL}/interview/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.blob();
}

export async function getReport(sessionId) {
  const res = await fetch(`${BASE_URL}/interview/${sessionId}/report`);
  return asJson(res);
}
