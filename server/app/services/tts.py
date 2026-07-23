import sys
import wave
from pathlib import Path

# Project root (server/)
SERVER_DIR = Path(__file__).resolve().parents[2]

# Ensure project root is in sys.path so 'app' imports work consistently
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from piper import PiperVoice

from app.utils import generate_filename

# Model location relative to server directory
MODEL_PATH = SERVER_DIR / "models" / "tts" / "en_US-hfc_female-medium.onnx"

# Load Piper Voice model globally
voice = PiperVoice.load(str(MODEL_PATH))


def generate_tts_audio(text: str) -> Path:
    """Synthesizes text to a WAV audio file.

    Returns the path relative to SERVER_DIR for container/deployment
    portability.
    """
    output_dir = SERVER_DIR / "output" / "speech"
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensures folder structure exists
    filename = generate_filename("audio", "audio", "wav")
    output_wav = output_dir / filename

    with wave.open(str(output_wav), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    # Return relative path (e.g., 'output/speech/file_name.wav')
    return output_wav.relative_to(SERVER_DIR)


if __name__ == "__main__":
    print("--- Running TTS Pipeline Test ---")

    test_text: str = (
        "First, I wake up. Then, I get dressed. I walk to school. "
        "I do not ride a bike. I do not ride the bus. I like to go to school. "
        "It rains. I do not like rain. I eat lunch. I eat a sandwich and an apple."
    )

    filename = generate_filename("test value", "audio", "wav")

    # 1. Generate audio
    rel_path = generate_tts_audio(test_text, filename)
    full_path = SERVER_DIR / rel_path

    # 2. Run Assertions
    assert full_path.exists(), f"Assertion Failed: File missing at {full_path}"
    assert full_path.stat().st_size > 0, "Assertion Failed: Generated file is 0 bytes."

    # 3. Read back WAV metadata for verification
    with wave.open(str(full_path), "rb") as wav:
        frames = wav.getnframes()
        rate = wav.getframerate()
        duration = frames / float(rate)
        channels = wav.getnchannels()

    print("✔ Generation successful!")
    print(f"  • Relative Path : {rel_path}")
    print(f"  • Audio Duration: {duration:.2f} seconds")
    print(f"  • Sample Rate   : {rate} Hz ({channels} channel(s))")
