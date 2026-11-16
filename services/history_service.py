#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StreamScribe History Service
Stores and queries download and transcription history using SQLite.
"""

import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class HistoryItem:
    id: Optional[int] = None
    title: str = ""
    url: str = ""
    file_path: str = ""
    file_size_bytes: int = 0
    format_type: str = "video"  # "video", "audio", "transcription"
    quality: str = ""
    download_date: float = 0.0
    status: str = "completed"   # "completed", "failed", "cancelled"
    error_message: Optional[str] = None


class HistoryService:
    """Manages persistent download history with SQLite."""
    
    def __init__(self, db_dir: Optional[Path] = None):
        if db_dir is None:
            db_dir = Path.home() / ".streamscribe"
        db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_dir / "history.db"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size_bytes INTEGER DEFAULT 0,
                    format_type TEXT DEFAULT 'video',
                    quality TEXT DEFAULT '',
                    download_date REAL NOT NULL,
                    status TEXT DEFAULT 'completed',
                    error_message TEXT
                )
            """)
            conn.commit()

    def add_item(self, item: HistoryItem) -> int:
        if not item.download_date:
            item.download_date = time.time()
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO history (title, url, file_path, file_size_bytes, format_type, quality, download_date, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.title, item.url, item.file_path, item.file_size_bytes,
                item.format_type, item.quality, item.download_date, item.status,
                item.error_message
            ))
            conn.commit()
            return cursor.lastrowid

    def get_items(self, limit: int = 100, offset: int = 0) -> List[HistoryItem]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM history ORDER BY download_date DESC LIMIT ? OFFSET ?
            """, (limit, offset))
            rows = cursor.fetchall()
            return [HistoryItem(**dict(row)) for row in rows]

    def clear_history(self) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM history")
            conn.commit()
            return True

    def delete_item(self, item_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM history WHERE id = ?", (item_id,))
            conn.commit()
            return True


history_service = HistoryService()
