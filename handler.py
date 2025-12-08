import base64
import os
import tempfile

import runpod
import whisper


# --------- LOAD MODEL ONCE --------- #

MODEL_NAME = "large-v3"
print(f"Loading Whisper model: {MODEL_NAME} (this may take some time on cold start)...")
model = whisper.load_model(MODEL_NAME)
print("Model loaded.")


def handler(job: dict):
    """
    RunPod handler.

    Expects JSON like:
    {
      "input": {
        "audio_base64": "<base64-encoded audio bytes>",
        "language": "ur"          # optional, default is 'ur'
      }
    }

    Returns:
    {
      "text": "... full transcript ...",
      "segments": [
        {"id": 0, "start": 0.0, "end": 4.2, "text": "..."},
        ...
      ]
    }
    """
    job_input = job.get("input", {})

    audio_b64 = job_input.get("audio_base64")
    language = job_input.get("language", "ur")

    if not audio_b64:
        return {"error": "audio_base64 is required in input"}

    # Decode base64 -> temp file
    audio_bytes = base64.b64decode(audio_b64)
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        # This matches your local call:
        # model.transcribe(AUDIO_FILE, language="ur", task="transcribe", fp16=True)
        result = model.transcribe(
            tmp_path,
            language=language,
            task="transcribe",
            fp16=True
        )

        # Keep structure close to local whisper output
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "id": seg.get("id"),
                "start": seg.get("start"),
                "end": seg.get("end"),
                "text": seg.get("text", ""),
            })

        return {
            "text": result.get("text", ""),
            "segments": segments
        }

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


# Required for RunPod Serverless
runpod.serverless.start({"handler": handler})

