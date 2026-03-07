import os
import sys
import subprocess
import time
import re
import threading
import pty
import select
from rich.console import Console
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.console import Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeElapsedColumn

console = Console()
CACHED_PASSWORD = None

# ─────────────────────────────────────────────────────────────
#   Config & State
# ─────────────────────────────────────────────────────────────

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "desc": "Zsh + P10k + Modern CLI Tools"},
    {"id": "php",      "name": "PHP Engine",        "desc": "PHP 8.1 - 8.5 + Extensions"},
    {"id": "mariadb",  "name": "MariaDB Database",  "desc": "SQL Server + Security Wizard"},
    {"id": "node",     "name": "Node.js (NVM)",     "desc": "Node LTS & Package Manager"},
    {"id": "composer", "name": "PHP Composer",      "desc": "Dependency Management"},
    {"id": "valet",    "name": "Laravel Valet",     "desc": "Local Development Server"},
]

states = {c["id"]: True for c in COMPONENTS}

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

def show_password_prompt():
    panel = Panel(
        Text("Administrative privileges are required for this step.\nPlease confirm your password.", justify="center"),
        title="[bold yellow]🔒 SECURITY CHECK",
        border_style="yellow",
        padding=(1, 2)
    )
    console.print("\n")
    console.print(Align.center(panel))
    console.print("\n")
    # Forzamos a Prompt a usar /dev/tty si es posible para mayor robustez
    return Prompt.ask("  [bold cyan]Password[/]", password=True)

# ─────────────────────────────────────────────────────────────
#   Interactive Selector System (FIXED FOR CURL | BASH)
# ─────────────────────────────────────────────────────────────

def interactive_select(title, options, multi=False, initial_states=None):
    idx = 0
    selected_states = initial_states.copy() if initial_states else {opt['id']: False for opt in options}
    
    import tty, termios
    
    def getch():
        """Lee una tecla directamente desde /dev/tty para evitar errores de IOCTL."""
        # Abrimos el dispositivo de terminal directamente
        fd = os.open('/dev/tty', os.O_RDONLY)
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd) # Modo que permite leer tecla a tecla
            ch = os.read(fd, 3) # Leemos hasta 3 bytes para capturar secuencias de flechas (\x1b[A, etc)
            if isinstance(ch, bytes):
                return ch.decode('utf-8', errors='ignore')
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            os.close(fd)

    def render():
        items = [Text("\n")]
        for i, opt in enumerate(options):
            is_active = (i == idx)
            is_sel = selected_states[opt['id']] if multi else (i == idx)
            mark = " ● " if (multi and is_sel) or (not multi and is_active) else " ○ "
            mark_style = "bold cyan" if (multi and is_sel) or (not multi and is_active) else "dim"
            line = Text()
            line.append("  ┃ " if is_active else "    ", style="bold cyan")
            line.append(mark, style=mark_style)
            line.append(f"{opt['name']:<25}", style="bold white" if is_active else "dim")
            if 'desc' in opt: line.append(f" {opt['desc']}", style="dim italic")
            items.append(line); items.append(Text("\n"))
        
        footer = Text()
        shortcuts = [("↑↓", "Nav"), ("SPACE", "Toggle") if multi else ("ENTER", "Select"), ("Q", "Quit")]
        for k, a in shortcuts: footer.append(f" {k} ", style="bold cyan"); footer.append(f"{a}   ", style="dim")

        return Group(get_header(title.upper(), "INTERACTIVE SELECTION"), Align.center(Group(*items)), Rule(style="dim #333333"), Align.center(footer), Text("\n"))

    with Live(render(), auto_refresh=False, screen=True) as live:
        while True:
            key = getch()
            # Mapeo de teclas (flechas envían secuencias \x1b[A, \x1b[B, etc)
            if key in ('\x1b[A', 'k'): idx = (idx - 1) % len(options)
            elif key in ('\x1b[B', 'j'): idx = (idx + 1) % len(options)
            elif key == ' ' and multi:
                cid = options[idx]['id']
                selected_states[cid] = not selected_states[cid]
            elif key in ('\r', '\n'):
                if not multi: return options[idx]['id']
                return selected_states
            elif key.lower() == 'q': sys.exit(0)
            live.update(render(), refresh=True)

# ─────────────────────────────────────────────────────────────
#   Execution Engine (PTY Enabled for Sudo Interception)
# ─────────────────────────────────────────────────────────────

