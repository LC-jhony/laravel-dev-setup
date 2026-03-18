import os
import sys
import subprocess
import time
import re
import threading
import pty
import select
import shutil
import signal
import termios
import tty
from rich.console import Console, Group
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeElapsedColumn
from rich.table import Table
from rich import box

# ─────────────────────────────────────────────────────────────
#   Configuración Global y Señales
# ─────────────────────────────────────────────────────────────

console = Console()
CACHED_PASSWORD = None
KEEPALIVE_STARTED = False
CURRENT_PROCESS = None

def graceful_exit(sig, frame):
    global CURRENT_PROCESS
    if CURRENT_PROCESS:
        try: os.killpg(os.getpgid(CURRENT_PROCESS.pid), signal.SIGTERM)
        except: pass
    console.print("\n\n [bold red]◆ INSTALACIÓN INTERRUMPIDA[/]\n")
    sys.exit(130)

signal.signal(signal.SIGINT, graceful_exit)

THEMES = {
    "primary": "#ff3366",      # Rosa/Vermellón vibrante
    "secondary": "#3498db",    # Azul brillante
    "text": "#ecf0f1",         # Blanco humo
    "highlight": "bold #f1c40f", # Amarillo dorado
    "dim": "dim", 
    "success": "#2ecc71",      # Verde esmeralda
    "error": "#e74c3c",        # Rojo carmesí
    "warning": "#f39c12",      # Naranja ámbar
    "border": "#9b59b6",       # Púrpura vibrante
    "info": "#1abc9c"          # Turquesa
}

def get_theme(): return THEMES

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "icon": ">_", "desc": "Zsh + P10k + Modern CLI Tools", "bin": "zsh"},
    {"id": "php",      "name": "PHP Engine",        "icon": "🐘", "desc": "Engine + Laravel Extensions", "bin": "php"},
    {"id": "mariadb",  "name": "MariaDB Database",  "icon": "🗄️", "desc": "SQL Server + Security", "bin": "mariadb"},
    {"id": "node",     "name": "Node.js (NVM)",     "icon": "⬢", "desc": "JS Runtime & Package Manager", "bin": "node"},
    {"id": "composer", "name": "PHP Composer",      "icon": "📦", "desc": "Global Dependencies", "bin": "composer"},
    {"id": "valet",    "name": "Laravel Valet",     "icon": "⚡", "desc": "Local Dev Server (.test)", "bin": "valet"},
]

# ─────────────────────────────────────────────────────────────
#   Motor de Detección y Seguridad
# ─────────────────────────────────────────────────────────────

def detect_installed():
    info = {}
    for c in COMPONENTS:
        is_installed = False; ver = None
        if shutil.which(c['bin']):
            is_installed = True
            try:
                if c['id'] == 'php': cmd = "php -r 'echo PHP_MAJOR_VERSION.\".\".PHP_MINOR_VERSION;'"
                elif c['id'] == 'node': cmd = "node -v"
                elif c['id'] == 'composer': cmd = "composer --version | awk '{print $3}'"
                else: cmd = f"{c['bin']} --version"
                ver = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip().lstrip('v').split()[0]
            except: ver = "Presente"
        if c['id'] == 'node' and not is_installed and os.path.exists(os.path.expanduser("~/.nvm")):
            is_installed = True; ver = "NVM"
        info[c['id']] = ver if is_installed else None
    return info

