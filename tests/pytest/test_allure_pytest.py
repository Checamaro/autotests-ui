import allure


def test_feature():
    with allure.step("Opening browser"):
        ...  # Тут код открытия браузера

    with allure.step("Creating course"):
        ...  # Тут код создания курса

    with allure.step("Closing browser"):
        ...  # Тут код закрытия браузера
