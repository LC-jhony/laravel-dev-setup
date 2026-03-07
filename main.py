import os
import sys
import subprocess
import time
import re
from rich.console import Console
from rich.live import Live
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.console import Group
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn, TimeElapsedColumn

console = Console()

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
        Align.center(Text(title_str, style="bold cyan")),
        Align.center(Text(subtitle_str, style="dim italic")),
        Text("\n"),
        Rule(style="dim #333333")
    )

# ─────────────────────────────────────────────────────────────
#   Interactive Selector System
# ─────────────────────────────────────────────────────────────

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
            if key == '\x1b[A': idx = (idx - 1) % len(options)
            elif key == '\x1b[B': idx = (idx + 1) % len(options)
            elif key == ' ' and multi:
                cid = options[idx]['id']
                selected_states[cid] = not selected_states[cid]
            elif key in ('\r', '\n'):
                if not multi: return options[idx]['id']
                return selected_states
            elif key.lower() == 'q': sys.exit(0)
            live.update(render(), refresh=True)

# ─────────────────────────────────────────────────────────────
#   Execution Engine
# ─────────────────────────────────────────────────────────────

def run_bash_cmd(cmd_label, script_name, extra_args=None, progress=None):
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
    
    try:
        # Pausamos el progreso para que la terminal sea 100% interactiva
        if progress:
            progress.stop()
            console.print(f"\n  [bold cyan]▶[/] [white]Deploying:[/] [bold white]{cmd_label}[/]")
            console.print(f"  [dim]──────────────────────────────────────────────────[/]\n")
        
        # Ejecutamos con herencia de stdio para que formularios y sudo funcionen
        result = subprocess.run(["bash", "-c", full_cmd], check=False)
        
        if progress:
            console.print(f"\n  [dim]──────────────────────────────────────────────────[/]")
            progress.start()
            
        return result.returncode == 0
    except Exception as e:
        if progress: progress.start()
        console.print(f"\n  [bold red]ERROR[/] {e}")
        return False

# ─────────────────────────────────────────────────────────────
#   Main Entry Point
# ─────────────────────────────────────────────────────────────

def main():
    # 1. Selección de Componentes
    global states
    states = interactive_select("Components", COMPONENTS, multi=True, initial_states=states)

    # 2. Configuración de PHP
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

    # 3. Confirmación y Sudo Inicial
    console.clear()
    console.print(get_header())
    console.print("\n  [bold yellow]PRIVILEGE ESCALATION[/]")
    console.print("  [dim]Authentication required to apply system changes.[/]\n")
    try:
        subprocess.run(["sudo", "-v"], check=True)
    except:
        console.print("\n  [bold red]ABORTED[/] [dim]Authentication failed.[/]\n")
        sys.exit(1)

    # 4. Ejecución
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
        console=console,
        transient=False
    ) as progress:
        
        overall_task = progress.add_task("[bold white]Overall Deployment", total=len(selected_list))
        
        for c in selected_list:
            # Caso Node.js pide versión manual antes de empezar su tarea
            args = []
            if c['id'] == 'node':
                progress.stop()
                console.print("\n")
                node_ver = Prompt.ask("  [bold cyan]?[/] [white]Enter Node.js version[/] [dim](e.g. 22, lts, 20.10.0)[/]", default="lts")
                args = [node_ver]
                progress.start()
            elif c['id'] == 'php':
                args = [selected_versions['php']]
            
            comp_task = progress.add_task(f"[cyan]Installing {c['name']}...", total=None)
            
            # La función run_bash_cmd ahora detiene/inicia el progreso internamente
            success = run_bash_cmd(c['name'], c['id'], args, progress)
            
            if success:
                progress.update(comp_task, description=f"[green]✓ {c['name']} Complete", completed=100, total=100)
                progress.advance(overall_task)
            else:
                progress.update(comp_task, description=f"[red]✗ {c['name']} Failed")
                console.print(f"\n  [bold red]CRITICAL ERROR[/] [dim]Failed to install {c['name']}.[/]")
                sys.exit(1)
        
        progress.update(overall_task, description="[bold green]All systems ready")

    console.print("\n\n" + Align.center(Text("✨ DEPLOYMENT SUCCESSFUL", style="bold green")))
    console.print(Align.center(Text("Environment is optimized. Please restart your terminal.", style="dim")))
    console.print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n  [bold red]ABORTED[/] [dim]Installation cancelled by user.[/]\n")
        sys.exit(130)
