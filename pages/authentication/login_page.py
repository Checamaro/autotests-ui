import re

from playwright.sync_api import Page
import allure
from components.authentication.login_form_component import LoginFormComponent
from elements.button import Button
from elements.link import Link
from elements.text import Text
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.login_form = LoginFormComponent(page)

        self.login_button = Button(page, 'login-page-login-button', 'Login')
        self.registration_link = Link(page, 'login-page-registration-link', 'Registration')
        self.wrong_email_or_password_alert = Text(page, 'login-page-wrong-email-or-password-alert',
                                                  'Wrong email or password')

    def click_login_button(self):
        self.login_button.click()

    def click_registration_link(self):
        self.registration_link.click()
        self.check_current_url(re.compile(".*/#/auth/registration"))

    @allure.step("Check visible wrong email or password alert")
    def check_visible_wrong_email_or_password_alert(self):
        self.wrong_email_or_password_alert.check_visible()
        self.wrong_email_or_password_alert.check_have_text('Wrong email or password')

    @allure.step("Check visible empty login page")
    def check_visible(self):
        self.check_current_url(re.compile(r".*/#/auth/login"))

        self.login_form.check_visible(email="", password="")
        self.login_button.check_visible()
        self.registration_link.check_visible()

    @allure.step("Check that login button is disabled")
    def check_disabled_login_button(self):
        self.login_button.check_disabled()

    @allure.step("Check that login button is enabled")
    def check_enabled_login_button(self):
        self.login_button.check_enabled()
