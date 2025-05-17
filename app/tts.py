import os
import uuid
import tempfile
import subprocess
import logging
import sys
import re
import pkg_resources

# Konfigurasi encoding UTF-8 untuk mendukung karakter khusus
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Impor g2p-id
try:
    from g2p_id import G2P
except ImportError:
    logger.error("Pustaka g2p-id tidak terinstal. Instal dengan: pip install g2p-id")
    raise ImportError("Pustaka g2p-id diperlukan untuk konversi fonem. Instal dengan: pip install g2p-id")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path ke folder utilitas TTS
COQUI_DIR = os.path.join(BASE_DIR, "coqui_utils")

# Jalur path ke file model TTS
COQUI_MODEL_PATH = os.path.join(COQUI_DIR, "checkpoint_1260000-inference.pth")

# Jalur path ke file konfigurasi
COQUI_CONFIG_PATH = os.path.join(COQUI_DIR, "config.json")

# Nama speaker
COQUI_SPEAKER = "wibowo"  # Sesuaikan dengan speaker yang valid di speakers.pth

# Periksa versi Coqui TTS
try:
    tts_version = pkg_resources.get_distribution("TTS").version
    logger.info(f"Versi Coqui TTS: {tts_version}")
except pkg_resources.DistributionNotFound:
    logger.warning("Coqui TTS tidak terdeteksi. Pastikan terinstal dengan: pip install TTS")

# Inisialisasi G2P
try:
    g2p = G2P()
    logger.info("Inisialisasi G2P berhasil")
except Exception as e:
    logger.error(f"Gagal menginisialisasi G2P: {e}")
    raise Exception(f"Gagal menginisialisasi G2P: {e}")

def transcribe_text_to_speech(text: str) -> str:
    """
    Fungsi untuk mengonversi teks menjadi suara menggunakan TTS engine yang ditentukan.
    Args:
        text (str): Teks yang akan diubah menjadi suara.
    Returns:
        str: Path ke file audio hasil konversi.
    """
    logger.info("Memulai proses Text-to-Speech")
    path = _tts_with_coqui(text)
    logger.info(f"Hasil TTS: {path}")
    return path

def _tts_with_coqui(text: str) -> str:
    # Periksa keberadaan file model dan konfigurasi
    if not os.path.exists(COQUI_MODEL_PATH):
        logger.error(f"File model TTS tidak ditemukan: {COQUI_MODEL_PATH}")
        return f"[ERROR] Model TTS tidak ditemukan: {COQUI_MODEL_PATH}"
    if not os.path.exists(COQUI_CONFIG_PATH):
        logger.error(f"File konfigurasi TTS tidak ditemukan: {COQUI_CONFIG_PATH}")
        return f"[ERROR] File konfigurasi TTS tidak ditemukan: {COQUI_CONFIG_PATH}"

    # Konversi teks ke fonem menggunakan g2p-id
    logger.info(f"Teks input: {text}")
    try:
        phoneme_text = g2p(text)  # Konversi teks ke fonem
        logger.info(f"Teks fonem dari g2p-id: {phoneme_text}")

        # Saring fonem untuk kompatibilitas dan kejernihan
        phoneme_text = re.sub(r'[ˈˌ]', '', phoneme_text)  # Hapus aksen stres
        phoneme_text = phoneme_text.replace('ɔ', 'o')  # Ganti ɔ dengan o
        phoneme_text = phoneme_text.replace('ə', 'e')  # Ganti ə dengan e
        phoneme_text = phoneme_text.replace('ɛ', 'e')  # Ganti ɛ dengan e
        phoneme_text = phoneme_text.replace('ɪ', 'i')  # Ganti ɪ dengan i
        phoneme_text = phoneme_text.replace('ʃ', 'sh')  # Ganti ʃ dengan sh
        phoneme_text = phoneme_text.replace('ʧ', 'ch')  # Ganti ʧ dengan ch
        phoneme_text = phoneme_text.replace('ʤ', 'j')   # Ganti ʤ dengan j
        phoneme_text = phoneme_text.replace('ʔ', '')    # Hapus glottal stop
        phoneme_text = phoneme_text.replace('_', ' ')   # Ganti _ dengan spasi
        phoneme_text = re.sub(r'\s+', ' ', phoneme_text).strip()  # Normalisasi spasi
        phoneme_text = phoneme_text.encode('ascii', 'ignore').decode('ascii')  # Hapus non-ASCII
        logger.info(f"Teks fonem setelah penyaringan: {phoneme_text}")

        if not phoneme_text:
            logger.error("Fonem kosong setelah penyaringan")
            return "[ERROR] Fonem kosong setelah penyaringan"

    except Exception as e:
        logger.error(f"Gagal mengonversi teks ke fonem: {e}")
        return f"[ERROR] Gagal mengonversi teks ke fonem: {e}"

    tmp_dir = tempfile.gettempdir()
    output_path = os.path.join(tmp_dir, f"tts_{uuid.uuid4()}.wav")

    # Jalankan Coqui TTS dengan subprocess menggunakan --text
    cmd = [
        "tts",
        "--text", phoneme_text,  # Gunakan teks fonem langsung
        "--model_path", COQUI_MODEL_PATH,
        "--config_path", COQUI_CONFIG_PATH,
        "--speaker_idx", COQUI_SPEAKER,
        "--out_path", output_path
    ]
    
    logger.info(f"Menjalankan perintah TTS: {' '.join(cmd)}")
    try:
        process = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        logger.info(f"TTS stdout: {process.stdout}")
        if process.stderr:
            logger.warning(f"TTS stderr: {process.stderr}")
        logger.info(f"File audio TTS berhasil dibuat: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"TTS subprocess gagal: {e}")
        logger.error(f"Output: {e.stdout}")
        logger.error(f"Error: {e.stderr}")
        return f"[ERROR] TTS subprocess failed: {e}\nOutput: {e.stdout}\nError: {e.stderr}"
    except FileNotFoundError:
        logger.error("Perintah 'tts' tidak ditemukan. Pastikan TTS terinstal.")
        return "[ERROR] Perintah 'tts' tidak ditemukan. Pastikan TTS terinstal."

    return output_path