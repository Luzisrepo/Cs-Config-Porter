# CS:GO / CS2 Settings Porter

<div align="center">

<img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Platform">
<img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/License-MIT-066da5?style=for-the-badge&logo=open-source-initiative&logoColor=white" alt="License">

## Enterprise-Grade Configuration Management for Counter-Strike

**Streamline the migration and backup of game settings across Steam accounts with a robust, user-friendly desktop application.**

[Overview](#overview) • [Features](#features) • [Installation](#installation) • [Usage](#usage) • [Technical Documentation](#technical-documentation) • [Contributing](#contributing)

</div>

## Overview

The CS:GO/CS2 Settings Porter is a professional desktop utility designed to facilitate the efficient transfer, backup, and restoration of Counter-Strike: Global Offensive and Counter-Strike 2 configuration settings. This tool addresses the common challenge of maintaining consistent gameplay environments across multiple Steam accounts or after system migrations, providing a reliable and automated solution.

## Features

### Core Functionality
*   **Cross-Account Settings Transfer**: Seamlessly copy configuration profiles from one Steam account to another.
*   **Comprehensive Backup Creation**: Generate timestamped, versioned backups of all game settings.
*   **One-Click Restoration**: Easily revert to any previously saved backup point.
*   **Automatic Account Discovery**: Intelligently scans and identifies all Steam accounts with existing CS:GO/CS2 configurations.

### User Interface & Experience
*   **Structured Tabbed Interface**: Logical organization of functions within a single, clean window.
*   **Integrated Operation Log**: Real-time, detailed logging of all application activities for auditability.
*   **Visual Progress Feedback**: Clear indicators for ongoing operations.
*   **Streamlined Account Management**: Built-in browser for effortless source and target account selection.

### Advanced Capabilities
*   **Pre-Operation Safeguards**: Configurable option to auto-create backups before any transfer operation.
*   **Custom Directory Support**: Flexible configuration for Steam installation and backup storage paths.
*   **Robust Error Handling**: Comprehensive validation and user-friendly error messaging.
*   **Asynchronous Processing**: Non-blocking operations ensure application responsiveness.

## Application Interface

### Dashboard
*Figure 1: Primary application dashboard displaying detected Steam accounts and quick-access functions.*
<img width="1916" height="1026" alt="Application Dashboard" src="https://github.com/user-attachments/assets/b0e77d0d-e8f7-4d87-9df2-5c8404ac8a87" />

### Settings Transfer Module
*Figure 2: Interface for selecting source and target accounts and initiating the transfer process.*
<img width="1919" height="1027" alt="Settings Transfer Interface" src="https://github.com/user-attachments/assets/7108f1ea-884a-473d-8ab6-ea8ca019c8ff" />

### Backup & Restore Modules
*Figure 3: Dedicated tabs for creating new backups and restoring from existing archives.*
<img width="1919" height="1025" alt="Backup and Restore Interfaces" src="https://github.com/user-attachments/assets/52a3c926-117c-4e3c-b0d7-f266abdc49db" />

## Installation

### Method A: Pre-Compiled Executable (Recommended for End Users)
1.  Download the latest release package from the official [Releases page](https://github.com/Luzisrepo/Cs-Config-Porter/releases).
2.  Extract the contents of the ZIP archive to a directory of your choice.
3.  Execute the `CSGOSettingsPorter.exe` file.
    *   *Note: No additional software or dependencies are required.*

### Method B: Source Code Execution (For Developers or Contributors)

#### Prerequisites
*   Python 3.8 or newer installed on your system. ([Download Python](https://www.python.org/downloads/))
*   A standard Windows installation of the Steam client.

#### Procedure
```bash
# Clone the repository to your local machine
git clone https://github.com/Luzisrepo/Cs-Config-Porter.git
cd Cs-Config-Porter

# Install required Python modules
pip install -r requirements.txt

# Launch the application
python csporter.py
```

#### Dependency Information
The application utilizes the following:
*   `tkinter` (included with standard Python distributions on Windows)
*   Python Standard Library modules only.

## Usage Guide

### Initial Configuration
1.  Launch `CSGOSettingsPorter.exe`.
2.  The application will attempt to auto-locate your Steam installation directory. Verify this path on the **Settings** tab.
3.  Upon successful detection, all Steam accounts containing CS:GO/CS2 configuration data will be listed in the **Dashboard**.

### Transferring Settings Between Accounts
1.  Navigate to the **Port Settings** tab.
2.  In the **Source Account** field, input the Steam ID or select an account from the detected list.
3.  In the **Target Account** field, input or select the destination Steam ID.
4.  Configure operational preferences:
    *   Enable **"Create backup of target account before porting"** (Recommended).
5.  Initiate the process by selecting **Port Settings**.
6.  Monitor the progress and outcome in the operation log panel.

### Creating a Configuration Backup
1.  Access the **Backup** tab.
2.  Select the desired Steam account from the dropdown menu.
3.  Specify a backup storage location (default directory is pre-configured).
4.  Select **Create Backup**.
5.  A new backup folder will be created with the naming convention: `{account_id}_{YYYY-MM-DD_HH-MM-SS}`.

### Restoring from a Backup
1.  Navigate to the **Restore** tab.
2.  From the list of available backups (refresh if necessary), select the desired archive.
3.  Choose the target Steam account for restoration.
4.  Select **Restore Backup**.
5.  Observe the restoration progress in the log.

### Application Settings
*   **Steam Installation Path**: Update if Steam is installed in a non-standard location.
*   **Backup Directory**: Define the default storage path for created backups.
*   Settings are saved and applied immediately upon modification.

## Building from Source

### Automated Build Process (Windows)
A batch script is provided to simplify the compilation process:
```bash
# Execute the build script from the repository root
build.bat
```
This script performs the following actions sequentially:
1.  Validates the Python installation.
2.  Installs PyInstaller if not present.
3.  Cleans previous build artifacts.
4.  Compiles the standalone executable.
5.  Outputs the final executable to the `dist/` directory.

### Manual Compilation with PyInstaller
```bash
# Install the PyInstaller package
pip install pyinstaller

# Execute PyInstaller with recommended parameters
pyinstaller --onefile --windowed --name="CSGOSettingsPorter" --clean --noconfirm csporter.py
```

### Common Build Parameters
*   `--onefile`: Packages the application into a single executable file.
*   `--windowed`: Prevents a console window from appearing.
*   `--clean`: Removes temporary files from previous builds.
*   `--icon=icon.ico`: Specifies a custom application icon (optional).

## Project Structure

```
Cs-Config-Porter/
├── csporter.py              # Primary application source code
├── build.bat                # Automated build script for Windows
├── requirements.txt         # Python package dependencies
├── README.md               # Project documentation
├── dist/                   # Output directory for compiled executables
│   └── CSGOSettingsPorter.exe
├── build/                  # Temporary files generated during compilation
└── backups/                # User-generated backup storage (created at runtime)
```

## Technical Documentation

### Operational Methodology
1.  **Path Resolution**: The application interfaces with the Steam `userdata` directory structure, specifically `Steam/userdata/{STEAM_ID}/730/local/cfg`.
2.  **File Management**: It identifies and processes all relevant `.cfg` configuration files.
3.  **Transfer Protocol**: Executes a complete copy of all configuration files from the source to the target directory.
4.  **Backup Protocol**: Creates compressed, timestamped archives of the target configuration folder.

### Standard Directory Paths
```
# Default Steam Installation Path
C:\Program Files (x86)\Steam\userdata

# CS:GO/CS2 Configuration Storage Path (per account)
{STEAM_ID}\730\local\cfg

# Default Backup Storage Directory
C:\Program Files (x86)\Steam\cs_backups
```

### Supported File Types
*   Primary configuration files (`config.cfg`, `autoexec.cfg`)
*   Video settings (`video.txt`)
*   All user-generated and game-generated `.cfg` files within the target directory.

## Important Notes & Compliance

### Security & Privacy
*   **Local Execution Only**: The application performs all operations locally and does not require network access.
*   **No Telemetry**: No user data, configurations, or usage statistics are collected or transmitted.
*   **Data Integrity**: Built-in safeguards ensure original data is preserved via backups before modification.

### System Requirements & Limitations
*   **Supported OS**: Microsoft Windows (10 or newer recommended).
*   **Game Support**: Counter-Strike: Global Offensive and Counter-Strike 2 exclusively.
*   **Prerequisite Software**: A functioning installation of the Steam client is required.

### Troubleshooting

| Issue | Recommended Resolution |
| :--- | :--- |
| Steam installation path not found. | Manually specify the correct path in the **Settings** tab. |
| No Steam accounts are detected. | Ensure CS:GO/CS2 has been launched at least once under the target account. |
| "Permission denied" errors. | Ensure the application has appropriate read/write permissions for the involved directories. |
| Compiled executable fails to launch. | Install the latest [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe). |

## Contributing

We welcome contributions from the community. Please follow the standard process below.

### Reporting Issues
1.  Review the existing [Issues](https://github.com/Luzisrepo/Cs-Config-Porter/issues) to avoid duplicates.
2.  Submit a new issue with the following information:
    *   A clear, descriptive title.
    *   Detailed steps to reproduce the problem.
    *   Relevant screenshots or error messages.
    *   Your system environment details.

### Submitting Enhancements
1.  Examine current feature requests.
2.  Propose new enhancements with a clear description of the use case, expected behavior, and proposed solution.

### Development Workflow
1.  **Fork** the main repository.
2.  **Create a feature branch**: `git checkout -b feature/descriptive-name`
3.  **Commit your changes**: `git commit -m 'Add descriptive commit message'`
4.  **Push to the branch**: `git push origin feature/descriptive-name`
5.  **Open a Pull Request** for review.

### Local Development Environment
```bash
# 1. Clone your forked repository
git clone https://github.com/YOUR_USERNAME/Cs-Config-Porter.git
cd Cs-Config-Porter

# 2. Create and activate a Python virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install development tools
pip install pyinstaller

# 4. Run the application for testing
python csporter.py

# 5. Build a test executable
build.bat
```

## License

Distributed under the MIT License. Refer to the [LICENSE](LICENSE) file for the full text.

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

## Acknowledgments

*   Valve Corporation for Counter-Strike: Global Offensive and Counter-Strike 2.
*   The Steam platform and its consistent userdata structure.
*   The Python Software Foundation and the open-source community.
*   All contributors and users who provide feedback and support.

## Contact & Support

*   **Official Repository**: [https://github.com/Luzisrepo/Cs-Config-Porter](https://github.com/Luzisrepo/Cs-Config-Porter)
*   **Issue Tracker**: [GitHub Issues](https://github.com/Luzisrepo/Cs-Config-Porter/issues)
*   **Maintainer**: [Luzisrepo](https://github.com/Luzisrepo)

## Project Metrics

[![Star History Chart](https://api.star-history.com/svg?repos=Luzisrepo/Cs-Config-Porter&type=Date)](https://star-history.com/#Luzisrepo/Cs-Config-Porter&Date)

---

<div align="center">
A professional tool for the Counter-Strike community.

**CS:GO/CS2 Settings Porter**
</div>
