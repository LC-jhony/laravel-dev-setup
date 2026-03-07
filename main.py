import os
import sys
import subprocess
import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.prompt import Prompt
from rich import box
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.console import Group

console = Console()

# ─────────────────────────────────────────────────────────────
#   Config & State
# ─────────────────────────────────────────────────────────────

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "desc": "Zsh + P10k + Modern Tools"},
    {"id": "php",      "name": "PHP Engine",        "desc": "PHP 8.1 - 8.4 + Extensions"},
    {"id": "mariadb",  "name": "MariaDB Database",  "desc": "SQL Server + Security Wizard"},
    {"id": "node",     "name": "Node.js (NVM)",     "desc": "Node LTS & Package Manager"},
    {"id": "composer", "name": "PHP Composer",      "desc": "Dependency Management"},
    {"id": "valet",    "name": "Laravel Valet",     "desc": "Local Dev Server"},
]

states = {c["id"]: True for c in COMPONENTS}
current_index = 0

# ─────────────────────────────────────────────────────────────
#   UI Components (Minimalist)
# ─────────────────────────────────────────────────────────────

def get_header():
    return Group(
        Text("\n"),
        Align.center(Text("LARAVEL DEV SETUP", style="bold cyan tracking5")),
        Align.center(Text("minimalist installer engine", style="dim italic")),
        Text("\n"),
        Rule(style="dim")
    )

def get_menu_content():
    items = []
    items.append(Text("\n"))
    
    for i, c in enumerate(COMPONENTS):
        is_active = (i == current_index)
        is_selected = states[c["id"]]
        
        # Select markers: ● (selected) ○ (unselected)
        mark = "●" if is_selected else "○"
        mark_style = "cyan" if is_selected else "dim"
        
        # Focus bar
        focus = "  ┃ " if is_active else "    "
        
        # Build the line
        line = Text()
        line.append(focus, style="bold cyan" if is_active else "dim")
        line.append(f"{mark} ", style=mark_style)
        
        name_style = "bold white" if is_active else ("white" if is_selected else "dim")
        line.append(f"{c['name']:<25}", style=name_style)
        line.append(f" {c['desc']}", style="dim italic")
        
        items.append(line)
        items.append(Text("\n")) # Spacing

    return Align.center(Group(*items))

def get_footer():
    shortcuts = [
        ("↑↓", "Move"),
        ("SPC", "Toggle"),
        ("ENT", "Install"),
        ("Q", "Quit")
    ]
    text = Text()
    for key, action in shortcuts:
        text.append(f" {key} ", style="bold cyan")
        text.append(f"{action}  ", style="dim")
    return Align.center(text)

def draw_main_ui():
    return Group(
        get_header(),
        get_menu_content(),
        Rule(style="dim"),
        get_footer()
    )

# ─────────────────────────────────────────────────────────────
#   Execution Engine
# ─────────────────────────────────────────────────────────────

def run_bash_cmd(cmd_label, script_name, extra_args=None):
    console.print(f"\n[bold cyan]─── {cmd_label} [/][dim]───────────────────────────────────────[/]")
    
    cmd = f"source lib/ui.sh && source lib/detect.sh && source lib/repo.sh && source installers/{script_name}.sh && install_{script_name}"
    if extra_args:
        cmd += f" {' '.join(extra_args)}"
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    try:
        process = subprocess.Popen(
            ["bash", "-c", cmd],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1, universal_newlines=True,
            errors="replace", env=env
        )
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None: break
            if line:
                sys.stdout.write(f"  [dim]│[/] {line}")
                sys.stdout.flush()
            
        process.wait()
        return process.returncode == 0
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        return False

# ─────────────────────────────────────────────────────────────
#   Main Loop
# ─────────────────────────────────────────────────────────────

def main():
    global current_index
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

    with Live(draw_main_ui(), auto_refresh=False, screen=True) as live:
        while True:
            key = getch()
            if key == '\x1b[A': current_index = (current_index - 1) % len(COMPONENTS)
            elif key == '\x1b[B': current_index = (current_index + 1) % len(COMPONENTS)
            elif key == ' ': states[COMPONENTS[current_index]["id"]] = not states[COMPONENTS[current_index]["id"]]
            elif key in ('\r', '\n'): break
            elif key.lower() == 'q': sys.exit(0)
            live.update(draw_main_ui(), refresh=True)

    console.clear()
    selected = [c for c in COMPONENTS if states[c["id"]]]
    if not selected: return

    console.print(Text("\n  INITIALIZING SETUP\n", style="bold cyan"))
    subprocess.run(["sudo", "-v"], check=True)

    for c in selected:
        args = None
        if c["id"] == "php":
            version = Prompt.ask("\n  [cyan]?[/] [white]PHP Version[/]", choices=["8.4", "8.3", "8.2"], default="8.4")
            args = [version]
        
        if not run_bash_cmd(c["name"], c["id"], args):
            console.print(f"\n[bold red]✖ {c['name']} failed.[/]")
            sys.exit(1)

    console.print(Text("\n\n  ✨ SETUP COMPLETE", style="bold green"))
    console.print(Text("  Re-login to apply changes.\n", style="dim"))

if __name__ == "__main__":
    main()
