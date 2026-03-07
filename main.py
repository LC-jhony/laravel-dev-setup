import os
import sys
import subprocess
import time
import re
import threading
import pty
import select
import shutil
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
#   Configuración Global
# ─────────────────────────────────────────────────────────────

console = Console()
CACHED_PASSWORD = None
KEEPALIVE_STARTED = False

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "icon": "[bold white]>_[/]", "desc": "Zsh + P10k + Modern CLI Tools", "bin": "zsh"},
    {"id": "php",      "name": "PHP Engine",        "icon": "[bold blue]🐘[/]", "desc": "Engine + Laravel Extensions", "bin": "php"},
    {"id": "mariadb",  "name": "MariaDB Database",  "icon": "[bold white]🗄️[/]", "desc": "SQL Server + Security", "bin": "mariadb"},
    {"id": "node",     "name": "Node.js (NVM)",     "icon": "[bold green]⬢[/]", "desc": "JS Runtime & Package Manager", "bin": "node"},
    {"id": "composer", "name": "PHP Composer",      "icon": "[bold yellow]📦[/]", "desc": "Global Dependencies", "bin": "composer"},
    {"id": "valet",    "name": "Laravel Valet",     "icon": "[bold cyan]⚡[/]", "desc": "Local Dev Server (.test)", "bin": "valet"},
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
    console.clear()
    content = Group(
        Text("\nAcceso Administrativo Requerido", style="bold white"),
        Text("\nSe requieren permisos de sudo para este componente.", style="dim"),
    )
    panel = Panel(Align.center(content, vertical="middle"), title="[bold yellow] 🔐 SECURITY CHECK ", border_style="bright_yellow", padding=(2, 4), box=box.DOUBLE)
    console.print("\n" * (max(0, console.height // 4)), Align.center(panel))
    pwd = Prompt.ask(" [bold yellow]Contraseña de sistema[/]", password=True)
    proc = subprocess.Popen(["sudo", "-S", "-v"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.communicate(input=f"{pwd}\n".encode())
    if proc.returncode == 0:
        global KEEPALIVE_STARTED
        if not KEEPALIVE_STARTED:
            KEEPALIVE_STARTED = True
            def keep_alive():
                while True: subprocess.run(["sudo", "-n", "true"], check=False, stderr=subprocess.DEVNULL); time.sleep(60)
            threading.Thread(target=keep_alive, daemon=True).start()
        return pwd
    return modern_modal_password()

# ─────────────────────────────────────────────────────────────
#   UI Helpers (Modern & Minimalist)
# ─────────────────────────────────────────────────────────────

def get_header(title="LARAVEL DEV SETUP", sub="PREMIUM BOOTSTRAPPER"):
    return Group(
        Text("\n"),
        Align.center(Text(title, style="bold cyan tracking5")),
        Align.center(Text(sub, style="dim italic")),
        Text("\n"),
        Rule(style="dim #333333")
    )

def getch():
    import tty, termios
    fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
    try: tty.setraw(fd); ch = sys.stdin.read(1)
    finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

# ─────────────────────────────────────────────────────────────
#   Orquestador de Ejecución
# ─────────────────────────────────────────────────────────────

def run_bash_cmd(script_id, extra_args=None, progress=None):
    global CACHED_PASSWORD
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
    
    process = subprocess.Popen(["bash", "-c", full_cmd], stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, close_fds=True, env=env)
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
                            if progress: progress.console.print(f"  [dim]│[/] {clean}")
                    buffer = lines[-1]
            if process.poll() is not None and not r: break
        except: break
    process.wait()
    return process.returncode == 0

# ─────────────────────────────────────────────────────────────
#   Flujo Principal (The App)
# ─────────────────────────────────────────────────────────────

def main():
    console.clear(); console.print(get_header())
    with console.status(" [bold cyan]Iniciando escaneo...[/]"):
        installed_info = detect_installed()
        time.sleep(0.5)

    # 1. Selección de Componentes (Checkbox UI)
    idx = 0; states = {c['id']: (not installed_info[c['id']]) for c in COMPONENTS}
    while True:
        console.clear(); console.print(get_header("MENU DE SELECCIÓN", "↑↓ Navegar · Espacio para marcar · Enter confirmar"))
        for i, c in enumerate(COMPONENTS):
            active = (i == idx)
            mark_text = " [bold cyan]●[/] " if states[c['id']] else " [dim]○[/] "
            icon_text = f"{c['icon']} "
            tag_text = f" [green][v{installed_info[c['id']]}] [/]" if installed_info[c['id']] else ""
            
            # Construimos la línea usando markup para que Rich procese todo correctamente
            line = Text.from_markup(
                f"{'  ┃ ' if active else '    '}{mark_text}{icon_text}",
                style="cyan" if active else "default"
            )
            line.append(f"{c['name']:<22}", style="bold white" if active else ("white" if states[c['id']] else "dim"))
            line.append(Text.from_markup(tag_text))
            line.append(f" {c['desc']}", style="dim italic")
            console.print(line)
        
        key = getch()
        if key == '\x1b':
            r = sys.stdin.read(2)
            if r == '[A': idx = (idx - 1) % len(COMPONENTS)
            elif r == '[B': idx = (idx + 1) % len(COMPONENTS)
        elif key == ' ': states[COMPONENTS[idx]['id']] = not states[COMPONENTS[idx]['id']]
        elif key in ('\r', '\n'): break
        elif key.lower() == 'q': sys.exit(0)

    selected_ids = [c['id'] for c in COMPONENTS if states[c['id']]]
    if not selected_ids: return

    # 2. Instalación en Vivo
    console.clear(); console.print(get_header("DESPLIEGUE EN CURSO", "Configurando tu entorno de desarrollo"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, style="dim", complete_style="cyan"),
        TextColumn("[bold white]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console, transient=False
    ) as progress:
        
        overall = progress.add_task("Progreso Total", total=len(selected_ids))
        
        for sid in selected_ids:
            c = next(comp for comp in COMPONENTS if comp['id'] == sid)
            args = []
            
            if sid == 'php':
                progress.stop(); console.clear(); console.print(get_header("PHP ENGINE", "Selecciona la versión a instalar"))
                v_opts = ["8.4", "8.3", "8.2", "8.1"]; v_idx = 0
                while True:
                    for i, v in enumerate(v_opts):
                        console.print(Text(f"  {' ➜ ' if i == v_idx else '   '} PHP {v} {'(Recomendado)' if v=='8.4' else ''}", style="bold cyan" if i == v_idx else "white"))
                    k = getch()
                    if k == '\x1b':
                        r = sys.stdin.read(2)
                        if r == '[A': v_idx = (v_idx - 1) % len(v_opts)
                        elif r == '[B': v_idx = (v_idx + 1) % len(v_opts)
                    elif k in ('\r', '\n'): args = [v_opts[v_idx]]; break
                    console.clear(); console.print(get_header("PHP ENGINE", "Selecciona la versión a instalar"))
                console.clear(); console.print(get_header("DESPLIEGUE EN CURSO")); progress.start()
            
            elif sid == 'node':
                progress.stop(); console.print("\n")
                node_v = Prompt.ask(f"  [bold cyan]?[/] [white]Ingresa versión de Node.js[/] [dim](ej: 22, lts, 20.10)[/]", default="lts")
                args = [node_v]; progress.start()

            task = progress.add_task(f"Instalando {c['name']}...", total=None)
            success = run_bash_cmd(sid, args, progress)
            
            if success:
                progress.update(task, description=f"[green]✓ {c['name']} Listo", completed=100, total=100)
                progress.advance(overall)
            else:
                progress.update(task, description=f"[red]✗ {c['name']} Falló")
                console.print(f"\n  [bold red]ERROR CRÍTICO[/] [dim]Fallo en {c['name']}. Revisa los logs arriba.[/]")
                sys.exit(1)

    # 3. Éxito Final
    console.clear()
    panel = Panel(Align.center(Group(
        Text("\n✨ DESPLIEGUE COMPLETADO ✨", style="bold green"),
        Text("\nTu entorno Laravel ha sido optimizado profesionalmente.", style="white"),
        Text("\nReinicia tu terminal para activar todos los cambios.", style="dim italic")
    )), border_style="green", box=box.DOUBLE, padding=(1, 4))
    console.print("\n" * (console.height // 4), Align.center(panel))

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        console.print("\n\n [bold red]INSTALACIÓN CANCELADA[/]\n"); sys.exit(130)
