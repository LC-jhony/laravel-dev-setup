import os
import sys
import subprocess
import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.prompt import Prompt
from rich import box
from rich.align import Align
from rich.text import Text
from rich.style import Style

console = Console()

# ─────────────────────────────────────────────────────────────
#   Config & State
# ─────────────────────────────────────────────────────────────

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "desc": "Zsh + P10k + Modern CLI Tools", "icon": "🐚"},
    {"id": "php",      "name": "PHP Engine",        "desc": "Versions 8.1 - 8.4 + Extensions", "icon": "🐘"},
    {"id": "mariadb",  "name": "MariaDB Database",  "desc": "SQL Server + Security Wizard", "icon": "🗄️ "},
    {"id": "node",     "name": "Node.js (NVM)",     "desc": "Node LTS & Package Manager", "icon": "🟢"},
    {"id": "composer", "name": "PHP Composer",      "desc": "Global Dependency Management", "icon": "📦"},
    {"id": "valet",    "name": "Laravel Valet",     "desc": "Local Development Server", "icon": "⚡"},
]

states = {c["id"]: True for c in COMPONENTS}
current_index = 0

# ─────────────────────────────────────────────────────────────
#   UI Components
# ─────────────────────────────────────────────────────────────

def get_header():
    title = Text.assemble(
        ("LARAVEL", "bold cyan"), " ", ("DEV", "bold white"), " ", ("SETUP", "bold magenta")
    )
    subtitle = Text("Professional Development Environment Bootstrap", style="dim")
    
    header_content = VerticalGroup(
        Align.center(title),
        Align.center(subtitle)
    )
    
    return Panel(header_content, style="cyan", box=box.HORIZONTALS, padding=(1, 0))

class VerticalGroup:
    def __init__(self, *renderables):
        self.renderables = renderables
    def __rich__(self):
        from rich.console import Group
        return Group(*self.renderables)

def get_dashboard():
    table = Table(box=None, expand=True, show_header=False, padding=(0, 2))
    table.add_column("Status", width=6)
    table.add_column("Icon", width=4)
    table.add_column("Details")

    for i, c in enumerate(COMPONENTS):
        cid = c["id"]
        is_selected = states[cid]
        is_active = (i == current_index)
        
        # Style logic
        check_mark = "✅" if is_selected else "⬜"
        name_style = "bold white" if is_selected else "dim"
        if is_active:
            name_style = "bold reverse cyan"
            row_style = "on #222222"
        else:
            row_style = ""

        name_text = Text.assemble(
            (f" {c['name']} ", name_style),
            ("\n   " + c['desc'], "dim italic")
        )

        table.add_row(
            Align.center(check_mark),
            Align.center(c['icon']),
            name_text,
            style=row_style
        )
    
    return Panel(
        table, 
        title="[bold white]COMPONENTS[/]", 
        border_style="dim",
        padding=(1, 1)
    )

def get_footer():
    shortcuts = [
        ("[bold magenta]↑/↓[/]", "Navigate"),
        ("[bold magenta]Space[/]", "Toggle"),
        ("[bold green]Enter[/]", "Install"),
        ("[bold red]Q[/]", "Quit")
    ]
    parts = [f"{key} {desc}" for key, desc in shortcuts]
    return Panel(Align.center("  •  ".join(parts)), style="dim", box=box.SIMPLE)

def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(get_header(), size=5),
        Layout(get_dashboard(), name="main"),
        Layout(get_footer(), size=3)
    )
    return layout

# ─────────────────────────────────────────────────────────────
#   Installation Logic
# ─────────────────────────────────────────────────────────────

def run_bash_cmd(cmd_label, script_name, extra_args=None):
    console.print(f"\n[bold cyan]▶[/] [white]Installing:[/] [bold cyan]{cmd_label}[/]")
    
    cmd = f"source lib/ui.sh && source lib/detect.sh && source lib/repo.sh && source installers/{script_name}.sh && install_{script_name}"
    if extra_args:
        cmd += f" {' '.join(extra_args)}"
    
    try:
        process = subprocess.Popen(
            ["bash", "-c", cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        for line in process.stdout:
            sys.stdout.write(f"  [dim]│[/] {line}")
            sys.stdout.flush()
            
        process.wait()
        return process.returncode == 0
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        return False

# ─────────────────────────────────────────────────────────────
#   Main Execution
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
            if ch == '\x1b':
                ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    # Keyboard loop
    with Live(make_layout(), auto_refresh=False, screen=True) as live:
        while True:
            key = getch()
            
            if key == '\x1b[A': # Up
                current_index = (current_index - 1) % len(COMPONENTS)
            elif key == '\x1b[B': # Down
                current_index = (current_index + 1) % len(COMPONENTS)
            elif key == ' ': # Toggle
                cid = COMPONENTS[current_index]["id"]
                states[cid] = not states[cid]
            elif key in ('\r', '\n'): # Enter
                break
            elif key.lower() == 'q':
                sys.exit(0)
            
            live.update(make_layout(), refresh=True)

    # Final review
    console.clear()
    console.print(get_header())
    
    selected = [c for c in COMPONENTS if states[c["id"]]]
    if not selected:
        console.print("\n[yellow]No components selected. Exiting.[/]")
        return

    # Sudo Auth
    console.print(Panel("[bold yellow]Password Required[/]\n[dim]The installer needs sudo privileges to continue.", box=box.ROUNDED, expand=False))
    subprocess.run(["sudo", "-v"], check=True)

    # Start Progress
    for c in selected:
        args = None
        if c["id"] == "php":
            console.print("")
            version = Prompt.ask("[bold cyan]?[/] [white]Choose PHP Version[/]", choices=["8.5", "8.4", "8.3", "8.2", "8.1"], default="8.4")
            args = [version]
        
        success = run_bash_cmd(c["name"], c["id"], args)
        if not success:
            console.print(f"\n[bold red]FATAL:[/] {c['name']} failed. Check logs above.")
            sys.exit(1)

    console.print("\n" + Panel.fit("[bold green]✨ EVERYTHING IS READY! ✨[/]\n[dim]Log out and back in to apply all changes.", border_style="green", padding=(1, 5)))

if __name__ == "__main__":
    main()
