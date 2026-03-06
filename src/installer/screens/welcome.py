"""Welcome screen for the installer."""

from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, Sparkline


class WelcomeScreen(Screen):
    """Welcome screen shown when the app starts."""

    DEFAULT_CSS = """
    WelcomeScreen {
        align: center middle;
    }

    #logo {
        text-style: bold;
        text-align: center;
        color: $accent;
        text-shadow: $accent 0 0 10;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
    }

    #description {
        margin-top: 2;
        text-align: center;
        color: $text;
    }

    #features {
        margin-top: 2;
        color: $text-muted;
        text-align: center;
    }

    #start-button {
        margin-top: 4;
        width: 30;
    }

    .ascii-art {
        text-align: center;
        color: $primary;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Middle():
            with Center():
                yield Static("""
  _                _              _    ____             
 | |    ___   __ _| |_ ___      | |  / ___|___  _ __  | |_ 
 | |   / _ \\ / _` | __/ _ \\     | | | |   / _ \\| '_ \\ | __|
 | |__| (_) | (_| | ||  __/     | | | |__| (_) | | | || |_ 
 |_____\\___/ \\__,_|\\__\\___|     |_|  \\____\\___/|_| |_| \\__|
                                                        
""", classes="ascii-art", id="logo")
                
                yield Static("Linux Development Environment Installer", id="subtitle")
                
                yield Static(
                    "Set up a complete Laravel development environment\n"
                    "with just a few clicks",
                    id="description"
                )
                
                yield Static(
                    "• ZSH + Powerlevel10k\n"
                    "• PHP 8.4 + Extensions\n"
                    "• Composer & Laravel\n"
                    "• Node.js & NPM\n"
                    "• MariaDB Database\n"
                    "• Laravel Valet",
                    id="features"
                )
                
                yield Button("▶  Start Installation", id="start", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start":
            self.app.push_screen("services")
