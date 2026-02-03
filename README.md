# CS:GO/CS2 Settings Porter

<div align="center">

![CS:GO Settings Porter](https://img.shields.io/badge/CS:GO-Settings%20Porter-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows-informational?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Transfer CS:GO/CS2 settings between Steam accounts with ease**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Building](#building) • [Contributing](#contributing)

</div>

## 📋 Overview

CS:GO/CS2 Settings Porter is a powerful GUI application that allows you to easily transfer, backup, and restore your Counter-Strike: Global Offensive and Counter-Strike 2 settings between different Steam accounts. Perfect for players who have multiple accounts or need to migrate their settings to a new system.

## ✨ Features

### 🚀 Core Functionality
- **Port Settings**: Copy CS:GO/CS2 configurations from one Steam account to another
- **Backup Creation**: Create timestamped backups of your settings
- **Restore Functionality**: Restore settings from previous backups
- **Account Detection**: Automatically detects Steam accounts with CS:GO/CS2 configs

### 🎨 User Interface
- **Modern GUI**: Clean, intuitive interface with tabbed navigation
- **Real-time Logging**: Detailed operation logs for every action
- **Progress Indicators**: Visual feedback during operations
- **Account Browser**: Easy account selection with integrated browser

### 🔧 Advanced Features
- **Auto-backup**: Option to create backup before porting
- **Custom Paths**: Configurable Steam and backup directories
- **Error Handling**: Comprehensive error messages and validation
- **Multi-threading**: Non-blocking operations for smooth UX

## 📸 Application Screenshots

### Dashboard
<img width="1916" height="1026" alt="image" src="https://github.com/user-attachments/assets/b0e77d0d-e8f7-4d87-9df2-5c8404ac8a87" />

### Port Settings Tab
<img width="1919" height="1027" alt="image" src="https://github.com/user-attachments/assets/7108f1ea-884a-473d-8ab6-ea8ca019c8ff" />

### Backup/Restore Tabs
<img width="1919" height="1025" alt="image" src="https://github.com/user-attachments/assets/52a3c926-117c-4e3c-b0d7-f266abdc49db" />

## 🚀 Installation

### Option 1: Download Pre-built Executable (Recommended)

1. **Download the latest release** from the [Releases page](https://github.com/Luzisrepo/Cs-Config-Porter/releases)
2. **Extract the ZIP file** to your preferred location
3. **Run `CSGOSettingsPorter.exe`**
   - No Python installation required
   - No dependencies needed
   - Works out of the box

### Option 2: Run from Source Code

#### Prerequisites
- **Python 3.8 or higher** ([Download Python](https://python.org))
- **Steam installed** on your Windows system

#### Installation Steps
```bash
# Clone the repository
git clone https://github.com/Luzisrepo/Cs-Config-Porter.git
cd Cs-Config-Porter

# Install dependencies
pip install -r requirements.txt

# Run the application
python csporter.py
```

#### Required Python Packages
The application requires:
- `tkinter` (usually included with Python on Windows)
- Standard library modules only (no external dependencies)

## 📖 Usage Guide

### First Launch
1. **Launch the application** from the executable or Python script
2. **Verify Steam Path**: The app auto-detects your Steam installation
   - If incorrect, update in Settings tab
3. **View Detected Accounts**: All Steam accounts with CS:GO/CS2 configs appear in the Dashboard

### Porting Settings Between Accounts
1. Navigate to **"Port Settings"** tab
2. **Select Source Account**: Enter Steam ID or browse detected accounts
3. **Select Target Account**: Enter or browse target Steam ID
4. **Configure Options**:
   - ✅ "Create backup of target account before porting" (recommended)
5. Click **"🚀 Port Settings"**
6. Monitor progress in the operation log

### Creating Backups
1. Go to **"Backup"** tab
2. **Select Account**: Choose which account to backup
3. **Choose Location**: Default or custom backup directory
4. Click **"💾 Create Backup"**
5. Backup is saved with timestamp: `{account_id}_{YYYY-MM-DD_HH-MM-SS}`

### Restoring Backups
1. Navigate to **"Restore"** tab
2. **Select Backup**: Choose from available backups (click Refresh if needed)
3. **Choose Target Account**: Select which account to restore to
4. Click **"↩ Restore Backup"**
5. Monitor restoration progress

### Settings Configuration
1. **Steam Path**: Update if Steam is installed in non-default location
2. **Backup Directory**: Change where backups are stored
3. **Save Settings**: Changes take effect immediately

## 🛠️ Building from Source

### Using the Provided Compiler Script
The repository includes a convenient build script for Windows:

```bash
# Simply run the compiler script
build.bat
```

The script will:
1. **Check Python installation**
2. **Install PyInstaller** if needed
3. **Clean previous builds**
4. **Create standalone executable**
5. **Output to `dist/CSGOSettingsPorter.exe`**

### Manual Building with PyInstaller
```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --windowed --name="CSGOSettingsPorter" --clean --noconfirm csporter.py
```

### Build Options
- `--onefile`: Creates single executable
- `--windowed`: No console window
- `--clean`: Clean build directory
- `--icon=icon.ico`: Add custom icon (optional)

## 📁 File Structure

```
Cs-Config-Porter/
├── csporter.py              # Main application source code
├── build.bat                # Windows build script
├── requirements.txt         # Python dependencies
├── README.md               # This documentation
├── dist/                   # Compiled executables (after build)
│   └── CSGOSettingsPorter.exe
├── build/                  # Build temporary files
└── backups/                # User backup storage (created at runtime)
```

## 🔍 Technical Details

### How It Works
1. **Steam UserData Structure**: The app navigates to `Steam/userdata/{STEAM_ID}/730/local/cfg`
2. **Configuration Files**: CS:GO/CS2 settings are stored as `.cfg` files
3. **Porting Process**: Copies all files from source to target directory
4. **Backup Process**: Creates timestamped copies of configuration folders

### Default Paths
```python
# Steam installation (default)
C:\Program Files (x86)\Steam\userdata

# CS:GO/CS2 configuration path
{STEAM_ID}\730\local\cfg

# Backup directory
C:\Program Files (x86)\Steam\cs_backups
```

### Supported Files
- All `.cfg` configuration files
- `autoexec.cfg`
- `config.cfg`
- `video.txt`
- Other user-created config files

## ⚠️ Important Notes

### Security Considerations
- **No Internet Access**: Application runs entirely locally
- **No Data Collection**: No telemetry or data transmission
- **Backup Safety**: Always creates backups before overwriting

### Limitations
- **Windows Only**: Designed for Windows Steam installations
- **CS:GO/CS2 Only**: Specifically for Counter-Strike series
- **Steam Required**: Must have Steam installed

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Steam path not found" | Update Steam path in Settings tab |
| "No accounts detected" | Ensure CS:GO/CS2 has been run on the account |
| "Permission denied" | Run as Administrator or check folder permissions |
| Executable won't run | Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) |

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Issues
1. Check existing [Issues](https://github.com/Luzisrepo/Cs-Config-Porter/issues)
2. Create new issue with:
   - Detailed description
   - Steps to reproduce
   - Screenshots if applicable
   - System information

### Feature Requests
1. Check existing feature requests
2. Submit new request with:
   - Use case description
   - Expected behavior
   - Potential implementation ideas

### Pull Requests
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Setup
```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/Cs-Config-Porter.git

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install development dependencies
pip install pyinstaller

# 4. Make changes and test
python csporter.py

# 5. Build and test executable
build.bat
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Luzisrepo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 Acknowledgments

- **Valve Corporation** for CS:GO and CS2
- **Steam** platform for userdata structure
- **Python community** for excellent libraries
- **Contributors** and users of this tool

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/Luzisrepo/Cs-Config-Porter/issues)
- **Repository**: [https://github.com/Luzisrepo/Cs-Config-Porter](https://github.com/Luzisrepo/Cs-Config-Porter)
- **Developer**: [Luzisrepo](https://github.com/Luzisrepo)

## 🌟 Star History

If you find this project useful, please consider giving it a star on GitHub!

[![Star History Chart](https://api.star-history.com/svg?repos=Luzisrepo/Cs-Config-Porter&type=Date)](https://star-history.com/#Luzisrepo/Cs-Config-Porter&Date)

---

<div align="center">
for the CS:GO/CS2 community

**Happy Gaming! 🎮**
</div>
