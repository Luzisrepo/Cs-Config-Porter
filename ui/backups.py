"""Backups tab: a segmented view for creating backups, and managing/restoring them."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import List, Optional

import customtkinter as ctk

from core import steam
from core.models import BackupRecord, OperationResult
from core.operations import (
    backup_config_files,
    create_backup,
    delete_backup,
    list_backups,
    restore_backup,
)
from . import theme
from .async_utils import run_operation
from .widgets import AccountSelector, FileChecklist, LogConsole


class BackupsTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self, text="Backups", font=(theme.FONT_FAMILY, 20, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(
            self, text="Create new backups, or restore and manage the ones you already have.",
            font=(theme.FONT_FAMILY, 13), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 10))

        self.segmented_var = ctk.StringVar(value="Create Backup")
        segmented = ctk.CTkSegmentedButton(
            self, values=["Create Backup", "Manage & Restore"], variable=self.segmented_var,
            command=self._on_segment_changed, selected_color=theme.ACCENT,
            selected_hover_color=theme.ACCENT_HOVER, unselected_color=theme.BG_PANEL,
            fg_color=theme.BG_PANEL,
        )
        segmented.pack(anchor="w", padx=20, pady=(0, 12))

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.create_pane = _CreateBackupPane(container, self.app)
        self.create_pane.grid(row=0, column=0, sticky="nsew")

        self.manage_pane = _ManagePane(container, self.app)
        self.manage_pane.grid(row=0, column=0, sticky="nsew")

        self.create_pane.tkraise()

    def _on_segment_changed(self, value: str) -> None:
        if value == "Create Backup":
            self.create_pane.tkraise()
        else:
            self.manage_pane.tkraise()
            self.manage_pane.refresh()

    def on_accounts_changed(self) -> None:
        self.create_pane.on_accounts_changed()
        self.manage_pane.on_accounts_changed()

    def on_tab_shown(self) -> None:
        if self.segmented_var.get() == "Manage & Restore":
            self.manage_pane.refresh()


class _CreateBackupPane(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_CARD, corner_radius=10)
        self.app = app
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self, text="Account to back up", font=(theme.FONT_FAMILY, 13, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(16, 6))
        self.account_selector = AccountSelector(self, on_change=self._on_account_changed)
        self.account_selector.pack(fill="x", padx=16)

        ctk.CTkLabel(self, text="Files to back up", text_color=theme.TEXT_MUTED).pack(
            anchor="w", padx=16, pady=(14, 4)
        )
        self.file_checklist = FileChecklist(self, height=180)
        self.file_checklist.pack(fill="both", expand=True, padx=16)

        location_row = ctk.CTkFrame(self, fg_color="transparent")
        location_row.pack(fill="x", padx=16, pady=(14, 6))
        ctk.CTkLabel(location_row, text="Backup location", text_color=theme.TEXT_MUTED).pack(anchor="w")
        entry_row = ctk.CTkFrame(location_row, fg_color="transparent")
        entry_row.pack(fill="x", pady=(4, 0))
        self.location_var = ctk.StringVar(value=str(self.app.backup_dir))
        ctk.CTkEntry(
            entry_row, textvariable=self.location_var, fg_color=theme.BG_INPUT, border_color=theme.BORDER,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            entry_row, text="Browse", width=90, command=self._browse_location,
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="right")

        self.dry_run_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            self, text="Dry run (preview only, no changes)", variable=self.dry_run_var,
            progress_color=theme.ACCENT, button_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(6, 6))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(6, 6))
        self.create_button = ctk.CTkButton(
            btn_row, text="💾  Create Backup", command=self._on_create_clicked,
            fg_color=theme.SUCCESS, hover_color=theme.SUCCESS_HOVER, text_color="#0d1f16",
        )
        self.create_button.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btn_row, text="Clear log", command=lambda: self.log_console.clear(),
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="left")

        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", progress_color=theme.ACCENT)
        self.progress.pack(fill="x", padx=16, pady=(4, 10))

        ctk.CTkLabel(self, text="Operation log", text_color=theme.TEXT_MUTED).pack(anchor="w", padx=16)
        self.log_console = LogConsole(self, height=130)
        self.log_console.pack(fill="both", expand=True, padx=16, pady=(4, 16))

    def on_accounts_changed(self) -> None:
        self.account_selector.set_accounts(self.app.accounts, only_with_config=True)
        self._on_account_changed()

    def _on_account_changed(self) -> None:
        account = self.account_selector.get_selected_account()
        if account and account.cfg_path.exists():
            self.file_checklist.set_files(steam.list_config_files(account.cfg_path))
        else:
            self.file_checklist.set_files([])

    def _browse_location(self) -> None:
        path = filedialog.askdirectory(title="Select backup directory", initialdir=self.location_var.get())
        if path:
            self.location_var.set(path)

    def _on_create_clicked(self) -> None:
        account = self.account_selector.get_selected_account()
        account_id = self.account_selector.get_account_id()
        selected_files = self.file_checklist.get_selected()
        backup_dir_str = self.location_var.get().strip()

        if not account_id:
            messagebox.showwarning("Missing information", "Please choose an account to back up.")
            return
        if not account or not account.cfg_path.exists():
            messagebox.showerror("Account not found", f"No CS config found for account {account_id}.")
            return
        if not selected_files:
            messagebox.showwarning("Nothing selected", "Select at least one file to back up.")
            return
        if not backup_dir_str:
            messagebox.showwarning("Missing information", "Please choose a backup location.")
            return

        backup_dir = Path(backup_dir_str)
        dry_run = self.dry_run_var.get()
        persona_name = account.persona_name

        self.app.backup_dir = backup_dir
        self.log_console.clear()
        self.log_console.log(f"Starting backup of account {account_id}" + (" (dry run)" if dry_run else ""))
        self.create_button.configure(state="disabled")

        def worker(log) -> OperationResult:
            if not dry_run:
                backup_dir.mkdir(parents=True, exist_ok=True)
            return create_backup(
                account_id, persona_name, account.cfg_path, backup_dir, selected_files,
                dry_run=dry_run, log=lambda m: log(m, "info"),
            )

        def on_done(result: OperationResult) -> None:
            self.progress.stop()
            self.create_button.configure(state="normal")
            if result is None:
                return
            if result.success:
                self.log_console.log("✓ Done.", "success")
                if not dry_run:
                    messagebox.showinfo("Success", "Backup created successfully.")
            else:
                self.log_console.log(f"✗ {result.error}", "error")
                messagebox.showerror("Backup failed", result.error or "Unknown error")

        self.progress.start()
        run_operation(self, worker, self.log_console, on_done=on_done)


class _ManagePane(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.BG_CARD, corner_radius=10)
        self.app = app
        self._backups: List[BackupRecord] = []
        self._build()

    def _build(self) -> None:
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(16, 6))
        self.location_label = ctk.CTkLabel(
            top_row, text=f"Location: {self.app.backup_dir}", text_color=theme.TEXT_MUTED, anchor="w",
        )
        self.location_label.pack(side="left")
        ctk.CTkButton(
            top_row, text="⟳ Refresh", width=90, command=self.refresh,
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=theme.BG_INPUT, corner_radius=8)
        self.list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def on_accounts_changed(self) -> None:
        pass  # backups list doesn't depend on live account discovery

    def refresh(self) -> None:
        self.location_label.configure(text=f"Location: {self.app.backup_dir}")
        try:
            self._backups = list_backups(self.app.backup_dir)
        except OSError:
            self._backups = []

        for child in self.list_frame.winfo_children():
            child.destroy()

        if not self._backups:
            ctk.CTkLabel(
                self.list_frame, text="No backups found yet.", text_color=theme.TEXT_MUTED,
            ).pack(anchor="w", padx=8, pady=8)
            return

        for record in self._backups:
            self._build_row(record)

    def _build_row(self, record: BackupRecord) -> None:
        row = ctk.CTkFrame(self.list_frame, fg_color=theme.BG_CARD, corner_radius=8)
        row.pack(fill="x", padx=4, pady=4)

        text_box = ctk.CTkFrame(row, fg_color="transparent")
        text_box.pack(side="left", fill="x", expand=True, padx=12, pady=8)
        ctk.CTkLabel(
            text_box, text=record.label, font=(theme.FONT_FAMILY, 13, "bold"),
            text_color=theme.TEXT_PRIMARY, anchor="w",
        ).pack(anchor="w")
        subtitle = f"Account {record.account_id or 'unknown'} · {record.file_count} file(s) · {record.display_size}"
        ctk.CTkLabel(text_box, text=subtitle, text_color=theme.TEXT_MUTED, anchor="w").pack(anchor="w")

        btn_box = ctk.CTkFrame(row, fg_color="transparent")
        btn_box.pack(side="right", padx=12, pady=8)
        ctk.CTkButton(
            btn_box, text="Restore", width=80, command=lambda r=record: self._open_restore_dialog(r),
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER, text_color=theme.ACCENT_TEXT,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn_box, text="Open", width=60, command=lambda r=record: self._open_folder(r),
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn_box, text="Delete", width=70, command=lambda r=record: self._delete(r),
            fg_color=theme.DANGER, hover_color=theme.DANGER_HOVER, text_color="#2a0d0d",
        ).pack(side="left", padx=4)

    def _open_folder(self, record: BackupRecord) -> None:
        try:
            if sys.platform == "win32":
                os.startfile(record.path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(record.path)], check=False)
            else:
                subprocess.run(["xdg-open", str(record.path)], check=False)
        except OSError as exc:
            messagebox.showerror("Couldn't open folder", str(exc))

    def _delete(self, record: BackupRecord) -> None:
        if not messagebox.askyesno("Delete backup", f"Permanently delete backup '{record.name}'?"):
            return
        try:
            delete_backup(record.path)
        except OSError as exc:
            messagebox.showerror("Delete failed", str(exc))
            return
        self.refresh()

    def _open_restore_dialog(self, record: BackupRecord) -> None:
        RestoreDialog(self, self.app, record, on_restored=self.refresh)


class RestoreDialog(ctk.CTkToplevel):
    def __init__(self, master, app, record: BackupRecord, on_restored):
        super().__init__(master)
        self.app = app
        self.record = record
        self.on_restored = on_restored

        self.title(f"Restore backup — {record.name}")
        self.geometry("560x620")
        self.configure(fg_color=theme.BG_ROOT)
        self.transient(master.winfo_toplevel())
        self.grab_set()

        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self, text=f"Restore: {self.record.label}", font=(theme.FONT_FAMILY, 15, "bold"),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=18, pady=(16, 4))

        ctk.CTkLabel(self, text="Restore to account", text_color=theme.TEXT_MUTED).pack(
            anchor="w", padx=18, pady=(8, 4)
        )
        self.target_selector = AccountSelector(self)
        self.target_selector.pack(fill="x", padx=18)
        self.target_selector.set_accounts(self.app.accounts, only_with_config=False)
        default_account = next(
            (a for a in self.app.accounts if a.account_id == self.record.account_id), None
        )
        if default_account:
            self.target_selector.combobox.set(default_account.label)
            self.target_selector.id_var.set(default_account.account_id)
        elif self.record.account_id:
            self.target_selector.id_var.set(self.record.account_id)

        ctk.CTkLabel(self, text="Files to restore", text_color=theme.TEXT_MUTED).pack(
            anchor="w", padx=18, pady=(14, 4)
        )
        self.file_checklist = FileChecklist(self, height=170)
        self.file_checklist.pack(fill="both", expand=True, padx=18)
        self.file_checklist.set_files(backup_config_files(self.record.path))

        self.backup_before_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            self, text="Back up target's current state before restoring", variable=self.backup_before_var,
            progress_color=theme.ACCENT, button_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=18, pady=(12, 4))

        self.dry_run_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            self, text="Dry run (preview only, no changes)", variable=self.dry_run_var,
            progress_color=theme.ACCENT, button_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=18, pady=(2, 8))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(4, 6))
        self.restore_button = ctk.CTkButton(
            btn_row, text="↩  Restore", command=self._on_restore_clicked,
            fg_color=theme.SUCCESS, hover_color=theme.SUCCESS_HOVER, text_color="#0d1f16",
        )
        self.restore_button.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btn_row, text="Cancel", command=self.destroy,
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="left")

        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", progress_color=theme.ACCENT)
        self.progress.pack(fill="x", padx=18, pady=(4, 8))

        self.log_console = LogConsole(self, height=100)
        self.log_console.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    def _on_restore_clicked(self) -> None:
        target_id = self.target_selector.get_account_id()
        selected_files = self.file_checklist.get_selected()

        if not target_id:
            messagebox.showwarning("Missing information", "Please choose a target account.", parent=self)
            return
        if not selected_files:
            messagebox.showwarning("Nothing selected", "Select at least one file to restore.", parent=self)
            return

        target_account = self.target_selector.get_selected_account()
        target_persona = target_account.persona_name if target_account else None
        target_path = self.app.userdata_path / target_id / steam.CS_CFG_SUBPATH
        dry_run = self.dry_run_var.get()
        backup_before = self.backup_before_var.get()
        backup_root = self.app.backup_dir
        backup_source_path = self.record.path

        self.log_console.clear()
        self.log_console.log("Starting restore" + (" (dry run)" if dry_run else ""))
        self.restore_button.configure(state="disabled")

        def worker(log) -> OperationResult:
            return restore_backup(
                backup_source_path, target_path, selected_files,
                backup_before=backup_before, backup_root=backup_root,
                target_account_id=target_id, target_persona_name=target_persona,
                dry_run=dry_run, log=lambda m: log(m, "info"),
            )

        def on_done(result: Optional[OperationResult]) -> None:
            self.progress.stop()
            self.restore_button.configure(state="normal")
            if result is None:
                return
            if result.success:
                self.log_console.log("✓ Done.", "success")
                if not dry_run:
                    messagebox.showinfo("Success", "Backup restored successfully.", parent=self)
                    self.app.refresh_accounts()
                    self.on_restored()
            else:
                self.log_console.log(f"✗ {result.error}", "error")
                messagebox.showerror("Restore failed", result.error or "Unknown error", parent=self)

        self.progress.start()
        run_operation(self, worker, self.log_console, on_done=on_done)
