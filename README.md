# 🚀 Laravel Dev Setup — Premium Installer

Un ecosistema modular, interactivo y profesional diseñado para transformar una instalación limpia de **Ubuntu 24.04+ o WSL2** en una estación de trabajo Laravel de élite en minutos. Olvídate de configuraciones manuales; este asistente orquesta cada detalle con una interfaz visual de alta fidelidad.

---

## ⚡ Instalación Relámpago

No necesitas descargar nada manualmente. Copia y pega este comando en tu terminal:

```bash
curl -sSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/install.sh | bash
```

> **¿Qué hace este comando?** Prepara tu sistema (instala Python 3, Git y la librería Rich) y lanza automáticamente el asistente visual interactivo.

---

## 🛠️ Stack Tecnológico Incluido

Elige qué componentes instalar mediante el menú interactivo:

*   **💻 Shell Elite**: Configuración de **Zsh** potenciada con **Powerlevel10k**, **Zinit** y plugins esenciales (Autosugerencias y Resaltado de Sintaxis).
*   **🐘 PHP Engine**: Soporte para múltiples versiones (**8.1 a 8.4**) con el set completo de extensiones optimizadas para Laravel.
*   **🗄️ MariaDB Database**: Servidor SQL de alto rendimiento con asistente de seguridad interactivo integrado.
*   **⬢ Node.js (NVM)**: Instalación profesional de Node.js mediante NVM, permitiendo elegir versiones LTS o específicas.
*   **📦 PHP Composer**: El gestor de dependencias estándar de la industria, instalado globalmente.
*   **⚡ Laravel Valet (Linux)**: Entorno de servidor minimalista y ultra-rápido con soporte automático para dominios `.test`.
*   **🎯 Laravel Installer**: Herramienta de línea de comandos para crear nuevos proyectos instantáneamente.

---

## ⌨️ Atajos de Teclado y Navegación

La interfaz ha sido diseñada para ser fluida e intuitiva:

| Tecla | Acción |
| :--- | :--- |
| **↑ / ↓** | Navegar entre los componentes del menú. |
| **Espacio** | Marcar o desmarcar un componente para instalar. |
| **T** | **Alternar Temas**: Cambia instantáneamente entre Modo Oscuro y Claro. |
| **Enter** | Confirmar selección e iniciar el despliegue. |
| **Q** | Salir del instalador de forma segura. |
| **Ctrl + C** | Cancelar instalación en curso (Cierre limpio de procesos). |

---

## ✨ Características Premium

### 🌓 Temas Dinámicos (Dark/Light)
Diseñado para ser legible en cualquier entorno. Si tu terminal tiene fondo claro, presiona **`T`** para activar el modo de alta visibilidad.

### 🔒 Modal de Seguridad Inteligente
No más prompts feos de `sudo` rompiendo la estética. Cuando el sistema requiera permisos, aparecerá un **Modal Centrado con bordes dobles** pidiendo tu contraseña de forma elegante. Incluye un sistema de **Keep-Alive** que mantiene la sesión activa para que solo tengas que ingresarla una vez.

### 🔍 Escaneo de Pre-vuelo
Antes de mostrarte el menú, el script escanea tu sistema. Si detecta que ya tienes un componente instalado (ej. PHP 8.2), te mostrará la versión actual en color verde y lo desmarcará automáticamente para ahorrarte tiempo.

### 🚀 Force TTY Technology
Gracias a nuestra gestión avanzada de descriptores de archivos, garantizamos que las flechas del teclado y la interactividad funcionen perfectamente, incluso si ejecutas el instalador directamente desde una URL (`curl | bash`).

---

## 📂 Estructura del Ecosistema

*   **`install.sh`**: El "Bootstrapper". Prepara el terreno y garantiza que Python tenga todo lo necesario.
*   **`main.py`**: El "Cerebro". Gestiona la UI Rich, la lógica de selección y la orquestación de subprocesos.
*   **`lib/`**: Librerías de soporte para detección de OS, gestión de repositorios y estilos visuales.
*   **`installers/`**: Scripts modulares de Bash que contienen la lógica de instalación "hardcore" de cada tecnología.

---

## 📋 Requisitos Mínimos

*   **Sistema**: **EXCLUSIVAMENTE Ubuntu 24.04+** o WSL2 (basado en Ubuntu 24.04).
*   **Usuario**: Debe tener privilegios de `sudo`.
*   **Internet**: Conexión activa para la descarga de paquetes oficiales.

---

## 🤝 Contribuciones y Soporte

¿Encontraste un bug o tienes una idea "Nivel 100"?
1. Haz un **Fork** del repositorio.
2. Crea una rama: `git checkout -b mejora/increible`.
3. Envía un **Pull Request**.

---

**Desarrollado con ❤️ por y para desarrolladores de Laravel.**
