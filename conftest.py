import allure
import pytest

from client.custom_requester import CustomRequester
from client.services.auth_service import AuthService
from client.services.cart_service import CartService
from client.services.catalog_service import CatalogService
from pages.cart_page import CartPage
from pages.contact_modal import ContactModal
from pages.header import Header
from pages.home_page import HomePage
from pages.login_modal import LoginModal
from pages.order_modal import OrderModal
from pages.product_page import ProductPage
from pages.signup_modal import SignupModal
from settings import FRONT_URL, UI_TIMEOUT
from steps.auth_steps import login_as
from utils.data_generator import DEFAULT_PASSWORD, unique_username


@pytest.fixture
def home_page(page):
    return HomePage(page, FRONT_URL, UI_TIMEOUT)


@pytest.fixture
def product_page(page):
    return ProductPage(page, FRONT_URL, UI_TIMEOUT)


@pytest.fixture
def login_modal(page):
    return LoginModal(page, FRONT_URL, UI_TIMEOUT)


@pytest.fixture
def signup_modal(page):
    return SignupModal(page, FRONT_URL, UI_TIMEOUT)


@pytest.fixture
def header(page):
    return Header(page, FRONT_URL, UI_TIMEOUT)


@pytest.fixture
def registered_user(auth):
    username = unique_username()
    # Фронт кодирует пароль сам, AuthService делает то же для API:
    # в базе должен лежать base64, а в фикстурах и формах - открытый пароль.
    auth.signup(username, DEFAULT_PASSWORD)
    return {"username": username, "password": DEFAULT_PASSWORD}


@pytest.fixture
def logged_in_user(page, home_page, header, login_modal, registered_user):
    login_as(
        home_page, header, login_modal, registered_user["username"], registered_user["password"]
    )
    page.locator(header.USERNAME_LABEL).wait_for(state="visible", timeout=UI_TIMEOUT)
    return registered_user


@pytest.fixture
def cart_page(page):
    return CartPage(page, FRONT_URL, UI_TIMEOUT)


@pytest.fixture(scope="session")
def requester():
    return CustomRequester()


@pytest.fixture(scope="session")
def catalog(requester):
    return CatalogService(requester)


@pytest.fixture(scope="session")
def auth(requester):
    return AuthService(requester)


@pytest.fixture
def authenticated_user(auth):
    username = unique_username()
    auth.signup(username, DEFAULT_PASSWORD)
    token = auth.login(username, DEFAULT_PASSWORD)
    return {"username": username, "token": token}


@pytest.fixture(scope="session")
def cart(requester):
    return CartService(requester)


@pytest.fixture
def cart_with_product(cart, authenticated_user):
    item_id = cart.add_to_cart(authenticated_user["token"], product_id=1)
    yield {"item_id": item_id, "token": authenticated_user["token"]}
    try:
        # /deleteitem не проверяет владельца - тем и пользуемся.
        # Дефект зафиксирован в test_cart_item_cannot_be_deleted_without_owner_token.
        cart.delete_item(item_id)
    except AssertionError:
        # Уборка best-effort: стенд иногда отвечает "Not found."
        # а упавший teardown красит прошедший тест.
        pass


@pytest.fixture
def order_modal(page):
    return OrderModal(page, FRONT_URL, UI_TIMEOUT)


@pytest.fixture
def contact_modal(page):
    return ContactModal(page, FRONT_URL, UI_TIMEOUT)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    page = item.funcargs.get("page")
    if page is None:
        return

    allure.attach(
        page.screenshot(full_page=True),
        name="Скриншот при падении",
        attachment_type=allure.attachment_type.PNG,
    )
    allure.attach(
        page.url,
        name="URL",
        attachment_type=allure.attachment_type.TEXT,
    )
