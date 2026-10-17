import allure
import pytest

from steps.auth_steps import login_as
from steps.cart_steps import add_product_to_cart

pytestmark = [pytest.mark.cross, allure.feature("Сквозные сценарии")]
SAMSUNG_ID=1
SAMSUNG_TITLE= "Samsung galaxy s6"
NEXUS_ID = 3
NEXUS_TITLE= "Nexus 6"


@pytest.mark.smoke
@allure.title("Товар, добавленный через API, виден в корзине в браузере")
def test_api_added_product_visible_in_ui(
    auth, cart, registered_user, home_page, header, login_modal, cart_page,
):
    token = auth.login(registered_user["username"], registered_user["password"])
    cart.add_to_cart(token, product_id=SAMSUNG_ID)

    login_as(
        home_page, header, login_modal, registered_user["username"], registered_user["password"]
    )
    cart_page.open()
    assert SAMSUNG_TITLE in cart_page.get_item_titles()


@pytest.mark.regression
@allure.title("Товар, добавленный в браузере, виден в корзине через API")
def test_ui_added_product_visible_in_api(
    auth, cart, registered_user, home_page, header, product_page, logged_in_user
):
    add_product_to_cart(home_page, product_page, NEXUS_TITLE)
    token = auth.login(registered_user["username"], registered_user["password"])
    body = cart.view_cart(token)
    assert [item.prod_id for item in body.Items] == [NEXUS_ID]


@pytest.mark.regression
@allure.title("Цены в каталоге API и на витрине совпадают")
def test_catalog_prices_match_between_api_and_ui(catalog, home_page):
    api_prices = {item.title.strip(): item.price for item in catalog.get_entries().Items}
    home_page.open()
    ui_titles = home_page.get_product_titles()
    ui_prices = home_page.get_product_prices()
    assert set(ui_titles)== set(api_prices)
    for title, raw_price in zip(ui_titles, ui_prices):
        assert float(raw_price.lstrip("$")) == api_prices[title]
