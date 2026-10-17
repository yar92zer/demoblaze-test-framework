import allure
import pytest

from steps.auth_steps import login_as
from steps.cart_steps import add_product_to_cart

pytestmark = [
    pytest.mark.ui,
    pytest.mark.regression,
    allure.feature("Известные дефекты стенда"),
]


@pytest.mark.xfail(
    reason="Дефект гость получает 'Product added', авторизованный - с точкой",
    strict=True,
    raises=AssertionError,
)
@allure.title("Текст подтверждения одинаков для гостя и авторизованного")
def test_add_to_cart_alert_is_consistent(
    home_page, product_page, header, login_modal, registered_user
):
    guest_message = add_product_to_cart(home_page, product_page, "Nexus 6")
    login_as(
        home_page, header, login_modal, registered_user["username"], registered_user["password"]
    )
    user_message = add_product_to_cart(home_page, product_page, "Nexus 6")
    assert guest_message == user_message


@pytest.mark.xfail(
    reason="Дефект: Previous возвращает набор со сдвигом, один товар подменяется",
    strict=True,
    raises=AssertionError,
)
@allure.title("Возврат на предыдущую страницу показывает исходные товары")
def test_previous_page_returns_to_first(home_page):
    home_page.open()
    first_page = home_page.get_product_titles()
    home_page.go_to_next_page()
    home_page.go_to_previous_page()
    assert home_page.get_product_titles() == first_page


@pytest.mark.xfail(
    reason="Дефект №13: форма обратной связи не отправляет данные на бэкенд",
    strict=True,
    raises=AssertionError,
)
@allure.title("Форма обратной связи отправляет сообщение на бэкенд")
def test_contact_form_sends_message_to_backend(page, home_page, header, contact_modal):
    home_page.open()
    header.open_contact_modal()
    sent=[]
    page.on("request", lambda r: sent.append(r) if r.method == "POST" else None)
    contact_modal.send_message("qa@example.com", "QA Tester", "Проверка")
    assert sent, "форма не отправила ни одного POST-запроса"

