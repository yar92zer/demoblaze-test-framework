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
