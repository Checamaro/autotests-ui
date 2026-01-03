import pytest

from fixtures.pages import dashboard_page
from pages.dashboard_page import DashboardPage
from pages.registration_page import RegistrationPage


@pytest.mark.regression
@pytest.mark.registration

def test_successful_registration(
        registration_page: RegistrationPage,
        dashboard_page: DashboardPage,
        email = "user.name@gmail.com",
        username="username",
        password = "password"
):
    registration_page.visit("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/auth/registration")
    registration_page.fill_registration_form(email=email, username=username, password=password)
    registration_page.check_registration_button_to_be_enabled()
    registration_page.click_registration_button()
    dashboard_page.check_dashboard_title_to_have_text()