def run_bash_cmd(cmd_label, script_name, extra_args=None, progress=None):
    global CACHED_PASSWORD
    
    cmd_parts = [
        "export SUDO=sudo",
        "source lib/ui.sh",
        "source lib/detect.sh",
        "source lib/repo.sh",
        f"source installers/{script_name}.sh",
        "detect_os"
    ]
    
    if script_name == "php":
        version = extra_args[0] if extra_args else "8.4"
        cmd_parts.append("setup_repo")
        cmd_parts.append(f"install_php {version}")
        cmd_parts.append(f"set_default_php {version}")
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
    env["PYTHONIOENCODING"] = "utf-8"
    
    process = subprocess.Popen(
        ["bash", "-c", full_cmd],
        stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
        close_fds=True, env=env
    )
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
                    pwd_to_send = CACHED_PASSWORD or show_password_prompt()
                    CACHED_PASSWORD = pwd_to_send
                    os.write(master_fd, (pwd_to_send + "\n").encode())
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
        except (IOError, OSError): break

    process.wait()
    if progress: console.print(f"\n  [dim]──────────────────────────────────────────────────[/]")
    return process.returncode == 0

# ─────────────────────────────────────────────────────────────
#   Main Entry Point
# ─────────────────────────────────────────────────────────────

def main():
    global CACHED_PASSWORD
    states = interactive_select("Components", COMPONENTS, multi=True, initial_states={c["id"]: True for c in COMPONENTS})

    selected_versions = {}
    if states['php']:
        opts = [
            {"id": "8.4", "name": "PHP 8.4 (Stable)"},
            {"id": "8.3", "name": "PHP 8.3"},
            {"id": "8.2", "name": "PHP 8.2"},
            {"id": "8.1", "name": "PHP 8.1"},
            {"id": "8.5", "name": "PHP 8.5 (Experimental)"}
        ]
        selected_versions['php'] = interactive_select("PHP Engine", opts)

    console.clear()
    console.print(get_header())
    
    panel = Panel(
        Text("Administrative privileges are required for system configuration.\nPlease enter your password to authorize deployment.", justify="center"),
        title="[bold yellow]🔒 PRIVILEGE ESCALATION", border_style="yellow", padding=(1, 2)
    )
    console.print("\n", Align.center(panel), "\n")
    
    authenticated = False
    while not authenticated:
        pwd = Prompt.ask("  [bold cyan]Password[/]", password=True)
        proc = subprocess.Popen(["sudo", "-S", "-v"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.communicate(input=f"{pwd}\n".encode())
        if proc.returncode == 0:
            authenticated = True
            CACHED_PASSWORD = pwd
            console.print(Align.center(Text("✓ Authentication Successful", style="bold green")))
            time.sleep(0.5)
        else:
            console.print("  [bold red]✖ Incorrect password. Please try again.[/]")

    def keep_sudo_alive():
        while True:
            subprocess.run(["sudo", "-n", "true"], check=False)
            time.sleep(60)
    threading.Thread(target=keep_sudo_alive, daemon=True).start()

    selected_list = [c for c in COMPONENTS if states[c['id']]]
    if not selected_list:
        console.print("\n  [yellow]No items selected. Exiting.[/]\n")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, style="dim", complete_style="cyan"),
        TextColumn("[bold white]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console, transient=False
    ) as progress:
        overall_task = progress.add_task("[bold white]Overall Deployment", total=len(selected_list))
        for c in selected_list:
            args = []
            if c['id'] == 'node':
                progress.stop()
                node_ver = Prompt.ask("\n  [bold cyan]?[/] [white]Enter Node.js version[/] [dim](e.g. 22, lts)[/]", default="lts")
                args = [node_ver]
                progress.start()
            elif c['id'] == 'php':
                args = [selected_versions['php']]
            
            comp_task = progress.add_task(f"[cyan]Installing {c['name']}...", total=None)
            success = run_bash_cmd(c['name'], c['id'], args, progress)
            if success:
                progress.update(comp_task, description=f"[green]✓ {c['name']} Complete", completed=100, total=100)
                progress.advance(overall_task)
            else:
                progress.update(comp_task, description=f"[red]✗ {c['name']} Failed")
                sys.exit(1)
        progress.update(overall_task, description="[bold green]All systems ready")

    console.print("\n\n")
    console.print(Align.center(Text("✨ DEPLOYMENT SUCCESSFUL", style="bold green")))
    console.print(Align.center(Text("Environment is optimized. Please restart your terminal.", style="dim")))
    console.print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n  [bold red]ABORTED[/] [dim]Installation cancelled by user.[/]\n")
        sys.exit(130)
