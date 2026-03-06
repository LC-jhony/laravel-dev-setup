"""Completion screen shown after installation."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static


class DoneScreen(Screen):
    """Screen shown when installation is complete."""

    DEFAULT_CSS = """
    DoneScreen {
        align: center middle;
    }

    #done-container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 2 4;
    }

    #title {
        text-style: bold;
        text-align: center;
        color: $success;
    }

    #message {
        text-align: center;
        margin-top: 1;
        margin-bottom: 2;
    }

    #services-list {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    #exit-button {
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        services = self.app.selected_services
        
        service_names = {
            "zsh": "ZSH + Powerlevel10k",
            "git": "Git",
            "basics": "Basic Tools",
            "mariadb": "MariaDB",
            "php": "PHP 8.4",
            "composer": "Composer",
            "nvm": "NVM + Node.js",
            "valet": "Laravel Valet",
            "laravel": "Laravel Installer",
            "sites": "~/Sites Directory",
        }
        
        installed = [service_names.get(s, s) for s in services]
        
        yield Header()
        with Static(id="done-container"):
            yield Static("Installation Complete!", id="title")
            yield Static(
                "Your Laravel development environment has been\n"
                "successfully set up!",
                id="message"
            )
            yield Static(
                "Installed:\n" + "\n".join(f"  ✓ {s}" for s in installed),
                id="services-list"
            )
            yield Button("Exit", id="exit", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "exit":
            self.app.exit()
