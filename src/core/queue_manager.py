#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe Queue Manager
Thread-safe concurrent task queue with PySide6 signals.
"""

import time
import uuid
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QObject, Signal

from core.engine import DownloadEngine, DownloadCancelledException
from core.transcriber import WhisperTranscriber
from services.config_service import config_service
from services.history_service import history_service, HistoryItem
from services.logger import get_logger

logger = get_logger("queue_manager")


@dataclass
class QueueTask:
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    url: str = ""
    title: str = "Başlık Yükleniyor..."
    uploader: str = ""
    thumbnail_url: str = ""
    duration_str: str = ""
    quality: str = "1080p"
    audio_only: bool = False
    embed_subs: bool = True
    transcribe_after_download: bool = False
    output_dir: str = ""
    
    # Playlist Grouping
    playlist_id: Optional[str] = None
    playlist_title: Optional[str] = None
    playlist_index: int = 0
    playlist_total: int = 0

    # Live Status
    status: str = "queued"  # "queued", "downloading", "transcribing", "completed", "failed", "cancelled"
    percent: float = 0.0
    speed_bytes_sec: float = 0.0
    eta_seconds: int = 0
    downloaded_bytes: int = 0
    total_bytes: int = 0
    final_filepath: Optional[str] = None
    error_message: Optional[str] = None
    
    # Internal references
    engine: Optional[DownloadEngine] = None
    transcriber: Optional[WhisperTranscriber] = None


class QueueSignals(QObject):
    task_added = Signal(QueueTask)
    task_updated = Signal(QueueTask)
    task_completed = Signal(QueueTask)
    task_failed = Signal(QueueTask)
    task_cancelled = Signal(QueueTask)
    all_tasks_completed = Signal()


class QueueManager:
    """Manages concurrent downloads and transcription tasks with Qt Signals."""

    def __init__(self):
        self.signals = QueueSignals()
        self.tasks: Dict[str, QueueTask] = {}
        self._lock = threading.RLock()
        self._executor: Optional[ThreadPoolExecutor] = None
        self._is_running = False
        self._reinit_executor()

    def _reinit_executor(self):
        max_workers = config_service.settings.max_concurrent_downloads
        if self._executor is not None:
            self._executor.shutdown(wait=False)
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="DownloadWorker")

    def add_task(self, task: QueueTask) -> str:
        """Adds a task to the queue and submits it to the threadpool."""
        with self._lock:
            self.tasks[task.task_id] = task

        # Emit OUTSIDE the lock to prevent re-entrant deadlocks with Qt slots
        self.signals.task_added.emit(task)
        self._executor.submit(self._run_task, task.task_id)
        return task.task_id

    def cancel_task(self, task_id: str):
        """Cancels a queued or actively downloading task."""
        task_to_emit = None
        with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return

            if task.status == "queued":
                task.status = "cancelled"
                task_to_emit = task
            else:
                if task.engine:
                    task.engine.cancel()
                if task.transcriber:
                    task.transcriber.cancel()
                task.status = "cancelled"
                task_to_emit = task

        if task_to_emit:
            self.signals.task_cancelled.emit(task_to_emit)

    def cancel_all(self):
        """Cancels all active and queued tasks."""
        with self._lock:
            task_ids = list(self.tasks.keys())
        for task_id in task_ids:
            self.cancel_task(task_id)

    def get_task(self, task_id: str) -> Optional[QueueTask]:
        with self._lock:
            return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[QueueTask]:
        with self._lock:
            return list(self.tasks.values())

    def _run_task(self, task_id: str):
        task = self.get_task(task_id)
        if not task or task.status == "cancelled":
            return

        settings = config_service.settings
        base_dir = task.output_dir or settings.download_dir

        # Group playlist downloads in a dedicated subfolder named after the playlist
        if task.playlist_title and not task.output_dir:
            import re
            safe_title = re.sub(r'[\\/*?:"<>|]', '', task.playlist_title).strip() or "Oynatma_Listesi"
            output_dir = os.path.join(base_dir, safe_title)
        else:
            output_dir = base_dir

        task.output_dir = output_dir
        engine = DownloadEngine(output_dir)
        task.engine = engine
        task.status = "downloading"
        self.signals.task_updated.emit(task)

        # Throttling progress updates to avoid flooding the Qt GUI event loop
        last_progress_time = 0.0

        def on_engine_progress(info: Dict[str, Any]):
            nonlocal last_progress_time
            if task.status == "cancelled":
                return

            now = time.time()
            is_finished = info.get('status') == 'processing' or info.get('percent', 0.0) >= 100.0

            # Throttle to max ~10 updates per second (every 100ms), unless finished
            if not is_finished and (now - last_progress_time) < 0.1:
                return

            last_progress_time = now
            task.percent = info.get('percent', 0.0)
            task.downloaded_bytes = info.get('downloaded_bytes', 0)
            task.total_bytes = info.get('total_bytes', 0)
            task.speed_bytes_sec = info.get('speed', 0.0)
            task.eta_seconds = info.get('eta', 0)
            self.signals.task_updated.emit(task)

        try:
            # 1. Download Media
            filepath = engine.download(
                url=task.url,
                quality=task.quality,
                audio_only=task.audio_only,
                embed_subs=task.embed_subs,
                sub_langs=settings.subtitle_langs,
                cookie_file=settings.custom_cookie_file or None,
                cookies_from_browser=settings.cookie_browser if settings.cookie_browser != "none" else None,
                progress_callback=on_engine_progress
            )
            task.final_filepath = filepath

            # 2. Transcribe with Whisper if requested
            if task.transcribe_after_download:
                task.status = "transcribing"
                task.percent = 99.0
                self.signals.task_updated.emit(task)
                
                transcriber = WhisperTranscriber(
                    model_size=settings.whisper_model,
                    device=settings.whisper_device
                )
                task.transcriber = transcriber
                transcriber.transcribe(
                    media_path=filepath,
                    output_formats=settings.transcribe_output_formats
                )

            task.status = "completed"
            task.percent = 100.0
            self.signals.task_completed.emit(task)

            # Record in SQLite history
            history_service.add_item(HistoryItem(
                title=task.title,
                url=task.url,
                file_path=filepath,
                file_size_bytes=task.total_bytes,
                format_type="audio" if task.audio_only else "video",
                quality=task.quality,
                status="completed"
            ))

        except DownloadCancelledException:
            task.status = "cancelled"
            self.signals.task_cancelled.emit(task)
        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            logger.error(f"Task {task_id} failed: {e}")
            self.signals.task_failed.emit(task)
            history_service.add_item(HistoryItem(
                title=task.title,
                url=task.url,
                file_path="",
                format_type="audio" if task.audio_only else "video",
                quality=task.quality,
                status="failed",
                error_message=str(e)
            ))
        finally:
            self._check_if_all_done()

    def _check_if_all_done(self):
        with self._lock:
            all_done = all(t.status in ("completed", "failed", "cancelled") for t in self.tasks.values())
        if all_done:
            self.signals.all_tasks_completed.emit()


# Global Singleton Queue Manager
queue_manager = QueueManager()
