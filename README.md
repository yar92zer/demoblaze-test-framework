[![Tests](https://github.com/yar92zer/demoblaze-test-framework/actions/workflows/ci.yml/badge.svg)](https://github.com/yar92zer/demoblaze-test-framework/actions/workflows/ci.yml)

# Demoblaze Test Framework

Тестовый фреймворк для публичного демо-магазина demoblaze.com: API-клиент
(`https://api.demoblaze.com`), UI на Playwright (`https://www.demoblaze.com`)
и сквозные тесты, проверяющие, что оба слоя видят одни и те же данные.

Тесты идут против живого публичного стенда — нужен интернет, и красный прогон
может означать недоступность чужого сервиса.

[Allure-отчёт последнего прогона](https://yar92zer.github.io/demoblaze-test-framework) ·
[Контракт API](api-contract.md)

## Стек

Python 3.11, pytest, requests, Pydantic, Playwright, Allure, pytest-xdist, GitHub Actions

## Что покрыто

40 тестов, при живом стенде — 34 passed и 6 xfailed:

| Слой | Тестов | Домены |
|---|--------|---|
| `tests/api/` | 13     | каталог, авторизация, корзина, известные дефекты |
| `tests/ui/` | 24     | авторизация, каталог, корзина, заказ, контакты, известные дефекты |
| `tests/cross/` | 3      | сквозные API + UI |

Плюс 13 задокументированных дефектов стенда, шесть из них зафиксированы
`xfail(strict=True)` — почини стенд, и прогон покраснеет: №1, №4, №9 в
`tests/api/test_known_defects.py`, №7, №11, №13 в `tests/ui/test_known_defects.py`.

## Структура

```
demoblaze-test-framework/
├── .github/workflows/
│   ├── ci.yml                 lint + stand + api + ui + nightly regression
│   └── pages.yml              сборка Allure и деплой в ветку gh-pages
├── client/                    API-клиент
│   ├── custom_requester.py    транспорт: сессия, таймауты, разбор тела, Allure
│   ├── endpoints.py           пути эндпоинтов одним Enum
│   ├── services/              base, auth, cart, catalog
│   └── models/                Pydantic-валидация: product, cart
├── pages/                     Page Object'ы
│   ├── base_page.py           обёртки над Playwright
│   ├── base_modal.py          общий базовый класс модалок: wait_open, close
│   ├── home_page.py           витрина: категории, пагинация, карточки
│   ├── product_page.py
│   ├── cart_page.py
│   ├── header.py
│   ├── login_modal.py
│   ├── signup_modal.py
│   ├── order_modal.py
│   └── contact_modal.py
├── steps/                     сценарии, проходящие через несколько страниц
│   ├── auth_steps.py          открыть форму входа, войти под пользователем
│   └── cart_steps.py          добавить товар, открыть корзину с товаром
├── utils/
│   ├── data_generator.py      уникальный логин на каждый тест
│   ├── assertions.py          assert_no_error, assert_status_code
│   ├── encoders.py            base64: encode_password, decode_token
│   └── retry.py               with_retry поверх tenacity
├── tests/
│   ├── api/                   test_catalog, test_auth, test_cart, test_known_defects
│   ├── ui/                    + test_order, test_contacts
│   └── cross/                 test_api_ui
├── conftest.py                фикстуры обоих слоёв, скриншот при падении
├── settings.py                base_url, front_url, таймаут, ретраи из .env
├── probe_demoblaze.py         разведка контракта: чем снят api-contract.md
├── api-contract.md            подтверждённый контракт стенда
├── pytest.ini
├── ruff.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── .gitattributes
└── README.md
```

API: `CustomRequester → Service → Tests`. UI: `BasePage → Page Object → Steps → Tests`.

Page Object описывает одну страницу и ничего не знает о соседних. Сценарий
«открыть витрину → карточку товара → добавить в корзину» затрагивает три
страницы сразу, поэтому живёт в `steps/`: так страницы не импортируют друг
друга, а повторяющиеся цепочки не копируются по тестам. Каждый шаг помечен
`@allure.step` и в отчёте читается одной строкой.

`conftest.py` в корне — фикстуры нужны всем трём наборам тестов.

## Запуск

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
pytest -v
```

Выборочно:

```bash
pytest -m smoke          # 13
pytest -m regression     # 19, только позитивные — это не полный прогон
pytest -m negative       # 8
pytest -m ui             # 24
pytest -m cross          # 3
pytest tests/api         # 13
pytest -n 4              # параллельно
pytest -m ui --headed    # с видимым браузером
```

Allure:

```bash
pytest --alluredir=allure-results && allure serve allure-results
```

К упавшему UI-тесту автоматически прикладываются скриншот и URL страницы.

## Конфигурация

Работает без настройки. Чтобы переопределить — скопируйте `.env.example` в `.env`:
`BASE_URL`, `FRONT_URL`, `TIMEOUT`, `RETRY_ATTEMPTS`.

## CI

GitHub Actions: `lint` (ruff), `api` и `ui` smoke на каждый push/PR, полный
`regression` — ночью в 06:00 UTC и по кнопке.

Allure-отчёт собирает отдельный workflow `pages.yml` после каждого прогона
`Tests`, в том числе красного, — пропускаются только отменённые. Результаты
всех джоб сливаются в один отчёт, он деплоится в ветку `gh-pages`, оттуда его
раздаёт GitHub Pages. Папка `history` из прошлой версии `gh-pages` копируется в
новые результаты, поэтому в отчёте видны тренды между прогонами.

Перед тестами идёт джоба `stand`: до трёх раз запрашивает `/entries` и падает,
если стенд не отдаёт товары. От неё зависят `api`, `ui` и `regression`, так что
лежащий стенд даёт одну понятную ошибку вместо россыпи красных тестов. `lint`
от стенда не зависит.

На push и PR гоняются только `tests/api` и `tests/ui`. Кросс-тесты (`tests/cross/`)
туда не попадают, хотя `test_api_added_product_visible_in_ui` помечен `smoke`, —
они запускаются только в ночном `regression`.
