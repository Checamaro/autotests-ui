# Тест-кейсы: authorization

Источник требований: `src/Providers/AuthenticationProvider.tsx`, `src/Pages/Authentication/LoginPage.tsx`,
`src/Navigation/Authentication/AuthenticationRoute.tsx`, `src/index.tsx` приложения UI Course.
Кейсы ещё не загружены в Qase: следующий шаг — `test-designer` заводит их в проект `UI`
и проставляет `@qase.id` в тестах.

| № | Qase ID | Название | Тип | Приоритет | Автотест |
|---|---|---|---|---|---|
| 1 | — | Вход с неверными email или паролем (пользователя нет) | negative | High | `test_wrong_email_or_password_authorization` |
| 2 | — | Регистрация, выход и повторный вход | positive | High | `test_successful_authorization` |
| 3 | — | Переход со страницы входа на регистрацию | navigation | Medium | `test_navigate_from_authorization_to_registration` |
| 4 | — | Кнопка Login неактивна при пустом email и/или пароле | validation | Medium | `test_login_button_disabled_with_empty_fields` |
| 5 | — | Кнопка Login активна при заполненных полях | validation | Medium | `test_login_button_enabled_with_filled_fields` |
| 6 | — | Пароль маскируется в форме входа | security | Medium | `test_password_masked_in_login_form` |
| 7 | — | Вход зарегистрированного пользователя | positive | High | `test_successful_authorization_of_registered_user` |
| 8 | — | Неверный пароль / пароль в другом регистре для существующего пользователя | negative, security | High | `test_wrong_password_for_registered_user` |
| 9 | — | Гостя перенаправляет на вход с dashboard, courses, create course | access-control | High | `test_unauthorized_user_redirected_to_login` |
| 10 | — | Выход завершает сессию: нет доступа по «Назад» и по прямой ссылке | access-control | High | `test_logout_ends_session` |
| 11 | — | Сессия сохраняется после перезагрузки страницы | session | Medium | `test_session_persists_after_reload` |

## Вопросы к требованиям (не автоматизировано)
- Авторизованный пользователь может открыть `#/auth/login` — редиректа на dashboard нет
  (маршруты `/auth/*` обёрнуты в `PublicRoute`). Ожидаемое ли это поведение?
- Email сравнивается с учётом регистра: `USER.NAME@gmail.com` не входит. Обычно email регистронезависим.

## Найдено по пути (регистрация, вне объёма задачи)
- Кнопка «Registration» активна при пустом username: в `RegistrationPage.tsx` условие проверяет
  `request.password === ''` дважды вместо username.
- Проверка «User already exists» сравнивает email **и** пароль: тот же email с другим паролем регистрируется повторно.
