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
@allure.title("Токен обратимо декодируется и содержит логин пользователя")
def test_token_is_reversible(authenticated_user):
    decoded = decode_token(authenticated_user["token"])
    username = authenticated_user["username"]
    assert decoded.startswith(username)
    assert decoded[len(username) :].isdigit()


@pytest.mark.auth
@pytest.mark.negative
@allure.title("Вход с неверным паролем отклоняется")
def test_login_with_wrong_password(auth):
    username = unique_username()
    auth.signup(username, DEFAULT_PASSWORD)
    with pytest.raises(AssertionError):
        auth.login(username, "wrong_password")
