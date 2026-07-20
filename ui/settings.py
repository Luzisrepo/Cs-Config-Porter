"""Settings tab: Steam path, backup directory, and a bit of app info."""
from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from core import steam
from . import theme


class SettingsTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self, text="Application Settings", font=(theme.FONT_FAMILY, 20, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(
            self, text="Configure where the app looks for Steam accounts and stores backups.",
            font=(theme.FONT_FAMILY, 13), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=10)
        card.pack(fill="x", padx=20, pady=(0, 14))

        # --- Steam path ---
        ctk.CTkLabel(
            card, text="Steam userdata path", font=(theme.FONT_FAMILY, 13, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(16, 4))
        steam_row = ctk.CTkFrame(card, fg_color="transparent")
        steam_row.pack(fill="x", padx=16)
        self.steam_path_var = ctk.StringVar(value=str(self.app.userdata_path))
        ctk.CTkEntry(
            steam_row, textvariable=self.steam_path_var, fg_color=theme.BG_INPUT, border_color=theme.BORDER,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            steam_row, text="Browse", width=80, command=self._browse_steam_path,
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            steam_row, text="Auto-detect", width=100, command=self._autodetect_steam_path,
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="left")

        # --- Backup dir ---
        ctk.CTkLabel(
            card, text="Default backup directory", font=(theme.FONT_FAMILY, 13, "bold"),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(18, 4))
        backup_row = ctk.CTkFrame(card, fg_color="transparent")
        backup_row.pack(fill="x", padx=16, pady=(0, 16))
        self.backup_dir_var = ctk.StringVar(value=str(self.app.backup_dir))
        ctk.CTkEntry(
            backup_row, textvariable=self.backup_dir_var, fg_color=theme.BG_INPUT, border_color=theme.BORDER,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            backup_row, text="Browse", width=80, command=self._browse_backup_dir,
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="left")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 6))
        ctk.CTkButton(
            btn_row, text="💾  Save Settings", command=self._save,
            fg_color=theme.SUCCESS, hover_color=theme.SUCCESS_HOVER, text_color="#0d1f16",
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btn_row, text="Reset to Defaults", command=self._reset,
            fg_color=theme.DANGER, hover_color=theme.DANGER_HOVER, text_color="#2a0d0d",
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(self, text="", text_color=theme.SUCCESS)
        self.status_label.pack(anchor="w", padx=20, pady=(6, 0))

        info_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=10)
        info_card.pack(fill="both", expand=True, padx=20, pady=(14, 20))
        ctk.CTkLabel(
            info_card, text="About", font=(theme.FONT_FAMILY, 13, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(14, 6))
        info_text = (
            "CS:GO / CS2 Settings Porter lets you copy config files between Steam accounts, "
            "create backups, and restore them later, choosing exactly which files are touched.\n\n"
            "All operations run locally — no network access, no telemetry.\n"
            "Restart CS:GO/CS2 after porting or restoring for changes to take effect."
        )
        ctk.CTkLabel(
            info_card, text=info_text, justify="left", text_color=theme.TEXT_MUTED, wraplength=760,
        ).pack(anchor="w", padx=16, pady=(0, 16))

    # --- actions ---------------------------------------------------------

    def _browse_steam_path(self) -> None:
        path = filedialog.askdirectory(title="Select Steam userdata folder", initialdir=self.steam_path_var.get())
        if path:
            self.steam_path_var.set(path)

    def _autodetect_steam_path(self) -> None:
        detected = steam.autodetect_userdata_path()
        if detected:
            self.steam_path_var.set(str(detected))
            self.app.steam_install_path = steam.autodetect_steam_install()
            self.status_label.configure(text=f"✓ Found Steam userdata at {detected}", text_color=theme.SUCCESS)
        else:
            self.status_label.configure(
                text="Couldn't auto-detect Steam. Please browse to it manually.", text_color=theme.DANGER
            )

    def _browse_backup_dir(self) -> None:
        path = filedialog.askdirectory(title="Select backup directory", initialdir=self.backup_dir_var.get())
        if path:
            self.backup_dir_var.set(path)

    def _save(self) -> None:
        new_steam_path = Path(self.steam_path_var.get().strip())
        new_backup_dir = Path(self.backup_dir_var.get().strip())

        if not new_steam_path.exists():
            messagebox.showerror("Invalid path", f"Steam userdata path not found:\n{new_steam_path}")
            return

        self.app.userdata_path = new_steam_path
        self.app.backup_dir = new_backup_dir
        self.app.steam_install_path = self.app.steam_install_path or steam.autodetect_steam_install()

        self.status_label.configure(text="✓ Settings saved", text_color=theme.SUCCESS)
        self.after(3000, lambda: self.status_label.configure(text=""))

        self.app.refresh_accounts()

    def _reset(self) -> None:
        detected = steam.autodetect_userdata_path() or steam.default_userdata_path()
        self.steam_path_var.set(str(detected))
        self.backup_dir_var.set(str(Path.home() / "CS Settings Backups"))
        self.status_label.configure(text="✓ Reset to defaults (not yet saved)", text_color=theme.SUCCESS)
        self.after(3000, lambda: self.status_label.configure(text=""))
