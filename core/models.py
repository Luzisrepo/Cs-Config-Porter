"""Plain data structures shared across the core and UI layers."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class SteamAccount:
    """A Steam account discovered under Steam/userdata."""
    account_id: str
    persona_name: Optional[str]
    cfg_path: Path
    has_cs_config: bool
    file_count: int = 0

    @property
    def label(self) -> str:
        """Human friendly label used in dropdowns and lists."""
        if self.persona_name:
            return f"{self.persona_name}  ({self.account_id})"
        return self.account_id


@dataclass
class ConfigFile:
    """A single file living under an account's CS:GO/CS2 cfg directory."""
    relative_path: str  # posix-style path relative to the cfg root
    absolute_path: Path
    size_bytes: int
    modified: datetime

    @property
    def display_size(self) -> str:
        size = self.size_bytes
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


@dataclass
class BackupRecord:
    """A single backup folder on disk, with metadata read from its manifest."""
    name: str
    path: Path
    account_id: Optional[str]
    persona_name: Optional[str]
    created: Optional[datetime]
    file_count: int
    total_size_bytes: int = 0

    @property
    def display_size(self) -> str:
        size = float(self.total_size_bytes)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @property
    def label(self) -> str:
        who = self.persona_name or self.account_id or "unknown"
        when = self.created.strftime("%Y-%m-%d %H:%M:%S") if self.created else "unknown time"
        return f"{who} — {when}"


@dataclass
class OperationResult:
    """Outcome of a port / backup / restore operation."""
    success: bool
    dry_run: bool
    messages: list = field(default_factory=list)
    error: Optional[str] = None
