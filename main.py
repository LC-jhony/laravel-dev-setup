import os
import sys
import subprocess
import time
import re
import threading
import pty
import select
import shutil
from collections import deque
from rich.console import Console, Group
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeElapsedColumn
from rich.table import Table
from rich.layout import Layout
from rich import box

# ─────────────────────────────────────────────────────────────
#   Config & System State
# ─────────────────────────────────────────────────────────────

console = Console()
CACHED_PASSWORD = None
KEEPALIVE_STARTED = False

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "desc": "Zsh + P10k + Modern CLI Tools", "bin": "zsh"},
    {"id": "php",      "name": "PHP Engine",        "desc": "PHP 8.1 - 8.4 + Extensions", "bin": "php"},
    {"id": "mariadb",  "name": "MariaDB Database",  "desc": "SQL Server + Security Wizard", "bin": "mariadb"},
    {"id": "node",     "name": "Node.js (NVM)",     "desc": "Node LTS & Package Manager", "bin": "node"},
    {"id": "composer", "name": "PHP Composer",      "desc": "Dependency Management", "bin": "composer"},
    {"id": "valet",    "name": "Laravel Valet",     "desc": "Local Development Server", "bin": "valet"},
]

installation_states = {}
installation_logs = deque(maxlen=8)
current_component_id = None

# ─────────────────────────────────────────────────────────────
#   UI Components
# ─────────────────────────────────────────────────────────────

def get_header(title="LARAVEL DEV SETUP", sub="PREMIUM ENVIRONMENT BOOTSTRAP"):
    grid = Table.grid(expand=True)
    grid.add_column(justify="center")
    grid.add_row(Text(f"\n{title}", style="bold cyan tracking5"))
    grid.add_row(Text(sub, style="dim italic"))
    return Panel(grid, style="dim #333333", box=box.MINIMAL)

def get_status_table():
    table = Table(box=box.SIMPLE, expand=True, border_style="dim")
    table.add_column("Component", style="white")
    table.add_column("Status", justify="right")
    for c in COMPONENTS:
        state = installation_states.get(c['id'], 'skip')
        if state == 'pending': status = Text("⌛ Pendiente", style="dim")
        elif state == 'installing': status = Text("🛠️ Instalando", style="bold yellow")
        elif state == 'success': status = Text("✅ Completado", style="bold green")
        elif state == 'failed': status = Text("❌ Fallido", style="bold red")
        else: continue
        table.add_row(c['name'], status)
    return Panel(table, title="[bold]📋 Deployment Stack", border_style="cyan")

def get_log_panel():
    log_text = Text()
    for line in installation_logs: log_text.append(f"  > {line}\n", style="dim")
    return Panel(log_text, title="[bold]📜 Live Output", border_style="dim", padding=(1, 1))

def create_install_layout(progress_renderable):
    layout = Layout()
    layout.split_column(Layout(get_header(), size=5), Layout(name="main", ratio=1), Layout(progress_renderable, size=3))
    layout["main"].split_row(Layout(get_status_table(), ratio=1), Layout(get_log_panel(), ratio=2))
    return layout

