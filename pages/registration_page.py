from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from components.authentication.registration_form_component import RegistrationFormComponent


class RegistrationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.registration_form = RegistrationFormComponent(page)
        self.login_link = page.get_by_test_id('registration-page-login-link')

    def click_login_link(self):
        self.login_link.click()

    def click_registration_button(self):
        self.registration_form.registration_button.click()

    def check_registration_button_to_be_enabled(self):
        expect(self.registration_form.registration_button).to_be_enabled()
