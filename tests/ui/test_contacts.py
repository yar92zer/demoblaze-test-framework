import allure
import pytest

pytestmark = [pytest.mark.ui, allure.feature("Обратная связь")]


@pytest.mark.smoke
@allure.title("Форма обратной связи показывает подтверждение отправки")
def test_contact_form_shows_confirmation(home_page, header, contact_modal):
    home_page.open()
    header.open_contact_modal()
    message = contact_modal.send_message(
        "qa@example.com", "QA Tester", "Проверка формы обратной связи"
    )
    assert message == "Thanks for the message!!"
