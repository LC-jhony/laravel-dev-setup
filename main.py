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
CURRENT_PROCESS = None # Para rastrear y matar procesos activos

def graceful_exit(sig, frame):
    """Manejador global para Ctrl+C."""
    global CURRENT_PROCESS
    if CURRENT_PROCESS:
        try:
            os.killpg(os.getpgid(CURRENT_PROCESS.pid), signal.SIGTERM)
        except:
            pass
    
    theme = get_theme()
    console.print(f"\n\n [bold {theme['error']}]⚠ INSTALACIÓN INTERRUMPIDA POR EL USUARIO[/]\n")
    sys.exit(130)

signal.signal(signal.SIGINT, graceful_exit)

THEMES = {
    "dark": {
        "primary": "cyan", "secondary": "blue", "text": "white", "highlight": "bold white",
        "dim": "dim", "success": "green", "error": "red", "border": "dim #333333", "modal_border": "bright_yellow"
    },
    "light": {
        "primary": "blue", "secondary": "magenta", "text": "grey15", "highlight": "bold black",
        "dim": "grey37", "success": "dark_green", "error": "dark_red", "border": "grey70", "modal_border": "blue"
    }
}

current_theme_key = "dark"
def get_theme(): return THEMES[current_theme_key]

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

def modern_modal_password():
    theme = get_theme()
    console.clear()
    content = Group(Text("\nAcceso Administrativo Requerido", style=f"bold {theme['text']}"), Text("\nSe requieren permisos de sudo para este componente.", style=theme['dim']))
    panel = Panel(Align.center(content, vertical="middle"), title=f"[bold yellow] 🔐 SECURITY CHECK ", border_style=theme['modal_border'], padding=(2, 4), box=box.DOUBLE)
    console.print("\n" * (max(0, console.height // 4)), Align.center(panel))
    pwd = Prompt.ask(f" [bold {theme['primary']}]Contraseña de sistema[/]", password=True)
    proc = subprocess.Popen(["sudo", "-S", "-v"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.communicate(input=f"{pwd}\n".encode())
    if proc.returncode == 0:
        global KEEPALIVE_STARTED
        if not KEEPALIVE_STARTED:
            KEEPALIVE_STARTED = True
            def keep_alive():
                while True: subprocess.run(["sudo", "-n", "true"], check=False, stderr=subprocess.DEVNULL); time.sleep(60)
            t = threading.Thread(target=keep_alive, daemon=True); t.start()
        return pwd
    return modern_modal_password()

# ─────────────────────────────────────────────────────────────
#   Orquestador
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
    env = os.environ.copy(); env["PYTHONIOENCODING"], env["LARAVEL_SETUP_RICH"] = "utf-8", "1"
    
    # Usamos setsid para crear un nuevo grupo de procesos y poder matarlos a todos si se cancela
    process = subprocess.Popen(["bash", "-c", full_cmd], stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, close_fds=True, env=env, preexec_fn=os.setsid)
    CURRENT_PROCESS = process
    os.close(slave_fd); buffer = ""
    
    while True:
        try:
            r, _, _ = select.select([master_fd], [], [], 0.1)
            if master_fd in r:
                data = os.read(master_fd, 1024)
                if not data: break
                chunk = data.decode('utf-8', errors='replace'); buffer += chunk
                if "password for" in buffer.lower() and ":" in buffer:
                    if progress: progress.stop()
                    CACHED_PASSWORD = CACHED_PASSWORD or modern_modal_password()
                    os.write(master_fd, (CACHED_PASSWORD + "\n").encode()); buffer = ""
                    if progress: progress.start()
                elif "\n" in buffer:
                    lines = buffer.split("\n")
                    for line in lines[:-1]:
                        clean = line.strip()
                        if clean and "password for" not in clean.lower():
                            if progress: progress.console.print(f"  [{theme['dim']}]│[/] {clean}")
                    buffer = lines[-1]
            if process.poll() is not None and not r: break
        except: break
    
    process.wait()
    CURRENT_PROCESS = None
    return process.returncode == 0

# ─────────────────────────────────────────────────────────────
#   Main Flow
# ─────────────────────────────────────────────────────────────

def get_header(title="LARAVEL DEV SETUP", sub="PREMIUM BOOTSTRAPPER"):
    theme = get_theme()
    mode = "🌓 DARK" if current_theme_key == "dark" else "☀️ LIGHT"
    return Group(Text("\n"), Align.right(Text(f"{mode}  ", style=f"{theme['dim']} italic")), Align.center(Text(title, style=f"bold {theme['primary']} tracking5")), Align.center(Text(sub, style=f"{theme['dim']} italic")), Text("\n"), Rule(style=theme['border']))

def getch():
    import tty, termios
    fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
    try: tty.setraw(fd); ch = sys.stdin.read(1)
    finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

def main():
    global current_theme_key
    console.clear(); console.print(get_header())
    with console.status(" [bold]Escaneando sistema...[/]"): installed_info = detect_installed(); time.sleep(0.5)

    idx = 0; states = {c['id']: (not installed_info[c['id']]) for c in COMPONENTS}
    while True:
        theme = get_theme()
        console.clear(); console.print(get_header("MENU DE SELECCIÓN", "↑↓ Nav · Espacio Marcar · T Tema · Enter Confirmar"))
        for i, c in enumerate(COMPONENTS):
            active = (i == idx); mark = f" [bold {theme['primary']}]●[/] " if states[c['id']] else f" [{theme['dim']}]○[/] "
            style = theme['highlight'] if active else (theme['text'] if states[c['id']] else theme['dim'])
            tag = f" [{theme['success']}][v{installed_info[c['id']]}] [/]" if installed_info[c['id']] else ""
            line = Text(); line.append("  ┃ " if active else "    ", style=theme['primary']); line.append(Text.from_markup(mark))
            line.append(f"{c['name']:<22}", style=style); line.append(Text.from_markup(tag))
            line.append(" ➜ ", style=theme['dim']); line.append(f"{c['icon']} ", style="default"); line.append(f"{c['desc']}", style=f"{theme['dim']} italic")
            console.print(line)
        key = getch()
        if key == '\x1b':
            r = sys.stdin.read(2)
            if r == '[A': idx = (idx - 1) % len(COMPONENTS)
            elif r == '[B': idx = (idx + 1) % len(COMPONENTS)
        elif key == ' ': states[COMPONENTS[idx]['id']] = not states[COMPONENTS[idx]['id']]
        elif key.lower() == 't': current_theme_key = "light" if current_theme_key == "dark" else "dark"
        elif key in ('\r', '\n'): break
        elif key.lower() == 'q': sys.exit(0)

    selected_ids = [c['id'] for c in COMPONENTS if states[c['id']]]
    if not selected_ids: return

    theme = get_theme(); selected_php = "8.4"
    if states['php']:
        v_opts = ["8.4", "8.3", "8.2", "8.1"]; v_idx = 0
        while True:
            console.clear(); console.print(get_header("PHP ENGINE", "Selecciona versión"))
            for i, v in enumerate(v_opts):
                active = (i == v_idx); console.print(Text(f"  {' ➜ ' if active else '   '} PHP {v} {'(Recomendado)' if v=='8.4' else ''}", style=f"bold {theme['primary']}" if active else theme['text']))
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
            if sid == 'node':
                progress.stop(); console.print("\n"); node_v = Prompt.ask(f"  [bold {theme['primary']}]?[/] [white]Versión de Node.js[/]", default="lts"); args = [node_v]; progress.start()
            task = progress.add_task(f"Instalando {c['name']}...", total=None)
            if run_bash_cmd(sid, args, progress):
                progress.update(task, description=f"[{theme['success']}]✓ {c['name']} Listo", completed=100, total=100); progress.advance(overall)
            else:
                progress.update(task, description=f"[{theme['error']}]✗ {c['name']} Falló"); sys.exit(1)

    theme = get_theme(); console.clear(); panel = Panel(Align.center(Group(Text("\n✨ DESPLIEGUE COMPLETADO ✨", style=f"bold {theme['success']}"), Text("\nTu entorno Laravel ha sido optimizado profesionalmente.", style=theme['text']))), border_style=theme['success'], box=box.DOUBLE, padding=(1, 4))
    console.print("\n" * (console.height // 4), Align.center(panel))

if __name__ == "__main__":
    main()
