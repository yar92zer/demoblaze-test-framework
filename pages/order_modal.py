import allure

from pages.base_modal import BaseModal


class OrderModal(BaseModal):
    MODAL = "#orderModal"
    TOTAL_LABEL = "#orderModal #totalm"
    NAME_INPUT = "#orderModal #name"
    COUNTRY_INPUT = "#orderModal #country"
    CITY_INPUT = "#orderModal #city"
    CARD_INPUT = "#orderModal #card"
    MONTH_INPUT = "#orderModal #month"
    YEAR_INPUT = "#orderModal #year"
    PURCHASE_BUTTON = "#orderModal button.btn-primary"
    CLOSE_BUTTON = "#orderModal button.btn-secondary"
    CONFIRMATION = ".sweet-alert"
    CONFIRMATION_TITLE = ".sweet-alert h2"
    CONFIRMATION_TEXT = ".sweet-alert p"
    CONFIRMATION_OK_BUTTON = ".sweet-alert button.confirm"

    def get_total(self) -> str:
        return self.get_text(self.TOTAL_LABEL).strip()

    @allure.step("Заполняем форму заказа")
    def fill_order(self, order: dict[str, str]) -> None:
        fields = {
            "name": self.NAME_INPUT,
            "country": self.COUNTRY_INPUT,
            "city": self.CITY_INPUT,
            "card": self.CARD_INPUT,
            "month": self.MONTH_INPUT,
            "year": self.YEAR_INPUT,
        }
        for key, locator in fields.items():
            if key in order:
                self.fill(locator, order[key])

    # Одна кнопка даёт два разных диалога: при валидной форме - sweetalert
    # в DOM, при пустой - нативный alert из purchaseOrder(). Отсюда два метода.
    @allure.step("Подтверждаем покупку")
    def purchase(self) -> None:
        self.click(self.PURCHASE_BUTTON)
        self.wait_visible(self.CONFIRMATION)

    def purchase_expecting_alert(self) -> str:
        return self.click_expecting_alert(self.PURCHASE_BUTTON)

    def get_confirmation_title(self) -> str:
        return self.get_text(self.CONFIRMATION_TITLE).strip()

    def get_confirmation_text(self) -> str:
        return self.get_text(self.CONFIRMATION_TEXT).strip()

    def confirm(self) -> None:
        self.click(self.CONFIRMATION_OK_BUTTON)
        self.page.locator(self.CONFIRMATION).wait_for(state="hidden", timeout=self.timeout)
