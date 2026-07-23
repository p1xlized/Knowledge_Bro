import httpx
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static


class MenuScreen(Screen):
    """The landing screen that checks API health before continuing."""

    BINDINGS = [
        ("r", "refresh_health", "Refresh Server Status"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    MenuScreen {
        align: center middle;
        background: $surface;
    }

    #menu-box {
        width: 60;
        height: auto;
        border: heavy $primary;
        padding: 2 4;
        background: $panel;
    }

    #server-status {
        margin: 1 0 2 0;
        content-align: center middle;
    }

    .menu-button {
        width: 100%;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="menu-box"):
            yield Static("⚡ [bold cyan]Knowledge Bro TUI[/bold cyan]", id="title")
            yield Static("Checking server connection...", id="server-status")

            yield Button(
                "Go to Dashboard",
                variant="primary",
                id="btn-dashboard",
                classes="menu-button",
                disabled=True,
            )
            yield Button(
                "Retry Connection",
                variant="default",
                id="btn-retry",
                classes="menu-button",
            )
            yield Button("Quit", variant="error", id="btn-quit", classes="menu-button")

    def on_mount(self) -> None:
        """Check API health when the screen loads."""
        self.check_api_health()

    @work(exclusive=True)
    async def check_api_health(self) -> None:
        """Async worker to check the /api/health endpoint without freezing UI."""
        status_widget = self.query_one("#server-status", Static)
        dash_btn = self.query_one("#btn-dashboard", Button)

        status_widget.update("[yellow]Checking server connection...[/yellow]")

        # Adjust URL/port to match your running server if different
        api_url = "http://127.0.0.1:8000/api/health"

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(api_url)

                if response.status_code == 200:
                    status_widget.update(
                        "[bold green]● Server Online[/bold green] (http://127.0.0.1:8000)"
                    )
                    dash_btn.disabled = False
                else:
                    status_widget.update(
                        f"[bold red]✖ Server Error[/bold red] ({response.status_code})"
                    )
                    dash_btn.disabled = True

        except httpx.RequestError:
            status_widget.update(
                "[bold red]✖ Cannot connect to server![/bold red]\n[dim]Is FastAPI running on port 8000?[/dim]"
            )
            dash_btn.disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-dashboard":
            self.app.push_screen("dashboard")
        elif event.button.id == "btn-retry":
            self.check_api_health()
        elif event.button.id == "btn-quit":
            self.app.exit()

    def action_refresh_health(self) -> None:
        self.check_api_health()

    def action_quit(self) -> None:
        self.app.exit()


class DashboardScreen(Screen):
    """Main dashboard screen for querying and interacting with content."""

    BINDINGS = [
        ("b", "go_back", "Back to Menu"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    DashboardScreen {
        layout: vertical;
    }

    #input-box {
        margin: 1 2;
    }

    #output-area {
        height: 1fr;
        border: solid green;
        margin: 1 2;
        padding: 1;
    }

    .button-container {
        height: auto;
        align: center middle;
        margin: 1 2;
    }

    Button {
        margin-right: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Input(placeholder="Type a query or command...", id="input-box")
        yield Static(
            "Welcome to Knowledge Bro Dashboard! Output will appear here.",
            id="output-area",
        )

        with Horizontal(classes="button-container"):
            yield Button("Submit", variant="primary", id="btn-submit")
            yield Button("Clear", variant="error", id="btn-clear")
            yield Button("Back to Menu", variant="default", id="btn-back")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        output = self.query_one("#output-area", Static)
        input_widget = self.query_one("#input-box", Input)

        if event.button.id == "btn-submit":
            text = input_widget.value.strip()
            if text:
                output.update(f"Processing query: [bold cyan]{text}[/bold cyan]")
                input_widget.value = ""
            else:
                output.update("[red]Please enter a query first![/red]")

        elif event.button.id == "btn-clear":
            input_widget.value = ""
            output.update("Cleared output.")

        elif event.button.id == "btn-back":
            self.app.pop_screen()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_toggle_dark(self) -> None:
        self.app.theme = (
            "textual-light" if self.app.theme == "textual-dark" else "textual-dark"
        )

    def action_quit(self) -> None:
        self.app.exit()


class KnowledgeApp(App):
    """Main App managing screens."""

    SCREENS = {
        "menu": MenuScreen,
        "dashboard": DashboardScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("menu")


if __name__ == "__main__":
    app = KnowledgeApp()
    app.run()
