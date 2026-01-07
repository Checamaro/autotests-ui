import re
from playwright.sync_api import Page
from components.authentication.registration_form_component import RegistrationFormComponent
from pages.base_page import BasePage
from elements.link import Link
from elements.button import Button



class RegistrationPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.registration_form = RegistrationFormComponent(page)

        self.login_link = Link(page, 'registration-page-login-link', 'Login link')
        self.registration_button = Button(page, 'registration-page-registration-button', 'Registration')

    def click_registration_button(self):
        self.registration_form.registration_button.click()

    def click_login_link(self):
        self.login_link.click()
        self.check_current_url(re.compile(".*/#/auth/login"))
