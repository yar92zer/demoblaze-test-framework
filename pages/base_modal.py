from pages.base_page import BasePage


class BaseModal(BasePage):
    MODAL: str = ""
    CLOSE_BUTTON: str = ""

    def wait_open(self) -> None:
        self.page.locator(f"{self.MODAL}.show").wait_for(state="visible", timeout=self.timeout)

    def close(self) -> None:
        self.click(self.CLOSE_BUTTON)
