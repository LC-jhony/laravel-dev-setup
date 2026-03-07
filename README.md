# 🚀 Laravel Dev Setup — Premium Linux Orchestrator

[![Ubuntu 24.04](https://img.shields.io/badge/Ubuntu-24.04-orange?logo=ubuntu&logoColor=white)](https://ubuntu.com/)
[![WSL2 Ready](https://img.shields.io/badge/WSL2-Compatible-blue?logo=windows&logoColor=white)](https://learn.microsoft.com/en-us/windows/wsl/about)
[![PHP](https://img.shields.io/badge/PHP-8.1_--_8.4-777BB4?logo=php&logoColor=white)](https://www.php.net/)
[![Laravel](https://img.shields.io/badge/Laravel-11--12-FF2D20?logo=laravel&logoColor=white)](https://laravel.com/)

Un ecosistema modular, interactivo y de alto rendimiento diseñado para transformar una instalación limpia de **Ubuntu 24.04 (Noble Numbat) o WSL2** en una estación de trabajo Laravel de élite en minutos. Olvídate de configuraciones manuales; este asistente orquesta cada detalle con una interfaz visual de alta fidelidad basada en Python Rich.

---

## ⚡ Instalación Instantánea

No necesitas clonar nada. Ejecuta este comando en tu terminal para iniciar el despliegue:

```bash
curl -sSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/install.sh | bash
```

> **Nota de Seguridad**: El script de inicio (`install.sh`) detectará tu OS, preparará las dependencias críticas (Git, Python 3, Pip, Rich) y lanzará el orquestador principal sin interrumpir tu flujo de trabajo.

---

## 🛠️ Stack de Tecnologías Premium

Personaliza tu entorno seleccionando los componentes exactos que necesitas:

*   **💻 Shell Elite (Zsh + P10k)**: Configuración de **Zsh** optimizada con **Zinit**, **Powerlevel10k**, resaltado de sintaxis y autosugerencias inteligentes.
*   **🐘 PHP Engine Multi-Versión**: Elige entre **PHP 8.1, 8.2, 8.3 o 8.4** con todas las extensiones oficiales de Laravel (bcmath, xml, curl, sqlite3, etc.).
*   **🗄️ MariaDB Engine**: Servidor SQL de alto rendimiento con un asistente de seguridad interactivo inyectado directamente en la UI.
*   **⬢ Node.js (NVM)**: Instalación de Node.js gestionada por NVM, permitiendo seleccionar versiones LTS o versiones específicas sobre la marcha.
*   **📦 PHP Composer**: Instalación global del gestor de dependencias estándar de la industria.
*   **⚡ Laravel Valet (Linux)**: Entorno de servidor ultra-rápido con soporte automático para dominios `.test` y proxy inverso ligero.
*   **🎯 Laravel Installer**: Herramienta CLI para crear nuevos proyectos de forma instantánea.

---

## ⌨️ Control y Navegación Maestros

Nuestra interfaz visual no es solo estética; es funcional y reactiva:

| Tecla | Acción |
| :--- | :--- |
| **↑ / ↓** | Navegar entre los componentes del menú. |
| **Espacio** | Marcar o desmarcar un componente para instalar. |
| **T** | **Toggle Theme**: Alterna entre Modo Oscuro y Modo Claro instantáneamente. |
| **Enter** | Confirmar selección e iniciar el despliegue orquestado. |
| **Q** | Salir del instalador de forma segura. |
| **Ctrl + C** | Cancelación limpia con cierre de subprocesos activos. |

---

## ✨ Características de Ingeniería de Élite

### 🌓 Motor de Temas Adaptativo
Diseñado para la legibilidad absoluta. Si prefieres fondos claros o trabajas en entornos de alta iluminación, presiona **`T`** para cambiar a un tema de alta visibilidad sin reiniciar el script.

### 🔒 Inyección PTY y Seguridad Inteligente
Gracias a la tecnología de **Pseudo-Terminal (PTY)**, el orquestador puede detectar prompts de `sudo` e inyectar un modal de seguridad elegante con bordes dobles (`box.DOUBLE`). Una vez autenticado, un sistema de **Keep-Alive** mantiene la sesión sudo activa de forma segura.

### 🔍 Detección Pre-vuelo (Smart Scan)
El script escanea tu sistema antes de mostrar el menú. Si detecta que ya tienes instalado un componente (ej. Node.js v20), lo marcará con un badge verde `[v20.x]` y lo deseleccionará automáticamente para optimizar el tiempo de instalación.

### 🚀 Zero-Blocking Architecture
Todas las instalaciones de paquetes (`apt`) se ejecutan en modo no interactivo (`DEBIAN_FRONTEND=noninteractive`) mientras que los asistentes que requieren tu atención (como MariaDB o selección de Node) toman el control total de la terminal de forma transparente.

---

## 📂 Arquitectura del Proyecto

*   **`install.sh`**: El "Bootstrapper". Valida el OS, instala el entorno Python y prepara el terreno.
*   **`main.py`**: El "Cerebro". Gestiona la UI Rich, la lógica de selección y la orquestación de subprocesos mediante PTY.
*   **`lib/`**: Librerías de soporte compartidas entre Python y Bash para detección de OS y gestión de repositorios.
*   **`installers/`**: Scripts modulares de Bash que encapsulan la lógica de instalación de cada tecnología de forma aislada.

---

## 📋 Requisitos del Sistema

*   **Sistema Operativo**: Ubuntu 24.04 (Noble Numbat) o superior / WSL2 (Ubuntu 24.04).
*   **Usuario**: Privilegios de `sudo`.
*   **Conectividad**: Acceso a internet para descarga de repositorios oficiales.

---

**Desarrollado con ❤️ para el ecosistema Laravel.**
