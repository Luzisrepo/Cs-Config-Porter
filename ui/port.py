"""Port Settings tab: copy chosen config files from one Steam account to another."""
from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from core import steam
from core.operations import OperationResult, port_settings
from . import theme
from .async_utils import run_operation
from .widgets import AccountSelector, FileChecklist, LogConsole


class PortTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self, text="Port Settings Between Accounts", font=(theme.FONT_FAMILY, 20, "bold"),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(
            self, text="Copy CS:GO/CS2 config files from one Steam account to another.",
            font=(theme.FONT_FAMILY, 13), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        columns = ctk.CTkFrame(self, fg_color="transparent")
        columns.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        columns.grid_columnconfigure(0, weight=1, uniform="cols")
        columns.grid_columnconfigure(1, weight=1, uniform="cols")
        columns.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(columns, fg_color=theme.BG_CARD, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = ctk.CTkFrame(columns, fg_color=theme.BG_CARD, corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # --- Source ---
        ctk.CTkLabel(
            left, text="Source account", font=(theme.FONT_FAMILY, 13, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(14, 6))
        self.source_selector = AccountSelector(left, on_change=self._on_source_changed)
        self.source_selector.pack(fill="x", padx=16)

        ctk.CTkLabel(
            left, text="Files to copy", text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(14, 4))
        self.file_checklist = FileChecklist(left, height=200)
        self.file_checklist.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # --- Target & options ---
        ctk.CTkLabel(
            right, text="Target account", font=(theme.FONT_FAMILY, 13, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(14, 6))
        self.target_selector = AccountSelector(right)
        self.target_selector.pack(fill="x", padx=16)

        options = ctk.CTkFrame(right, fg_color="transparent")
        options.pack(fill="x", padx=16, pady=(18, 6))

        self.backup_before_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(
            options, text="Back up target account before porting", variable=self.backup_before_var,
            progress_color=theme.ACCENT, button_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", pady=4)

        self.dry_run_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(
            options, text="Dry run (preview only, no changes)", variable=self.dry_run_var,
            progress_color=theme.ACCENT, button_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", pady=4)

        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(10, 6))
        self.port_button = ctk.CTkButton(
            btn_row, text="🚀  Port Settings", command=self._on_port_clicked,
            fg_color=theme.SUCCESS, hover_color=theme.SUCCESS_HOVER, text_color="#0d1f16",
        )
        self.port_button.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btn_row, text="Clear log", command=self._clear_log,
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="left")

        self.progress = ctk.CTkProgressBar(right, mode="indeterminate", progress_color=theme.ACCENT)
        self.progress.pack(fill="x", padx=16, pady=(6, 10))

        ctk.CTkLabel(right, text="Operation log", text_color=theme.TEXT_MUTED).pack(
            anchor="w", padx=16
        )
        self.log_console = LogConsole(right, height=150)
        self.log_console.pack(fill="both", expand=True, padx=16, pady=(4, 16))

    # --- data wiring -----------------------------------------------------

    def on_accounts_changed(self) -> None:
        self.source_selector.set_accounts(self.app.accounts, only_with_config=True)
        self.target_selector.set_accounts(self.app.accounts, only_with_config=False)
        self._on_source_changed()

    def _on_source_changed(self) -> None:
        account = self.source_selector.get_selected_account()
        if account and account.cfg_path.exists():
            self.file_checklist.set_files(steam.list_config_files(account.cfg_path))
        else:
            self.file_checklist.set_files([])

    def _clear_log(self) -> None:
        self.log_console.clear()

    # --- action ------------------------------------------------------------

    def _on_port_clicked(self) -> None:
        source_account = self.source_selector.get_selected_account()
        source_id = self.source_selector.get_account_id()
        target_id = self.target_selector.get_account_id()
        selected_files = self.file_checklist.get_selected()

        if not source_id or not target_id:
            messagebox.showwarning("Missing information", "Please choose both a source and a target account.")
            return
        if source_id == target_id:
            messagebox.showwarning("Same account", "Source and target accounts can't be the same.")
            return
        if not source_account or not source_account.cfg_path.exists():
            messagebox.showerror("Source not found", f"No CS config found for account {source_id}.")
            return
        if not selected_files:
            messagebox.showwarning("Nothing selected", "Select at least one file to port.")
            return

        target_account = self.target_selector.get_selected_account()
        target_persona = target_account.persona_name if target_account else None
        source_path = source_account.cfg_path
        target_path = self.app.userdata_path / target_id / steam.CS_CFG_SUBPATH
        dry_run = self.dry_run_var.get()
        backup_before = self.backup_before_var.get()
        backup_dir = self.app.backup_dir

        self.log_console.clear()
        self.log_console.log(f"Starting port: {source_id} → {target_id}" + (" (dry run)" if dry_run else ""))
        self.port_button.configure(state="disabled")

        def worker(log) -> OperationResult:
            return port_settings(
                source_path, target_path, selected_files,
                backup_before=backup_before, backup_root=backup_dir,
                target_account_id=target_id, target_persona_name=target_persona,
                dry_run=dry_run, log=lambda m: log(m, "info"),
            )

        def on_done(result: OperationResult) -> None:
            self.progress.stop()
            self.port_button.configure(state="normal")
            if result is None:
                return
            if result.success:
                self.log_console.log("✓ Done.", "success")
                if not dry_run:
                    messagebox.showinfo("Success", f"Settings ported from {source_id} to {target_id}.")
                self.app.refresh_accounts()
            else:
                self.log_console.log(f"✗ {result.error}", "error")
                messagebox.showerror("Port failed", result.error or "Unknown error")

        self.progress.start()
        run_operation(self, worker, self.log_console, on_done=on_done)
