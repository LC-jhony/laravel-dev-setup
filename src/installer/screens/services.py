"""Services selection screen."""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, SelectionList


class ServicesScreen(Screen):
    """Screen for selecting which services to install."""

    DEFAULT_CSS = """
    ServicesScreen {
        align: center middle;
    }

    #services-container {
        width: 70;
        height: 80%;
        border: solid $primary;
        padding: 1 2;
    }

    #title {
        text-style: bold;
        text-align: center;
        color: $accent;
        margin-bottom: 1;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 2;
    }

    SelectionList {
        margin-bottom: 2;
        height: 100%;
    }

    #buttons {
        align: center middle;
        height: auto;
    }

    #install-button {
        width: 100%;
    }

    #select-all {
        margin-bottom: 1;
    }
    """

    SERVICES = [
        ("zsh", "ZSH + Powerlevel10k + Plugins", True),
        ("git", "Git", True),
        ("basics", "Unzip + Basic Tools", True),
        ("mariadb", "MariaDB (Database)", True),
        ("php", "PHP 8.4 + Extensions", True),
        ("composer", "Composer", True),
        ("nvm", "NVM + Node.js", True),
        ("valet", "Laravel Valet", True),
        ("laravel", "Laravel Installer", True),
        ("sites", "~/Sites Directory", True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Static(id="services-container"):
            yield Static("Select Services to Install", id="title")
            yield Static("Choose the components you want to install", id="subtitle")
            yield SelectionList(
                *[
                    (service_id, description, selected)
                    for service_id, description, selected in self.SERVICES
                ],
                id="service-list"
            )
            with Static(id="buttons"):
                yield Button("Select All", id="select-all", variant="default")
                yield Button("Install Selected", id="install", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        service_list = self.query_one("#service-list", SelectionList)
        
        if event.button.id == "select-all":
            service_list.select_all()
        elif event.button.id == "install":
            selected = service_list.selected
            if selected:
                self.app.selected_services = list(selected)
                self.app.push_screen("install")
            else:
                self.notify("Please select at least one service to install")
