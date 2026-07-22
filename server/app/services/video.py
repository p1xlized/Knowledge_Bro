from pathlib import Path

import yt_dlp


def get_audio_from_url(url: str, output_path: str | Path) -> Path:
    """Downloads audio from YouTube, TikTok, Instagram, etc.,

    and saves it as a 16kHz mono WAV file.
    """
    output_path = Path(output_path).with_suffix(
        ""
    )  # Strip extension so yt-dlp manages it

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
    print(f"Downloaded audio to: {final_wav_path}")
    return final_wav_path


# Test
if __name__ == "__main__":
    audio_file = get_audio_from_url(
        "https://www.youtube.com/watch?v=5C_HPTJg5ek",
        "output/audio/tiktok_audio.wav",
    )
