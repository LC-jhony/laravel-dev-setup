# 🚀 Laravel Dev Setup — Premium Installer

Un instalador modular, interactivo y profesional diseñado para configurar un entorno completo de desarrollo Laravel en **Ubuntu, Debian y WSL2**. Olvídate de configuraciones manuales tediosas; este asistente orquesta todo el proceso con una interfaz visual de alta fidelidad.

---

## ⚡ Instalación Instantánea (Recomendado)

Copia y pega este comando en tu terminal para iniciar la configuración automática. No necesitas clonar el repositorio manualmente:

```bash
curl -sSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/install.sh | bash
```

> **Nota:** Este comando prepara automáticamente las dependencias (Python 3, Pip, Git) y lanza el asistente visual directamente en tu terminal.

---

## 🛠️ Componentes Incluidos

Elige exactamente qué quieres instalar mediante nuestro menú interactivo:

*   **💻 Shell Elite**: Zsh + Powerlevel10k + Zinit + Plugins (Autosuggestions, Syntax Highlighting).
*   **🐘 PHP Engine**: Instalación de múltiples versiones (8.1 a 8.5) con extensiones optimizadas para Laravel.
*   **🗄️ MariaDB Server**: Base de datos SQL con asistente de seguridad interactivo integrado.
*   **🟢 Node.js (NVM)**: Gestión profesional de Node.js (Versiones LTS o manuales).
*   **📦 PHP Composer**: Instalación global de la última versión estable.
*   **⚡ Laravel Valet (Linux)**: Servidor de desarrollo local ultra-rápido con dominios `.test`.
*   **🎯 Laravel Installer**: La CLI oficial para crear proyectos instantáneamente.

---

## ✨ Características Premium

*   **Interfaz Visual (Rich)**: Menús elegantes con navegación por flechas de teclado, incluso a través de instalaciones remotas.
*   **Force TTY Technology**: Hemos solucionado el error `Inappropriate ioctl for device`, garantizando que el teclado funcione siempre, sin importar cómo lances el script.
*   **Smart Sudo Handler**: Sistema de interceptación PTY que permite ingresar la contraseña de `sudo` de forma visual y moderna, con un hilo "Keep-Alive" que evita que se te vuelva a pedir durante la instalación.
*   **Detección Inteligente**: El script identifica si estás en Ubuntu o Debian y configura automáticamente los repositorios de **Ondrej Surý**.
*   **Barras de Progreso Dinámicas**: Seguimiento en tiempo real de cada paso de la instalación.

---

## 📋 Requisitos

*   **OS**: Ubuntu 22.04+, Debian 11+ o WSL2.
*   **Permisos**: Usuario con privilegios de `sudo`.
*   **Conexión**: Acceso a internet para descargar paquetes y repositorios.

---

## 📂 Ejecución Local

Si prefieres descargar el código primero:

```bash
git clone --depth 1 https://github.com/LC-jhony/laravel-dev-setup.git
cd laravel-dev-setup
bash install.sh
```

---

## 🤝 Contribuir

¿Tienes una idea para mejorar el instalador?
1. Haz un **Fork** del proyecto.
2. Crea una rama para tu mejora: `git checkout -b feature/nueva-mejora`.
3. Envía un **Pull Request**.

---

**Desarrollado para desarrolladores que valoran su tiempo.**
