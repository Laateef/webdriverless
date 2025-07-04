from typing import Optional

from tab import Tab
from webdriverbidi import execute


class Browser:
    port: int

    def __init__(self, port: int) -> None:
        """
        Initialize a Browser instance.

        Args:
            port: The port number where the WebDriver BiDi server is running.
        """
        self.port = port

    def get_tabs(self) -> list[Tab]:
        """
        Get the list of currently open tabs in the browser.

        Returns:
            A list of Tab objects representing the open tabs.
        """
        if response := execute(self.port, "browsingContext.getTree", {"maxDepth": 1}):
            return [
                Tab(port=self.port, id=context["context"], url=context["url"])
                for context in response["contexts"]
            ]
        return []

    def create_tab(self) -> Optional[Tab]:
        """
        Create a new tab in the browser.

        Returns:
            A Tab object representing the newly created tab, or None if creation failed.
        """
        if context := execute(
            self.port,
            "browsingContext.create",
            {"type": "tab"},
        ):
            return Tab(port=self.port, id=context["context"], url="")
        return None
