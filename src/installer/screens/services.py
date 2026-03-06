"""Services selection screen."""

from textual.app import ComposeResult
from textual.containers import Center, Middle, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, SelectionList


class ServicesScreen(Screen):
    """Screen for selecting which services to install."""

    DEFAULT_CSS = """
    ServicesScreen {
        align: center middle;
    }

    #title {
        text-style: bold;
        text-align: center;
        color: $accent;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    SelectionList {
        border: solid $primary;
        margin: 1 2;
    }

    SelectionList > .selection-list--option {
        padding: 0 1;
    }

    .service-icon {
        width: 3;
    }

    #buttons {
        align: center middle;
        height: auto;
    }

    #install-button {
        width: 25;
    }
    
    #select-all {
        width: 15;
    }
    
    #deselect-all {
        width: 15;
    }
    """

    SERVICES = [
        ("zsh", "⚡ ZSH + Powerlevel10k + Plugins", True),
        ("git", "📚 Git - Version Control", True),
        ("basics", "🔧 Unzip + Basic Tools", True),
        ("mariadb", "🗄️ MariaDB - Database", True),
        ("php", "🐘 PHP 8.4 + Extensions", True),
        ("composer", "📦 Composer - PHP Package Manager", True),
        ("nvm", "🟢 NVM + Node.js", True),
        ("valet", "🚀 Laravel Valet", True),
        ("laravel", "✨ Laravel Installer", True),
        ("sites", "📁 ~/Sites Directory", True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Middle():
            with Center():
                yield Static("Select Services to Install", id="title")
                yield Static("Choose the components you want to install", id="subtitle")
                
                yield SelectionList(
                    *[
                        (service_id, description, selected)
                        for service_id, description, selected in self.SERVICES
                    ],
                    id="service-list"
                )
                
                with VerticalScroll(id="buttons"):
                    yield Button("Select All", id="select-all", variant="default")
                    yield Button("Deselect All", id="deselect-all", variant="default")
                    yield Button("▶  Install Selected", id="install", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        service_list = self.query_one("#service-list", SelectionList)
        
        if event.button.id == "select-all":
            service_list.select_all()
        elif event.button.id == "deselect-all":
            service_list.clear_selection()
        elif event.button.id == "install":
            selected = service_list.selected
            if selected:
                self.app.selected_services = list(selected)
                self.app.push_screen("install")
            else:
                self.notify("Please select at least one service to install", severity="warning")
