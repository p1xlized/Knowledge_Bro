import sys
from pathlib import Path

import yt_dlp

# Project root (server/)
SERVER_DIR = Path(__file__).resolve().parents[2]

# Ensure project root is in sys.path so imports work consistently
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from app.utils import generate_filename


def get_audio_from_url(url: str, file_name: str) -> Path:
    """Downloads audio from YouTube, TikTok, Instagram, etc.,
    and saves it as a 16kHz mono WAV file in output/audio/.

    Returns the path relative to SERVER_DIR for portability.
    """
    output_dir = SERVER_DIR / "output" / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensures folder structure exists

    # Base path without extension for yt-dlp outtmpl
    output_path = output_dir / Path(file_name).stem

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_path),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        # Convert to 16kHz mono audio for STT models
        "postprocessor_args": ["-ar", "16000", "-ac", "1"],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    final_wav_path = output_path.with_suffix(".wav")

    # Return relative path (e.g., 'output/audio/filename.wav')
    return final_wav_path.relative_to(SERVER_DIR)


if __name__ == "__main__":
    import wave

    print("--- Running Audio Extractor Pipeline Test ---")

    test_url = "https://www.youtube.com/watch?v=5C_HPTJg5ek"
    filename = generate_filename("test audio download", "audio", "wav")

    # 1. Download & process audio
    rel_path = get_audio_from_url(test_url, filename)
    full_path = SERVER_DIR / rel_path

    # 2. Run Assertions
    assert full_path.exists(), f"Assertion Failed: File missing at {full_path}"
    assert full_path.stat().st_size > 0, "Assertion Failed: Downloaded file is 0 bytes."

    # 3. Verify WAV properties (16kHz, mono)
    with wave.open(str(full_path), "rb") as wav:
        channels = wav.getnchannels()
        rate = wav.getframerate()
        frames = wav.getnframes()
        duration = frames / float(rate)

        assert channels == 1, f"Expected 1 channel (mono), got {channels}"
        assert rate == 16000, f"Expected 16000 Hz sample rate, got {rate}"

    print("✔ Download & conversion successful!")
    print(f"  • Relative Path : {rel_path}")
    print(f"  • Audio Duration: {duration:.2f} seconds")
    print(f"  • Format Specs  : {rate} Hz ({channels} channel / mono)")
