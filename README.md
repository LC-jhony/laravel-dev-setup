# 🚀 LARAVEL DEV SETUP (Pro Edition)

> **The ultimate automated installer for your Laravel development environment on Linux (Ubuntu, Debian, WSL).**

[![Linux](https://img.shields.io/badge/OS-Linux-brightgreen.svg)](https://www.linux.org/)
[![PHP](https://img.shields.io/badge/PHP-8.1--8.5-blue.svg)](https://www.php.net/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

```text
 ██╗      █████╗ ██████╗  █████╗ ██╗   ██╗███████╗██╗
 ██║     ██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝██║
 ██║     ███████║██████╔╝███████║██║   ██║█████╗  ██║
 ██║     ██╔══██║██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║
 ███████╗██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████╗
 ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝

          ██████╗ ███████╗██╗   ██╗    ███████╗███████╗████████╗██╗   ██╗██████╗
          ██╔══██╗██╔════╝██║   ██║    ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗
          ██║  ██║█████╗  ██║   ██║    ███████╗█████╗     ██║   ██║   ██║██████╔╝
          ██║  ██║██╔══╝  ╚██╗ ██╔╝    ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝
          ██████╔╝███████╗ ╚████╔╝     ███████║███████╗   ██║   ╚██████╔╝██║
          ╚═════╝ ╚══════╝  ╚═══╝      ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝
```

---

## ⚡ Quick Professional Install

Run the following command in your terminal to start the automated installation:

### 🔵 Via curl (Recommended)
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/installer.sh)
```

### 🟠 Via wget
```bash
bash <(wget -qO- https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/installer.sh)
```

---

## 🌟 Professional Features

| Feature | Description |
| :--- | :--- |
| **🚀 One-Line Setup** | Automated cloning and wizard execution (like `rustup` or `nvm`). |
| **🧠 System Detection** | Automatically detects OS (Ubuntu/Debian), architecture, and existing PHP versions. |
| **🧩 Modular Design** | Each component is a separate module (`shell`, `php`, `mariadb`, `node`, `composer`, `valet`). |
| **🐘 PHP Wizard** | Choose version (8.1-8.5), package profile (Default/Minimal), and web server integration. |
| **🐚 Modern Shell** | Zsh + Powerlevel10k + Zinit + Plugins for a elite terminal experience. |
| **🎯 Laravel Stack** | Global Composer, Laravel Installer, and MariaDB (secured). |

---

## 🛠️ Components Included

- **Shell Environment**: `git`, `unzip`, `zsh`, `fzf`, `zoxide`, `Powerlevel10k`.
- **PHP Stack**: PHP 8.1 - 8.5 via `ondrej/php` (Ubuntu) or `sury.org` (Debian).
- **Database**: MariaDB Server + Client + Secure Installation.
- **Node.js**: NVM (Node Version Manager) + Node.js LTS.
- **Tools**: Composer Global + Laravel Installer + Valet Linux.

---

## 🖥️ Modular Structure

```text
laravel-dev-setup/
├── installer.sh            ← Professional bootstrap (curl/wget)
├── install.sh              ← Main interactive wizard
├── lib/
│   ├── ui.sh               ← Colors, banner, spinner, UI helpers
│   ├── detect.sh           ← OS, Arch, and PHP auto-detection
│   └── repo.sh             ← Automated PPA and Repository setup
└── installers/
    ├── php.sh              ← PHP core + extensions logic
    ├── node.sh             ← NVM + Node.js management
    ├── shell.sh            ← Zsh environment setup
    └── ...                 (mariadb, composer, valet)
```

---

## 🆚 Supported Systems

- **Ubuntu**: 20.04, 22.04, 24.04 (and derivatives like Mint, Pop!_OS)
- **Debian**: 11, 12 (and derivatives like Kali, Raspbian)
- **WSL/WSL2**: Fully compatible with Linux distributions on Windows.

---

## 📝 License

This project is licensed under the MIT License. Developed with ❤️ by [LC-jhony](https://github.com/LC-jhony).
