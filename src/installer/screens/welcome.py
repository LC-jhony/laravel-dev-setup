"""Welcome screen for the installer."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static


class WelcomeScreen(Screen):
    """Welcome screen shown when the app starts."""

    DEFAULT_CSS = """
    WelcomeScreen {
        align: center middle;
    }

    #welcome-container {
        width: 60;
        height: auto;
        border: solid $primary;
        padding: 2 4;
    }

    #title {
        text-style: bold;
        text-align: center;
        color: $accent;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
    }

    #description {
        margin-top: 2;
        text-align: center;
    }

    #start-button {
        margin-top: 3;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Static(id="welcome-container"):
            yield Static("Laravel Dev Setup", id="title")
            yield Static("Linux Development Environment Installer", id="subtitle")
            yield Static(
                "This installer will help you set up a complete\n"
                "Laravel development environment on your Linux system.\n\n"
                "Select the components you want to install:",
                id="description"
            )
            yield Button("Start Installation", id="start", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start":
            self.app.push_screen("services")
