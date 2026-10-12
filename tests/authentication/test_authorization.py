import re

import pytest

from config import settings
from tools.allure.tags import AllureTag
from pages.authentication.login_page import LoginPage
from pages.authentication.registration_page import RegistrationPage
from pages.dashboard.dashboard_page import DashboardPage
import allure
from tools.allure.epics import AllureEpic
from tools.allure.features import AllureFeature
from tools.allure.stories import AllureStory
from allure_commons.types import Severity

from tools.routes import AppRoute


@pytest.mark.regression
@pytest.mark.authorization
@allure.tag(AllureTag.REGISTRATION, AllureTag.AUTHORIZATION)
@allure.epic(AllureEpic.LMS)
@allure.feature(AllureFeature.AUTHENTICATION)
@allure.story(AllureStory.AUTHORIZATION)
@allure.parent_suite(AllureEpic.LMS)
@allure.suite(AllureFeature.AUTHENTICATION)
@allure.sub_suite(AllureStory.AUTHORIZATION)
class TestAuthorization:
    @pytest.mark.xdist_group(name="authorization-group")
    @pytest.mark.parametrize(
        "email, password",
        [
            ("user.name@gmail.com", "password"),
            ("user.name@gmail.com", "  "),
            ("  ", "password")
        ]
    )
    @allure.tag(AllureTag.USER_LOGIN)
    @allure.title('User login with wrong email or password')
    @allure.severity(Severity.CRITICAL)
    def test_wrong_email_or_password_authorization(self, login_page: LoginPage, email: str, password: str):
        login_page.visit(AppRoute.LOGIN)
        login_page.login_form.fill(email=email, password=password)
        login_page.click_login_button()
        login_page.check_visible_wrong_email_or_password_alert()

    @allure.tag(AllureTag.USER_LOGIN)
    @allure.title('User login with correct email or password')
    @allure.severity(Severity.BLOCKER)
    def test_successful_authorization(
            self,
            login_page: LoginPage,
            dashboard_page: DashboardPage,
            registration_page: RegistrationPage
    ):
        registration_page.visit(AppRoute.REGISTRATION)
        registration_page.registration_form.fill(email=settings.test_user.email, username=settings.test_user.username,
                                                 password=settings.test_user.password)
        registration_page.click_registration_button()

        dashboard_page.dashboard_toolbar_view.check_visible()
        dashboard_page.navbar.check_visible(settings.test_user.username)
        dashboard_page.sidebar.check_visible()
        dashboard_page.sidebar.click_logout()

        login_page.login_form.fill(email=settings.test_user.email, password=settings.test_user.password)
        login_page.click_login_button()

        dashboard_page.dashboard_toolbar_view.check_visible()
        dashboard_page.navbar.check_visible(settings.test_user.username)
        dashboard_page.sidebar.check_visible()

    @allure.tag(AllureTag.NAVIGATION)
    @allure.title('Navigate from login page to registration page')
    @allure.severity(Severity.NORMAL)
    def test_navigate_from_authorization_to_registration(
            self,
            login_page: LoginPage,
            registration_page: RegistrationPage
    ):
        login_page.visit(AppRoute.LOGIN)
        login_page.click_registration_link()

        registration_page.registration_form.check_visible(email="", username="", password="")

    @pytest.mark.parametrize(
        "email, password",
        [
            ("", ""),
            (settings.test_user.email, ""),
            ("", settings.test_user.password)
        ],
        ids=["empty-email-and-password", "empty-password", "empty-email"]
    )
    @allure.tag(AllureTag.USER_LOGIN, AllureTag.VALIDATION)
    @allure.title('Login button is disabled when email or password is empty')
    @allure.severity(Severity.NORMAL)
    def test_login_button_disabled_with_empty_fields(self, login_page: LoginPage, email: str, password: str):
        login_page.visit(AppRoute.LOGIN)
        login_page.login_form.fill(email=email, password=password)
        login_page.check_disabled_login_button()

    @allure.tag(AllureTag.USER_LOGIN, AllureTag.VALIDATION)
    @allure.title('Login button is enabled when email and password are filled')
    @allure.severity(Severity.NORMAL)
    def test_login_button_enabled_with_filled_fields(self, login_page: LoginPage):
        login_page.visit(AppRoute.LOGIN)
        login_page.login_form.fill(email=settings.test_user.email, password=settings.test_user.password)
        login_page.check_enabled_login_button()

    @allure.tag(AllureTag.USER_LOGIN, AllureTag.SECURITY)
    @allure.title('Password is masked in login form')
    @allure.severity(Severity.NORMAL)
    def test_password_masked_in_login_form(self, login_page: LoginPage):
        login_page.visit(AppRoute.LOGIN)
        login_page.login_form.fill(email=settings.test_user.email, password=settings.test_user.password)
        login_page.login_form.check_password_masked()

    @allure.tag(AllureTag.USER_LOGIN)
    @allure.title('Registered user logs in with correct email and password')
    @allure.severity(Severity.BLOCKER)
    def test_successful_authorization_of_registered_user(
            self,
            login_page_with_logged_out_state: LoginPage,
            dashboard_page_with_logged_out_state: DashboardPage
    ):
        login_page_with_logged_out_state.visit(AppRoute.LOGIN)
        login_page_with_logged_out_state.login_form.fill(
            email=settings.test_user.email,
            password=settings.test_user.password
        )
        login_page_with_logged_out_state.click_login_button()

        dashboard_page_with_logged_out_state.check_authorized(settings.test_user.username)

    @pytest.mark.parametrize(
        "password",
        [
            f"{settings.test_user.password}-wrong",
            settings.test_user.password.upper()
        ],
        ids=["wrong-password", "password-in-different-case"]
    )
    @allure.tag(AllureTag.USER_LOGIN, AllureTag.SECURITY)
    @allure.title('Registered user cannot log in with wrong password')
    @allure.severity(Severity.CRITICAL)
    def test_wrong_password_for_registered_user(self, login_page_with_logged_out_state: LoginPage, password: str):
        login_page_with_logged_out_state.visit(AppRoute.LOGIN)
        login_page_with_logged_out_state.login_form.fill(email=settings.test_user.email, password=password)
        login_page_with_logged_out_state.click_login_button()

        login_page_with_logged_out_state.check_visible_wrong_email_or_password_alert()
        login_page_with_logged_out_state.check_current_url(re.compile(r".*/#/auth/login"))

    @pytest.mark.parametrize(
        "route",
        [AppRoute.DASHBOARD, AppRoute.COURSES, AppRoute.CREATE_COURSES],
        ids=["dashboard", "courses", "create-course"]
    )
    @allure.tag(AllureTag.ACCESS_CONTROL)
    @allure.title('Unauthorized user is redirected to login page from protected page')
    @allure.severity(Severity.CRITICAL)
    def test_unauthorized_user_redirected_to_login(self, login_page: LoginPage, route: AppRoute):
        login_page.visit(route)
        login_page.check_visible()

    @allure.tag(AllureTag.USER_LOGOUT, AllureTag.SESSION, AllureTag.ACCESS_CONTROL)
    @allure.title('Logout ends session and closes access to protected pages')
    @allure.severity(Severity.CRITICAL)
    def test_logout_ends_session(self, dashboard_page_with_state: DashboardPage, login_page_with_state: LoginPage):
        dashboard_page_with_state.visit(AppRoute.DASHBOARD)
        dashboard_page_with_state.check_authorized(settings.test_user.username)

        dashboard_page_with_state.sidebar.click_logout()
        login_page_with_state.check_visible()

        # После выхода защищённая страница недоступна ни кнопкой «Назад», ни по прямой ссылке
        login_page_with_state.go_back()
        login_page_with_state.check_visible()

        dashboard_page_with_state.visit(AppRoute.DASHBOARD)
        login_page_with_state.check_visible()

    @allure.tag(AllureTag.SESSION)
    @allure.title('Session persists after page reload')
    @allure.severity(Severity.NORMAL)
    def test_session_persists_after_reload(self, dashboard_page_with_state: DashboardPage):
        dashboard_page_with_state.visit(AppRoute.DASHBOARD)
        dashboard_page_with_state.check_authorized(settings.test_user.username)

        dashboard_page_with_state.reload()
        dashboard_page_with_state.check_authorized(settings.test_user.username)
