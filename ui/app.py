"""The main application window."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import customtkinter as ctk

from core import steam
from core.models import SteamAccount
from . import theme
from .backups import BackupsTab
from .dashboard import DashboardTab
from .port import PortTab
from .settings import SettingsTab

ctk.set_appearance_mode("dark")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CS:GO / CS2 Settings Porter")
        self.geometry("1100x780")
        self.minsize(940, 640)
        self.configure(fg_color=theme.BG_ROOT)

        # --- shared state, editable from the Settings tab ---
        self.steam_install_path: Path | None = steam.autodetect_steam_install()
        self.userdata_path: Path = steam.autodetect_userdata_path() or steam.default_userdata_path()
        self.backup_dir: Path = Path.home() / "CS Settings Backups"
        self.persona_names: Dict[str, str] = {}
        self.accounts: List[SteamAccount] = []

        self._build_layout()
        self.refresh_accounts()

    # --- layout -------------------------------------------------------

    def _build_layout(self) -> None:
        header = ctk.CTkFrame(self, fg_color=theme.BG_PANEL, corner_radius=0, height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=8)
        ctk.CTkLabel(
            title_box, text="CS:GO / CS2 Settings Porter",
            font=(theme.FONT_FAMILY, 18, "bold"), text_color=theme.TEXT_PRIMARY,
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_box, text="Move, back up, and restore your game configs",
            font=(theme.FONT_FAMILY, 12), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w")

        self.tabview = ctk.CTkTabview(
            self, fg_color=theme.BG_ROOT, segmented_button_fg_color=theme.BG_PANEL,
            segmented_button_selected_color=theme.ACCENT,
            segmented_button_selected_hover_color=theme.ACCENT_HOVER,
            segmented_button_unselected_color=theme.BG_PANEL,
            text_color=theme.TEXT_PRIMARY, text_color_disabled=theme.TEXT_MUTED,
        )
        self.tabview.pack(fill="both", expand=True, padx=14, pady=(10, 0))

        tab_dashboard = self.tabview.add("Dashboard")
        tab_port = self.tabview.add("Port Settings")
        tab_backups = self.tabview.add("Backups")
        tab_settings = self.tabview.add("Settings")
        self.tabview.configure(command=self._on_tab_changed)

        self.dashboard = DashboardTab(tab_dashboard, self)
        self.dashboard.pack(fill="both", expand=True)

        self.port_tab = PortTab(tab_port, self)
        self.port_tab.pack(fill="both", expand=True)

        self.backups_tab = BackupsTab(tab_backups, self)
        self.backups_tab.pack(fill="both", expand=True)

        self.settings_tab = SettingsTab(tab_settings, self)
        self.settings_tab.pack(fill="both", expand=True)

        self.status_var = ctk.StringVar(value="Ready")
        ctk.CTkLabel(
            self, textvariable=self.status_var, anchor="w",
            text_color=theme.TEXT_MUTED, font=(theme.FONT_FAMILY, 11),
        ).pack(fill="x", side="bottom", padx=18, pady=(2, 8))

    def _on_tab_changed(self) -> None:
        selected = self.tabview.get()
        if selected == "Backups":
            self.backups_tab.on_tab_shown()
        elif selected == "Dashboard":
            self.dashboard.on_tab_shown()

    # --- shared state management --------------------------------------

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def refresh_accounts(self) -> None:
        self.persona_names = steam.load_persona_names(self.steam_install_path)
        self.accounts = steam.discover_accounts(self.userdata_path, self.persona_names)

        self.dashboard.on_accounts_changed()
        self.port_tab.on_accounts_changed()
        self.backups_tab.on_accounts_changed()

        found = sum(1 for a in self.accounts if a.has_cs_config)
        if self.userdata_path.exists():
            self.set_status(f"Found {found} account(s) with CS configs under {self.userdata_path}")
        else:
            self.set_status(f"Steam userdata path not found: {self.userdata_path}")


def main() -> None:
    app = App()
    app.mainloop()
