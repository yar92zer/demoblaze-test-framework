import allure
import pytest

from utils.data_generator import DEFAULT_PASSWORD, unique_username
from utils.encoders import decode_token

pytestmark = allure.feature("Авторизация")


@pytest.mark.smoke
@pytest.mark.auth
@allure.title("Регистрация и вход возвращают рабочий токен")
def test_signup_and_login(auth):
    username = unique_username()
    auth.signup(username, DEFAULT_PASSWORD)
    token = auth.login(username, DEFAULT_PASSWORD)
    assert decode_token(token).startswith(username)


@pytest.mark.auth
@pytest.mark.regression
@allure.title("Проверка валидного токена возвращает его владельца")
def test_check_returns_token_owner(auth, authenticated_user):
    body = auth.check(authenticated_user["token"])
    assert body.Item.username == authenticated_user["username"]


@pytest.mark.auth
@pytest.mark.negative
@allure.title("Вход с неверным паролем отклоняется")
def test_login_with_wrong_password(auth):
    username = unique_username()
    auth.signup(username, DEFAULT_PASSWORD)
    with pytest.raises(AssertionError, match="Wrong password"):
        auth.login(username, "wrong_password")
