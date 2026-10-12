### <Название: действие + объект + условие, например «Вход с паролем в другом регистре»>
- **Qase ID:** UI-<N> (заполняется после загрузки)
- **Фича / страница:** authorization / `#/auth/login`
- **Тип:** positive | negative | access-control | navigation | security
- **Приоритет:** High | Medium | Low
- **Техника:** классы эквивалентности | граничные значения | таблица решений | переходы состояний
- **Предусловия / состояние браузера:** чистый | зарегистрирован и вошёл | зарегистрирован, но вышел
- **Тестовые данные:** settings.test_user (email, password в верхнем регистре)
- **Шаги:**
  1. Открыть `#/auth/login`
  2. Ввести email и пароль, нажать «Login»
- **Ожидаемый результат:** алерт «Wrong email or password», URL остаётся `#/auth/login`
- **Автоматизирован:** нет | `tests/authentication/test_authorization.py::TestAuthorization::test_...`
