from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Static


class KnowledgeApp(App):
    """A Textual TUI for Knowledge Bro."""

    # Key bindings shown at the bottom automatically
    BINDINGS = [
        ("d", "toggle_dark", "Toggle Dark Mode"),
        ("q", "quit", "Quit App"),
    ]

    # Optional TCSS (Textual CSS) styling
    CSS = """
    Screen {
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
        """Create child widgets for the app layout."""
        yield Header(show_clock=True)

        yield Input(placeholder="Type a query or command...", id="input-box")

        yield Static(
            "Welcome to Knowledge Bro! Output will appear here.", id="output-area"
        )

        with Horizontal(classes="button-container"):
            yield Button("Submit", variant="primary", id="btn-submit")
            yield Button("Clear", variant="error", id="btn-clear")

        yield Footer()

    # Event handlers: method name matches 'on_<widget>_<event>'
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

    def action_toggle_dark(self) -> None:
        """An action triggered by the 'd' key binding."""
        self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"


if __name__ == "__main__":
    app = KnowledgeApp()
    app.run()
