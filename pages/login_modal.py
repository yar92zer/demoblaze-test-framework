import allure

from pages.base_modal import BaseModal


class LoginModal(BaseModal):
    MODAL = "#logInModal"
    USERNAME_INPUT = "#loginusername"
    PASSWORD_INPUT = "#loginpassword"
    SUBMIT_BUTTON = "#logInModal button.btn-primary"
    CLOSE_BUTTON = "#logInModal button.btn-secondary"


    @allure.step("Логинимся под {username}")
    def login(self, username: str, password: str) -> None:
        # Заполнить форму и отправить.
        self.wait_open()
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        # logIn() в success-колбэке делает location.reload(): без перехвата
        # навигации следующая команда попадёт в уничтоженный контекст.
        with self.page.expect_navigation():
            self.click(self.SUBMIT_BUTTON)

    @allure.step("Пробуем войти и ловим алерт")
    def login_expecting_alert(self, username: str, password: str) -> str:
        # Алерт прилетает из AJAX-коллбэка logIn(), поэтому хелпер, а не expect_event.
        self.wait_open()
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        return self.click_expecting_alert(self.SUBMIT_BUTTON)
