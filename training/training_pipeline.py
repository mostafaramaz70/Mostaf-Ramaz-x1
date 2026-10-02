"""
Ramaz X1 Training Pipeline
Version: 1.0.0

Purpose:
Design the path for User-driven agent training from multiple sources:
1. PDF files
2. Telegram channels
3. Videos

Important:
- This does NOT inject hardcoded trading concepts.
- It only prepares and stores training material taught/approved by User.
- Final acceptance of training into agent memory is controlled by User flow.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class TrainingItem:
    """Normalized training unit before being sent to an agent."""

    def __init__(
        self,
        title: str,
        content: str,
        source_type: str,
        source_ref: str,
        tags: Optional[List[str]] = None,
        media_meta: Optional[Dict[str, Any]] = None,
    ):
        self.id = f"TRAIN-SRC-{uuid.uuid4().hex[:8].upper()}"
        self.title = title
        self.content = content
        self.source_type = source_type  # PDF | TELEGRAM | VIDEO | MANUAL
        self.source_ref = source_ref
        self.tags = tags or []
        self.media_meta = media_meta or {}
        self.created_at = datetime.utcnow().isoformat()
        self.status = "PENDING_USER_APPROVAL"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "source_type": self.source_type,
            "source_ref": self.source_ref,
            "tags": self.tags,
            "media_meta": self.media_meta,
            "created_at": self.created_at,
            "status": self.status,
        }


class PDFTrainingSource:
    """
    PDF training intake.

    Expected flow:
    1. User uploads PDF
    2. System extracts text (future: pypdf / pdfplumber)
    3. User reviews extracted content
    4. Approved content becomes TrainingItem
    """

    source_type = "PDF"

    def ingest(self, file_path: str, title: str = "", tags: Optional[List[str]] = None) -> TrainingItem:
        # Placeholder extraction layer (to be connected to real PDF parser)
        extracted_text = (
            f"[PDF_PLACEHOLDER]\n"
            f"File: {file_path}\n"
            f"Extract full text with PDF parser in next integration step.\n"
            f"User must review and approve before agent training."
        )

        return TrainingItem(
            title=title or f"PDF Training - {file_path.split('/')[-1]}",
            content=extracted_text,
            source_type=self.source_type,
            source_ref=file_path,
            tags=tags or ["pdf", "user-training"],
            media_meta={"file_path": file_path, "parser": "pending"},
        )


class TelegramTrainingSource:
    """
    Telegram channel training intake.

    Expected flow:
    1. User connects channel / provides export / bot feed
    2. System collects messages (text, captions)
    3. User filters relevant educational messages
    4. Approved messages become TrainingItems
    """

    source_type = "TELEGRAM"

    def ingest_channel_message(
        self,
        channel_id: str,
        message_id: str,
        text: str,
        title: str = "",
        tags: Optional[List[str]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> TrainingItem:
        return TrainingItem(
            title=title or f"Telegram {channel_id} #{message_id}",
            content=text,
            source_type=self.source_type,
            source_ref=f"telegram://{channel_id}/{message_id}",
            tags=tags or ["telegram", "channel", "user-training"],
            media_meta={
                "channel_id": channel_id,
                "message_id": message_id,
                **(extra or {}),
            },
        )

    def ingest_export(self, export_path: str, channel_id: str = "unknown") -> List[TrainingItem]:
        """
        Placeholder for Telegram Desktop JSON/HTML export parsing.
        """
        placeholder = TrainingItem(
            title=f"Telegram Export - {channel_id}",
            content=(
                f"[TELEGRAM_EXPORT_PLACEHOLDER]\n"
                f"Export path: {export_path}\n"
                f"Parse messages in next integration step.\n"
                f"Only User-approved educational messages should be trained."
            ),
            source_type=self.source_type,
            source_ref=export_path,
            tags=["telegram", "export", "user-training"],
            media_meta={"export_path": export_path, "channel_id": channel_id},
        )
        return [placeholder]


class VideoTrainingSource:
    """
    Video training intake.

    Expected flow:
    1. User provides video (file/url: YouTube/local)
    2. System gets transcript (future: whisper / subtitle / manual transcript)
    3. User reviews transcript
    4. Approved transcript becomes TrainingItem
    """

    source_type = "VIDEO"

    def ingest(
        self,
        video_ref: str,
        title: str = "",
        transcript: str = "",
        tags: Optional[List[str]] = None,
        duration_sec: Optional[int] = None,
    ) -> TrainingItem:
        content = transcript.strip() if transcript else (
            f"[VIDEO_PLACEHOLDER]\n"
            f"Video: {video_ref}\n"
            f"Transcript pending.\n"
            f"User must provide/approve transcript before agent training."
        )

        return TrainingItem(
            title=title or f"Video Training - {video_ref}",
            content=content,
            source_type=self.source_type,
            source_ref=video_ref,
            tags=tags or ["video", "user-training"],
            media_meta={
                "video_ref": video_ref,
                "duration_sec": duration_sec,
                "transcript_present": bool(transcript.strip()) if transcript else False,
            },
        )


class TrainingPipeline:
    """
    Central training path.

    Steps:
    1. Ingest from PDF / Telegram / Video
    2. Hold as PENDING_USER_APPROVAL
    3. User approves
    4. Push into target agent via agent.receive_training()
    """

    def __init__(self):
        self.pdf = PDFTrainingSource()
        self.telegram = TelegramTrainingSource()
        self.video = VideoTrainingSource()
        self.pending: Dict[str, Dict[str, Any]] = {}

    def add_from_pdf(self, file_path: str, title: str = "", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        item = self.pdf.ingest(file_path=file_path, title=title, tags=tags)
        self.pending[item.id] = item.to_dict()
        return self.pending[item.id]

    def add_from_telegram_message(
        self,
        channel_id: str,
        message_id: str,
        text: str,
        title: str = "",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        item = self.telegram.ingest_channel_message(
            channel_id=channel_id,
            message_id=message_id,
            text=text,
            title=title,
            tags=tags,
        )
        self.pending[item.id] = item.to_dict()
        return self.pending[item.id]

    def add_from_telegram_export(self, export_path: str, channel_id: str = "unknown") -> List[Dict[str, Any]]:
        items = self.telegram.ingest_export(export_path=export_path, channel_id=channel_id)
        result = []
        for item in items:
            self.pending[item.id] = item.to_dict()
            result.append(self.pending[item.id])
        return result

    def add_from_video(
        self,
        video_ref: str,
        title: str = "",
        transcript: str = "",
        tags: Optional[List[str]] = None,
        duration_sec: Optional[int] = None,
    ) -> Dict[str, Any]:
        item = self.video.ingest(
            video_ref=video_ref,
            title=title,
            transcript=transcript,
            tags=tags,
            duration_sec=duration_sec,
        )
        self.pending[item.id] = item.to_dict()
        return self.pending[item.id]

    def list_pending(self) -> List[Dict[str, Any]]:
        return list(self.pending.values())

    def approve(self, training_id: str) -> Dict[str, Any]:
        if training_id not in self.pending:
            return {"status": "NOT_FOUND", "training_id": training_id}
        self.pending[training_id]["status"] = "APPROVED"
        self.pending[training_id]["approved_at"] = datetime.utcnow().isoformat()
        return self.pending[training_id]

    def reject(self, training_id: str, reason: str = "") -> Dict[str, Any]:
        if training_id not in self.pending:
            return {"status": "NOT_FOUND", "training_id": training_id}
        self.pending[training_id]["status"] = "REJECTED"
        self.pending[training_id]["rejected_at"] = datetime.utcnow().isoformat()
        self.pending[training_id]["reject_reason"] = reason
        return self.pending[training_id]

    def push_to_agent(self, training_id: str, agent) -> Dict[str, Any]:
        """
        Push approved training into agent.receive_training().
        Agent must implement receive_training().
        """
        item = self.pending.get(training_id)
        if not item:
            return {"status": "NOT_FOUND", "training_id": training_id}

        if item.get("status") != "APPROVED":
            return {
                "status": "NOT_APPROVED",
                "training_id": training_id,
                "message": "User approval required before training agent",
            }

        payload = {
            "title": item["title"],
            "content": item["content"],
            "source": item["source_type"],
            "tags": item.get("tags", []),
            "source_ref": item.get("source_ref"),
            "media_meta": item.get("media_meta", {}),
        }

        result = agent.receive_training(payload)
        item["status"] = "PUSHED_TO_AGENT"
        item["pushed_at"] = datetime.utcnow().isoformat()
        item["agent_result"] = result

        return {
            "status": "PUSHED",
            "training_id": training_id,
            "agent_result": result,
        }
