"""Small reusable UI building blocks shared by every tab."""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

import customtkinter as ctk

from core.models import ConfigFile, SteamAccount
from . import theme


class StatCard(ctk.CTkFrame):
    """A single labeled statistic, used on the Dashboard."""

    def __init__(self, master, title: str, value: str = "—", **kwargs):
        super().__init__(master, fg_color=theme.BG_CARD, corner_radius=10, **kwargs)
        self._title_label = ctk.CTkLabel(
            self, text=title, font=(theme.FONT_FAMILY, 12), text_color=theme.TEXT_MUTED, anchor="w"
        )
        self._title_label.pack(fill="x", padx=16, pady=(14, 0))
        self._value_label = ctk.CTkLabel(
            self, text=value, font=(theme.FONT_FAMILY, 26, "bold"), text_color=theme.ACCENT, anchor="w"
        )
        self._value_label.pack(fill="x", padx=16, pady=(0, 14))

    def set_value(self, value: str) -> None:
        self._value_label.configure(text=value)


class LogConsole(ctk.CTkFrame):
    """A read-only, color-tagged scrolling log, used for operation output."""

    def __init__(self, master, height: int = 160, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.textbox = ctk.CTkTextbox(
            self, height=height, font=(theme.FONT_MONO, 12),
            fg_color=theme.BG_INPUT, text_color=theme.LOG_INFO, wrap="word",
        )
        self.textbox.pack(fill="both", expand=True)
        theme.apply_log_tags(self.textbox)
        self.textbox.configure(state="disabled")

    def log(self, message: str, level: str = "info") -> None:
        self.textbox.configure(state="normal")
        self.textbox.insert("end", message + "\n", level)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear(self) -> None:
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")


class AccountSelector(ctk.CTkFrame):
    """Pick a Steam account from a dropdown of discovered accounts, or type a
    Steam ID manually (e.g. for an account that hasn't logged into CS yet).

    The manual entry is always the source of truth for `get_account_id()`;
    picking a dropdown item just fills the entry in for convenience.
    """

    def __init__(self, master, on_change: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_change = on_change
        self._label_to_account: Dict[str, SteamAccount] = {}

        self.combobox = ctk.CTkComboBox(
            self, values=["No accounts found"], state="readonly",
            command=self._handle_pick, fg_color=theme.BG_INPUT,
            border_color=theme.BORDER, button_color=theme.ACCENT,
            button_hover_color=theme.ACCENT_HOVER, dropdown_fg_color=theme.BG_CARD,
        )
        self.combobox.pack(fill="x")

        self.id_var = ctk.StringVar()
        entry_row = ctk.CTkFrame(self, fg_color="transparent")
        entry_row.pack(fill="x", pady=(6, 0))
        ctk.CTkLabel(
            entry_row, text="Steam ID:", text_color=theme.TEXT_MUTED, width=70, anchor="w"
        ).pack(side="left")
        self.id_entry = ctk.CTkEntry(
            entry_row, textvariable=self.id_var, fg_color=theme.BG_INPUT, border_color=theme.BORDER,
        )
        self.id_entry.pack(side="left", fill="x", expand=True)
        self.id_var.trace_add("write", lambda *_: self._notify())

    def set_accounts(self, accounts: List[SteamAccount], only_with_config: bool = False) -> None:
        pool = [a for a in accounts if a.has_cs_config] if only_with_config else list(accounts)
        self._label_to_account = {a.label: a for a in pool}
        previous_id = self.id_var.get().strip()

        if self._label_to_account:
            self.combobox.configure(values=list(self._label_to_account.keys()), state="readonly")
        else:
            self.combobox.configure(values=["No accounts found"], state="disabled")
            self.combobox.set("No accounts found")

        # Keep whatever manual ID was already typed; only auto-fill on first load.
        if not previous_id and pool:
            first_account = pool[0]
            self.combobox.set(first_account.label)
            self.id_var.set(first_account.account_id)
        elif previous_id:
            match = next((a for a in pool if a.account_id == previous_id), None)
            if match:
                self.combobox.set(match.label)

    def _handle_pick(self, label: str) -> None:
        account = self._label_to_account.get(label)
        if account:
            self.id_var.set(account.account_id)
        self._notify()

    def _notify(self) -> None:
        if self._on_change:
            self._on_change()

    def get_selected_account(self) -> Optional[SteamAccount]:
        return self._label_to_account.get(self.combobox.get())

    def get_account_id(self) -> str:
        return self.id_var.get().strip()


class FileChecklist(ctk.CTkFrame):
    """A scrollable list of checkboxes, one per config file, with select-all controls."""

    def __init__(self, master, on_change: Optional[Callable[[], None]] = None, height: int = 220, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_change = on_change
        self._vars: Dict[str, ctk.BooleanVar] = {}
        self._files: List[ConfigFile] = []

        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 6))

        self.summary_label = ctk.CTkLabel(
            controls, text="No files loaded", text_color=theme.TEXT_MUTED, anchor="w"
        )
        self.summary_label.pack(side="left")

        ctk.CTkButton(
            controls, text="None", width=60, fg_color=theme.BG_INPUT,
            hover_color=theme.BORDER, command=self.select_none,
        ).pack(side="right", padx=(6, 0))
        ctk.CTkButton(
            controls, text="All", width=60, fg_color=theme.BG_INPUT,
            hover_color=theme.BORDER, command=self.select_all,
        ).pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(
            self, height=height, fg_color=theme.BG_INPUT, corner_radius=8,
        )
        self.scroll_frame.pack(fill="both", expand=True)

    def set_files(self, files: List[ConfigFile]) -> None:
        for child in self.scroll_frame.winfo_children():
            child.destroy()
        self._vars.clear()
        self._files = files

        if not files:
            ctk.CTkLabel(
                self.scroll_frame, text="No config files found here.", text_color=theme.TEXT_MUTED
            ).pack(anchor="w", padx=8, pady=8)
            self.summary_label.configure(text="No files loaded")
            self._notify()
            return

        for f in files:
            var = ctk.BooleanVar(value=True)
            self._vars[f.relative_path] = var
            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=2)
            ctk.CTkCheckBox(
                row, text=f.relative_path, variable=var, command=self._notify,
                fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                checkmark_color=theme.ACCENT_TEXT,
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=f.display_size, text_color=theme.TEXT_MUTED, width=70, anchor="e"
            ).pack(side="right")

        self._notify()

    def select_all(self) -> None:
        for var in self._vars.values():
            var.set(True)
        self._notify()

    def select_none(self) -> None:
        for var in self._vars.values():
            var.set(False)
        self._notify()

    def get_selected(self) -> List[str]:
        return [rel for rel, var in self._vars.items() if var.get()]

    def _notify(self) -> None:
        selected = self.get_selected()
        self.summary_label.configure(text=f"{len(selected)} of {len(self._files)} file(s) selected")
        if self._on_change:
            self._on_change()
