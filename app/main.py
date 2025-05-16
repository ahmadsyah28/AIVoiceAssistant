from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import scipy.io.wavfile
import numpy as np
from app.stt import transcribe_speech_to_text
from app.llm import generate_response
from app.tts import transcribe_text_to_speech

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Server FastAPI berjalan. Gunakan endpoint /voice-chat (POST) untuk interaksi suara."}

@app.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):
    try:
        print("Menerima file audio...")
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=422, detail="File audio kosong")

        print(f"Ukuran audio: {len(audio_bytes)} bytes")
        # Simpan sementara untuk debugging
        with open("temp.wav", "wb") as f:
            f.write(audio_bytes)
        sr, audio_data = scipy.io.wavfile.read("temp.wav")
        print(f"Sample rate: {sr}, Bentuk audio: {audio_data.shape}")
        os.unlink("temp.wav")

        print("Memulai transkripsi (STT)...")
        transcript = transcribe_speech_to_text(audio_bytes)
        if transcript.startswith("[ERROR]"):
            raise HTTPException(status_code=500, detail=transcript)
        print(f"Hasil transkripsi: {transcript}")

        print("Meminta respons dari LLM...")
        response_text = generate_response(transcript)
        if response_text.startswith("[ERROR]"):
            raise HTTPException(status_code=500, detail=response_text)
        print(f"Respons LLM: {response_text}")

        print("Mengonversi teks ke suara (TTS)...")
        audio_output_path = transcribe_text_to_speech(response_text)
        if audio_output_path.startswith("[ERROR]"):
            raise HTTPException(status_code=500, detail=audio_output_path)
        print(f"File audio keluaran: {audio_output_path}")

        return FileResponse(audio_output_path, media_type="audio/wav")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error detail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"[ERROR] Gagal memproses: {str(e)}")
