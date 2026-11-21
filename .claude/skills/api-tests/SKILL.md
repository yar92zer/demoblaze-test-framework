---
name: api-tests
description: Как писать и править API-тесты demoblaze в tests/api/ — сервисы client/, фикстуры conftest.py, маркеры, xfail для дефектов стенда. Использовать, когда просят добавить или починить API-тест, завести новый эндпоинт в клиенте или модель ответа.
---

# API-тесты demoblaze

## Прежде чем писать код

- Источник правды — `api-contract.md`. Если эндпоинта или поля там нет, код
  не писать: сначала подтвердить через `probe_demoblaze.py` или ручной
  запрос, потом внести в `api-contract.md`.

## Слои

```
тест -> фикстура (conftest.py) -> сервис (client/services) -> CustomRequester -> стенд
```

- Тест работает через сервисы `catalog`, `auth`, `cart`. Напрямую
  `requester` вызывать только когда проверяется сам транспорт (код 500,
  сырое тело), как в `test_view_with_non_numeric_id_does_not_crash`.
- Новый эндпоинт добавляется так:
  1. значение в `Endpoint` (`client/endpoints.py`);
  2. метод сервиса с `@allure.step("API: ...")`, внутри
     `self.requester.post(...)`, затем `assert_no_error(response.body)`;
  3. если тело — объект, pydantic-модель в `client/models/` и возврат
     `Model(**response.body)`.
- Ассерты на бизнес-данные пишутся в тесте, а не в сервисе. В сервисе
  только `assert_no_error` и проверка формы ответа (как в `AuthService.login`).

## Особенности стенда, которые надо учитывать в тестах

- **Бизнес-ошибка приходит с кодом 200** и полем `errorMessage` в теле.
  `assert_status_code` в requester проверяет только, что стенд жив.
  Негативный кейс проверяется так:
  `with pytest.raises(AssertionError, match="<текст errorMessage>"):`
  вокруг вызова сервиса.
- **Тип тела зависит от исхода**: `/login` и `/deleteitem` при успехе
  отдают JSON-строку (`str`), при ошибке `dict`; `/addtocart` отдаёт
  пустое тело `text/html`, и `_parse` возвращает `""`. Не обращаться к
  `body["..."]`, не проверив тип.
- **Неверный тип параметра даёт 500 и HTML** вместо JSON. Ожидать такой
  ответ через `requester.post(..., expected_status=500)`.
- **id позиции корзины генерирует клиент**: `CartService.add_to_cart`
  создаёт uuid4 и возвращает его. По нему же и удаляется позиция.
- Пароль кодирует `AuthService` (`encode_password`), а фикстуры и тесты
  передают открытый `DEFAULT_PASSWORD`. Тело `/signup` и `/login` руками
  не собирать: регистрация и вход должны идти в одном формате.

## Данные и изоляция (стенд общий)

- Пользователя брать только из фикстур (`authenticated_user`,
  `registered_user`), имя генерирует `unique_username()` с префиксом `qa_`.
  Хардкод-кредов нет.
- Всё созданное убирается в teardown через yield-фикстуру. Уборка
  best-effort: `AssertionError` в teardown глотается, как в
  `cart_with_product`, чтобы флап стенда не красил прошедший тест.
- Ассерты по корзине привязаны к своему `item_id` (`item_id in ids`), а не
  к количеству. Исключение — пустая корзина только что созданного юзера.
- Названия товаров брать из фикстуры `product_titles`, не хардкодить.

## Фикстуры

| Фикстура | Scope | Что даёт |
|---|---|---|
| `requester` | session | `CustomRequester` |
| `catalog`, `auth`, `cart` | session | сервисы |
| `product_titles` | session | `{id: title.strip()}` из `/entries` |
| `registered_user` | function | `{"username", "password"}`, только signup |
| `authenticated_user` | function | `{"username", "token"}`, signup + login |
| `cart_with_product` | function | `{"item_id", "token"}`, товар 1, чистится в teardown |

Новую фикстуру добавлять в корневой `conftest.py`, рядом с похожими.

## Оформление теста

```python
pytestmark = allure.feature("Корзина")  # одна на модуль


@pytest.mark.cart  # домен, по желанию
@pytest.mark.regression  # уровень, ровно один
@allure.title("Корзина нового пользователя пуста")
def test_new_user_cart_is_empty(cart, authenticated_user):
    body = cart.view_cart(authenticated_user["token"])
    assert body.Items == []
```

- Уровень — ровно один из `smoke` / `regression` / `negative`. Домен
  (`auth`, `cart`) вешается поверх. В `pytest.ini` стоит `--strict-markers`,
  так что новый маркер без записи в `pytest.ini` уронит сбор.
- `@allure.title` по-русски, имя функции `test_<что_проверяется>`.
- После добавления или удаления теста обновить счётчики в README: таблицу
  «Что покрыто» и команды `pytest -m ...`.

## Известные дефекты стенда

- Тест пишется на **правильное** поведение и помечается
  `xfail(strict=True, raises=<исключение>, reason="Дефект №N: ...")` в
  `tests/api/test_known_defects.py`.
- `raises` указывать обязательно: без него xfail проглотит любое падение,
  включая недоступность стенда.
- Новый дефект сначала подтверждается ручным запросом, потом попадает в
  `api-contract.md`, и только после этого — в тест.

## Проверка перед коммитом

```powershell
pytest tests/api -m smoke
pytest tests/api
ruff check .
ruff format --check .
```

Последние две команды — те же, что в джобе `lint` в `.github/workflows/ci.yml`.
