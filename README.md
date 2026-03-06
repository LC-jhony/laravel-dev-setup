# Laravel Dev Setup

Instalador de entorno de desarrollo Laravel para Linux usando TUI (Textual).

## Características

- Interfaz visual interactiva
- Instalación de componentes esenciales:
  - PHP (última versión estable)
  - Composer
  - Node.js, NPM, Yarn
  - Docker
  - MySQL / MariaDB
  - Nginx
  - Laravel Installer
  - Laravel Valet
  - Git
  - Redis
- Soporte para múltiples distribuciones Linux (Ubuntu, Debian, Fedora, Arch)

## Requisitos

- Python 3.9+
```bash
 pip install textual textual[dev]
  pip install textual --break-system-packages
```
The system is using an externally-managed Python environment (Ubuntu/Debian). The safest approach is to use [pipx] or add [--break-system-packages.] Let me try [pipx] first:
- Linux
- Acceso sudo

## Instalación

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/install.sh)"
```

O clonar el repositorio:

```bash
git clone https://github.com/LC-jhony/laravel-dev-setup.git
cd laravel-dev-setup
bash install.sh
```

## Uso

```bash
python3 -m installer
```

## Tecnologías

- [Textual](https://textual.textualize.io/) - Framework TUI
- Python 3.9+

## Licencia

MIT
