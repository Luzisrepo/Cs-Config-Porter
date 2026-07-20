# CS:GO / CS2 Settings Porter

A small Windows desktop tool for moving, backing up, and restoring CS:GO/CS2
config files (`config.cfg`, `video.txt`, autoexecs, etc.) between Steam
accounts on the same machine.

Rebuilt from the ground up with a cleaner architecture and a few features
the original didn't have:

- **Per-file selection** — every operation shows a checklist of the actual
  files found, so you can port, back up, or restore just the ones you want
  instead of an all-or-nothing folder copy.
- **Account nicknames** — accounts are labeled with your Steam persona name
  (read from `loginusers.vdf`) instead of just a numeric ID, wherever that's
  available.
- **Dry run** — every operation has a "preview only" switch that logs exactly
  what would happen without touching any files.
- **Backup manager** — a dedicated view lists every backup with its account,
  file count, and size, and lets you restore, open, or delete each one.
- **Non-destructive by default** — porting and restoring only touch the files
  you select; unlike the original, they no longer wipe out the entire target
  folder first.
- **Auto-detected Steam path** — reads the Windows registry to find your
  Steam install automatically, with manual override in Settings.

## Requirements

- Windows 10 or newer
- A Steam installation with CS:GO or CS2 launched at least once per account
  you want to work with
- Python 3.10+ if running from source (not needed for the compiled `.exe`)

## Running from source

```bash
pip install -r requirements.txt
python main.py
```

## Building a standalone executable

```bash
build.bat
```

This installs PyInstaller if needed and produces `dist\CSGOSettingsPorter.exe`.

## Project layout

```
csporter/
├── main.py              # entry point
├── core/                # UI-independent logic
│   ├── models.py        # SteamAccount / ConfigFile / BackupRecord / OperationResult
│   ├── steam.py         # Steam path detection, persona names, account/file discovery
│   └── operations.py    # port / backup / restore, dry-run aware
├── ui/                  # CustomTkinter interface
│   ├── app.py           # main window, shared state
│   ├── theme.py         # color palette
│   ├── widgets.py        # AccountSelector, FileChecklist, LogConsole, StatCard
│   ├── async_utils.py    # background-thread helper for long-running operations
│   ├── dashboard.py, port.py, backups.py, settings.py   # the four tabs
├── requirements.txt
└── build.bat
```

## How it finds your data

Steam stores each account's CS:GO/CS2 settings under:

```
<Steam install>\userdata\<account_id>\730\local\cfg\
```

Backups are plain folders (`<account_id>_<timestamp>`) containing a copy of
the selected files plus a small `_manifest.json` with the account ID, persona
name, and timestamp, so the Backup Manager can display useful details even
without decoding the folder name.

## Notes

- Everything runs locally; there's no network access and nothing is collected
  or transmitted.
- Restart CS:GO/CS2 after porting or restoring for changes to take effect.
