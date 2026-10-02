import allure

from pages.base_modal import BaseModal


class SignupModal(BaseModal):
    MODAL = "#signInModal"
    USERNAME_INPUT = "#sign-username"
    PASSWORD_INPUT = "#sign-password"
    SUBMIT_BUTTON = "#signInModal button.btn-primary"
    CLOSE_BUTTON = "#signInModal button.btn-secondary"

    @allure.step("Регистрируем пользователя {username}")
    def register(self, username: str, password: str) -> str:
        # Зарегистрировать пользователя, вернуть текст алерта.
        self.wait_open()
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        return self.click_expecting_alert(self.SUBMIT_BUTTON)
