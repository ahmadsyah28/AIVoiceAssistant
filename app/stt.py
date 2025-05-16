import os
import uuid
import tempfile
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path ke folder utilitas STT
WHISPER_DIR = os.path.join(BASE_DIR, "whisper.cpp")

# Path ke binary whisper-cli untuk Windows
WHISPER_BINARY = os.path.join(WHISPER_DIR, "build", "bin", "Release", "whisper-cli.exe")

# Path ke file model Whisper
WHISPER_MODEL_PATH = os.path.join(WHISPER_DIR, "models", "ggml-large-v3-turbo.bin")

def transcribe_speech_to_text(file_bytes: bytes, file_ext: str = ".wav") -> str:
    """
    Transkrip file audio menggunakan whisper.cpp CLI
    Args:
        file_bytes (bytes): Isi file audio
        file_ext (str): Ekstensi file, default ".wav"
    Returns:
        str: Teks hasil transkripsi
    """
    # Verifikasi keberadaan binary dan model
    if not os.path.exists(WHISPER_BINARY):
        return f"[ERROR] Whisper binary not found at: {WHISPER_BINARY}"
    if not os.path.exists(WHISPER_MODEL_PATH):
        return f"[ERROR] Whisper model not found at: {WHISPER_MODEL_PATH}"

    print(f"Using Whisper binary: {WHISPER_BINARY}")
    print(f"Using Whisper model: {WHISPER_MODEL_PATH}")

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, f"{uuid.uuid4()}{file_ext}")
        result_path = os.path.join(tmpdir, "transcription.txt")

        # Simpan audio ke file temporer
        with open(audio_path, "wb") as f:
            f.write(file_bytes)
        print(f"Audio saved to: {audio_path}")

        # Jalankan whisper.cpp dengan subprocess
        cmd = [
            WHISPER_BINARY,
            "-m", WHISPER_MODEL_PATH,
            "-f", audio_path,
            "-otxt",
            "-of", os.path.join(tmpdir, "transcription")
        ]
        print(f"Running command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"Whisper stdout: {result.stdout}")
            print(f"Whisper stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            return f"[ERROR] Whisper failed: {e.stderr}"
        except FileNotFoundError as e:
            return f"[ERROR] Whisper binary execution failed: {str(e)}"
        
        # Baca hasil transkripsi
        try:
            with open(result_path, "r", encoding="utf-8") as result_file:
                transcript = result_file.read()
                print(f"Transcription: {transcript}")
                return transcript
        except FileNotFoundError:
            return "[ERROR] Transcription file not found"
