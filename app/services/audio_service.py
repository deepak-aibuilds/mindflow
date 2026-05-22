from faster_whisper import WhisperModel
import tempfile, os

model = WhisperModel("base", device="cpu", compute_type="int8")

def extract_voice(file: bytes) -> dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(file)
        tmp_path = tmp.name
    try:
        segments, info = model.transcribe(tmp_path)
        transcript = " ".join(seg.text for seg in segments)
        return {"content": transcript}
    finally:
        os.unlink(tmp_path)