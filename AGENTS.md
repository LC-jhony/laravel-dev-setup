# AGENTS.md - Linux Installer (Textual TUI)

This document provides guidelines for agents working on this Linux installer project using Textual TUI framework.

## Project Overview

This is a Python TUI application for deploying/configuring services on Linux. It uses the [Textual](https://github.com/Textualize/textual) framework for terminal user interface.

---

## Build, Test, and Run Commands

### Installation

```bash
# Install in development mode
pip install -e .

# Or install from source
pip install .
```

### Running the Application

```bash
# Run the installer
python -m installer

# Or run with textual CLI (with hot-reload)
textual run --dev src/installer/app.py

# Run in production mode
textual run src/installer/app.py
```

### Testing

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_app.py

# Run a single test method
pytest tests/test_app.py::test_install_step

# Run tests with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Run Ruff (linting)
ruff check .

# Run Ruff (formatting)
ruff format .

# Run MyPy (type checking)
mypy src/

# Run all checks
ruff check . && ruff format . && mypy src/
```

---

## Code Style Guidelines

### Python Version

- Minimum Python 3.9
- Use latest Python features when appropriate

### Type Hints

Textualize strongly recommends type hints. Always include:
- Function argument types
- Return types
- Variable annotations where helpful

```python
from typing import Optional

def get_service_status(service_name: str) -> Optional[dict]:
    ...
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Classes | PascalCase | `InstallScreen`, `ServiceWidget` |
| Functions/Methods | snake_case | `run_installer()`, `on_button_pressed()` |
| Variables | snake_case | `service_name`, `install_progress` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Private Methods | snake_case with underscore | `_validate_input()` |

### Imports

Group imports in this order:
1. Standard library
2. Third-party packages (Textual, etc.)
3. Local application imports

```python
import os
import subprocess
from typing import Optional

from textual.app import App, ComposeResult
from textual.widgets import Button, Static, ProgressBar
from textual.screen import Screen

from installer.config import ConfigManager
from installer.services import ServiceManager
```

### File Organization

```
installer/
├── __init__.py
├── __main__.py          # Entry point: python -m installer
├── app.py               # Main App class
├── config.py            # Configuration management
├── screens/
│   ├── __init__.py
│   ├── welcome.py       # Welcome screen
│   ├── services.py     # Service selection
│   ├── install.py      # Installation progress
│   └── done.py         # Completion screen
├── widgets/
│   ├── __init__.py
│   ├── service_card.py # Service selection widget
│   └── progress.py     # Progress display
├── services/
│   ├── __init__.py
│   ├── base.py         # Base service class
│   └── docker.py       # Docker installation
└── styles/
    └── tui.css         # Textual CSS styles
```

---

## Textual-Specific Guidelines

### App Structure

```python
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static

class InstallerApp(App):
    CSS_PATH = "styles/tui.css"
    
    def on_mount(self) -> None:
        self.push_screen(WelcomeScreen())

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Linux Service Installer")
        yield Footer()
```

### Screens

```python
from textual.screen import Screen
from textual.widgets import Button
from textual.app import ComposeResult

class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Static("Welcome to the Installer")
        yield Button("Start Installation", id="start")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.push_screen(ServiceSelectionScreen())
```

### Message Handling

```python
def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "start":
        self.start_installation()
```

### CSS Styling

Textual uses CSS-like styling. Place in `styles/tui.css`:

```css
Screen {
    background: $surface;
}

Button {
    margin: 1;
}

# Install the application:

Static#title {
    text-align: center;
    text-style: bold;
}
```

---

## Error Handling

- Use exceptions for error conditions
- Display errors in TUI using `Toast` or error panels
- Log errors for debugging

```python
from textual.widgets import Toast

def install_service(self, service: str) -> None:
    try:
        subprocess.run(["apt", "install", service], check=True)
    except subprocess.CalledProcessError as e:
        self.show_toast(f"Installation failed: {e}")
        self.logger.error(f"Install failed: {e}")
```

---

## Testing Guidelines

```python
import pytest
from textual.app import AppTester

from installer.app import InstallerApp

@pytest.fixture
def app():
    return InstallerApp()

async def test_welcome_screen(app):
    tester = AppTester(app)
    async with tester.run_test() as pilot:
        assert "Welcome" in tester.app.screen.query_one("#title").renderable
```

---

## Common Issues

- **Import errors**: Ensure package is installed (`pip install -e .`)
- **Style not loading**: Check `CSS_PATH` is correct relative to project root
- **Screen not found**: Use `self.app.push_screen()` for navigation

---

## Dependencies

Key packages:
- `textual` - TUI framework
- `pytest` - Testing
- `pytest-asyncio` - Async testing
- `ruff` - Linting/formatting
- `mypy` - Type checking

---

## Git Commit Messages

Follow conventional commits:
- `feat: add service selection screen`
- `fix: resolve installation timeout`
- `refactor: extract docker service to module`
- `test: add installation flow tests`
