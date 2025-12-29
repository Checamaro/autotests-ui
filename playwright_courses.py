from playwright.sync_api import sync_playwright, expect

with sync_playwright() as playwright:
    # Открываем браузер и создаем новую страницу
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Переходим на страницу регистрации
    page.goto("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/registration")

    # Заполняем поле email
    email_input = page.get_by_test_id('registration-form-email-input').locator('input')
    email_input.fill("user.name@gmail.com")

    # Заполняем поле username
    username_input = page.get_by_test_id('registration-form-username-input').locator('input')
    username_input.fill("username")

    # Заполняем поле пароль
    password_input = page.get_by_test_id('registration-form-password-input').locator('input')
    password_input.fill("password")

    # Проверяем, что кнопка "Registration" кликабельна и нажимаем
    registration_button = page.get_by_test_id('registration-page-registration-button')
    expect(registration_button).to_be_enabled()
    registration_button.click()

    context.storage_state(path='browser-state.json')

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state='browser-state.json')
    page = context.new_page()

    page.goto("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/courses")

    courses_list_toolbar_title_text = page.get_by_test_id('courses-list-toolbar-title-text')
    expect(courses_list_toolbar_title_text).to_have_text('Courses')

    courses_list_empty_view_title_text = page.get_by_test_id('courses-list-empty-view-title-text')
    expect(courses_list_empty_view_title_text).to_have_text('There is no results')

    courses_list_empty_view_description_text = page.get_by_test_id('courses-list-empty-view-description-text')
    expect(courses_list_empty_view_description_text).to_have_text(
        'Results from the load test pipeline will be displayed here')
