import allure
import pytest

from client.endpoints import Endpoint
from utils.encoders import decode_token

pytestmark = [allure.feature("Известные дефекты стенда")]


@pytest.mark.negative
@pytest.mark.xfail(
    reason="Дефект /deleteitem не требует токена, позиция удаляется по одному id",
    strict=True,
    raises=pytest.fail.Exception,
)
@allure.title("Позицию корзины нельзя удалить без токена владельца")
def test_cart_item_cannot_be_deleted_without_owner_token(cart, authenticated_user):
    item_id = cart.add_to_cart(authenticated_user["token"], product_id=1)
    with pytest.raises(AssertionError):
        cart.delete_item(item_id)
    assert cart.view_cart(authenticated_user["token"]).Items


@pytest.mark.regression
@pytest.mark.xfail(
    reason="Дефект №1: токен не подписан и обратимо декодируется",
    strict=True,
    raises=AssertionError,
)
@allure.title("Токен не раскрывает логин пользователя")
def test_token_does_not_reveal_username(authenticated_user):
    decoded = decode_token(authenticated_user["token"])
    assert not decoded.startswith(authenticated_user["username"])


@pytest.mark.negative
@pytest.mark.xfail(
    reason="Дефект нечисловой id валит бэкенд с 500 и HTML вместо JSON",
    strict=True,
    raises=AssertionError,
)
@allure.title("Нечисловой id не должен валить бэкенд")
def test_view_with_non_numeric_id_does_not_crash(requester):
    response = requester.post(Endpoint.VIEW, payload={"id": "abc"})
    assert response.status == 200
