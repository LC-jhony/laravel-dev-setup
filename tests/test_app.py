"""Tests for the Laravel Dev Setup Installer."""

import pytest

from textual.app import AppTester

from installer.app import InstallerApp


@pytest.fixture
def app() -> InstallerApp:
    return InstallerApp()


async def test_welcome_screen_loads(app: InstallerApp) -> None:
    """Test that the welcome screen loads correctly."""
    tester = AppTester(app)
    async with tester.run_test() as pilot:
        assert "Laravel Dev Setup" in tester.app.screen.query_one("#title").renderable


async def test_navigate_to_services(app: InstallerApp) -> None:
    """Test navigation from welcome to services screen."""
    tester = AppTester(app)
    async with tester.run_test() as pilot:
        await pilot.click("#start")
        assert tester.app.screen.__class__.__name__ == "ServicesScreen"


async def test_services_screen_has_selections(app: InstallerApp) -> None:
    """Test that services screen shows all service options."""
    tester = AppTester(app)
    async with tester.run_test() as pilot:
        await pilot.click("#start")
        service_list = tester.app.screen.query_one("#service-list")
        assert len(service_list.index) > 0
