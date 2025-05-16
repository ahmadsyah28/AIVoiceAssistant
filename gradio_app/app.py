import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile

def voice_chat(audio):
    if audio is None:
        print("Tidak ada audio yang direkam!")
        return None
    
    sr, audio_data = audio
    print(f"Sample rate: {sr}, Bentuk audio: {audio_data.shape}")

    # simpan sebagai .wav
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        scipy.io.wavfile.write(tmpfile.name, sr, audio_data)
        audio_path = tmpfile.name

    try:
    # kirim ke endpoint FastAPI
        with open(audio_path, "rb") as f:
            files = {"audio": ("voice.wav", f, "audio/wav")}
            response = requests.post("http://localhost:8000/voice-chat", files=files)

        #hapus file temporer
        os.unlink(audio_path)

        if response.status_code == 200:
            # simpan file respons audio dari chatbot
            output_audio_path = os.path.join(tempfile.gettempdir(), "tts_output.wav")
            with open(output_audio_path, "wb") as f:
                f.write(response.content)
            return output_audio_path
        else:
            print(f"Error backend: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error mengirim audio: {e}")
        return None

# UI Gradio
with gr.Blocks() as demo:
    gr.Markdown("# 🎙️ Voice Chatbot")
    gr.Markdown("Berbicara langsung ke mikrofon dan dapatkan jawaban suara dari asisten AI.")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources="microphone", type="numpy", label="🎤 Rekam Pertanyaan Anda")
            submit_btn = gr.Button("🔁 Submit")
        with gr.Column():
            audio_output = gr.Audio(type="filepath", label="🔊 Balasan dari Asisten")

    submit_btn.click(
        fn=voice_chat,
        inputs=audio_input,
        outputs=audio_output
    )

demo.launch()
