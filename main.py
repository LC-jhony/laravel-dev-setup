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
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
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
        line = Text()
        
        if is_active:
            # Active focus state
            line.append("  ┃ ", style="bold cyan")
            line.append(mark, style=mark_style)
            line.append(f"{c['name']:<25}", style="bold white")
            line.append(f" {c['desc']}", style="dim")
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

def run_bash_cmd(cmd_label, script_name, extra_args=None, progress=None, task_id=None):
    # Minimalist execution banner
    if not progress:
        console.print(f"\n  [bold cyan]INITIALIZING[/] [white]{cmd_label}[/]")
        console.print(f"  [dim]──────────────────────────────────────────────────[/]")
    
    # Base command: load environment and installer
    cmd_parts = [
        "export SUDO=sudo",
        "source lib/ui.sh",
        "source lib/detect.sh",
        "source lib/repo.sh",
        f"source installers/{script_name}.sh",
        "detect_os"
    ]
    
    # Specific logic for components
    if script_name == "php":
        version = extra_args[0] if extra_args else "8.4"
        cmd_parts.append("setup_repo")
        cmd_parts.append(f"install_php {version}")
        cmd_parts.append(f"set_default_php {version}")
    else:
        call_cmd = f"install_{script_name}"
        if extra_args:
            call_cmd += f" {' '.join(extra_args)}"
        cmd_parts.append(call_cmd)
    
    cmd = " && ".join(cmd_parts)
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["LANG"] = "en_US.UTF-8"
    
    try:
        process = subprocess.Popen(
            ["bash", "-c", cmd],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            env=env, bufsize=0
        )
        
        line_buffer = ""
        while True:
            char = process.stdout.read(1)
            if not char and process.poll() is not None:
                break
            if char:
                try:
                    decoded = char.decode('utf-8', errors='replace')
                    line_buffer += decoded
                    if decoded == '\n':
                        clean_line = line_buffer.replace('\n', '').replace('\r', '')
                        if progress:
                            progress.console.print(f"  [dim]│[/] {clean_line}")
                        else:
                            sys.stdout.write(f"  [dim]│ [/]{line_buffer}")
                            sys.stdout.flush()
                        line_buffer = ""
                except:
                    pass
            
        process.wait()
        
        if process.returncode == 0:
            if not progress:
                console.print(f"\n  [bold green]SUCCESS[/] [dim]{cmd_label} configured.[/]")
        else:
            if not progress:
                console.print(f"\n  [bold red]FAILURE[/] [dim]Installation interrupted.[/]")
            
        return process.returncode == 0
    except Exception as e:
        if progress:
            progress.console.print(f"\n  [bold red]ERROR[/] [dim]{e}[/]")
        else:
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

    # Setup Progress Display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, style="dim", complete_style="cyan"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        expand=False
    ) as progress:
        
        overall_task = progress.add_task("[bold white]Overall Deployment", total=len(selected))
        
        for c in selected:
            args = None
            if c["id"] == "php":
                progress.stop() # Pause progress to ask
                console.print("\n")
                version = Prompt.ask("  [bold cyan]?[/] [white]Select PHP Engine[/]", choices=["8.4", "8.3", "8.2", "8.1"], default="8.4")
                args = [version]
                progress.start()
            
            if c["id"] == "node":
                progress.stop()
                console.print("\n")
                version = Prompt.ask("  [bold cyan]?[/] [white]Select Node.js Version[/]", choices=["22", "20", "18", "lts", "node"], default="lts")
                args = [version]
                progress.start()

            # Add a specific task for this component
            comp_task = progress.add_task(f"[cyan]Installing {c['name']}...", total=None)
            
            success = run_bash_cmd(c["name"], c["id"], args, progress, comp_task)
            
            if success:
                progress.update(comp_task, description=f"[green]✓ {c['name']} Complete", completed=100, total=100)
                progress.advance(overall_task)
            else:
                progress.update(comp_task, description=f"[red]✗ {c['name']} Failed")
                sys.exit(1)

    # Final Success Message
    console.print("\n\n" + "  [bold green]DEPLOYMENT COMPLETE[/]")
    console.print("  [dim]The environment has been optimized and is ready for use.[/]\n")
    console.print("  [dim]Please restart your terminal session.[/]\n")


if __name__ == "__main__":
    main()
