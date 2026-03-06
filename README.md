# 🚀 Laravel Dev Setup

> Instalador interactivo para entorno de desarrollo Laravel en Linux (Ubuntu / Debian)
> con una interfaz de terminal polida — barras de progreso, menús con toggles y colores ANSI.

```
██████╗ ██╗  ██╗██████╗
██╔══██╗██║  ██║██╔══██╗
██████╔╝███████║██████╔╝
██╔═══╝ ██╔══██║██╔═══╝
██║     ██║  ██║██║
╚═╝     ╚═╝  ╚═╝╚═╝
Linux Dev Environment Installer — v1.2.0
```

---

## ✨ Componentes

| # | Componente | Descripción |
|---|-----------|-------------|
| 1 | **Shell Setup** | `git` · `unzip` · `zsh` · `zinit` · `Powerlevel10k` · `fzf` · `zoxide` |
| 2 | **PHP** | PHP 8.1 – 8.5 via repositorio `ondrej/php` (Ubuntu) / `sury.org` (Debian) |
| 3 | **MariaDB** | `mariadb-server` + `mariadb-client` + `mariadb-secure-installation` |
| 4 | **Node.js** | NVM `v0.40.4` + Node.js `24` (configurable) |
| 5 | **Composer** | Instalación global con verificación SHA-384 → `/usr/local/bin/composer` |
| 6 | **Laravel Valet** | `cpriego/valet-linux` + `valet park ~/Sites` + `laravel/installer` |

Cada componente es **opcional** — puedes activar/desactivar los que necesites desde el menú de toggles.

---

## 📦 Requisitos

- Ubuntu 20.04 / 22.04 / 24.04 o Debian 11 / 12
- `bash` 4+
- `curl`
- Acceso `sudo` (o ejecutar como root)

---

## ⚡ Instalación rápida

```bash
git clone https://github.com/LC-jhony/laravel-dev-setup.git
cd laravel-dev-setup
bash install.sh
```

O en una sola línea:

```bash
git clone https://github.com/LC-jhony/laravel-dev-setup.git && cd laravel-dev-setup && bash install.sh
```

---

## 🗂️ Estructura del proyecto

```
laravel-dev-setup/
│
├── install.sh              ← Punto de entrada principal
│
├── lib/                    ← Helpers reutilizables (no instalan nada)
│   ├── ui.sh               ← Colores, banner, spinner, menús, barras
│   ├── detect.sh           ← Detección de OS y PHP existente
│   └── repo.sh             ← Setup de repositorios PPA / sury.org
│
└── installers/             ← Cada archivo instala un componente
    ├── shell.sh            ← Zsh + zinit + Powerlevel10k
    ├── php.sh              ← PHP via ondrej/php
    ├── mariadb.sh          ← MariaDB server + client
    ├── node.sh             ← NVM + Node.js 24
    ├── composer.sh         ← Composer global
    └── valet.sh            ← Laravel Valet Linux
```

---

## 🖥️ Flujo del instalador

```
┌─────────────────────────────────────────┐
│  1. Menú de componentes (toggles)       │  ← Activa/desactiva con 1-6
│  2. Versión de PHP                      │  ← Solo si PHP está activo
│  3. Perfil de paquetes PHP              │  ← Default / Minimal / Custom
│  4. Resumen de instalación             │  ← Confirmación antes de instalar
│  5. Instalación con barras de progreso  │  ← Cada paso muestra █████ 100%
│  6. Pantalla de finalización            │  ← Quick reference de comandos
└─────────────────────────────────────────┘
```

---

## 📦 Paquetes PHP (perfil Default)

```
php8.4  php8.4-cli    php8.4-common  php8.4-curl   php8.4-pgsql
php8.4-fpm  php8.4-gd  php8.4-imap   php8.4-intl   php8.4-mbstring
php8.4-mysql  php8.4-opcache  php8.4-soap  php8.4-xml  php8.4-zip
```

---

## 🔧 Configuración Zsh incluida

El instalador escribe un `~/.zshrc` completo con:

- **Zinit** como gestor de plugins
- **Powerlevel10k** como tema del prompt
- Plugins: `zsh-syntax-highlighting` · `zsh-autosuggestions` · `zsh-completions` · `fzf-tab`
- Snippets OMZ: `git` · `sudo` · `laravel` · `command-not-found`
- **Zoxide** (navegación inteligente de directorios)
- Historial de 5000 entradas con deduplicación
- PATH automático para Composer global y NVM

---

## 🌐 Uso de Valet después de instalar

```bash
# Los sitios en ~/Sites se sirven automáticamente como <nombre>.test
cd ~/Sites
laravel new myapp      # → http://myapp.test

# Comandos útiles
valet status           # Estado del servicio
valet park             # Registrar directorio actual
valet link myapp       # Enlazar directorio arbitrario
valet secure myapp     # HTTPS local
```

---

## 🆚 Distribuciones soportadas

| Distro | Codename | Repositorio PHP |
|--------|----------|-----------------|
| Ubuntu 20.04 | focal | ondrej/php PPA |
| Ubuntu 22.04 | jammy | ondrej/php PPA |
| Ubuntu 24.04 | noble | ondrej/php PPA |
| Linux Mint, Pop!_OS, Elementary | — | ondrej/php PPA |
| Debian 11 | bullseye | sury.org |
| Debian 12 | bookworm | sury.org |
| Kali, Raspbian, Devuan | — | sury.org |

---

## 📝 Licencia

MIT © [LC-jhony](https://github.com/LC-jhony)
