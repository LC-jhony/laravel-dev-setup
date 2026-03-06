"""Completion screen shown after installation."""

from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static


class DoneScreen(Screen):
    """Screen shown when installation is complete."""

    DEFAULT_CSS = """
    DoneScreen {
        align: center middle;
    }

    #success-icon {
        text-style: bold;
        text-align: center;
        color: $success;
        text-shadow: $success 0 0 20;
    }

    #title {
        text-style: bold;
        text-align: center;
        color: $success;
    }

    #message {
        text-align: center;
        margin-top: 1;
    }

    #services-list {
        width: 40;
        height: auto;
        border: solid $primary;
        padding: 1 2;
        margin: 2 0;
    }

    #services-list Static {
        color: $text;
    }

    #tip {
        text-align: center;
        color: $text-muted;
        margin-top: 2;
    }

    #exit-button {
        width: 20;
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        services = self.app.selected_services
        
        service_names = {
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
        
        installed = [service_names.get(s, s) for s in services]
        
        yield Header(show_clock=True)
        with Middle():
            with Center():
                yield Static("🎉", id="success-icon")
                yield Static("Installation Complete!", id="title")
                yield Static(
                    "Your Laravel development environment\nhas been successfully set up!",
                    id="message"
                )
                
                yield Static(
                    "Installed services:\n" + "\n".join(f"  ✓ {s}" for s in installed),
                    id="services-list"
                )
                
                yield Static(
                    "Tip: Run 'valet install' to configure Laravel Valet\n"
                    "Then create a new project with: laravel new myproject",
                    id="tip"
                )
                
                yield Button("✕ Exit", id="exit", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "exit":
            self.app.exit()
