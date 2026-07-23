import wave
from pathlib import Path

from piper import PiperVoice

# project root (server/)
SERVER_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = SERVER_DIR / "models" / "tts" / "en_US-hfc_female-medium.onnx"

# Load Voice
voice = PiperVoice.load(str(MODEL_PATH))


def run_tts(text: str, file_name: str):
    output_dir = SERVER_DIR / "output" / "speech"
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensures folder structure exists

    output_wav = output_dir / file_name

    with wave.open(str(output_wav), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)  # Fixed: using the text argument

    print(f"Done! Audio saved to: {output_wav}")


test: str = """First, I wake up. Then, I get dressed. I walk to school. I do not ride a bike. I do not ride the bus. I like to go to school. It rains. I do not like rain. I eat lunch. I eat a sandwich and an apple.

I play outside. I like to play. I read a book. I like to read books. I walk home. I do not like walking home. My mother cooks soup for dinner. The soup is hot. Then, I go to bed. I do not like to go to bed.
"""

run_tts(test, "test_text_1.wav")
