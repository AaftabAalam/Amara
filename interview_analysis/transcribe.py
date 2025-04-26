from fastapi import UploadFile, File
import uuid
import os
import shutil
import whisper


model = whisper.load_model("small")

UPLOAD_DIR = "audio_logs"
TRANSCRIPTION_DIR = "transcriptions"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

async def transcribe_audio(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[-1]
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = model.transcribe(file_path)
    transcription_text = result["text"]

    transcription_filename = f"transcription_{uuid.uuid4().hex}.txt"
    transcription_filepath = os.path.join(TRANSCRIPTION_DIR, transcription_filename)

    with open(transcription_filepath, "w") as f:
        f.write(transcription_text)

    os.remove(file_path)

    return  {"file_saved_as": transcription_filename}
