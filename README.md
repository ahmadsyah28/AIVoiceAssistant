# Voice Chatbot

Voice Chatbot adalah aplikasi berbasis suara yang memungkinkan pengguna berinteraksi dengan asisten AI melalui input suara. Aplikasi ini memproses audio masukan menggunakan Speech-to-Text (STT), menghasilkan respons teks dengan Large Language Model (LLM), dan mengonversi respons tersebut kembali ke suara menggunakan Text-to-Speech (TTS). Proyek ini dibangun untuk praktikum Pemrosesan Bahasa Alami.

## Fitur
- **Input Suara**: Rekam suara melalui antarmuka Gradio.
- **Pipeline Pemrosesan**: STT (Whisper), LLM (Gemini), dan TTS (Coqui TTS).
- **Backend**: FastAPI untuk menangani permintaan HTTP.
- **Frontend**: Gradio untuk antarmuka pengguna berbasis web.

## Teknologi yang Digunakan
- **Python**: Bahasa pemrograman utama.
- **FastAPI**: Framework untuk backend API.
- **Gradio**: Antarmuka pengguna untuk perekaman dan pemutaran audio.
- **Whisper.cpp**: Speech-to-Text untuk transkripsi audio.
- **Google Gemini**: Large Language Model untuk menghasilkan respons teks.
- **Coqui TTS**: Text-to-Speech untuk menghasilkan audio dari teks.

## Prasyarat
Sebelum menjalankan proyek, pastikan Anda memiliki:
- Python 3.8 atau lebih tinggi.
- CMake dan compiler (misalnya, Visual Studio Build Tools) untuk mengompilasi Whisper.cpp.
- API key untuk Google Gemini.
- File model dan konfigurasi untuk Whisper.cpp dan Coqui TTS (tidak disertakan di repositori).

## Struktur Folder
```
voice-chatbot/
├── app/
│   ├── stt.py              # Logika Speech-to-Text (Whisper)
│   ├── llm.py              # Logika Large Language Model (Gemini)
│   ├── tts.py              # Logika Text-to-Speech (Coqui TTS)
│   ├── main.py             # Backend FastAPI
├── gradio_app/
│   ├── app.py              # Frontend Gradio
├── requirements.txt        # Dependensi Python
├── README.md               # Dokumentasi proyek
├── .gitignore              # File yang diabaikan Git
```

## Instalasi
1. **Kloning Repositori**:
   ```bash
   git clone https://github.com/username/voice-chatbot.git
   cd voice-chatbot
   ```

2. **Buat dan Aktifkan Virtual Environment**:
   ```bash
   python -m venv env
   .\env\Scripts\activate  # Windows
   source env/bin/activate  # Linux/macOS
   ```

3. **Instal Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Siapkan Whisper.cpp**:
   - Unduh dan kompilasi Whisper.cpp ke `app/whisper.cpp/`.
   - Tempatkan model `ggml-large-v3-turbo.bin` di `app/whisper.cpp/models/`.
   - Pastikan `whisper-cli.exe` ada di `app/whisper.cpp/build/bin/Release/` (Windows).

5. **Siapkan Coqui TTS**:
   - Unduh file model `checkpoint_1260000-inference.pth`, `config.json`, dan `speakers.pth`.
   - Tempatkan di `app/coqui_utils/`.

6. **Konfigurasi API Key**:
   - Buat file `.env` di root proyek.
   - Tambahkan:
     ```
     GEMINI_API_KEY=your_api_key
     ```

## Menjalankan Aplikasi
1. **Jalankan Backend (FastAPI)**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Jalankan Frontend (Gradio)**:
   ```bash
   cd gradio_app
   python app.py
   ```

3. **Akses Aplikasi**:
   - Buka `http://127.0.0.1:7860` di browser.
   - Rekam audio menggunakan mikrofon, lalu klik "Submit" untuk mendapatkan respons suara.

## Pengujian
- **Uji dengan File Audio**:
  ```bash
  curl -X POST -F "audio=@path/to/audio.wav" http://localhost:8000/voice-chat -o output.wav
  ```
- **Uji Whisper Secara Manual**:
  ```bash
  cd app/whisper.cpp
  .\build\bin\Release\whisper-cli.exe -m models\ggml-large-v3-turbo.bin -f samples\jfk.wav -otxt -of transcription
  ```

## Catatan
- File `app/whisper.cpp/` dan `app/coqui_utils/` tidak disertakan di repositori karena ukuran besar dan ketentuan pengumpulan.
- Pastikan semua file model dan binary tersedia di lokasi yang sesuai sebelum menjalankan aplikasi.
- Jika terjadi error, periksa log di terminal backend (`uvicorn`) dan frontend (`app.py`).

## Kontribusi
1. Fork repositori.
2. Buat branch baru (`git checkout -b feature/nama-fitur`).
3. Commit perubahan (`git commit -m 'Menambahkan fitur X'`).
4. Push ke branch (`git push origin feature/nama-fitur`).
5. Buat Pull Request.

## Lisensi
Proyek ini dilisensikan di bawah [MIT License](LICENSE).