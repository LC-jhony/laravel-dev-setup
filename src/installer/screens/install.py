"""Installation progress screen."""

import asyncio

from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, ProgressBar, Spinner


class InstallScreen(Screen):
    """Screen showing installation progress."""

    DEFAULT_CSS = """
    InstallScreen {
        align: center middle;
    }

    #title {
        text-style: bold;
        text-align: center;
        color: $accent;
    }

    #current-task {
        text-align: center;
        color: $text;
        margin: 1 0;
    }

    #progress-container {
        width: 50;
        margin: 2 0;
    }

    ProgressBar {
        height: 2;
    }

    #status-text {
        text-align: center;
        color: $success;
        text-style: bold;
    }

    #logs {
        width: 60;
        height: 8;
        border: solid $primary;
        background: $panel;
        padding: 1;
    }

    #logs Static {
        color: $text-muted;
    }

    #cancel-button {
        width: 20;
        margin-top: 2;
    }

    Spinner {
        margin-bottom: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._running = False
        self._log_lines: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Middle():
            with Center():
                yield Static("Installing Services", id="title")
                
                yield Spinner()
                
                yield Static("Preparing installation...", id="current-task")
                
                with Static(id="progress-container"):
                    yield ProgressBar(total=100, show_eta=False, id="progress")
                
                yield Static("0%", id="status-text")
                
                yield Static("Starting...", id="logs")
                
                yield Button("✕ Cancel Installation", id="cancel", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        """Start the installation when the screen mounts."""
        self._running = True
        asyncio.create_task(self._run_installation())

    def add_log(self, message: str) -> None:
        """Add a log message."""
        self._log_lines.append(message)
        if len(self._log_lines) > 20:
            self._log_lines.pop(0)
        logs = self.query_one("#logs", Static)
        logs.update("\n".join(self._log_lines))

    async def _run_installation(self) -> None:
        """Run the installation process."""
        services = self.app.selected_services
        total = len(services)
        
        status_text = self.query_one("#status-text", Static)
        current_task = self.query_one("#current-task", Static)
        progress = self.query_one("#progress", ProgressBar)
        
        service_names = {
            "zsh": "⚡ Installing ZSH + Powerlevel10k + Plugins...",
            "git": "📚 Installing Git...",
            "basics": "🔧 Installing Basic Tools (unzip, curl, wget)...",
            "mariadb": "🗄️ Installing MariaDB Server...",
            "php": "🐘 Installing PHP 8.4 + Extensions...",
            "composer": "📦 Installing Composer...",
            "nvm": "🟢 Installing NVM + Node.js...",
            "valet": "🚀 Installing Laravel Valet...",
            "laravel": "✨ Installing Laravel Installer...",
            "sites": "📁 Creating ~/Sites Directory...",
        }
        
        self.add_log("Starting installation process...")
        self.add_log(f"Selected {total} service(s) to install")
        self.add_log("")
        
        for i, service in enumerate(services):
            if not self._running:
                self.add_log("\n⚠️ Installation cancelled by user")
                break
                
            task_name = service_names.get(service, f"Installing {service}...")
            current_task.update(task_name)
            self.add_log(f"→ {task_name}")
            
            await asyncio.sleep(1.5)
            
            progress.advance(1)
            percentage = int(((i + 1) / total) * 100)
            status_text.update(f"{percentage}%")
            
            self.add_log(f"✓ {service} installed successfully\n")
        
        if self._running:
            self.add_log("\n✅ All services installed successfully!")
            await asyncio.sleep(1)
            self.app.push_screen("done")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "cancel":
            self._running = False
            self.app.pop_screen()
