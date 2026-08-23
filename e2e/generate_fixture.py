"""Regenerates e2e/fixtures/sample_answer.wav — a short synthesized "candidate
answer" clip used as Chromium's fake microphone input in e2e_test.py, so the
voice-answer path exercises real MediaRecorder -> Scribe STT, not just curl.

Run from the backend venv (needs the app's ElevenLabs config):
    backend/.venv/bin/python e2e/generate_fixture.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings  # noqa: E402
from app.voice.client import get_elevenlabs_client  # noqa: E402

OUT_PATH = Path(__file__).parent / "fixtures" / "sample_answer.wav"
TEXT = "I built a retrieval augmented generation system for internal documentation search."


def main() -> None:
    settings = get_settings()
    client = get_elevenlabs_client()
    audio_chunks = client.text_to_speech.convert(
        voice_id=settings.elevenlabs_voice_id,
        text=TEXT,
        model_id="eleven_multilingual_v2",
        output_format="wav_16000",
    )
    audio = b"".join(audio_chunks)
    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_bytes(audio)
    print(f"wrote {len(audio)} bytes to {OUT_PATH}")


if __name__ == "__main__":
    main()
