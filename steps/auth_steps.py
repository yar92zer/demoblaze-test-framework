import allure

from pages.header import Header
from pages.home_page import HomePage
from pages.login_modal import LoginModal


@allure.step("Открываем форму входа")
def open_login_form(home_page: HomePage, header: Header) -> None:
    home_page.open()
    header.open_login_modal()


@allure.step("Входим под {username}")
def login_as(
    home_page: HomePage, header: Header, login_modal: LoginModal, username: str, password: str
) -> None:
    open_login_form(home_page, header)
    login_modal.login(username, password)
