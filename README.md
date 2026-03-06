# Laravel Dev Setup

Instalador de entorno de desarrollo Laravel para Linux usando Rich.

## Características

- Interfaz visual interactiva en terminal
- Instalación de componentes esenciales:
  - ZSH + Powerlevel10k + Plugins
  - Git
  - Unzip y herramientas básicas
  - MariaDB (Database)
  - PHP 8.4 + Extensiones
  - Composer
  - NVM + Node.js
  - Laravel Valet
  - Laravel Installer
  - ~/Sites Directory

## Requisitos

- Python 3.9+

## Instalación de dependencias

```bash
pip install rich questionary
```

## Instalación del proyecto

```bash
# Clone the repository
git clone https://github.com/LC-jhony/laravel-dev-setup.git
cd laravel-dev-setup

# Install the package
pip install -e .

# Run the installer
python3 -m installer
```

O directamente:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/install.sh)"
```

## Uso

```bash
python3 -m installer
```

## Tecnologías

- [Rich](https://rich.readthedocs.io/) - Rich terminal output
- [Questionary](https://questionary.readthedocs.io/) - Interactive prompts
- Python 3.9+

## Licencia

MIT
