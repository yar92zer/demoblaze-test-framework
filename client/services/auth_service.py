import allure

from client.endpoints import Endpoint
from client.models.auth import CheckResponse
from client.services.base_service import BaseService
from utils.assertions import assert_no_error
from utils.encoders import encode_password


class AuthService(BaseService):
    @allure.step("API: регистрируем {username}")
    def signup(self, username: str, password: str) -> None:
        response = self.requester.post(
            Endpoint.SIGNUP,
            payload={"username": username, "password": encode_password(password)},
        )
        assert_no_error(response.body)

    @allure.step("API: логинимся под {username}")
    def login(self, username: str, password: str) -> str:
        response = self.requester.post(
            Endpoint.LOGIN,
            payload={"username": username, "password": encode_password(password)},
        )
        assert_no_error(response.body)

        body = response.body
        if not isinstance(body, str) or ":" not in body:
            raise AssertionError(f"Ожидали строку вида 'Auth_token: <...>', получили: {body!r}")
        return body.split(":", 1)[1].strip()

    @allure.step("API: проверяем токен")
    def check(self, token: str) -> CheckResponse:
        response = self.requester.post(
            Endpoint.CHECK,
            payload={"token": token},
        )
        assert_no_error(response.body)
        return CheckResponse(**response.body)
