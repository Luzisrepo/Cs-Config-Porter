"""Port / backup / restore logic. Pure Python, no UI dependencies.

Every operation:
- accepts an explicit list of relative file paths to act on (never silently
  touches files the caller didn't select),
- supports a dry_run flag that logs intended actions without changing disk,
- reports progress through a `log(str)` callback so the UI can stream
  status updates from a background thread.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Sequence

from .models import BackupRecord, OperationResult
from .steam import list_config_files

LogFn = Callable[[str], None]

MANIFEST_NAME = "_manifest.json"


def _noop_log(_msg: str) -> None:
    pass


def _copy_selected(
    source_root: Path,
    dest_root: Path,
    relative_paths: Sequence[str],
    dry_run: bool,
    log: LogFn,
) -> int:
    """Copy each selected relative path from source_root to dest_root.

    Overwrites existing files at the destination but never deletes files
    that weren't selected. Returns the number of files copied.
    """
    copied = 0
    for rel in relative_paths:
        src = source_root / rel
        dst = dest_root / rel
        if not src.exists():
            log(f"  skip (missing in source): {rel}")
            continue
        if dry_run:
            log(f"  would copy: {rel}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            log(f"  copied: {rel}")
        copied += 1
    return copied


def _write_manifest(backup_path: Path, account_id: Optional[str], persona_name: Optional[str],
                     relative_paths: Sequence[str]) -> None:
    manifest = {
        "account_id": account_id,
        "persona_name": persona_name,
        "created": datetime.now().isoformat(),
        "files": list(relative_paths),
    }
    (backup_path / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _read_manifest(backup_path: Path) -> Optional[dict]:
    manifest_path = backup_path / MANIFEST_NAME
    if not manifest_path.exists():
        return None
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# --- Backup -------------------------------------------------------------

def create_backup(
    account_id: str,
    persona_name: Optional[str],
    cfg_path: Path,
    backup_root: Path,
    selected_relative_paths: Sequence[str],
    dry_run: bool = False,
    log: LogFn = _noop_log,
) -> OperationResult:
    if not selected_relative_paths:
        return OperationResult(success=False, dry_run=dry_run, error="No files were selected to back up.")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_name = f"{account_id}_{timestamp}"
    backup_path = backup_root / backup_name

    messages = [f"Backing up {len(selected_relative_paths)} file(s) for account {account_id}"]
    log(messages[0])

    try:
        if not dry_run:
            backup_path.mkdir(parents=True, exist_ok=False)
        copied = _copy_selected(cfg_path, backup_path, selected_relative_paths, dry_run, log)
        if not dry_run:
            _write_manifest(backup_path, account_id, persona_name, selected_relative_paths)
        summary = f"{'Would create' if dry_run else 'Created'} backup '{backup_name}' with {copied} file(s)."
        messages.append(summary)
        log(summary)
        return OperationResult(success=True, dry_run=dry_run, messages=messages)
    except OSError as exc:
        err = f"Backup failed: {exc}"
        log(err)
        return OperationResult(success=False, dry_run=dry_run, messages=messages, error=err)


def list_backups(backup_root: Path) -> List[BackupRecord]:
    records: List[BackupRecord] = []
    if not backup_root.exists():
        return records

    for entry in sorted(backup_root.iterdir(), key=lambda p: p.name, reverse=True):
        if not entry.is_dir():
            continue

        manifest = _read_manifest(entry)
        files = [p for p in entry.rglob("*") if p.is_file() and p.name != MANIFEST_NAME]
        total_size = sum(p.stat().st_size for p in files if p.exists())

        account_id = None
        persona_name = None
        created = None

        if manifest:
            account_id = manifest.get("account_id")
            persona_name = manifest.get("persona_name")
            created_str = manifest.get("created")
            if created_str:
                try:
                    created = datetime.fromisoformat(created_str)
                except ValueError:
                    created = None

        if account_id is None:
            # Fall back to parsing the "{account_id}_{timestamp}" folder name.
            parts = entry.name.split("_", 1)
            if len(parts) == 2 and parts[0].isdigit():
                account_id = parts[0]
                try:
                    created = created or datetime.strptime(parts[1], "%Y-%m-%d_%H-%M-%S")
                except ValueError:
                    pass

        if created is None:
            try:
                created = datetime.fromtimestamp(entry.stat().st_mtime)
            except OSError:
                created = None

        records.append(
            BackupRecord(
                name=entry.name,
                path=entry,
                account_id=account_id,
                persona_name=persona_name,
                created=created,
                file_count=len(files),
                total_size_bytes=total_size,
            )
        )
    return records


def delete_backup(backup_path: Path) -> None:
    shutil.rmtree(backup_path)


def backup_config_files(backup_path: Path) -> List:
    """List files inside an existing backup, for the restore file-picker."""
    files = list_config_files(backup_path)
    return [f for f in files if f.relative_path != MANIFEST_NAME]


# --- Port -----------------------------------------------------------------

def port_settings(
    source_cfg_path: Path,
    target_cfg_path: Path,
    selected_relative_paths: Sequence[str],
    backup_before: bool = False,
    backup_root: Optional[Path] = None,
    target_account_id: Optional[str] = None,
    target_persona_name: Optional[str] = None,
    dry_run: bool = False,
    log: LogFn = _noop_log,
) -> OperationResult:
    if not selected_relative_paths:
        return OperationResult(success=False, dry_run=dry_run, error="No files were selected to port.")

    messages = []
    try:
        if backup_before and target_cfg_path.exists() and any(target_cfg_path.iterdir()):
            if not backup_root:
                raise ValueError("Backup requested but no backup directory was configured.")
            log("Backing up target account before porting...")
            existing_files = [f.relative_path for f in list_config_files(target_cfg_path)]
            backup_result = create_backup(
                target_account_id or "target", target_persona_name, target_cfg_path,
                backup_root, existing_files, dry_run=dry_run, log=log,
            )
            messages.extend(backup_result.messages)
            if not backup_result.success:
                return OperationResult(success=False, dry_run=dry_run, messages=messages, error=backup_result.error)

        if not dry_run:
            target_cfg_path.mkdir(parents=True, exist_ok=True)

        log(f"Copying {len(selected_relative_paths)} file(s)...")
        copied = _copy_selected(source_cfg_path, target_cfg_path, selected_relative_paths, dry_run, log)
        summary = f"{'Would port' if dry_run else 'Ported'} {copied} file(s) to account {target_account_id}."
        messages.append(summary)
        log(summary)
        if not dry_run:
            log("Note: restart CS:GO/CS2 for changes to take effect.")
        return OperationResult(success=True, dry_run=dry_run, messages=messages)
    except (OSError, ValueError) as exc:
        err = f"Port failed: {exc}"
        log(err)
        return OperationResult(success=False, dry_run=dry_run, messages=messages, error=err)


# --- Restore ----------------------------------------------------------------

def restore_backup(
    backup_path: Path,
    target_cfg_path: Path,
    selected_relative_paths: Sequence[str],
    backup_before: bool = False,
    backup_root: Optional[Path] = None,
    target_account_id: Optional[str] = None,
    target_persona_name: Optional[str] = None,
    dry_run: bool = False,
    log: LogFn = _noop_log,
) -> OperationResult:
    if not selected_relative_paths:
        return OperationResult(success=False, dry_run=dry_run, error="No files were selected to restore.")

    messages = []
    try:
        if backup_before and target_cfg_path.exists() and any(target_cfg_path.iterdir()):
            if not backup_root:
                raise ValueError("Backup requested but no backup directory was configured.")
            log("Backing up current target state before restoring...")
            existing_files = [f.relative_path for f in list_config_files(target_cfg_path)]
            pre_result = create_backup(
                target_account_id or "target", target_persona_name, target_cfg_path,
                backup_root, existing_files, dry_run=dry_run, log=log,
            )
            messages.extend(pre_result.messages)
            if not pre_result.success:
                return OperationResult(success=False, dry_run=dry_run, messages=messages, error=pre_result.error)

        if not dry_run:
            target_cfg_path.mkdir(parents=True, exist_ok=True)

        log(f"Restoring {len(selected_relative_paths)} file(s)...")
        copied = _copy_selected(backup_path, target_cfg_path, selected_relative_paths, dry_run, log)
        summary = f"{'Would restore' if dry_run else 'Restored'} {copied} file(s) to account {target_account_id}."
        messages.append(summary)
        log(summary)
        if not dry_run:
            log("Note: restart CS:GO/CS2 for changes to take effect.")
        return OperationResult(success=True, dry_run=dry_run, messages=messages)
    except (OSError, ValueError) as exc:
        err = f"Restore failed: {exc}"
        log(err)
        return OperationResult(success=False, dry_run=dry_run, messages=messages, error=err)
