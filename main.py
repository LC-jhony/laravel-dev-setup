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
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn

console = Console()

# ─────────────────────────────────────────────────────────────
#   Config & State
# ─────────────────────────────────────────────────────────────

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "desc": "Zsh + P10k + Modern CLI Tools"},
    {"id": "php",      "name": "PHP Engine",        "desc": "PHP 8.1 - 8.4 + Extensions"},
    {"id": "mariadb",  "name": "MariaDB Database",  "desc": "SQL Server + Security Wizard"},
    {"id": "node",     "name": "Node.js (NVM)",     "desc": "Node LTS & Package Manager"},
    {"id": "composer", "name": "PHP Composer",      "desc": "Dependency Management"},
    {"id": "valet",    "name": "Laravel Valet",     "desc": "Local Development Server"},
]

states = {c["id"]: True for c in COMPONENTS}

# ─────────────────────────────────────────────────────────────
#   UI Helpers
# ─────────────────────────────────────────────────────────────

def clean_ansi(text):
    """Elimina códigos de color ANSI y caracteres de control para evitar desorden."""
    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text).replace('\r', '').strip()

def get_header(title_str="LARAVEL DEV SETUP", subtitle_str="PREMIUM ENVIRONMENT BOOTSTRAP"):
    return Group(
        Text("\n"),
        Align.center(Text(title_str, style="bold cyan tracking5")),
        Align.center(Text(subtitle_str, style="dim italic")),
        Text("\n"),
        Rule(style="dim #333333")
    )

# ─────────────────────────────────────────────────────────────
#   Interactive Selector System
# ─────────────────────────────────────────────────────────────

def interactive_select(title, options, multi=False, initial_states=None):
    """Generic selector for components or versions."""
    idx = 0
    # Si es multi-selección usamos los estados pasados, si no, inicializamos uno solo
    selected_states = initial_states if initial_states else {opt['id']: False for opt in options}
    
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
            if 'desc' in opt:
                line.append(f" {opt['desc']}", style="dim italic")
            
            items.append(line)
            items.append(Text("\n"))
            
        footer_text = Text()
        shortcuts = [("↑↓", "Nav"), ("SPC", "Toggle") if multi else ("ENT", "Select"), ("Q", "Quit")]
        for k, a in shortcuts:
            footer_text.append(f" {k} ", style="bold cyan"); footer_text.append(f"{a}  ", style="dim")

        return Group(
            get_header(title.upper(), "INTERACTIVE SELECTION"),
            Align.center(Group(*items)),
            Rule(style="dim #333333"),
            Align.center(footer_text),
            Text("\n")
        )

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

def run_bash_cmd(cmd_label, script_name, extra_args=None):
    console.print(f"\n  [bold cyan]▶[/] [white]Deploying:[/] [bold white]{cmd_label}[/]")
    
    cmd = f"export SUDO=sudo && source lib/ui.sh && source lib/detect.sh && source lib/repo.sh && source installers/{script_name}.sh && install_{script_name}"
    if extra_args:
        cmd += f" {' '.join(extra_args)}"
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    try:
        process = subprocess.Popen(
            ["bash", "-c", cmd],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=env, bufsize=0
        )
        
        while True:
            char = process.stdout.read(1)
            if not char and process.poll() is not None: break
            if char:
                decoded = char.decode('utf-8', errors='ignore')
                # Filtramos para que no se vea desordenado
                if decoded == '\n':
                    sys.stdout.write('\n     [dim]• [/]')
                else:
                    sys.stdout.write(decoded)
                sys.stdout.flush()
            
        process.wait()
        return process.returncode == 0
    except Exception as e:
        console.print(f"\n  [bold red]ERROR[/] {e}")
        return False

# ─────────────────────────────────────────────────────────────
#   Main Entry Point
# ─────────────────────────────────────────────────────────────

def main():
    # 1. Selección de Componentes
    global states
    states = interactive_select("Components", COMPONENTS, multi=True, initial_states=states)

    # 2. Configuración de Versiones
    selected_versions = {}
    if states['php']:
        opts = [{"id": v, "name": f"PHP {v}"} for v in ["8.4", "8.3", "8.2", "8.1"]]
        selected_versions['php'] = interactive_select("PHP Engine", opts)
    
    if states['node']:
        opts = [{"id": v, "name": f"Node.js {v}"} for v in ["22", "20", "18", "lts", "node"]]
        selected_versions['node'] = interactive_select("Node.js Version", opts)

    # 3. Confirmación y Sudo
    console.clear()
    console.print(get_header())
    console.print("\n  [bold yellow]PRIVILEGE ESCALATION[/]")
    console.print("  [dim]Authentication required to apply system changes.[/]\n")
    try:
        subprocess.run(["sudo", "-v"], check=True)
    except:
        sys.exit(1)

    # 4. Ejecución
    selected_list = [c for c in COMPONENTS if states[c['id']]]
    
    with Progress(
        TextColumn("  [bold cyan]{task.description:<30}"),
        BarColumn(bar_width=40, style="#222222", complete_style="cyan"),
        TextColumn("[bold white]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        
        overall_task = progress.add_task("Total Progress", total=len(selected_list))
        
        for c in selected_list:
            progress.update(overall_task, description=f"Installing {c['name']}")
            
            args = []
            if c['id'] == 'php': args = [selected_versions['php']]
            if c['id'] == 'node': args = [selected_versions['node']]
            
            # Detenemos temporalmente el progreso para mostrar el log limpio
            progress.stop()
            success = run_bash_cmd(c['name'], c['id'], args)
            progress.start()
            
            if not success:
                console.print(f"\n  [bold red]✖ {c['name']} failed.[/]")
                sys.exit(1)
            
            progress.advance(overall_task)
        
        progress.update(overall_task, description="All systems ready")

    console.print("\n\n" + Align.center(Text("✨ DEPLOYMENT SUCCESSFUL", style="bold green")))
    console.print(Align.center(Text("Environment is optimized. Please restart your terminal.", style="dim")))
    console.print("\n")

if __name__ == "__main__":
    main()
