import { useState } from "react";
import { uploadResume } from "../api/client";

export default function ResumeUpload({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const result = await uploadResume(file);
      onUploaded(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col items-start gap-3">
      <h2 className="text-lg font-medium text-[var(--text-h)]">Upload your resume</h2>
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        className="text-sm"
      />
      <button
        type="submit"
        disabled={!file || loading}
        className="rounded-md bg-[var(--accent)] px-4 py-2 font-medium text-white disabled:opacity-50"
      >
        {loading ? "Parsing resume…" : "Start"}
      </button>
      {error && <p className="text-red-500">{error}</p>}
    </form>
  );
}
