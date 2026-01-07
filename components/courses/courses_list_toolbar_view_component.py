from playwright.sync_api import Page
from components.base_component import BaseComponent
from elements.text import Text
from elements.button import Button

class CoursesListToolbarViewComponent(BaseComponent):
    def __init__(self, page: Page):
        super().__init__(page)
        self.courses_title = Text(page, 'courses-list-toolbar-title-text', 'Courses title')
        self.create_course_button = Button(page, 'courses-list-toolbar-create-course-button', 'Create course button')

    def check_visible(self):
        self.courses_title.check_visible()
        self.courses_title.check_have_text('Courses')
        self.create_course_button.check_visible()

    def click_create_course_button(self):
        self.create_course_button.click()
