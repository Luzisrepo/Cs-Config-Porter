"""Everything related to finding Steam, its accounts, and their CS config files."""
from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from .models import ConfigFile, SteamAccount

CS_CFG_SUBPATH = Path("730") / "local" / "cfg"

# SteamID64 = accountID (the userdata folder name) + this offset, for the
# public "individual" account universe. This lets us map the numeric
# userdata folder to the friendly name Steam stores in loginusers.vdf.
STEAM_ID64_INDIVIDUAL_OFFSET = 76561197960265728


def default_userdata_path() -> Path:
    """Best-guess default location of Steam/userdata on Windows."""
    return Path(r"C:\Program Files (x86)\Steam\userdata")


def autodetect_steam_install() -> Optional[Path]:
    """Try to find the Steam install directory via the Windows registry.

    Returns the *install* directory (the one containing userdata/), or None
    if it can't be determined (e.g. not on Windows, or Steam not installed).
    """
    if sys.platform != "win32":
        return None
    try:
        import winreg
    except ImportError:
        return None

    candidates = [
        (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
    ]
    for hive, subkey, value_name in candidates:
        try:
            with winreg.OpenKey(hive, subkey) as key:
                value, _ = winreg.QueryValueEx(key, value_name)
                path = Path(value)
                if path.exists():
                    return path
        except OSError:
            continue
    return None


def autodetect_userdata_path() -> Optional[Path]:
    """Try to find Steam/userdata automatically. Falls back to None."""
    install_path = autodetect_steam_install()
    if install_path:
        candidate = install_path / "userdata"
        if candidate.exists():
            return candidate
    default = default_userdata_path()
    if default.exists():
        return default
    return None


# --- Persona name resolution -------------------------------------------------

_VDF_BLOCK_RE = re.compile(r'"(\d{17})"\s*\{([^{}]*)\}', re.DOTALL)
_VDF_PERSONA_RE = re.compile(r'"PersonaName"\s*"([^"]*)"', re.IGNORECASE)


def load_persona_names(steam_install_path: Optional[Path]) -> Dict[str, str]:
    """Parse Steam/config/loginusers.vdf into {account_id: persona_name}.

    account_id here is the *32-bit* id used as the userdata folder name,
    not the full SteamID64 stored in the file. Returns an empty dict if the
    file can't be found or parsed -- this is a best-effort convenience
    feature, never required for the app to function.
    """
    result: Dict[str, str] = {}
    if not steam_install_path:
        return result

    vdf_path = steam_install_path / "config" / "loginusers.vdf"
    if not vdf_path.exists():
        return result

    try:
        text = vdf_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return result

    for steamid64_str, block in _VDF_BLOCK_RE.findall(text):
        match = _VDF_PERSONA_RE.search(block)
        if not match:
            continue
        try:
            steamid64 = int(steamid64_str)
        except ValueError:
            continue
        account_id = str(steamid64 - STEAM_ID64_INDIVIDUAL_OFFSET)
        result[account_id] = match.group(1)

    return result


# --- Account & file discovery ------------------------------------------------

def discover_accounts(userdata_path: Path, persona_names: Optional[Dict[str, str]] = None) -> List[SteamAccount]:
    """Scan Steam/userdata for account folders and detect CS:GO/CS2 configs."""
    from .models import SteamAccount  # local import to avoid a cycle at module load

    persona_names = persona_names or {}
    accounts: List[SteamAccount] = []

    if not userdata_path.exists():
        return accounts

    try:
        entries = sorted(userdata_path.iterdir(), key=lambda p: p.name)
    except OSError:
        return accounts

    for entry in entries:
        if not entry.is_dir() or not entry.name.isdigit():
            continue
        cfg_path = entry / CS_CFG_SUBPATH
        has_cfg = cfg_path.exists() and any(cfg_path.iterdir()) if cfg_path.exists() else False
        file_count = 0
        if has_cfg:
            file_count = sum(1 for p in cfg_path.rglob("*") if p.is_file())
        accounts.append(
            SteamAccount(
                account_id=entry.name,
                persona_name=persona_names.get(entry.name),
                cfg_path=cfg_path,
                has_cs_config=has_cfg,
                file_count=file_count,
            )
        )
    return accounts


def list_config_files(cfg_path: Path) -> List[ConfigFile]:
    """Recursively list every file under a cfg directory."""
    from .models import ConfigFile  # local import to avoid a cycle at module load

    files: List[ConfigFile] = []
    if not cfg_path.exists():
        return files

    for path in sorted(cfg_path.rglob("*")):
        if not path.is_file():
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        files.append(
            ConfigFile(
                relative_path=path.relative_to(cfg_path).as_posix(),
                absolute_path=path,
                size_bytes=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime),
            )
        )
    return files