def get_masked_input() -> str:
    """Lee entrada del usuario mostrando asteriscos, sin prompt interno."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        password = []
        while True:
            ch = sys.stdin.read(1)
            if ch == '\r' or ch == '\n':  # Enter
                print()  # Nueva línea
                break
            elif ch == '\x7f' or ch == '\x08':  # Backspace
                if password:
                    password.pop()
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif ch.isprintable():
                password.append(ch)
                sys.stdout.write('*')
                sys.stdout.flush()
            # Ignorar otros caracteres (escape, etc.)
        return "".join(password)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def modern_modal_password():
    theme = get_theme()
    max_attempts = 3
    error_message = ""
    
    for attempt in range(max_attempts):
        console.clear()
        
        # Mostrar mensaje de error si existe (con espacio mínimo)
        if error_message:
            error_text = Text(f"◆ {error_message}", style=f"bold {theme['error']}", justify="center")
            console.print(Align.center(error_text))
            console.print() # Una línea de espacio
        
        # Imprimir prompt estilizado y pedir contraseña con asteriscos
        console.print(f"[bold {theme['primary']}]Contraseña de sistema[/]: ", end='')
        pwd = get_masked_input()
        
        # Validar con sudo
        proc = subprocess.Popen(["sudo", "-S", "-v"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.communicate(input=f"{pwd}\n".encode())
        
        if proc.returncode == 0:
            # Iniciar keep-alive si es la primera vez
            global KEEPALIVE_STARTED
            if not KEEPALIVE_STARTED:
                KEEPALIVE_STARTED = True
                def keep_alive():
                    while True: 
                        subprocess.run(["sudo", "-n", "true"], check=False, stderr=subprocess.DEVNULL)
                        time.sleep(60)
                threading.Thread(target=keep_alive, daemon=True).start()
            
            # Guardar en caché y retornar
            global CACHED_PASSWORD
            CACHED_PASSWORD = pwd
            return pwd
        else:
            # Preparar mensaje de error para el siguiente intento
            intentos_restantes = max_attempts - attempt - 1
            if intentos_restantes > 0:
                error_message = f"Contraseña incorrecta. Intentos restantes: {intentos_restantes}"
            else:
                error_message = "Intentos agotados. Reintentando..."
    
    # Si se agotan todos los intentos, reiniciar el proceso
    return modern_modal_password()

# ─────────────────────────────────────────────────────────────
#   Orquestador de Ejecución
# ─────────────────────────────────────────────────────────────

def run_bash_cmd(script_id, extra_args=None, progress=None):
    global CACHED_PASSWORD, CURRENT_PROCESS
    theme = get_theme()
    cmd_parts = ["export SUDO=sudo", "source lib/ui.sh", "source lib/detect.sh", "source lib/repo.sh", f"source installers/{script_id}.sh", "detect_os"]
    if script_id == "php":
        v = extra_args[0] if extra_args else "8.4"
        cmd_parts += ["setup_repo", f"install_php {v}", f"set_default_php {v}"]
    else:
        call = f"install_{script_id}"
        if extra_args: call += f" {' '.join(extra_args)}"
        cmd_parts.append(call)
    
    full_cmd = " && ".join(cmd_parts)
    master_fd, slave_fd = pty.openpty()
    env = os.environ.copy()
    env["PYTHONIOENCODING"], env["LARAVEL_SETUP_RICH"] = "utf-8", "1"
    
    is_interactive = (progress is None)
    env["DEBIAN_FRONTEND"] = "interactive" if is_interactive else "noninteractive"

    process = subprocess.Popen(["bash", "-c", full_cmd], stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, close_fds=True, env=env, preexec_fn=os.setsid)
    CURRENT_PROCESS = process
    os.close(slave_fd)
    buffer = ""
    
    old_settings = None
    if is_interactive:
        try:
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except: pass

    try:
        while True:
            inputs = [master_fd]
            if is_interactive: inputs.append(sys.stdin)
            
            r, _, _ = select.select(inputs, [], [], 0.1)
            
            if master_fd in r:
                try:
                    data = os.read(master_fd, 1024)
                except OSError: break
                if not data: break
                
                chunk = data.decode('utf-8', errors='replace')
                buffer += chunk
                
                # Inyección automática de contraseña (SUDO)
                if "password for" in buffer.lower() and ":" in buffer:
                    if not is_interactive: progress.stop()
                    else: 
                        if old_settings: termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                    
                    CACHED_PASSWORD = CACHED_PASSWORD or modern_modal_password()
                    os.write(master_fd, (CACHED_PASSWORD + "\n").encode())
                    buffer = ""
                    
                    if not is_interactive: progress.start()
                    else:
                        if old_settings: tty.setcbreak(sys.stdin.fileno())
                
                else:
                    if is_interactive:
                        # Modo interactivo: volcar todo al instante
                        sys.stdout.write(buffer)
                        sys.stdout.flush()
                        buffer = ""
                    else:
                        # Modo progreso: procesar por líneas para la UI de Rich
                        if "\n" in buffer:
                            lines = buffer.split("\n")
                            for line in lines[:-1]:
                                clean = line.strip()
                                if clean and "password for" not in clean.lower():
                                    progress.console.print(f"  [{theme['dim']}]│[/] {clean}")
                            buffer = lines[-1]

            if is_interactive and sys.stdin in r:
                try:
                    input_data = os.read(sys.stdin.fileno(), 1024)
                    if input_data:
                        os.write(master_fd, input_data)
                except EOFError: pass

            if process.poll() is not None:
                # Volcado final
                if is_interactive and buffer:
                    sys.stdout.write(buffer); sys.stdout.flush()
                break
    except Exception: pass
    finally:
        if is_interactive and old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    process.wait()
    CURRENT_PROCESS = None
    return process.returncode == 0

# ─────────────────────────────────────────────────────────────
#   Flujo Principal
# ─────────────────────────────────────────────────────────────

def get_header(title="Laravel Dev Tools", sub="Development environment installer"):
    theme = get_theme()
    
    # Crear el texto del encabezado
    header_text = Text()
    
    # Título principal con colores alternados
    header_text.append("\n")
    header_text.append("  ◆ ", style=f"bold {theme['border']}")
    header_text.append(f"{title}", style=f"bold {theme['primary']}")
    header_text.append(" ◆  ", style=f"bold {theme['border']}")
    header_text.append("\n")
    
    # Subtítulo con estilo más destacado
    header_text.append(f"  {sub}\n", style=f"bold {theme['secondary']}")
    
    # Info del sistema con icono
    sys_info = "◆ Ubuntu 24.04 | x86_64"
    header_text.append(f"\n  {sys_info}", style=f"dim {theme['text']}")
    
    header_text.justify = "center"
    
    # Panel con borde colorido
    return Panel(
        header_text,
        border_style=theme['border'],
        box=box.ROUNDED,
        padding=(1, 2),
    )

def getch():
    import tty, termios
    # Verificar si stdin es un terminal interactivo
    if not sys.stdin.isatty():
        # Fallback para entornos no interactivos
        try:
            line = input()
            return line[0] if line else '\n'
        except (EOFError, KeyboardInterrupt):
            return 'q'
    
    try:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except (AttributeError, OSError, ValueError, termios.error):
        # Fallback para entornos sin soporte para modo raw
        try:
            line = input()
            return line[0] if line else '\n'
        except (EOFError, KeyboardInterrupt):
            return 'q'

def main():
    theme = get_theme()
    console.clear(); console.print(get_header())
    with console.status(" [bold]Escaneando sistema...[/]"): installed_info = detect_installed(); time.sleep(0.5)

    # UI de Entorno Optimizado
    missing = [c for c in COMPONENTS if not installed_info[c['id']]]
    if not missing:
        # Crear texto con componentes y versiones
        components_text = Text()
        components_text.append("\n", style=theme['text'])
        for c in COMPONENTS:
            version = installed_info[c['id']]
            if version:
                components_text.append(f"  ◆ {c['name']:<20}", style=theme['primary'])
                components_text.append(f"  v{version}\n", style=theme['success'])
            else:
                components_text.append(f"  ◆ {c['name']:<20}", style=theme['primary'])
                components_text.append(f"  —\n", style=theme['dim'])
        
        # Panel colorido con diseño mejorado
        panel = Panel(
            Align.center(Group(
                Text("\n◆ ENTORNO OPTIMIZADO ◆\n", style=f"bold {theme['success']}"),
                components_text,
                Text("\nTu sistema ya está completamente configurado.\n¿Deseas entrar al menú de todos modos?", justify="center", style=theme['text'])
            )),
            border_style=theme['border'],
            box=box.ROUNDED,
            padding=(1, 2),
            subtitle=f"[{theme['success']}]✓ Listo[/]",
        )
        
        console.print("\n", Align.center(panel))
        
        # Navegación colorida
        nav_text = Text()
        nav_text.append("\n  [", style=theme['text'])
        nav_text.append("ENTER", style=f"bold {theme['primary']}")
        nav_text.append("] ", style=theme['text'])
        nav_text.append("Menú    [", style=theme['text'])
        nav_text.append("Q", style=f"bold {theme['error']}")
        nav_text.append("] ", style=theme['text'])
        nav_text.append("Salir", style=theme['text'])
        console.print(Align.center(nav_text))
        
        # Leer tecla directamente con getch()
        try:
            choice = getch().lower()
            # Si la tecla es 'q' (o 'Q'), salir del instalador
            if choice == 'q': 
                console.print(f"\n[bold red]Saliendo del instalador...[/]")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            # Si hay error de entrada o interrupción, continuar al menú
            pass

    # Selección colorida con diseño mejorado
    idx = 0; states = {c['id']: (not installed_info[c['id']]) for c in COMPONENTS}
    while True:
        theme = get_theme()
        console.clear(); console.print(get_header("SELECCIÓN DE COMPONENTES", "↑↓ Navegar · Espacio Marcar · Enter Confirmar"))
        console.print()
        
        for i, c in enumerate(COMPONENTS):
            active = (i == idx)
            
            # Determinar colores según estado
            if active:
                # Elemento ACTIVO - colorido con indicador
                marker = "►"
                marker_style = f"bold {theme['primary']}"
                name_style = f"bold {theme['highlight']}"
                desc_style = f"italic {theme['text']}"
            else:
                # Elemento inactivo
                marker = " "
                marker_style = theme['dim']
                name_style = theme['dim']
                desc_style = f"italic {theme['dim']}"
            
            # Crear línea de componente
            line = Text()
            
            # Indicador de selección
            line.append(f"  {marker} ", style=marker_style)
            
            # Nombre del componente
            line.append(f"{c['name']:<22}", style=name_style)
            
            # Versión instalada
            if states[c['id']]:
                # Marcado para instalar - color verde brillante
                icon_version = f"{c['icon']} {installed_info[c['id']] if installed_info[c['id']] else '✓'}"
                line.append(f" {icon_version}  ", style=theme['success'])
            elif installed_info[c['id']]:
                # Ya instalado - color turquesa
                icon_version = f"{c['icon']} {installed_info[c['id']]}"
                line.append(f" {icon_version}  ", style=theme['info'])
            else:
                # No instalado - color dim
                line.append(f" {c['icon']} —  ", style=theme['dim'])
            
            # Descripción
            line.append(f"  {c['desc']}", style=desc_style)
            
            console.print(line)
        
        # Pie de página con información de navegación
        console.print()
        console.print(f"  [bold {theme['primary']}]●[/] [dim]Seleccionado[/]  [bold {theme['success']}]✓[/] [dim]Instalar[/]  [bold {theme['info']}]◆[/] [dim]Instalado[/]")
        key = getch()
        if key == '\x1b':
            r = sys.stdin.read(2)
            if r == '[A': idx = (idx - 1) % len(COMPONENTS)
            elif r == '[B': idx = (idx + 1) % len(COMPONENTS)
        elif key == ' ': states[COMPONENTS[idx]['id']] = not states[COMPONENTS[idx]['id']]
        elif key in ('\r', '\n'): break
        elif key.lower() == 'q': 
            console.print(f"\n[bold red]Saliendo del instalador...[/]")
            sys.exit(0)
        # Si se presiona cualquier otra tecla, continuar en el menú

    selected_ids = [c['id'] for c in COMPONENTS if states[c['id']]]
    if not selected_ids: return

    selected_php = "8.4"
    if states['php']:
        v_opts = ["8.4", "8.3", "8.2", "8.1"]; v_idx = 0
        while True:
            console.clear(); console.print(get_header("SELECCIÓN PHP", "Selecciona versión"))
            for i, v in enumerate(v_opts):
                active = (i == v_idx)
                if active:
                    prefix = "▸ "
                    style = f"bold {theme['primary']}"
                else:
                    prefix = "  "
                    style = theme['text']
                
                line = Text()
                line.append(prefix, style=theme['primary'])
                line.append(f"PHP {v}", style=style)
                if v == '8.4':
                    line.append("  (Recomendado)", style=f"dim {theme['success']}")
                console.print(line)
            
            k = getch()
            if k == '\x1b':
                r = sys.stdin.read(2)
                if r == '[A': v_idx = (v_idx - 1) % len(v_opts)
                elif r == '[B': v_idx = (v_idx + 1) % len(v_opts)
            elif k in ('\r', '\n'): selected_php = v_opts[v_idx]; break

    console.clear(); console.print(get_header("DESPLIEGUE EN CURSO"))
    theme = get_theme()
    with Progress(SpinnerColumn(), TextColumn(f"[bold {theme['primary']}]" + "{task.description}"), BarColumn(bar_width=40, style=theme['dim'], complete_style=theme['primary']), TextColumn(f"[bold {theme['text']}]" + "{task.percentage:>3.0f}%"), TimeElapsedColumn(), console=console, transient=False) as progress:
        overall = progress.add_task("Total", total=len(selected_ids))
        for sid in selected_ids:
            c = next(comp for comp in COMPONENTS if comp['id'] == sid); args = [selected_php] if sid == 'php' else []
            
            # EXCEPCIÓN DE INTERACTIVIDAD PARA MARIADB
            if sid == 'mariadb':
                progress.stop()
                console.print(f"\n  [bold {theme['primary']}]◆[/] [white]Iniciando configuración de MariaDB (Interactiva)...[/]")
                if run_bash_cmd(sid, args, None): # None = modo interactivo total
                    progress.advance(overall); progress.start()
                else: sys.exit(1)
            else:
                if sid == 'node':
                    progress.stop(); console.print("\n"); node_v = Prompt.ask(f"  [bold {theme['primary']}]?[/] [white]Versión de Node.js[/]", default="lts"); args = [node_v]; progress.start()
                task = progress.add_task(f"Instalando {c['name']}...", total=None)
                if run_bash_cmd(sid, args, progress):
                    progress.update(task, description=f"[{theme['success']}]◆ {c['name']} Listo", completed=100, total=100); progress.advance(overall)
                else:
                    progress.update(task, description=f"[{theme['error']}]✗ {c['name']} Falló"); sys.exit(1)

    console.clear()
    
    # Crear mensaje colorido con diseño mejorado
    msg_text = Text()
    msg_text.append("\n", style=theme['text'])
    msg_text.append("    ✦ ✦ ✦\n", style=f"bold {theme['border']}")
    msg_text.append("  ◆ DESPLIEGUE COMPLETADO ◆\n", style=f"bold {theme['success']}")
    msg_text.append("    ✦ ✦ ✦\n\n", style=f"bold {theme['border']}")
    msg_text.append("  Tu entorno Laravel ha sido optimizado profesionalmente.\n", style=f"{theme['text']}")
    msg_text.append("\n", style=theme['text'])
    
    # Panel colorido con borde púrpura
    panel = Panel(
        Align.center(msg_text),
        border_style=theme['border'],
        box=box.ROUNDED,
        padding=(1, 3),
        subtitle=f"[{theme['success']}]✓ Listo[/]",
    )
    
    console.print("\n" * (console.height // 4), Align.center(panel))
    console.print(f"\n[dim]Presiona cualquier tecla para continuar...[/]")

if __name__ == "__main__":
    main()
