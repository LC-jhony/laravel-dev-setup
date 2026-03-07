import os
import sys
import subprocess
import time
import re
import threading
import pty
import select
import shutil
from rich.console import Console
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.console import Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeElapsedColumn
from rich import box

console = Console()
CACHED_PASSWORD = None
KEEPALIVE_STARTED = False

# ─────────────────────────────────────────────────────────────
#   Config & State
# ─────────────────────────────────────────────────────────────

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "desc": "Zsh + P10k + Modern CLI Tools", "bin": "zsh"},
    {"id": "php",      "name": "PHP Engine",        "desc": "PHP 8.1 - 8.5 + Extensions", "bin": "php"},
    {"id": "mariadb",  "name": "MariaDB Database",  "desc": "SQL Server + Security Wizard", "bin": "mariadb"},
    {"id": "node",     "name": "Node.js (NVM)",     "desc": "Node LTS & Package Manager", "bin": "node"},
    {"id": "composer", "name": "PHP Composer",      "desc": "Dependency Management", "bin": "composer"},
    {"id": "valet",    "name": "Laravel Valet",     "desc": "Local Development Server", "bin": "valet"},
]

states = {}
installed_info = {}

# ─────────────────────────────────────────────────────────────
#   Detection System
# ─────────────────────────────────────────────────────────────

def detect_installed():
    global installed_info, states
    for c in COMPONENTS:
        version = None
        is_installed = False
        bin_path = shutil.which(c['bin'])
        if bin_path:
            is_installed = True
            try:
                if c['id'] == 'php': cmd = "php -r 'echo PHP_MAJOR_VERSION.\".\".PHP_MINOR_VERSION;'"
                elif c['id'] == 'node': cmd = "node -v"
                elif c['id'] == 'composer': cmd = "composer --version | awk '{print $3}'"
                elif c['id'] == 'mariadb': cmd = "mariadb --version | awk '{print $5}' | cut -d',' -f1"
                else: cmd = f"{c['bin']} --version"
                version_raw = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode().strip()
                version = version_raw.lstrip('v').split()[0]
            except: version = "Detectado"
        if c['id'] == 'node' and not is_installed:
             if os.path.exists(os.path.expanduser("~/.nvm")): is_installed = True; version = "NVM"
        installed_info[c['id']] = version if is_installed else None
        states[c['id']] = not is_installed

# ─────────────────────────────────────────────────────────────
#   Security Helpers
# ─────────────────────────────────────────────────────────────

def start_keep_alive():
    """Mantiene activa la sesión de sudo en segundo plano."""
    global KEEPALIVE_STARTED
    if KEEPALIVE_STARTED: return
    KEEPALIVE_STARTED = True
    def keep_alive():
        while True:
            subprocess.run(["sudo", "-n", "true"], check=False, stderr=subprocess.DEVNULL)
            time.sleep(60)
    threading.Thread(target=keep_alive, daemon=True).start()

