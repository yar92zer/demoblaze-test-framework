import allure

from pages.base_modal import BaseModal


class ContactModal(BaseModal):
    MODAL = "#exampleModal"
    EMAIL_INPUT = "#recipient-email"
    NAME_INPUT = "#recipient-name"
    MESSAGE_INPUT = "#message-text"

    # У кнопки Send message своего id нет, различаем по классу в футере.
    SEND_BUTTON = "#exampleModal button.btn-primary"
    CLOSE_BUTTON = "#exampleModal button.btn-secondary"


    @allure.step("Отправляем сообщение через форму контактов")
    def send_message(self, email: str, name: str, message: str) -> str:
        self.fill(self.EMAIL_INPUT, email)
        self.fill(self.NAME_INPUT, name)
        self.fill(self.MESSAGE_INPUT, message)
        return self.click_expecting_alert(self.SEND_BUTTON)

