# 🚀 Laravel Dev Setup — Premium Installer

Un instalador modular y profesional diseñado para configurar un entorno completo de desarrollo Laravel en **Ubuntu, Debian y WSL**. Olvídate de configurar manualmente PHP, bases de datos o servidores locales; este asistente lo hace todo por ti con una interfaz visual elegante.

---

## 🛠️ Componentes Incluidos

El asistente te permite seleccionar e instalar los siguientes componentes:

*   **💻 Shell Environment**: Zsh + Powerlevel10k + Zinit + Plugins (Autocompletado y resaltado de sintaxis).
*   **🐘 PHP Engine**: Soporte para múltiples versiones (8.1 a 8.5) con todas las extensiones necesarias para Laravel.
*   **🗄️ MariaDB Database**: Servidor SQL con asistente de seguridad interactivo.
*   **🟢 Node.js (NVM)**: Gestión de versiones de Node.js mediante NVM (Instalación manual o LTS).
*   **📦 PHP Composer**: Gestor de dependencias global para PHP.
*   **⚡ Laravel Valet (Linux)**: Servidor de desarrollo local elite con soporte para dominios `.test` automáticos.
*   **🎯 Laravel Installer**: Instalación global de la CLI de Laravel.

---

## 🚀 Cómo Empezar

### Instalación Rápida (Recomendado)
Puedes ejecutar el instalador directamente desde GitHub con el siguiente comando:

```bash
curl -sSL https://raw.githubusercontent.com/LC-jhony/laravel-dev-setup/main/install.sh | bash
```

### Ejecución Local
Si ya has clonado el repositorio, puedes iniciar el asistente directamente:

```bash
# Método 1: Usando el bootstrap de Bash
bash install.sh

# Método 2: Ejecutando el asistente visual de Python directamente
python3 main.py
```

---

## ✨ Características Premium

*   **Interfaz Visual (Rich)**: Menús interactivos con navegación mediante flechas de teclado.
*   **Escalación de Privilegios Segura**: Formulario moderno para contraseña de `sudo` con sistema de refresco automático (Keep-Alive) para evitar interrupciones.
*   **Barras de Progreso**: Visualización en tiempo real del avance general e individual de cada componente.
*   **Detección Inteligente**: Identifica automáticamente tu distribución (Ubuntu/Debian) y configura los repositorios adecuados (Ondrej/Sury).
*   **Modo Interactivo**: Pausa automáticamente la interfaz para configuraciones críticas como la seguridad de MariaDB o la selección manual de versiones.

---

## 📋 Requisitos Previos

*   **Sistema Operativo**: Ubuntu 22.04+, Debian 11+ o WSL2.
*   **Privilegios**: Acceso a `sudo`.
*   **Dependencias**: `curl` y `git` (el script `install.sh` las instalará automáticamente si faltan).

---

## 📂 Estructura del Proyecto

*   `install.sh`: Script de arranque (bootstrap) que prepara el entorno.
*   `main.py`: El corazón del instalador (interfaz visual y lógica de orquestación).
*   `lib/`: Scripts de ayuda para UI, detección de OS y gestión de repositorios.
*   `installers/`: Scripts individuales para cada componente tecnológico.

---

## 🤝 Contribuciones

Si encuentras algún error o tienes una sugerencia de mejora, siéntete libre de abrir un **Issue** o enviar un **Pull Request**.

---

**Desarrollado con ❤️ para la comunidad de Laravel.**
