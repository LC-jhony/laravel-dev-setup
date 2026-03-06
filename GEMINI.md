# 🚀 Laravel Dev Setup - Instruction Manual

This project is an interactive, modular Bash-based installer for a complete Laravel development environment on Linux (Ubuntu and Debian). It provides a polished terminal interface with progress indicators, toggle menus, and ANSI colors.

## 🛠️ Project Architecture

The installer is built using a modular structure to separate UI, detection logic, and individual component installations:

- **`install.sh`**: The main entry point. Orchestrates the installation wizard, gathers user preferences, and executes the selected installers in dependency order.
- **`lib/`**: Contains reusable helper scripts (not meant to be executed directly).
    - `ui.sh`: Defines colors, symbols, layout helpers (banner, sections, boxes), spinner/progress functions, and interactive menus/prompts.
    - `detect.sh`: Handles OS distribution/version detection and identifies existing PHP installations.
    - `repo.sh`: Configures external repositories like `ondrej/php` for Ubuntu and `sury.org` for Debian.
- **`installers/`**: Individual scripts responsible for installing specific components.
    - `shell.sh`: Configures Zsh, Zinit, Powerlevel10k, and standard CLI tools (`git`, `fzf`, `zoxide`).
    - `php.sh`: Installs selected PHP versions and extensions.
    - `mariadb.sh`: Installs and secures MariaDB.
    - `nodejs.sh`: Installs NVM and a specified Node.js version.
    - `composer.sh`: Performs a global installation of Composer.
    - `valet.sh`: Installs `cpriego/valet-linux` and the Laravel installer.

## 🚀 Getting Started

### Prerequisites
- Ubuntu (20.04+) or Debian (11+)
- `bash` version 4 or higher
- `curl` installed
- `sudo` privileges

### Running the Installer
To start the interactive installation process:
```bash
bash install.sh
```

### Development Guidelines
- **Strict Mode**: All scripts should use `set -euo pipefail` to ensure robust error handling.
- **UI Consistency**: Always use the helpers in `lib/ui.sh` (`section`, `msg_ok`, `msg_info`, `run_step`, etc.) for output to maintain a consistent look and feel.
- **Modularity**: New components should be added as a separate script in `installers/` and registered in the `STATES` array and loop within `install.sh`.

## ⚠️ Known Issues / TODOs
- **File Naming Mismatch**: The `install.sh` script expects `installers/node.sh`, but the file is currently named `installers/nodejs.sh`.
- **Duplicate Scripts**: Currently, `installers/php.sh` appears to be a duplicate of `installers/shell.sh`. This needs to be corrected to implement actual PHP installation logic.
- **Cross-Platform**: The project is strictly designed for Linux (Ubuntu/Debian). It will not work on macOS (native) or Windows (native) without WSL.

## 📦 Component Overview
- **Shell**: Zsh + Powerlevel10k + Zinit + Auto-suggestions + Syntax highlighting.
- **PHP**: Versions 8.1 to 8.5, configurable profiles (Default/Minimal/Custom).
- **Database**: MariaDB with secure installation wizard.
- **Node.js**: Managed via NVM.
- **Laravel Stack**: Composer + Valet Linux + Laravel Installer.
