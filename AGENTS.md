# AGENTS.md — Laravel Dev Setup

## 1. Build/Lint/Test Commands

This project uses Python for orchestration and Bash for installation scripts. There is no formal "build" process, but the following commands are critical for development and testing:

### Running the Orchestrator
- **Local Launch (Bootstrap)**:
  ```bash
  bash install.sh
  ```
- **Direct Orchestrator Launch**:
  ```bash
  python3 main.py
  ```

### Linting & Formatting
- **Python**:
  - The project uses the `rich` library for UI. No strict linter is defined in the repo, but standard Python conventions apply.
  - Check syntax: `python3 -m py_compile main.py`
- **Bash**:
  - Check syntax: `bash -n installers/*.sh lib/*.sh install.sh`
  - Format (if `shfmt` is available): `shfmt -w installers/*.sh lib/*.sh install.sh`

### Testing
There are no automated unit tests. Manual testing involves running the orchestrator and verifying:
1.  UI rendering (themes, navigation).
2.  Component detection (existing installations).
3.  Installation logic (via `run_bash_cmd`).
4.  Sudo password injection.
5.  Modular installer scripts (e.g., `installers/php.sh`, `installers/node.sh`).

To test a **single installer script** in isolation:
```bash
# Example: Test PHP installer logic
export LARAVEL_SETUP_RICH=1
source lib/ui.sh
source lib/detect.sh
source lib/repo.sh
source installers/php.sh
detect_os
setup_repo
install_php 8.4
```

## 2. Code Style Guidelines

### Python (`main.py`)
- **Imports**: Group standard library, third-party (`rich`), and local imports. Keep lines under 100 chars.
- **Formatting**: Use 4 spaces for indentation. No trailing whitespace.
- **Types**: Use type hints where practical (e.g., function arguments, return types).
- **Naming**:
  - Variables: `snake_case` (e.g., `current_theme_key`).
  - Functions: `snake_case` (e.g., `get_header`).
  - Constants: `UPPER_SNAKE_CASE` (e.g., `THEMES`).
- **Error Handling**:
  - Use `try...except` blocks for external commands (e.g., `subprocess.check_output`).
  - Avoid bare `except:`; catch specific exceptions or use `except Exception` with caution.
  - Graceful exit on `SIGINT` via `graceful_exit`.
- **UI Consistency**:
  - Use `rich` components (`Panel`, `Table`, `Progress`).
  - Respect `get_theme()` for dynamic styling.
  - Use `box.DOUBLE` for security modals.

### Bash (Installers & Libs)
- **Shebang**: Always `#!/bin/bash` at the top.
- **Indentation**: 2 spaces (consistent with existing scripts).
- **Variables**:
  - Local variables in functions: `local var`.
  - Global variables: `UPPER_SNAKE_CASE` (e.g., `PHP_PACKAGES_DEFAULT`).
- **Error Handling**:
  - Use `set -euo pipefail` at the start of scripts (check if adopted).
  - Check command exit codes (e.g., `if ! command -v ...`).
  - Use `run_step` wrapper for consistent UI feedback.
- **Modularity**:
  - Source `lib/ui.sh`, `lib/detect.sh`, `lib/repo.sh` at the top.
  - Define `install_<name>()` functions.
  - Use `section`, `msg_ok`, `msg_fail` for output.
- **Security**:
  - Use `$SUDO` variable for privilege escalation.
  - Avoid hardcoded credentials.

### General
- **Comments**: Avoid unless necessary (per instructions). If needed, keep them concise.
- **Dependencies**:
  - Python: `rich` (handled by `install.sh`).
  - Bash: Standard Ubuntu utilities (`apt`, `systemctl`, etc.).

## 3. Cursor/Copilot Rules
No specific `.cursorrules` or `.github/copilot-instructions.md` found. Follow general guidelines above.