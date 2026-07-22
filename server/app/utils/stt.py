from pathlib import Path

from faster_whisper import WhisperModel

# Load the base model (downloads automatically on first run ~145MB)
# Running on CPU with int8 quantization keeps RAM usage super low (~300MB)
model = WhisperModel("base.en", device="cpu", compute_type="int8")


def speech_to_text(audio_path: str | Path) -> str:
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    segments, info = model.transcribe(str(path), beam_size=5)

    # Combine segments into a single punctuated string
    full_text = " ".join([segment.text.strip() for segment in segments])
    return full_text


if __name__ == "__main__":
    SERVER_DIR = Path(__file__).resolve().parents[2]
    test_wav = SERVER_DIR / "output" / "speech" / "test_text_1.wav"

    if test_wav.exists():
        print("Transcribing with faster-whisper...")
        text = speech_to_text(test_wav)
        print(f"\nResult:\n{text}")
    else:
        print(f"File not found: {test_wav}")
