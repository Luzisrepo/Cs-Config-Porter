"""Dashboard tab."""
from __future__ import annotations

import customtkinter as ctk

from core.operations import list_backups
from . import theme
from .widgets import StatCard


class DashboardTab(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(
            self, text="Overview", font=(theme.FONT_FAMILY, 20, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=20, pady=(18, 2))
        ctk.CTkLabel(
            self, text="A snapshot of what's on this machine right now.",
            font=(theme.FONT_FAMILY, 13), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 12))

        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=20, pady=(0, 14))
        stats_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="stats")

        self.card_accounts = StatCard(stats_row, "Accounts with CS Config")
        self.card_accounts.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.card_backups = StatCard(stats_row, "Backups Saved")
        self.card_backups.grid(row=0, column=1, sticky="nsew", padx=8)

        self.card_steam = StatCard(stats_row, "Steam Userdata Path")
        self.card_steam.grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        actions = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=10)
        actions.pack(fill="x", padx=20, pady=(0, 14))
        ctk.CTkLabel(
            actions, text="Quick actions", font=(theme.FONT_FAMILY, 13, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        btn_row = ctk.CTkFrame(actions, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkButton(
            btn_row, text="⟳  Reload accounts", command=self.app.refresh_accounts,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER, text_color=theme.ACCENT_TEXT,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btn_row, text="Port settings", command=lambda: self.app.tabview.set("Port Settings"),
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            btn_row, text="Backups", command=lambda: self.app.tabview.set("Backups"),
            fg_color=theme.BG_INPUT, hover_color=theme.BORDER, text_color=theme.TEXT_PRIMARY,
        ).pack(side="left", padx=8)

        list_card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=10)
        list_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        ctk.CTkLabel(
            list_card, text="Detected Steam accounts", font=(theme.FONT_FAMILY, 13, "bold"),
            text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(14, 6))

        self.list_frame = ctk.CTkScrollableFrame(list_card, fg_color=theme.BG_INPUT, corner_radius=8)
        self.list_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def on_tab_shown(self) -> None:
        self._refresh_backup_count()

    def on_accounts_changed(self) -> None:
        accounts = self.app.accounts
        with_config = [a for a in accounts if a.has_cs_config]
        self.card_accounts.set_value(str(len(with_config)))
        self.card_steam.set_value(str(self.app.userdata_path))
        self._refresh_backup_count()

        for child in self.list_frame.winfo_children():
            child.destroy()

        if not accounts:
            ctk.CTkLabel(
                self.list_frame, text="No Steam accounts found. Check the Settings tab.",
                text_color=theme.TEXT_MUTED,
            ).pack(anchor="w", padx=8, pady=8)
            return

        for account in accounts:
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=3)

            badge_color = theme.SUCCESS if account.has_cs_config else theme.TEXT_MUTED
            badge_text = f"{account.file_count} file(s)" if account.has_cs_config else "no CS config"

            ctk.CTkLabel(
                row, text=account.label, text_color=theme.TEXT_PRIMARY, anchor="w",
            ).pack(side="left", padx=(4, 0))
            ctk.CTkLabel(
                row, text=badge_text, text_color=badge_color, anchor="e", width=110,
            ).pack(side="right", padx=4)

    def _refresh_backup_count(self) -> None:
        try:
            count = len(list_backups(self.app.backup_dir))
        except OSError:
            count = 0
        self.card_backups.set_value(str(count))