def modern_modal_password():
    """Muestra un modal centrado y estilizado para la contraseña."""
    # Guardamos la pantalla actual
    console.clear()
    
    content = Group(
        Text("\nAcceso Administrativo Requerido", style="bold white"),
        Text("\nEl instalador necesita permisos para aplicar cambios en el sistema.", style="dim"),
        Text("\nTu contraseña será usada solo en esta sesión y no se guardará en disco.", style="italic cyan small"),
    )
    
    modal_panel = Panel(
        Align.center(content, vertical="middle"),
        title="[bold yellow] 🔐 SEGURIDAD DEL SISTEMA ",
        border_style="bright_yellow",
        padding=(2, 4),
        box=box.DOUBLE
    )
    
    # Imprimimos espacios para centrar verticalmente (aproximado)
    console.print("\n" * (console.height // 4))
    console.print(Align.center(modal_panel))
    console.print("\n")
    
    pwd = Prompt.ask(" [bold yellow]Contraseña de sudo[/]", password=True)
    
    # Validar inmediatamente
    proc = subprocess.Popen(["sudo", "-S", "-v"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.communicate(input=f"{pwd}\n".encode())
    
    if proc.returncode == 0:
        start_keep_alive()
        console.clear() # Limpiar modal para volver a la instalación
        return pwd
    else:
        console.print(Align.center(Text("✖ Contraseña incorrecta. Reintentando...", style="bold red")))
        time.sleep(1.5)
        return modern_modal_password()

# ─────────────────────────────────────────────────────────────
#   UI Helpers
# ─────────────────────────────────────────────────────────────

def get_header(title_str="LARAVEL DEV SETUP", subtitle_str="PREMIUM ENVIRONMENT BOOTSTRAP"):
    return Group(
        Text("\n"),
        Align.center(Text(title_str, style="bold cyan tracking5")),
        Align.center(Text(subtitle_str, style="dim italic")),
        Text("\n"),
        Rule(style="dim #333333")
    )

def interactive_select(title, options, multi=False, initial_states=None):
    idx = 0
    selected_states = initial_states.copy() if initial_states else {opt['id']: False for opt in options}
    import tty, termios
    def getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b': ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def render():
        items = [Text("\n")]
        for i, opt in enumerate(options):
            is_active = (i == idx)
            is_sel = selected_states[opt['id']] if multi else (i == idx)
            mark = " ● " if (multi and is_sel) or (not multi and is_active) else " ○ "
            mark_style = "bold cyan" if (multi and is_sel) or (not multi and is_active) else "dim"
            status_tag = f" [bold green][INSTALADO: v{installed_info[opt['id']]}] [/]" if multi and installed_info.get(opt['id']) else ""
            line = Text()
            line.append("  ┃ " if is_active else "    ", style="bold cyan")
            line.append(mark, style=mark_style)
            line.append(f"{opt['name']:<25}", style="bold white" if is_active else "dim")
            line.append(status_tag)
            if 'desc' in opt: line.append(f" {opt['desc']}", style="dim italic")
            items.append(line); items.append(Text("\n"))
        footer = Text()
        shortcuts = [("↑↓", "Nav"), ("SPACE", "Toggle") if multi else ("ENTER", "Select"), ("Q", "Quit")]
        for k, a in shortcuts: footer.append(f" {k} ", style="bold cyan"); footer.append(f"{a}   ", style="dim")
        return Group(get_header(title.upper(), "INTERACTIVE SELECTION"), Align.center(Group(*items)), Rule(style="dim #333333"), Align.center(footer), Text("\n"))

    with Live(render(), auto_refresh=False, screen=True) as live:
        while True:
            key = getch()
            if key in ('\x1b[A', 'k'): idx = (idx - 1) % len(options)
            elif key in ('\x1b[B', 'j'): idx = (idx + 1) % len(options)
            elif key == ' ' and multi:
                cid = options[idx]['id']
                selected_states[cid] = not selected_states[cid]
            elif key in ('\r', '\n'): return selected_states if multi else options[idx]['id']
            elif key.lower() == 'q': sys.exit(0)
            live.update(render(), refresh=True)

# ─────────────────────────────────────────────────────────────
#   Execution Engine
# ─────────────────────────────────────────────────────────────

def run_bash_cmd(cmd_label, script_name, extra_args=None, progress=None):
    global CACHED_PASSWORD
    cmd_parts = ["export SUDO=sudo", "source lib/ui.sh", "source lib/detect.sh", "source lib/repo.sh", f"source installers/{script_name}.sh", "detect_os"]
    if script_name == "php":
        version = extra_args[0] if extra_args else "8.4"
        cmd_parts += ["setup_repo", f"install_php {version}", f"set_default_php {version}"]
    else:
        call_cmd = f"install_{script_name}"
        if extra_args: call_cmd += f" {' '.join(extra_args)}"
        cmd_parts.append(call_cmd)
    
    full_cmd = " && ".join(cmd_parts)
    
    if progress:
        progress.stop()
        console.print(f"\n  [bold cyan]▶[/] [white]Deploying:[/] [bold white]{cmd_label}[/]")
        console.print(f"  [dim]──────────────────────────────────────────────────[/]\n")
        progress.start()

    master_fd, slave_fd = pty.openpty()
    env = os.environ.copy()
    env["PYTHONIOENCODING"], env["LARAVEL_SETUP_RICH"] = "utf-8", "1"
    
    process = subprocess.Popen(["bash", "-c", full_cmd], stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, close_fds=True, env=env)
    os.close(slave_fd)

    buffer = ""
    while True:
        try:
            r, _, _ = select.select([master_fd], [], [], 0.1)
            if master_fd in r:
                data = os.read(master_fd, 1024)
                if not data: break
                chunk = data.decode('utf-8', errors='replace')
                buffer += chunk
                if "password for" in buffer.lower() and ":" in buffer:
                    if progress: progress.stop()
                    CACHED_PASSWORD = CACHED_PASSWORD or modern_modal_password()
                    os.write(master_fd, (CACHED_PASSWORD + "\n").encode())
                    buffer = ""
                    if progress: progress.start()
                elif "\n" in buffer:
                    lines = buffer.split("\n")
                    for line in lines[:-1]:
                        clean_line = line.strip()
                        if clean_line and "password for" not in clean_line.lower():
                             if progress: progress.console.print(f"  [dim]│[/] {clean_line}")
                             else: console.print(f"  [dim]│[/] {clean_line}")
                    buffer = lines[-1]
            if process.poll() is not None and not r: break
        except: break
    process.wait()
    return process.returncode == 0

# ─────────────────────────────────────────────────────────────
#   Main Entry Point
# ─────────────────────────────────────────────────────────────

def main():
    global states
    console.clear()
    console.print(get_header())
    with console.status(" [bold cyan]Escaneando componentes...[/]"): detect_installed(); time.sleep(0.5)

    states = interactive_select("Components", COMPONENTS, multi=True, initial_states=states)
    selected_versions = {}
    if states['php']:
        opts = [{"id": v, "name": f"PHP {v}"} for v in ["8.4", "8.3", "8.2", "8.1", "8.5"]]
        selected_versions['php'] = interactive_select("PHP Engine", opts)

    selected_list = [c for c in COMPONENTS if states[c['id']]]
    if not selected_list: return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(bar_width=40, style="dim", complete_style="cyan"), TextColumn("[bold white]{task.percentage:>3.0f}%"), TimeElapsedColumn(), console=console, transient=False) as progress:
        overall_task = progress.add_task("[bold white]Overall Deployment", total=len(selected_list))
        for c in selected_list:
            args = []
            if c['id'] == 'node':
                progress.stop(); node_ver = Prompt.ask("\n  [bold cyan]?[/] [white]Enter Node.js version[/]", default="lts"); args = [node_ver]; progress.start()
            elif c['id'] == 'php': args = [selected_versions['php']]
            
            comp_task = progress.add_task(f"[cyan]Installing {c['name']}...", total=None)
            if run_bash_cmd(c['name'], c['id'], args, progress):
                progress.update(comp_task, description=f"[green]✓ {c['name']} Complete", completed=100, total=100); progress.advance(overall_task)
            else:
                progress.update(comp_task, description=f"[red]✗ {c['name']} Failed"); sys.exit(1)
        progress.update(overall_task, description="[bold green]All systems ready")

    console.print("\n\n")
    console.print(Align.center(Text("✨ DEPLOYMENT SUCCESSFUL", style="bold green")))
    console.print(Align.center(Text("Environment is optimized. Please restart your terminal.", style="dim")))
    console.print("\n")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        console.print("\n\n  [bold red]ABORTED[/] [dim]Installation cancelled.[/]\n"); sys.exit(130)
