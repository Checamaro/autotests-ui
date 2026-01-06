from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from components.navigation.navbar_component import NavbarComponent
from components.courses.create_course_form_component import CreateCourseFormComponent
from components.courses.create_course_toolbar_view_component import CreateCourseToolbarViewComponent
from components.courses.create_course_exercises_toolbar_view_component import CreateCourseExercisesToolbarViewComponent
from components.views.image_upload_widget_component import ImageUploadWidgetComponent
from components.views.empty_view_component import EmptyViewComponent


class CreateCoursePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Компоненты
        self.navbar = NavbarComponent(page)
        self.create_course_form = CreateCourseFormComponent(page)
        self.create_course_toolbar_view = CreateCourseToolbarViewComponent(page)
        self.create_course_exercises_toolbar_view = CreateCourseExercisesToolbarViewComponent(page)
        self.image_upload_widget = ImageUploadWidgetComponent(page, 'create-course-preview')
        self.exercises_empty_view = EmptyViewComponent(page, 'create-course-exercises')

        self.create_course_title = page.get_by_test_id('create-course-toolbar-title-text')

    def check_visible_create_course_title(self):
        expect(self.create_course_title).to_be_visible()
        expect(self.create_course_title).to_have_text('Create course')

    def check_visible_exercises_empty_view(self):
        self.exercises_empty_view.check_visible(
            title='There is no exercises',
            description='Click on "Create exercise" button to create new exercise'
        )

    def upload_preview_image(self, image_path: str):
        self.image_upload_widget.upload_preview_image(image_path)
