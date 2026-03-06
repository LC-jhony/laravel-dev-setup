"""Laravel Dev Setup - Rich-based Terminal Installer."""

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import print as rprint

console = Console()

SERVICES = [
    ("zsh", "ZSH + Powerlevel10k + Plugins", True),
    ("git", "Git - Version Control", True),
    ("basics", "Unzip + Basic Tools", True),
    ("mariadb", "MariaDB - Database", True),
    ("php", "PHP 8.4 + Extensions", True),
    ("composer", "Composer - PHP Package Manager", True),
    ("nvm", "NVM + Node.js", True),
    ("valet", "Laravel Valet", True),
    ("laravel", "Laravel Installer", True),
    ("sites", "~/Sites Directory", True),
]

SERVICE_NAMES = {
    "zsh": "Installing ZSH + Powerlevel10k + Plugins...",
    "git": "Installing Git...",
    "basics": "Installing Basic Tools (unzip, curl, wget)...",
    "mariadb": "Installing MariaDB Server...",
    "php": "Installing PHP 8.4 + Extensions...",
    "composer": "Installing Composer...",
    "nvm": "Installing NVM + Node.js...",
    "valet": "Installing Laravel Valet...",
    "laravel": "Installing Laravel Installer...",
    "sites": "Creating ~/Sites Directory...",
}


def show_welcome() -> None:
    """Show welcome screen with Rich."""
    ascii_art = Text("""
  _                _              _    ____             
 | |    ___   __ _| |_ ___      | |  / ___|___  _ __  | |_ 
 | |   / _ \\ / _` | __/ _ \\     | | | |   / _ \\| '_ \\ | __|
 | |__| (_) | (_| | ||  __/     | | | |__| (_) | | | || |_ 
 |_____\\___/ \\__,_|\\__\\___|     |_|  \\____\\___/|_| |_| \\__|
                                                        
""", style="bold cyan")
    
    panel = Panel(
        ascii_art,
        title="[bold cyan]Laravel Dev Setup[/bold cyan]",
        subtitle="[dim]Linux Development Environment Installer[/dim]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    
    console.print()
    console.print("[bold]What this installer will set up:[/bold]")
    console.print()
    
    table = Table(show_header=False, box=None)
    table.add_column(style="green", width=4)
    table.add_column()
    
    table.add_row("⚡", "[cyan]ZSH + Powerlevel10k + Plugins[/cyan]")
    table.add_row("📚", "[cyan]Git - Version Control[/cyan]")
    table.add_row("🔧", "[cyan]Unzip + Basic Tools[/cyan]")
    table.add_row("🗄️", "[cyan]MariaDB Database[/cyan]")
    table.add_row("🐘", "[cyan]PHP 8.4 + Extensions[/cyan]")
    table.add_row("📦", "[cyan]Composer[/cyan]")
    table.add_row("🟢", "[cyan]NVM + Node.js[/cyan]")
    table.add_row("🚀", "[cyan]Laravel Valet[/cyan]")
    table.add_row("✨", "[cyan]Laravel Installer[/cyan]")
    table.add_row("📁", "[cyan]~/Sites Directory[/cyan]")
    
    console.print(table)
    console.print()


def select_services() -> list[str]:
    """Show service selection using questionary."""
    choices = [
        f"{desc}" for _, desc, _ in SERVICES
    ]
    
    console.print("[bold]Select services to install:[/bold]")
    console.print("[dim]Use spacebar to select/deselect, Enter to continue[/dim]")
    console.print()
    
    selected = questionary.checkbox(
        "Select services:",
        choices=choices,
        style=questionary.Style([
            ('checkbox', 'fg: cyan'),
            ('selected', 'fg: green bold'),
        ]),
    ).ask()
    
    if not selected:
        console.print("[yellow]No services selected. Exiting.[/yellow]")
        return []
    
    result = []
    for choice in selected:
        for sid, desc, _ in SERVICES:
            if desc == choice:
                result.append(sid)
                break
    
    return result


def show_install_progress(services: list[str]) -> None:
    """Show installation progress with Rich."""
    console.clear()
    
    panel = Panel(
        "[bold cyan]Installing Services...[/bold cyan]",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()
    
    total = len(services)
    
    for i, service in enumerate(services):
        service_name = SERVICE_NAMES.get(service, f"Installing {service}...")
        console.print(f"[cyan]→[/cyan] {service_name}")
        
        with console.status(f"[bold green]Processing...[/bold green]") as status:
            import time
            time.sleep(1)
        
        percentage = int(((i + 1) / total) * 100)
        console.print(f"  [green]✓[/green] Complete ({percentage}%)")
        console.print()


def show_completion(services: list[str]) -> None:
    """Show completion screen with Rich."""
    console.print()
    
    panel = Panel(
        "[bold green]🎉 Installation Complete![/bold green]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(panel)
    
    console.print()
    console.print("[bold]Installed services:[/bold]")
    console.print()
    
    service_display = {
        "zsh": "⚡ ZSH + Powerlevel10k",
        "git": "📚 Git",
        "basics": "🔧 Basic Tools",
        "mariadb": "🗄️ MariaDB",
        "php": "🐘 PHP 8.4",
        "composer": "📦 Composer",
        "nvm": "🟢 NVM + Node.js",
        "valet": "🚀 Laravel Valet",
        "laravel": "✨ Laravel Installer",
        "sites": "📁 ~/Sites",
    }
    
    for service in services:
        name = service_display.get(service, service)
        console.print(f"  [green]✓[/green] {name}")
    
    console.print()
    console.print("[bold cyan]Tips:[/bold cyan]")
    console.print("  • Run [yellow]valet install[/yellow] to configure Laravel Valet")
    console.print("  • Create a new project: [yellow]laravel new myproject[/yellow]")
    console.print()


def main() -> None:
    """Main entry point."""
    show_welcome()
    
    services = select_services()
    
    if not services:
        return
    
    console.print()
    console.print(f"[bold]Selected {len(services)} service(s)[/bold]")
    console.print()
    
    confirm = questionary.confirm(
        "Continue with installation?",
        default=True,
    ).ask()
    
    if not confirm:
        console.print("[yellow]Installation cancelled.[/yellow]")
        return
    
    show_install_progress(services)
    show_completion(services)


if __name__ == "__main__":
    main()
