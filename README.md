# UI Course Automation Tests

This project implements automated tests for
the [UI Course Test Application](https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/login). The
tests are written using **Python**, **Pytest**, **Allure** and **Playwright**. The test application’s source code is available
on [GitHub](https://github.com/Nikita-Filonov/qa-automation-engineer-ui-course).

## Project Overview

The goal of this project is to automate the testing of the UI Course application. The automated tests verify various
functionalities of the application to ensure its stability and correctness. The project structure follows best practices
for organizing test code with clear, maintainable scripts.

## Getting Started

### Clone the Repository

To get started, clone the project repository using Git:

```bash
git clone https://github.com/Checamaro/autotests-ui.git
cd autotests-ui
```

### Create a Virtual Environment

It's recommended to use a virtual environment to manage project dependencies. Follow the instructions for your operating
system:

#### Linux / MacOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

Once the virtual environment is activated, install the project dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Additional Playwright Setup (if needed)

If you're running Playwright for the first time, you might need to install the required browsers:

```bash
playwright install
```

### Running the Tests with Allure Report Generation

To run the tests and generate an Allure report, use the following command:

```bash
pytest -m "regression" --alluredir=./allure-results
```

This will execute all tests in the project and display the results in the terminal.

### Viewing the Allure Report

After the tests have been executed, you can generate and view the Allure report with:

```bash
allure serve allure-results
```

This command will open the Allure report in your default web browser.

## Структура проекта

Тесты построены по слоям (снизу вверх), каждый слой использует только нижележащий:

| Каталог | Назначение |
|---|---|
| `elements/` | Обёртки над элементами (`Button`, `Input`, `Text`, ...). Каждое действие и проверка — это шаг Allure, запись в лог и учёт покрытия (ui-coverage-tool). Локаторы — только `data-testid` |
| `components/` | Переиспользуемые блоки страницы: формы, навбар, сайдбар |
| `pages/` | Page objects: собирают компоненты и элементы, содержат методы `click_*` и `check_*` |
| `fixtures/` | Фикстуры браузера (чистое состояние, пользователь зарегистрирован и вошёл, вышел) и page objects |
| `tests/<feature>/` | Тесты по фичам (`authentication`, `courses`, `dashboard`) |
| `tools/` | Маршруты (`routes.py`), enum для Allure (`tools/allure`), логгер, вспомогательные скрипты |
| `docs/test-cases/` | Описание тест-кейсов по фичам, с привязкой к кейсам Qase |
| `templates/` | Шаблоны баг-репорта и тест-кейса |
| `.github/workflows/` | CI: запуск тестов и ИИ-разбор упавшего прогона |
| `.claude/` | Настройки ИИ-конвейера: агенты и скиллы Claude Code |

Тест вызывает только методы page objects; локаторы, `expect` и регулярные выражения живут в нижних слоях.

### Маркеры

`regression` (весь регресс), `authorization`, `registration`, `courses`, `dashboard`. Запуск одной фичи:

```bash
pytest -m courses
```

### Полезные команды

```bash
pytest -m regression --alluredir=allure-results -n 2   # регрессия в 2 потока
HEADLESS=false pytest -k <имя> -n 0                    # отладка с окном браузера
playwright show-trace tracing/<имя_теста>.zip          # трейс упавшего теста
python tools/ai/summarize_allure.py allure-results     # сводка падений для анализа
```

## Тестируемое приложение

SPA «UI Course» (React + MUI, HashRouter). Бэкенда нет: пользователи и курсы хранятся в localStorage браузера
(redux-persist), поэтому каждый новый браузерный контекст — «чистая база». Исходники приложения служат источником
требований; для работы ИИ-конвейера склонируйте их рядом с проектом:

```bash
git clone https://github.com/Nikita-Filonov/qa-automation-engineer-ui-course ../qa-automation-engineer-ui-course
```

## ИИ-конвейер QA

Проект использует конвейер субагентов Claude Code (определения — в `.claude/agents/`, правила — в `CLAUDE.md`):

```
ui-requirements-analyst → test-designer → autotest-writer → run-triager
```

| Агент | Что делает |
|---|---|
| `ui-requirements-analyst` | Анализирует фичу по исходникам приложения и живому приложению: маршруты, формы, валидация, хранение состояния; сравнивает с текущим покрытием, отмечает кандидатов в баги |
| `test-designer` | Проектирует тест-кейсы по отчёту аналитика и после подтверждения заводит их в Qase (проект `UI`); ведёт `docs/test-cases/<feature>.md` |
| `autotest-writer` | Пишет автотесты по кейсам, при необходимости расширяя elements → components → pages, проверяет локаторы в живом приложении, готовит PR |
| `run-triager` | Разбирает прогон (allure-results, трейсы, видео, GitHub Actions), классифицирует падения как баг приложения, проблему теста, окружение или флак |

Запуск: `/qa-pipeline <фича или страница>`, например `/qa-pipeline courses`. Отдельный скилл `/bug-report <описание>`
воспроизводит баг в браузере, оформляет его по шаблону `templates/bug.md` и после подтверждения заводит в GitHub Issues.

Правила работы конвейера:

- кейсы в Qase и баги в GitHub Issues создаются только после явного подтверждения;
- каждый новый тест привязан к кейсу Qase (`@qase.id(N)`);
- тест, падающий из-за подтверждённого бага приложения, помечается `@pytest.mark.xfail(reason="#<issue>", strict=True)`;
- изменения идут в ветках `ai/<коротко>` и попадают в `main` только через PR;
- не подгоняем тест под фактическое поведение, если оно противоречит исходникам приложения или здравому смыслу — заводим баг.

Для работы нужны MCP-серверы `playwright` и `qase` и CLI `gh` (авторизованный).

## CI

- **UI tests** (`.github/workflows/tests.yml`) — запуск регресса на `push` и `pull_request` в `main`, публикация Allure-отчёта.
- **AI triage** (`.github/workflows/ai-triage.yml`) — запускается после упавшего прогона `UI tests`: скачивает
  `allure-results`, формирует сводку падений (`tools/ai/summarize_allure.py`) и передаёт её на разбор Claude. Требуется
  секрет `CLAUDE_CODE_OAUTH_TOKEN`.
