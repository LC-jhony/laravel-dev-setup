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

console = Console()

# ─────────────────────────────────────────────────────────────
#   Config & State
# ─────────────────────────────────────────────────────────────

COMPONENTS = [
    {"id": "shell",    "name": "Shell Environment", "desc": "Zsh + P10k + Modern CLI Tools"},
    {"id": "php",      "name": "PHP Engine",        "desc": "Custom Versions & Extensions"},
    {"id": "mariadb",  "name": "MariaDB Database",  "desc": "SQL Server + Security Wizard"},
    {"id": "node",     "name": "Node.js (NVM)",     "desc": "Node LTS & Package Manager"},
    {"id": "composer", "name": "PHP Composer",      "desc": "Global Dependency Management"},
    {"id": "valet",    "name": "Laravel Valet",     "desc": "Elite Local Development Server"},
]

states = {c["id"]: True for c in COMPONENTS}
current_index = 0

# ─────────────────────────────────────────────────────────────
#   UI Components
# ─────────────────────────────────────────────────────────────

def get_header():
    title = "[bold cyan]██╗      █████╗ ██████╗  █████╗ ██╗   ██╗███████╗██╗     \n" \
            "██║     ██╔══██╗██╔══██╗██╔══██╗██║   ██║██╔════╝██║     \n" \
            "██║     ███████║██████╔╝███████║██║   ██║█████╗  ██║     \n" \
            "██║     ██╔══██║██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║     \n" \
            "███████╗██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████╗\n" \
            "╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝[/]"
    return Panel(Align.center(title), style="cyan", box=box.ROUNDED)

def get_dashboard_table():
    table = Table(box=None, expand=True)
    table.add_column("State", width=8, justify="center")
    table.add_column("ID", width=4, justify="right", style="dim")
    table.add_column("Component", style="bold white")
    table.add_column("Description", style="dim italic")

    for i, c in enumerate(COMPONENTS):
        cid = c["id"]
        checkbox = "[green]● [✔][/]" if states[cid] else "[dim]○ [ ][/]"
        
        # Highlight current cursor
        prefix = "[bold magenta]➜[/] " if i == current_index else "  "
        
        style = "on #333333" if i == current_index else ""
        table.add_row(
            prefix + checkbox,
            str(i + 1),
            c["name"],
            c["desc"],
            style=style
        )
    
    return Panel(table, title="[bold white]DASHBOARD: COMPONENT SELECTION[/]", subtitle="[dim]Use [bold white]↑/↓[/] to navigate · [bold white]Space[/] to toggle · [bold white]Enter[/] to Install · [bold white]Q[/] to Quit[/]", box=box.ROUNDED)

def run_bash_cmd(cmd_label, script_name, extra_args=None):
    console.print(f"\n[bold blue]➜[/] Installing [bold white]{cmd_label}[/]...")
    
    # We call bash to source the installer and run the function
    # Example: source installers/php.sh && install_php
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
            sys.stdout.write(f"   [dim]│[/] {line}")
            sys.stdout.flush()
            
        process.wait()
        if process.returncode == 0:
            console.print(f"   [bold green]✔[/] {cmd_label} installed successfully.")
        else:
            console.print(f"   [bold red]✘[/] {cmd_label} installation failed.")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error executing {cmd_label}: {e}[/]")
        sys.exit(1)

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
            if ch == '\x1b': # arrow keys
                ch += sys.stdin.read(2)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    with Live(auto_refresh=True) as live:
        while True:
            layout = Layout()
            layout.split_column(
                Layout(get_header(), size=8),
                Layout(get_dashboard_table())
            )
            live.update(layout)
            
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
            elif key.isdigit():
                idx = int(key) - 1
                if 0 <= idx < len(COMPONENTS):
                    cid = COMPONENTS[idx]["id"]
                    states[cid] = not states[cid]

    # Final Summary before installation
    console.clear()
    console.print(get_header())
    
    summary_table = Table(title="[bold white]READY TO DEPLOY[/]", box=box.ROUNDED)
    summary_table.add_column("Component", style="bold white")
    summary_table.add_column("Status", justify="center")
    
    selected_any = False
    for c in COMPONENTS:
        if states[c["id"]]:
            summary_table.add_row(c["name"], "[green]READY[/]")
            selected_any = True
            
    if not selected_any:
        console.print("[yellow]No components selected. Exiting.[/]")
        sys.exit(0)
        
    console.print(Align.center(summary_table))
    
    if Prompt.ask("\n[bold white]Begin installation?[/]", choices=["y", "n"], default="y") != "y":
        sys.exit(0)

    # Trigger Sudo
    console.print("\n[bold yellow]! Authentication Required[/]")
    subprocess.run(["sudo", "-v"], check=True)

    # Start Installation
    for c in COMPONENTS:
        if states[c["id"]]:
            # Special case for PHP version choice
            if c["id"] == "php":
                php_version = Prompt.ask("   Select PHP Version", choices=["8.5", "8.4", "8.3", "8.2", "8.1"], default="8.4")
                run_bash_cmd(c["name"], c["id"], [php_version])
            else:
                run_bash_cmd(c["name"], c["id"])

    console.print("\n[bold green]🎉 INSTALLATION COMPLETED SUCCESSFULLY![/]")

if __name__ == "__main__":
    main()
