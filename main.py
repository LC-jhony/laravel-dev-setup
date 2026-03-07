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

console = Console()
CACHED_PASSWORD = None
KEEPALIVE_STARTED = False

# ─────────────────────────────────────────────────────────────
#   Config & System State
# ─────────────────────────────────────────────────────────────

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "desc": "Zsh + P10k + Modern CLI Tools", "bin": "zsh"},
    {"id": "php",      "name": "PHP Engine",        "desc": "PHP 8.1 - 8.4 + Extensions", "bin": "php"},
    {"id": "mariadb",  "name": "MariaDB Database",  "desc": "SQL Server + Security Wizard", "bin": "mariadb"},
    {"id": "node",     "name": "Node.js (NVM)",     "desc": "Node LTS & Package Manager", "bin": "node"},
    {"id": "composer", "name": "PHP Composer",      "desc": "Dependency Management", "bin": "composer"},
    {"id": "valet",    "name": "Laravel Valet",     "desc": "Local Development Server", "bin": "valet"},
]

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
    panel = Panel(Align.center(Group(Text("\nAcceso Administrativo Requerido", style="bold white"), Text("\nEl instalador necesita permisos de sudo para continuar.", style="dim"))), title="[bold yellow] 🔐 SECURITY ", border_style="bright_yellow", padding=(2, 4), box=box.DOUBLE)
    console.print("\n" * (console.height // 4), Align.center(panel))
    pwd = Prompt.ask(" [bold yellow]Contraseña[/]", password=True)
    proc = subprocess.Popen(["sudo", "-S", "-v"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.communicate(input=f"{pwd}\n".encode())
    if proc.returncode == 0:
        global KEEPALIVE_STARTED
        if not KEEPALIVE_STARTED:
            KEEPALIVE_STARTED = True
            def keep_alive():
                while True: subprocess.run(["sudo", "-n", "true"], check=False); time.sleep(60)
            threading.Thread(target=keep_alive, daemon=True).start()
        console.clear(); return pwd
    return modern_modal_password()

def run_bash_cmd(script_name, extra_args=None, progress=None):
    global CACHED_PASSWORD
    cmd_parts = ["export SUDO=sudo", "source lib/ui.sh", "source lib/detect.sh", "source lib/repo.sh", f"source installers/{script_name}.sh", "detect_os"]
    if script_name == "php":
        v = extra_args[0] if extra_args else "8.4"
        cmd_parts += ["setup_repo", f"install_php {v}", f"set_default_php {v}"]
    else:
        call = f"install_{script_name}"; 
        if extra_args: call += f" {' '.join(extra_args)}"
        cmd_parts.append(call)
    
    full_cmd = " && ".join(cmd_parts)
    master_fd, slave_fd = pty.openpty()
    env = os.environ.copy(); env["PYTHONIOENCODING"], env["LARAVEL_SETUP_RICH"] = "utf-8", "1"
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
                            else: console.print(f"  [dim]│[/] {clean}")
                    buffer = lines[-1]
            if process.poll() is not None and not r: break
        except: break
    process.wait()
    return process.returncode == 0

# ─────────────────────────────────────────────────────────────
#   Main Flow
# ─────────────────────────────────────────────────────────────

def get_header(title="LARAVEL DEV SETUP", sub="PREMIUM ENVIRONMENT BOOTSTRAP"):
    return Group(Text("\n"), Align.center(Text(title, style="bold cyan tracking5")), Align.center(Text(sub, style="dim italic")), Text("\n"), Rule(style="dim #333333"))

def main():
    console.clear(); console.print(get_header())
    with console.status(" [bold cyan]Escaneando sistema...[/]"):
        installed_info = detect_installed()
        time.sleep(0.6)

    # UI Minimalista de "Todo Instalado"
    missing = [c for c in COMPONENTS if not installed_info[c['id']]]
    if not missing:
        table = Table(box=box.ROUNDED, border_style="green", title="[bold green]✅ ENTORNO OPTIMIZADO")
        table.add_column("Componente", style="white"); table.add_column("Versión Detectada", style="bold cyan", justify="center")
        for c in COMPONENTS: table.add_row(c['name'], f"v{installed_info[c['id']]}")
        console.clear(); console.print(get_header()); console.print("\n", Align.center(table), "\n")
        console.print(Align.center(Panel(Text("Tu sistema ya cuenta con todos los componentes necesarios.\n¿Deseas entrar al menú de configuración?", justify="center"), border_style="dim")))
        console.print(Align.center(Text("\n[ [bold cyan]ENTER[/] ] Ir al Menú   [ [bold red]Q[/] ] Salir", style="dim")))
        import tty, termios
        def get_simple():
            fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
            try: tty.setraw(fd); return sys.stdin.read(1)
            finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)
        if get_simple().lower() == 'q': sys.exit(0)

    # Selección
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
            line.append(f"{c['name']:<25}", style=style); line.append(tag); opts.append(line)
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

    # Instalación Minimalista
    console.clear(); console.print(get_header("INSTALLATION PROGRESS", "Please wait while we configure your environment"))
    with Progress(SpinnerColumn(), TextColumn("[bold cyan]{task.description}"), BarColumn(bar_width=40, style="dim", complete_style="cyan"), TextColumn("[bold white]{task.percentage:>3.0f}%"), TimeElapsedColumn(), console=console, transient=False) as progress:
        overall = progress.add_task("Total Deployment", total=len(selected_list))
        for c in selected_list:
            args = []
            if c['id'] == 'node':
                progress.stop(); console.print("\n"); node_v = Prompt.ask("  [bold cyan]?[/] [white]Enter Node.js version[/]", default="lts"); args = [node_v]; progress.start()
            elif c['id'] == 'php': args = [sel_versions['php']]
            
            task = progress.add_task(f"Installing {c['name']}...", total=None)
            success = run_bash_cmd(c['id'], args, progress)
            if success:
                progress.update(task, description=f"[green]✓ {c['name']} Complete", completed=100, total=100); progress.advance(overall)
            else:
                progress.update(task, description=f"[red]✗ {c['name']} Failed"); sys.exit(1)

    # Final
    console.clear(); panel = Panel(Align.center(Group(Text("\n✨ DEPLOYMENT SUCCESSFUL", style="bold green"), Text("\nYour system is now optimized for Laravel development.", style="dim"))), border_style="green", box=box.DOUBLE, padding=(1, 4))
    console.print("\n" * (console.height // 4), Align.center(panel))

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: console.print("\n\n [bold red]ABORTED[/]\n"); sys.exit(130)
