import allure
from playwright.sync_api import Response

from pages.base_page import BasePage


class CartPage(BasePage):
    url_path = "cart.html"

    VIEWCART_ENDPOINT = "/viewcart"

    # --- таблица позиций ---
    TABLE_BODY = "#tbodyid"
    ROWS = "#tbodyid tr"
    ROW_TITLES = "#tbodyid tr td:nth-child(2)"
    ROW_PRICES = "#tbodyid tr td:nth-child(3)"
    DELETE_LINKS = "#tbodyid tr td:nth-child(4) a"

    # --- итог и оформление ---
    # У #totalp свой id, у кнопки Place Order — нет, берём по data-target.
    TOTAL = "#totalp"
    PLACE_ORDER_BUTTON = "button[data-target='#orderModal']"

    @allure.step("Открываем корзину")
    def open(self, path: str | None = None) -> None:
        self._act_and_with_render(self.VIEWCART_ENDPOINT, lambda: super(CartPage, self).open(path))

    def get_item_titles(self) -> list[str]:
        return [text.strip() for text in self.page.locator(self.ROW_TITLES).all_inner_texts()]

    def get_item_prices(self) -> list[int]:
        return [int(text.strip()) for text in self.page.locator(self.ROW_PRICES).all_inner_texts()]

    @allure.step("Читаем итоговую сумму")
    def get_total(self) -> int:
        raw = self.get_text(self.TOTAL).strip()
        return int(raw) if raw else 0

    def get_items_count(self) -> int:
        return self.page.locator(self.ROWS).count()

    def is_empty(self) -> bool:
        return self.get_items_count() == 0

    @allure.step("Удаляем товар {title} из корзины")
    def delete_item(self, title: str) -> None:
        row = self.page.locator(self.ROWS).filter(has_text=title)
        self._act_and_with_render(self.VIEWCART_ENDPOINT, lambda: row.locator("a").click())

    @allure.step("Нажимаем Place Order")
    def place_order(self) -> None:
        self.click(self.PLACE_ORDER_BUTTON)

    def _wait_until_rendered(self, response: Response) -> None:
        body = response.json()
        expected = len(body.get("Items", [])) if isinstance(body, dict) else 0
        self.page.wait_for_function(
            "expected => document.querySelectorAll('#tbodyid tr').length === expected",
            arg=expected,
            timeout=self.timeout,
        )
