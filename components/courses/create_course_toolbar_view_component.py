import re

import allure
from playwright.sync_api import Page

from components.base_component import BaseComponent
from elements.button import Button
from elements.text import Text


class CreateCourseToolbarViewComponent(BaseComponent):
    def __init__(self, page: Page):
        super().__init__(page)

        self.title = Text(page, 'create-course-toolbar-title-text', 'Title')
        self.create_course_button = Button(
            page, 'create-course-toolbar-create-course-button', 'Create course'
        )

    @allure.step('Check visible course toolbar with title "{title}"')
    def check_visible(self, title: str = 'Create course'):
        self.title.check_visible()
        self.title.check_have_text(title)

        self.create_course_button.check_visible()

    @allure.step("Click save course button")
    def click_create_course_button(self):
        self.create_course_button.click()

    @allure.step("Click save course button and check redirect to courses list")
    def click_create_course_button_and_check_redirect(self):
        self.create_course_button.click()
        self.check_current_url(re.compile(r".*/#/courses$"))

    @allure.step("Check created course button is disabled")
    def check_disabled_create_course_button(self):
        self.create_course_button.check_disabled()

    @allure.step("Check created course button is enabled")
    def check_enabled_create_course_button(self):
        self.create_course_button.check_enabled()

    @allure.step("Check save course button is enabled: {is_enabled}")
    def check_create_course_button_state(self, is_enabled: bool):
        if is_enabled:
            self.create_course_button.check_enabled()
        else:
            self.create_course_button.check_disabled()
