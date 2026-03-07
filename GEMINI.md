# 🚀 Laravel Dev Setup — Instructional Context

This project is a professional, modular automation tool designed to bootstrap a complete Laravel development environment EXCLUSIVELY on Ubuntu 24.04 and newer (including WSL2 based on Ubuntu 24.04).

## 🛠 Project Overview

- **Orchestrator**: `main.py` serves as the primary entry point, providing an interactive CLI using the `rich` library. It handles component selection, system detection, and security (sudo) management.
- **Bootstrapper**: `install.sh` is a shell-based installer that prepares the environment (Git, Python, Pip, Rich) and launches the Python orchestrator. It performs an early OS check to ensure Ubuntu 24.04+.
- **Modular Installers**: Located in `installers/`, these are independent shell scripts for specific components (PHP, MariaDB, Node.js, Composer, Valet).
- **Core Library**: Located in `lib/`, these scripts provide shared functionality for UI styling (`ui.sh`), strict OS detection (`detect.sh`), and repository management (`repo.sh`).

### Main Technologies
- **Python 3**: Core orchestration and UI logic.
- **Rich Library**: Advanced terminal formatting, progress bars, and interactive components.
- **Bash**: Low-level system configuration and package management.
- **Pseudo-Terminal (PTY)**: Used for transparent `sudo` password injection and real-time output capture.

## 🚀 Building and Running

### Prerequisites
- Ubuntu 24.04+ or WSL2 (Ubuntu 24.04).
- Sudo privileges.

### Key Commands
- **Standard Installation (Remote)**:
  ```bash
  curl -sSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/install.sh | bash
  ```
- **Local Launch (Bootstrap)**:
  ```bash
  bash install.sh
  ```
- **Direct Orchestrator Launch**:
  ```bash
  python3 main.py
  ```

## 📐 Development Conventions

### UI Consistency
- **Themes**: Supports dynamic `dark` and `light` themes. All new UI components must respect the `get_theme()` palette in `main.py`.
- **Modals**: Security prompts and critical questions use centered, double-bordered panels (`box.DOUBLE`).
- **Interactive Just-in-Time**: Questions (like version selection) should occur right before the specific component installation begins.

### Orchestration Logic
- **PTY Injection**: `run_bash_cmd` in `main.py` uses a Pseudo-Terminal to detect `sudo` prompts and automatically inject the cached password.
- **Non-Interactive APT**: Shell scripts must use `DEBIAN_FRONTEND=noninteractive` for package installations to prevent blocking the UI.
- **Environment Awareness**: Shell scripts check for `LARAVEL_SETUP_RICH=1` to disable their own ANSI colors and spinners when being driven by Python.

### Component Structure
Each installer in `installers/` should follow this pattern:
1. `source lib/ui.sh`, `source lib/detect.sh`, etc.
2. Define an `install_<name>()` function.
3. Use `run_step` for individual tasks to maintain UI feedback.
4. Respect the `DISTRO_TYPE` variable populated by `detect_os`.
