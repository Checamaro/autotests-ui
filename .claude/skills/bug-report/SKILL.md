---
name: bug-report
description: Воспроизводит баг UI Course в браузере, оформляет по шаблону и заводит в GitHub Issues после подтверждения. Вызов /bug-report <описание проблемы>.
---
Проблема: $ARGUMENTS

1. Воспроизведи через Playwright MCP (или минимальным тестом); сохрани шаги, данные и скриншот
   (`browser_take_screenshot`). Найди место в исходниках приложения, которое объясняет поведение.
2. Заполни `templates/bug.md`. Заголовок: `[<Страница>] <что не так> при <условии>`.
3. Дубли: `gh issue list --state all --label bug --search "<ключевые слова>"`.
4. Покажи черновик и дождись «да».
5. `gh issue create --title "..." --body-file <файл> --label bug` — верни ссылку.
6. Если есть падающий автотест — предложи `@pytest.mark.xfail(reason="#<номер>", strict=True)`.
