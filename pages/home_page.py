import allure
from playwright.sync_api import Response

from pages.base_page import BasePage


class HomePage(BasePage):
    url_path = "index.html"
    BYCAT_ENDPOINT = "/bycat"
    PAGINATION_ENDPOINT = "/pagination"
    CATEGORY_LINKS = "a#itemc"
    # id="itemc" продублирован на всех трёх категориях, поэтому голый
    # #itemc даёт strict mode violation - различаем по тексту.
    CATEGORY_BY_NAME = "a#itemc:text-is('{name}')"
    PRODUCT_GRID = "#tbodyid"
    PRODUCT_CARDS = "#tbodyid .card"
    PRODUCT_TITLES = "#tbodyid a.hrefch"
    PRODUCT_PRICES = "#tbodyid .card-block h5"
    NEXT_BUTTON = "#next2"
    PREVIOUS_BUTTON = "#prev2"

    @allure.step("Открываем главную страницу")
    def open(self, path: str | None = None) -> None:
        super().open(path)
        self.wait_for_products()

    def wait_for_products(self) -> None:
        self.page.locator(self.PRODUCT_TITLES).first.wait_for(state="visible", timeout=self.timeout)

    @allure.step("Переключаемся на категорию {name}")
    def open_category(self, name: str) -> None:
        self._act_and_with_render(
            self.BYCAT_ENDPOINT, lambda: self.click(self.CATEGORY_BY_NAME.format(name=name))
        )

    def get_product_titles(self) -> list[str]:
        return [text.strip() for text in self.page.locator(self.PRODUCT_TITLES).all_inner_texts()]

    def get_product_prices(self) -> list[str]:
        return [text.strip() for text in self.page.locator(self.PRODUCT_PRICES).all_inner_texts()]

    def get_products_count(self) -> int:
        return self.page.locator(self.PRODUCT_CARDS).count()

    @allure.step("Открываем карточку товара {title}")
    def open_product(self, title: str) -> None:
        grid = self.page.locator(self.PRODUCT_GRID)
        grid.get_by_role("link", name=title, exact=True).click()

    @allure.step("Периходим на следующую страницу")
    def go_to_next_page(self) -> None:
        self._act_and_with_render(
            self.PAGINATION_ENDPOINT, lambda: self.click(self.NEXT_BUTTON))

    @allure.step("Возвращаемся на предыдущую страницу")
    def go_to_previous_page(self) -> None:
        self._act_and_with_render(
            self.PAGINATION_ENDPOINT, lambda: self.click(self.PREVIOUS_BUTTON))

    def _wait_until_rendered(self, response: Response) -> None:
        expected = [item["title"].strip() for item in response.json().get("Items", [])]
        self.page.wait_for_function(
            """expected => {
                const titles = [...document.querySelectorAll('#tbodyid a.hrefch')]
                    .map(link => link.textContent.trim());
                return titles.length === expected.length
                    && titles.every((title, index) => title === expected[index]);
            }""",
            arg=expected,
            timeout=self.timeout,
        )
