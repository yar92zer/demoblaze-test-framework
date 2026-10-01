import allure

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_page import ProductPage


@allure.step("Добавляем в корзину товар {title}")
def add_product_to_cart(home_page: HomePage, product_page: ProductPage, title: str) -> str:
    home_page.open()
    home_page.open_product(title)
    return product_page.add_to_cart()


@allure.step("Открываем корзину с товаром {title}")
def open_cart_with_product(
    home_page: HomePage, product_page: ProductPage, cart_page: CartPage, title: str
) -> None:
    add_product_to_cart(home_page, product_page, title)
    cart_page.open()
