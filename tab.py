from typing import Optional

from webdriverbidi import execute


class Tab:
    port: int
    id: str
    url: str

    def __init__(self, port: int, id: str, url: str) -> None:
        """
        Initialize a Tab instance.

        Args:
            port: The port number where the WebDriver BiDi server is running.
            id: The unique identifier for the tab.
            url: The current URL of the tab.
        """
        self.port = port
        self.id = id
        self.url = url

    def __str__(self) -> str:
        return f"Tab(port={self.port}, id={self.id}, url={self.url})"

    def navigate(self, url: str) -> bool:
        """
        Navigate the tab to a new URL.

        Args:
            url: The URL to navigate to.
        Returns:
            True if navigation was successful, False otherwise.
        """
        if result := execute(
            self.port,
            "browsingContext.navigate",
            {"url": url, "context": self.id, "wait": "complete"},
        ):
            self.url = result["url"]
            return True
        return False

    def reload(self) -> bool:
        """
        Reload this tab.

        Returns:
            True if reload was successful, False otherwise.
        """
        if response := execute(
            self.port,
            "browsingContext.reload",
            {
                "context": self.id,
                "wait": "complete",
            },
        ):
            self.url = response["url"]
            return True
        return False

    def close(self) -> bool:
        """
        Close this tab.

        Returns:
            True if the tab was closed successfully, False otherwise.
        """
        return (
            execute(self.port, "browsingContext.close", {"context": self.id})
            is not None
        )

    def evaluate(self, script: str) -> Optional[dict]:
        """
        Evaluate a JavaScript expression in the context of this tab.

        Args:
            script: The JavaScript expression to evaluate.
        Returns:
            The result of the evaluation, or None if evaluation failed.
        """
        if response := execute(
            self.port,
            "script.evaluate",
            {
                "expression": script,
                "target": {"context": self.id},
                "awaitPromise": True,
            },
        ):
            print(f"Evaluated script: {script} -> {response}")
            return response.get("result") or None
        return None

    def has_element_attribute(self, query: str, attribute: str) -> Optional[bool]:
        """
        Check if an element has a specific attribute.

        Args:
            query: The JavaScript query to select the element.
            attribute: The name of the attribute to check.
        Returns:
            True if the attribute exists, False if not, None if evaluation failed.
        """
        if response := self.evaluate(f""" {query}.hasAttribute('{attribute}') """):
            if response["type"] != "null":
                return response["value"]
        return None

    def get_element_attribute(self, query: str, attribute: str) -> Optional[str]:
        """
        Get the value of an attribute for an element selected by the query.

        Args:
            query: The JavaScript query to select the element.
            attribute: The name of the attribute to retrieve.
        Returns:
            The value of the attribute if found, None otherwise.
        """
        if response := self.evaluate(f""" {query}.{attribute} """):
            if response["type"] != "null":
                return response["value"]
        return None

    def set_element_attribute(self, query: str, attribute: str, value: str) -> bool:
        """
        Set the value of an attribute for an element selected by the query.

        Args:
            query: The JavaScript query to select the element.
            attribute: The name of the attribute to set.
            value: The value to set for the attribute.
        Returns:
            True if the attribute was set successfully, False otherwise.
        """
        return (
            self.evaluate(
                ";".join(
                    [
                        f""" var element = {query} """,
                        f""" element.{attribute} = '{value}' """,
                        """ element.dispatchEvent(new Event('input')) """,
                        """ element.dispatchEvent(new Event('change')) """,
                    ]
                ),
            )
            is not None
        )

    def remove_element_attribute(self, query: str, attribute: str) -> bool:
        """
        Remove an attribute from an element selected by the query.

        Args:
            query: The JavaScript query to select the element.
            attribute: The name of the attribute to remove.
        Returns:
            True if the attribute was removed successfully, False otherwise.
        """
        return (
            self.evaluate(f""" {query}.removeAttribute('{attribute}') """) is not None
        )

    def is_element_found(self, query: str) -> Optional[bool]:
        """
        Check if an element exists in the DOM based on the provided query.

        Args:
            query: The JavaScript query to select the element.
        Returns:
            True if the element is found, False if not found, None if evaluation failed.
        """
        if result := self.evaluate(query):
            return result["type"] != "null"
        return None

    def is_element_displayed(self, query: str) -> Optional[bool]:
        """
        Check if an element is displayed in the viewport.

        Args:
            query: The JavaScript query to select the element.
        Returns:
            True if the element is displayed, False if not displayed, None if evaluation failed.
        """
        if response := self.evaluate(
            ";".join(
                [
                    f""" var element = {query} """,
                    """ var rect = element.getBoundingClientRect() """,
                    "&&".join(
                        [
                            "rect.top >= 0",
                            "rect.left >= 0",
                            "rect.bottom <= (window.innerHeight || document.documentElement.clientHeight)",
                            "rect.right <= (window.innerWidth || document.documentElement.clientWidth)",
                        ]
                    ),
                ]
            ),
        ):
            return response["value"]
        return None

    def is_element_disabled(self, query: str) -> Optional[bool]:
        """
        Check if an element is disabled.

        Args:
            query: The JavaScript query to select the element.
        Returns:
            True if the element is disabled, False if not disabled, None if evaluation failed.
        """
        return self.has_element_attribute(query, "disabled")

    def is_element_equal_to(self, query1: str, query2: str) -> Optional[bool]:
        """
        Check if two elements are equal based on their queries.

        Args:
            query1: The JavaScript query for the first element.
            query2: The JavaScript query for the second element.
        Returns:
            True if the elements are equal, False if not equal, None if evaluation failed.
        """
        if result := self.evaluate(f""" {query1} === {query2} """):
            return result["value"]
        return None

    def focus_element(self, query: str) -> bool:
        """
        Focus on an element selected by the query.

        Args:
            query: The JavaScript query to select the element.
        Returns:
            True if the element was focused successfully, False otherwise.
        """
        return self.evaluate(f""" {query}.focus() """) is not None

    def click_element(self, query: str) -> bool:
        """
        Click on an element selected by the query.

        Args:
            query: The JavaScript query to select the element.
        Returns:
            True if the element was clicked successfully, False otherwise.
        """
        return self.evaluate(f""" {query}.click() """) is not None

    def scroll_element(self, query: str) -> bool:
        """
        Scroll an element into view.

        Args:
            query: The JavaScript query to select the element.
        Returns:
            True if the element was scrolled into view successfully, False otherwise.
        """
        return (
            self.evaluate(
                f""" {query}.scrollIntoView({{"block": "center", "inline": "nearest"}}) """
            )
            is not None
        )
