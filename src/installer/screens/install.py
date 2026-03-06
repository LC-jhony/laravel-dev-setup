"""Installation progress screen."""

import asyncio

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, ProgressBar


class InstallScreen(Screen):
    """Screen showing installation progress."""

    DEFAULT_CSS = """
    InstallScreen {
        align: center middle;
    }

    #install-container {
        width: 70;
        height: auto;
        border: solid $primary;
        padding: 2 4;
    }

    #title {
        text-style: bold;
        text-align: center;
        color: $accent;
        margin-bottom: 2;
    }

    #status {
        text-align: center;
        margin-bottom: 1;
    }

    #current-task {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    #progress-container {
        width: 100%;
        margin-bottom: 2;
    }

    #logs {
        height: 10;
        border: solid $surface;
        padding: 1;
        margin-bottom: 2;
    }

    #cancel-button {
        width: 100%;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._running = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Static(id="install-container"):
            yield Static("Installing Services", id="title")
            yield Static("0%", id="status")
            yield Static("Preparing...", id="current-task")
            yield ProgressBar(total=100, show_eta=False, id="progress")
            yield Static("", id="logs")
            yield Button("Cancel", id="cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        """Start the installation when the screen mounts."""
        self._running = True
        asyncio.create_task(self._run_installation())

    async def _run_installation(self) -> None:
        """Run the installation process."""
        services = self.app.selected_services
        total = len(services)
        
        status = self.query_one("#status", Static)
        current_task = self.query_one("#current-task", Static)
        progress = self.query_one("#progress", ProgressBar)
        logs = self.query_one("#logs", Static)
        
        for i, service in enumerate(services):
            if not self._running:
                break
                
            service_names = {
                "zsh": "Installing ZSH + Powerlevel10k + Plugins...",
                "git": "Installing Git...",
                "basics": "Installing Basic Tools...",
                "mariadb": "Installing MariaDB...",
                "php": "Installing PHP 8.4 + Extensions...",
                "composer": "Installing Composer...",
                "nvm": "Installing NVM + Node.js...",
                "valet": "Installing Laravel Valet...",
                "laravel": "Installing Laravel Installer...",
                "sites": "Creating ~/Sites Directory...",
            }
            
            task_name = service_names.get(service, f"Installing {service}...")
            current_task.update(task_name)
            logs.update(f"{logs.renderable}\n{task_name}")
            
            await asyncio.sleep(1)
            
            progress.advance(1)
            percentage = int(((i + 1) / total) * 100)
            status.update(f"{percentage}%")
        
        if self._running:
            self.app.push_screen("done")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "cancel":
            self._running = False
            self.app.pop_screen()
