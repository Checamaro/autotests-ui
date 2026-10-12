# QA-агент проекта autotests-ui

## Контекст
- Тестируемое приложение: SPA «UI Course» (React + MUI, HashRouter)
  https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/login
- Исходники приложения: https://github.com/Nikita-Filonov/qa-automation-engineer-ui-course —
  склонировать рядом в `../qa-automation-engineer-ui-course`. Это источник требований:
  маршруты (`src/index.tsx`, `src/Navigation`), формы и валидация (`src/Pages`, `src/Components/Forms`),
  логика авторизации (`src/Providers/AuthenticationProvider.tsx`).
- Бэкенда нет: пользователи и курсы хранятся в localStorage браузера (redux-persist, ключи `persist:users`,
  `persist:courses`). Каждый новый браузерный контекст — «чистая база».
- TMS: Qase, проект `UI` (через MCP-сервер `qase`). Баг-трекер: GitHub Issues (через `gh` CLI),
  метки `bug`, `ai-triage`, `flaky`, `test-issue`.
- Язык общения и комментариев в коде — русский; allure-заголовки тестов — на английском, как в проекте.

## Архитектура (слои снизу вверх)
- `elements/` — обёртки над элементами (`Button`, `Input`, `Text`, `Link`, ...), наследники `BaseElement`.
  Каждое действие/проверка: `allure.step` + `logger.info` + `track_coverage(ActionType.X)` (ui-coverage-tool).
  Локатор — только `data-testid`, передаётся строкой; динамические части — через `{}` и `**kwargs`.
- `components/` — переиспользуемые блоки страницы (формы, навбар, сайдбар), наследники `BaseComponent`.
  Публичные методы — с `@allure.step(...)`: `fill(...)`, `check_visible(...)`, `click_*`.
- `pages/` — страницы, наследники `BasePage`; собирают компоненты и элементы; методы `click_*`, `check_*`.
  Проверка URL — `check_current_url(re.compile(...))` внутри метода страницы/компонента, не в тесте.
- `fixtures/` — `browsers.py` (страница браузера, состояния), `pages.py` (фикстуры page objects).
  Состояния браузера: `chromium_page` (чистый), `chromium_page_with_state` (зарегистрирован и вошёл),
  `chromium_page_with_logged_out_state` (зарегистрирован, но вышел).
- `tools/routes.py` — `AppRoute`; `tools/allure/*` — enum для epic/feature/story/tag.
- `tests/<feature>/test_<feature>.py` — класс `Test<Feature>`; маркеры `@pytest.mark.regression` + маркер фичи;
  allure: tag, epic, feature, story, parent_suite, suite, sub_suite на классе; title и severity на тесте.

## Что делаем
- Тест вызывает только методы page objects — никаких `page.locator`, `expect` и regex в теле теста
  (исключение — `check_current_url` с regex, если метода страницы под это нет).
- Не хватает элемента/проверки — добавляем в нужный слой (элемент → компонент → страница), затем используем.
- Тестовые данные — из `settings.test_user` и производных от него; параметризация — с понятными `ids`.
- Каждый новый тест привязан к кейсу Qase: `@qase.id(N)`; id кейса указываем и в `docs/test-cases/<feature>.md`.
- Тест, который падает из-за подтверждённого бага приложения: `@pytest.mark.xfail(reason="#<issue>", strict=True)`.
- Новые маркеры — в `pytest.ini`, новые allure-значения — в `tools/allure/*.py`.
- Ветки `ai/<коротко>`, коммиты на русском: `test(auth): проверка выхода из системы`. В main — только через PR.

## Чего не делаем
- Никаких `time.sleep`/`wait_for_timeout` — только авто-ожидания Playwright и `expect`.
- Никаких XPath/CSS-локаторов в page objects (XPath допустим только в `get_raw_locator` для покрытия).
- Не подгоняем тест под фактическое поведение, если оно противоречит исходникам/здравому смыслу —
  останавливаемся и предлагаем `/bug-report`.
- Ничего не создаём в Qase и GitHub Issues без явного «да» (кроме CI, где правила задаёт workflow).
- Не выводим и не коммитим токены. Не меняем `.env` без запроса.

## Команды
- Установка: `pip install -r requirements.txt && playwright install --with-deps chromium`
- Регрессия: `pytest -m regression --alluredir=allure-results -n 2`
- Одна фича: `pytest -m authorization`
- Отладка с окном браузера: `HEADLESS=false pytest -k <имя> -n 0`
- Трейс упавшего теста: `playwright show-trace tracing/<имя_теста>.zip`
- Сводка падений для анализа: `python tools/ai/summarize_allure.py allure-results`

## Конвейер агентов
ui-requirements-analyst → test-designer → autotest-writer → run-triager.
Запуск: `/qa-pipeline <фича или страница>`. Подробности — `.claude/agents/`.
