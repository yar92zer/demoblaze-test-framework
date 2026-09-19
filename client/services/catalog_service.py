import allure

from client.endpoints import Endpoint
from client.models.product import EntriesResponse, Product
from client.services.base_service import BaseService
from utils.assertions import assert_no_error


class CatalogService(BaseService):
    @allure.step("API: получаем список товаров")
    def get_entries(self) -> EntriesResponse:
        response = self.requester.get(Endpoint.ENTRIES)
        assert_no_error(response.body)
        return EntriesResponse(**response.body)

    @allure.step("API: получаем товары категории")
    def get_by_category(self, category: str) -> EntriesResponse:
        response = self.requester.post(Endpoint.BYCAT, payload={"cat": category})
        assert_no_error(response.body)
        return EntriesResponse(**response.body)

    @allure.step("API: получаем товар {product_id}")
    def get_product(self, product_id: str) -> Product:
        response = self.requester.post(Endpoint.VIEW, payload={"id": product_id})
        assert_no_error(response.body)
        return Product(**response.body)
