# 🚀 Laravel Dev Setup

> Instalador interactivo para entorno de desarrollo Laravel en Linux (Ubuntu / Debian).
> Interfaz de terminal con barras de progreso, menús toggles y colores ANSI true-color.

```
██████╗ ██╗  ██╗██████╗
██╔══██╗██║  ██║██╔══██╗
██████╔╝███████║██████╔╝
██╔═══╝ ██╔══██║██╔═══╝
██║     ██║  ██║██║
╚═╝     ╚═╝  ╚═╝╚═╝
```

---

## ⚡ Instalación rápida

Elige el método que prefieras:

### 🔵 curl  *(recomendado)*
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/installer.sh)
```

### 🟠 wget
```bash
bash <(wget -qO- https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/installer.sh)
```

### curl | bash  *(one-liner)*
```bash
curl -fsSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/installer.sh | bash
```

### wget | bash  *(one-liner)*
```bash
wget -qO- https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/installer.sh | bash
```

> **Tip:** Se recomienda `bash <(...)` sobre `| bash` para instaladores interactivos,
> ya que permite leer correctamente la entrada del usuario (menús, confirmaciones, etc.).

### git clone manual
```bash
git clone https://github.com/LC-jhony/laravel-dev-setup.git
cd laravel-dev-setup
bash install.sh
```

---

## ✨ Componentes

Todos opcionales — actívalos o desactívalos desde el menú interactivo:

| # | Componente | Descripción |
|---|-----------|-------------|
| 1 | 🐚 **Shell Setup** | `git` · `unzip` · `zsh` · `zinit` · `Powerlevel10k` · `fzf` · `zoxide` |
| 2 | 🐘 **PHP** | PHP 8.1 – 8.5 via `ondrej/php` (Ubuntu) / `sury.org` (Debian) |
| 3 | 🗄️ **MariaDB** | `mariadb-server` + `mariadb-client` + `mariadb-secure-installation` |
| 4 | ⬡ **Node.js** | NVM `v0.40.4` + Node.js `24` |
| 5 | 🎼 **Composer** | Instalación global con verificación SHA-384 → `/usr/local/bin/composer` |
| 6 | 🎯 **Laravel Valet** | `cpriego/valet-linux` + `valet park ~/Sites` + `laravel/installer` |

---

## 🖥️ Flujo del instalador

```
  ┌─────────────────────────────────────────────────────┐
  │  [✔] 1.  Shell Setup    git · zsh · zinit · p10k   │
  │  [✔] 2.  PHP            8.5 / 8.4 / 8.3 …          │
  │  [✔] 3.  MariaDB        server + client             │
  │  [✔] 4.  Node.js        NVM v0.40.4 + Node 24      │
  │  [ ] 5.  Composer       getcomposer.org             │
  │  [ ] 6.  Laravel Valet  valet-linux                 │
  └─────────────────────────────────────────────────────┘
       ❯  Choice: _
```

1. **Toggle menu** — activa/desactiva componentes con los números 1-6
2. **Versión de PHP** — 8.1 / 8.2 / 8.3 / 8.4 ★ / 8.5
3. **Perfil de paquetes** — Default (15 ext.) · Minimal · Custom
4. **Resumen** — caja con todo lo seleccionado antes de proceder
5. **Instalación** — barras de progreso `████░░░ 67%` por cada paso
6. **Done** — quick reference con los comandos de cada herramienta

---

## 📦 Paquetes PHP (perfil Default)

```
php8.4  php8.4-cli    php8.4-common  php8.4-curl   php8.4-pgsql
php8.4-fpm  php8.4-gd  php8.4-imap   php8.4-intl   php8.4-mbstring
php8.4-mysql  php8.4-opcache  php8.4-soap  php8.4-xml  php8.4-zip
```

---

## 🔧 Configuración Zsh incluida (`~/.zshrc`)

- **Zinit** como gestor de plugins
- **Powerlevel10k** como tema del prompt
- Plugins: `zsh-syntax-highlighting` · `zsh-autosuggestions` · `zsh-completions` · `fzf-tab`
- Snippets OMZ: `git` · `sudo` · `laravel` · `command-not-found`
- **Zoxide** para navegación inteligente (`z` en lugar de `cd`)
- Historial de 5000 entradas con deduplicación
- PATH automático para Composer global y NVM

---

## 🗂️ Estructura del proyecto

```
laravel-dev-setup/
│
├── installer.sh            ← Bootstrap remoto (curl / wget)
├── install.sh              ← Wizard principal
│
├── lib/
│   ├── ui.sh               ← Colores, banner, spinner, menús, barras
│   ├── detect.sh           ← Detección de OS y PHP existente
│   └── repo.sh             ← Setup de repositorios PPA / sury.org
│
└── installers/
    ├── shell.sh            ← Zsh + zinit + Powerlevel10k
    ├── php.sh              ← PHP via ondrej/php
    ├── mariadb.sh          ← MariaDB server + client
    ├── node.sh             ← NVM + Node.js 24
    ├── composer.sh         ← Composer global
    └── valet.sh            ← Laravel Valet Linux
```

---

## 🌍 Uso de Valet después de instalar

```bash
cd ~/Sites
laravel new myapp      # → http://myapp.test

valet status           # Estado del servicio
valet park             # Registrar directorio actual
valet secure myapp     # Activar HTTPS local
```

---

## 🆚 Distros soportadas

| Distro | Repositorio PHP |
|--------|-----------------|
| Ubuntu 20.04 / 22.04 / 24.04 | `ondrej/php` PPA |
| Linux Mint, Pop!\_OS, Elementary, Zorin | `ondrej/php` PPA |
| Debian 11 / 12 | `sury.org` |
| Kali, Raspbian, Devuan | `sury.org` |

---

## 📝 Licencia

MIT © [LC-jhony](https://github.com/LC-jhony)
