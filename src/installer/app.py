"""Main application class for Laravel Dev Setup Installer."""

from textual.app import App

from installer.screens.welcome import WelcomeScreen
from installer.screens.services import ServicesScreen
from installer.screens.install import InstallScreen
from installer.screens.done import DoneScreen


class InstallerApp(App):
    """Main application for Laravel Dev Setup Installer."""

    CSS_PATH = "styles/installer.tcss"
    TITLE = "Laravel Dev Setup"
    SUB_TITLE = "Linux Development Environment Installer"

    SCREENS = {
        "welcome": WelcomeScreen,
        "services": ServicesScreen,
        "install": InstallScreen,
        "done": DoneScreen,
    }

    selected_services: list[str] = []

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.push_screen("welcome")


def main() -> None:
    """Main entry point."""
    app = InstallerApp()
    app.run()


if __name__ == "__main__":
    main()
