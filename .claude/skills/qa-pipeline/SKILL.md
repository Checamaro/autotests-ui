---
name: qa-pipeline
description: Полный конвейер QA для фичи или страницы UI Course — анализ исходников, тест-кейсы в Qase, автотесты на page objects, PR, разбор прогона. Вызов /qa-pipeline <фича или страница>.
---
Аргумент: $ARGUMENTS (например `authorization`, `courses`, `#/courses/create`).

После каждого шага коротко отчитайся и дождись моего «дальше»:

1. **Подготовка.** Проверь, что есть `../qa-automation-engineer-ui-course/src` и что MCP `playwright` и `qase`
   подключены. Если чего-то нет — скажи, что сделать, и остановись.
2. **Анализ.** Субагент `ui-requirements-analyst` для $ARGUMENTS.
3. **Тест-дизайн.** Его отчёт — субагенту `test-designer`. Покажи таблицу кейсов.
4. **Автоматизация.** Утверждённые кейсы — субагенту `autotest-writer`.
5. **Прогон и разбор.** `pytest -m regression --alluredir=allure-results -n 2`; при падениях — субагент `run-triager`.
6. **Итог.** Кейсов / автотестов / изменений во фреймворке / багов / ссылка на PR.
   Строка в `docs/ai-metrics.md`: дата | фича | кейсов | автотестов | багов | итераций правок.