# ─────────────────────────────────────────────────────────────
#   Core Logic
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
    panel = Panel(Align.center(Group(Text("\nAcceso Administrativo Requerido", style="bold white"), Text("\nEl instalador necesita permisos de sudo para continuar.", style="dim"))), title="[bold yellow] 🔐 SECURITY ", border_style="yellow", padding=(2, 4), box=box.DOUBLE)
    console.print("\n" * (console.height // 4), Align.center(panel))
    pwd = Prompt.ask(" [bold yellow]Contraseña[/]", password=True)
    proc = subprocess.Popen(["sudo", "-S", "-v"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.communicate(input=f"{pwd}\n".encode())
    if proc.returncode == 0:
        if not KEEPALIVE_STARTED: threading.Thread(target=lambda: (time.sleep(60), subprocess.run(["sudo", "-n", "true"], check=False)), daemon=True).start()
        console.clear(); return pwd
    return modern_modal_password()

def run_bash_cmd(script_name, extra_args=None):
    global CACHED_PASSWORD, installation_logs
    cmd_parts = ["export SUDO=sudo", "source lib/ui.sh", "source lib/detect.sh", "source lib/repo.sh", f"source installers/{script_name}.sh", "detect_os"]
    if script_name == "php":
        v = extra_args[0] if extra_args else "8.4"
        cmd_parts += ["setup_repo", f"install_php {v}", f"set_default_php {v}"]
    else:
        call = f"install_{script_name}"; 
        if extra_args: call += f" {' '.join(extra_args)}"
        cmd_parts.append(call)
    full_cmd = " && ".join(cmd_parts); master_fd, slave_fd = pty.openpty(); env = os.environ.copy()
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
                    CACHED_PASSWORD = CACHED_PASSWORD or modern_modal_password()
                    os.write(master_fd, (CACHED_PASSWORD + "\n").encode()); buffer = ""
                elif "\n" in buffer:
                    lines = buffer.split("\n")
                    for line in lines[:-1]:
                        clean = line.strip()
                        if clean and "password for" not in clean.lower(): installation_logs.append(clean)
                    buffer = lines[-1]
            if process.poll() is not None and not r: break
        except: break
    process.wait()
    return process.returncode == 0

# ─────────────────────────────────────────────────────────────
#   Main Flow
# ─────────────────────────────────────────────────────────────

def main():
    global installation_states
    console.clear(); console.print(get_header())
    
    with console.status(" [bold cyan]Escaneando sistema...[/]"):
        installed_info = detect_installed()
        time.sleep(0.6)

    # CHECK: ¿Está todo instalado?
    missing = [c for c in COMPONENTS if not installed_info[c['id']]]
    
    if not missing:
        # UI Minimalista de "Todo OK"
        table = Table(box=box.ROUNDED, border_style="green", title="[bold green]✅ ENTORNO OPTIMIZADO")
        table.add_column("Componente", style="white")
        table.add_column("Versión Detectada", style="bold cyan", justify="center")
        for c in COMPONENTS: table.add_row(c['name'], f"v{installed_info[c['id']]}")
        
        console.clear(); console.print(get_header())
        console.print("\n")
        console.print(Align.center(table))
        console.print("\n")
        
        confirm = Panel(Text("Parece que ya tienes todo instalado y configurado correctamente.\n¿Deseas entrar al menú de selección de todos modos?", justify="center"), border_style="dim")
        console.print(Align.center(confirm))
        console.print(Align.center(Text("\n[ [bold cyan]ENTER[/] ] Ir al Menú   [ [bold red]Q[/] ] Salir", style="dim")))
        
        import tty, termios
        def get_simple_key():
            fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
            try: tty.setraw(fd); return sys.stdin.read(1)
            finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)
        
        k = get_simple_key()
        if k.lower() == 'q': sys.exit(0)

    # 1. Selección Interactiva
    import tty, termios
    def getch():
        fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
        try: tty.setraw(fd); ch = sys.stdin.read(1); 
        finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch

    idx = 0; states = {c['id']: (not installed_info[c['id']]) for c in COMPONENTS}
    while True:
        opts = []
        for i, c in enumerate(COMPONENTS):
            mark = " ● " if states[c['id']] else " ○ "
            style = "bold cyan" if i == idx else ("white" if states[c['id']] else "dim")
            tag = f" [green][v{installed_info[c['id']]}] [/]" if installed_info[c['id']] else ""
            line = Text(); line.append("  ┃ " if i == idx else "    ", style="cyan")
            line.append(mark, style="bold cyan" if states[c['id']] else "dim")
            line.append(f"{c['name']:<25}", style=style); line.append(tag)
            opts.append(line)
        console.clear(); console.print(get_header("COMPONENTS SELECTION", "↑↓ Navigate · Space toggle · Enter confirm"))
        for o in opts: console.print(o)
        key = getch()
        if key == '\x1b':
            rest = sys.stdin.read(2)
            if rest == '[A': idx = (idx - 1) % len(COMPONENTS)
            elif rest == '[B': idx = (idx + 1) % len(COMPONENTS)
        elif key == ' ': states[COMPONENTS[idx]['id']] = not states[COMPONENTS[idx]['id']]
        elif key in ('\r', '\n'): break
        elif key.lower() == 'q': sys.exit(0)

    selected_list = [c for c in COMPONENTS if states[c['id']]]
    if not selected_list: return

    # 2. Versiones PHP
    sel_versions = {}
    if states['php']:
        v_opts = ["8.4", "8.3", "8.2", "8.1"]; v_idx = 0
        while True:
            console.clear(); console.print(get_header("PHP ENGINE", "Select version"))
            for i, v in enumerate(v_opts):
                style = "bold cyan" if i == v_idx else "white"
                console.print(Text(f"  {'➜ ' if i == v_idx else '  '} PHP {v}", style=style))
            k = getch()
            if k == '\x1b':
                r = sys.stdin.read(2)
                if r == '[A': v_idx = (v_idx - 1) % len(v_opts)
                elif r == '[B': v_idx = (v_idx + 1) % len(v_opts)
            elif k in ('\r', '\n'): sel_versions['php'] = v_opts[v_idx]; break

    for c in COMPONENTS: installation_states[c['id']] = 'pending' if states[c['id']] else 'skip'

    # 3. Live Installation
    with Progress(SpinnerColumn(), TextColumn("[bold cyan]{task.description}"), BarColumn(bar_width=None), TextColumn("[white]{task.percentage:>3.0f}%"), console=console) as progress:
        overall = progress.add_task("Instalando...", total=len(selected_list))
        with Live(create_install_layout(progress), console=console, screen=True, auto_refresh=True) as live:
            for c in selected_list:
                installation_states[c['id']] = 'installing'; args = []
                if c['id'] == 'node':
                    live.stop(); console.clear(); node_v = Prompt.ask("\n  [bold cyan]?[/] [white]Enter Node.js version[/]", default="lts"); args = [node_v]; live.start()
                elif c['id'] == 'php': args = [sel_versions['php']]
                success = run_bash_cmd(c['id'], args)
                installation_states[c['id']] = 'success' if success else 'failed'
                if not success: sys.exit(1)
                progress.advance(overall); time.sleep(0.4)

    # Final
    console.clear(); panel = Panel(Align.center(Group(Text("\n✨ DEPLOYMENT SUCCESSFUL", style="bold green"), Text("\nYour system is now optimized for Laravel development.", style="dim"))), border_style="green", box=box.DOUBLE, padding=(1, 4))
    console.print("\n" * (console.height // 4), Align.center(panel))

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: console.print("\n\n [bold red]ABORTED[/]\n"); sys.exit(130)
