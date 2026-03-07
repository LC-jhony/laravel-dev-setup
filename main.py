import os
import sys
import subprocess
import time
from rich.console import Console
from rich.live import Live
from rich.prompt import Prompt
from rich import box
from rich.align import Align
from rich.text import Text
from rich.rule import Rule
from rich.console import Group
from rich.style import Style

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
current_index = 0

# ─────────────────────────────────────────────────────────────
#   UI Components (Minimalist Pro)
# ─────────────────────────────────────────────────────────────

def get_header():
    # Spaced out header for a modern boutique look
    title = Text("L A R A V E L   D E V   S E T U P", style="bold cyan")
    subtitle = Text("PREMIUM ENVIRONMENT BOOTSTRAP", style="dim italic")
    
    return Group(
        Text("\n"),
        Align.center(title),
        Align.center(subtitle),
        Text("\n"),
        Rule(style="dim #333333")
    )

def get_menu_content():
    items = []
    items.append(Text("\n")) # Top padding
    
    for i, c in enumerate(COMPONENTS):
        is_active = (i == current_index)
        is_selected = states[c["id"]]
        
        # Iconography: High contrast circular symbols
        # ● = Enabled, ○ = Disabled
        if is_selected:
            mark = " ● "
            mark_style = "bold cyan"
        else:
            mark = " ○ "
            mark_style = "dim"
            
        # Selection Indicator & Line Background
        # We use a subtle vertical bar and high contrast text for focus
        line = Text()
        
        if is_active:
            # Active focus state
            line.append("  ┃ ", style="bold cyan")
            line.append(mark, style=mark_style)
            line.append(f"{c['name']:<25}", style="bold white")
            line.append(f" {c['desc']}", style="dim")
            # Wrap the line in a centered align later
        else:
            # Idle state
            line.append("    ", style="dim")
            line.append(mark, style=mark_style)
            line.append(f"{c['name']:<25}", style="dim" if not is_selected else "white")
            line.append(f" {c['desc']}", style="dim italic")
        
        items.append(line)
        items.append(Text("\n")) # List item spacing

    return Align.center(Group(*items))

def get_footer():
    # Tenue and elegant footer
    shortcuts = [
        ("↑↓", "Navigate"),
        ("SPACE", "Toggle"),
        ("ENTER", "Initialize"),
        ("Q", "Quit")
    ]
    
    footer_text = Text()
    for i, (key, action) in enumerate(shortcuts):
        footer_text.append(f" {key} ", style="bold cyan")
        footer_text.append(f"{action}", style="dim")
        if i < len(shortcuts) - 1:
            footer_text.append("   •  ", style="dim #333333")
            
    return Group(
        Rule(style="dim #333333"),
        Align.center(footer_text),
        Text("\n")
    )

def draw_main_ui():
    return Group(
        get_header(),
        get_menu_content(),
        get_footer()
    )

# ─────────────────────────────────────────────────────────────
#   Execution Logic
# ─────────────────────────────────────────────────────────────

def run_bash_cmd(cmd_label, script_name, extra_args=None):
    # Minimalist execution banner
    console.print(f"\n  [bold cyan]INITIALIZING[/] [white]{cmd_label}[/]")
    console.print(f"  [dim]──────────────────────────────────────────────────[/]")
    
    # We define SUDO=sudo to ensure scripts have the correct variable
    cmd = f"export SUDO=sudo && source lib/ui.sh && source lib/detect.sh && source lib/repo.sh && source installers/{script_name}.sh && install_{script_name}"
    if extra_args:
        cmd += f" {' '.join(extra_args)}"
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["LANG"] = "en_US.UTF-8"
    
    try:
        # We use binary mode and decode manually to handle special characters correctly
        process = subprocess.Popen(
            ["bash", "-c", cmd],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=env, bufsize=0
        )
        
        while True:
            char = process.stdout.read(1)
            if not char and process.poll() is not None:
                break
            if char:
                try:
                    # Decode with 'replace' to avoid crashing on partial multi-byte sequences
                    decoded = char.decode('utf-8', errors='replace')
                    # Prepend indentation for a clean UI look
                    if decoded == '\n':
                        sys.stdout.write('\n  [dim]│ [/]')
                    else:
                        sys.stdout.write(decoded)
                    sys.stdout.flush()
                except:
                    pass
            
        process.wait()
        
        if process.returncode == 0:
            console.print(f"\n  [bold green]SUCCESS[/] [dim]{cmd_label} configured.[/]")
        else:
            console.print(f"\n  [bold red]FAILURE[/] [dim]Installation interrupted.[/]")
            
        return process.returncode == 0
    except Exception as e:
        console.print(f"\n  [bold red]ERROR[/] [dim]{e}[/]")
        return False

# ─────────────────────────────────────────────────────────────
#   Main Entry Point
# ─────────────────────────────────────────────────────────────

def main():
    global current_index
    import tty, termios
    
    # Utility for raw keyboard input
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

    # Interaction Loop
    with Live(draw_main_ui(), auto_refresh=False, screen=True) as live:
        while True:
            key = getch()
            
            # Navigation
            if key == '\x1b[A': # Up
                current_index = (current_index - 1) % len(COMPONENTS)
            elif key == '\x1b[B': # Down
                current_index = (current_index + 1) % len(COMPONENTS)
            
            # Toggling
            elif key == ' ':
                cid = COMPONENTS[current_index]["id"]
                states[cid] = not states[cid]
            
            # Confirmation
            elif key in ('\r', '\n'):
                break
                
            # Exit
            elif key.lower() == 'q':
                sys.exit(0)
                
            live.update(draw_main_ui(), refresh=True)

    # Summary and Sudo
    console.clear()
    console.print(get_header())
    
    selected = [c for c in COMPONENTS if states[c["id"]]]
    if not selected:
        console.print("\n  [yellow]No items selected. Exiting.[/]\n")
        return

    # Modern Sudo Prompt
    console.print("\n  [bold yellow]PRIVILEGE ESCALATION[/]")
    console.print("  [dim]System password required for deployment.[/]\n")
    try:
        subprocess.run(["sudo", "-v"], check=True)
    except:
        console.print("\n  [bold red]ABORTED[/] [dim]Authentication failed.[/]\n")
        sys.exit(1)

    # Process Deployment
    for c in selected:
        args = None
        if c["id"] == "php":
            console.print("\n")
            version = Prompt.ask("  [bold cyan]?[/] [white]Select PHP Engine[/]", choices=["8.4", "8.3", "8.2", "8.1"], default="8.4")
            args = [version]
        
        if c["id"] == "node":
            console.print("\n")
            # We allow common LTS versions, numeric versions or 'lts'
            version = Prompt.ask("  [bold cyan]?[/] [white]Select Node.js Version[/]", choices=["22", "20", "18", "lts", "node"], default="lts")
            args = [version]
        
        if not run_bash_cmd(c["name"], c["id"], args):
            sys.exit(1)

    # Final Success Message
    console.print("\n\n" + "  [bold green]DEPLOYMENT COMPLETE[/]")
    console.print("  [dim]The environment has been optimized and is ready for use.[/]\n")
    console.print("  [dim]Please restart your terminal session.[/]\n")

if __name__ == "__main__":
    main()
