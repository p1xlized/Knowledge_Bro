import logging
import time
from pathlib import Path

from sqlmodel import Session

from app.db import Content, ContentStatus, ContentType, engine
from app.services.ai import generate_summary
from app.services.stt import generate_stt_text
from app.services.tts import generate_tts_audio
from app.services.video import get_audio_from_url
from app.utils import generate_filename, parse_link

logger = logging.getLogger("uvicorn.error")


def process_content_background(content_id: int):
    """Main background entry point executed by FastAPI BackgroundTasks.

    Uses its own DB session context to safely mutate state off the main thread.
    """
    start_time = time.time()
    logger.info(f"🚀 [Task Started] Processing content_id={content_id}")

    with Session(engine) as session:
        content = session.get(Content, content_id)
        if not content:
            logger.error(
                f"❌ [Task Aborted] Content ID {content_id} not found in database."
            )
            return

        # 1. Mark as PROCESSING
        content.status = ContentStatus.PROCESSING
        session.add(content)
        session.commit()
        logger.info(f"🔄 [Status Update] content_id={content_id} set to PROCESSING")

        try:
            if content.type == ContentType.ARTICLE:
                logger.info(
                    f"📰 [Article Pipeline] Extracting text from: {content.link}"
                )
                full_text = parse_link(content.link)
                logger.info(
                    f"  └─ Fetched {len(full_text)} chars. Generating summary..."
                )

                summary = generate_summary(full_text)
                content.ai_summary = summary
                content.transcript_text = full_text
                logger.info("  └─ AI summary generated successfully.")

                # Generate TTS audio
                audio_filename = generate_filename(
                    content.title or "article", "audio", "wav"
                )
                logger.info(f"  └─ Generating TTS audio file: {audio_filename}")

                # Pass both required arguments: text and filename
                audio_rel_path = generate_tts_audio(full_text)
                content.tts_audio_url = str(audio_rel_path)
                logger.info(f"  └─ TTS saved to: {audio_rel_path}")

            elif content.type == ContentType.VIDEO:
                logger.info(
                    f"🎬 [Video Pipeline] Downloading audio from: {content.link}"
                )
                audio_filename = generate_filename(
                    content.title or "video", "audio", "wav"
                )
                audio_rel_path = get_audio_from_url(content.link, audio_filename)
                content.video_audio_url = str(audio_rel_path)
                logger.info(f"  └─ Video audio extracted to: {audio_rel_path}")

                logger.info("  └─ Running STT and generating summary...")
                summary, transcript = generate_stt_text(content.link)
                content.ai_summary = summary
                content.transcript_text = transcript
                logger.info("  └─ STT and summary completed.")

            # 2. Mark as COMPLETED
            content.status = ContentStatus.COMPLETED
            content.error_message = None
            session.add(content)
            session.commit()

            elapsed = time.time() - start_time
            logger.info(
                f"✅ [Task Completed] content_id={content_id} processed in {elapsed:.2f}s"
            )

        except Exception as e:
            # 3. Mark as FAILED on error
            session.rollback()  # Clear uncommitted invalid state

            # Re-query content to update failure status safely
            content = session.get(Content, content_id)
            if content:
                content.status = ContentStatus.FAILED
                content.error_message = str(e)
                session.add(content)
                session.commit()

            elapsed = time.time() - start_time
            logger.exception(
                f"❌ [Task Failed] content_id={content_id} failed after {elapsed:.2f}s. Error: {e}"
            )
