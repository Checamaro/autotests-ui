import re
from pathlib import Path

import allure
from playwright.sync_api import Page

from components.courses.create_course_exercise_form_component import CreateCourseExerciseFormComponent
from components.courses.create_course_exercises_toolbar_view_component import CreateCourseExercisesToolbarViewComponent
from components.courses.create_course_form_component import CreateCourseFormComponent
from components.courses.create_course_toolbar_view_component import CreateCourseToolbarViewComponent
from components.navigation.navbar_component import NavbarComponent
from components.navigation.sidebar_component import SidebarComponent
from components.views.empty_view_component import EmptyViewComponent
from components.views.image_upload_widget_component import ImageUploadWidgetComponent
from pages.base_page import BasePage
from tools.courses import CourseData


class CreateCoursePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.navbar = NavbarComponent(page)
        self.sidebar = SidebarComponent(page)
        self.create_course_form = CreateCourseFormComponent(page)
        self.image_upload_widget = ImageUploadWidgetComponent(page, 'create-course-preview')
        self.exercises_empty_view = EmptyViewComponent(page, 'create-course-exercises')
        self.create_course_toolbar_view = CreateCourseToolbarViewComponent(page)
        self.create_course_exercise_form = CreateCourseExerciseFormComponent(page)
        self.create_course_exercises_toolbar_view = CreateCourseExercisesToolbarViewComponent(page)

    def check_visible_exercises_empty_view(self):
        self.exercises_empty_view.check_visible(
            title='There is no exercises',
            description='Click on "Create exercise" button to create new exercise'
        )

    @allure.step("Check exercises empty view is not visible")
    def check_hidden_exercises_empty_view(self):
        self.exercises_empty_view.check_not_visible()

    @allure.step("Check course form is in initial state of create course")
    def check_visible_initial_state(self):
        self.create_course_toolbar_view.check_visible(title="Create course")
        self.image_upload_widget.check_visible(is_image_uploaded=False)
        self.create_course_form.check_visible(
            title="", estimated_time="", description="", max_score="0", min_score="0"
        )
        self.create_course_exercises_toolbar_view.check_visible()
        self.check_visible_exercises_empty_view()
        self.create_course_toolbar_view.check_disabled_create_course_button()

    @allure.step("Check course form is filled with course data")
    def check_visible_course_form(self, course: CourseData, title: str = "Update course"):
        self.create_course_toolbar_view.check_visible(title=title)
        self.create_course_form.check_visible(
            title=course.title,
            estimated_time=course.estimated_time,
            description=course.description,
            max_score=course.max_score,
            min_score=course.min_score
        )

    @allure.step("Fill course form with course data and upload preview")
    def fill_course_form(self, course: CourseData, image: Path | None = None):
        if image is not None:
            self.image_upload_widget.upload_preview_image(str(image))
            self.image_upload_widget.check_visible(is_image_uploaded=True)

        self.create_course_form.fill(
            title=course.title,
            estimated_time=course.estimated_time,
            description=course.description,
            max_score=course.max_score,
            min_score=course.min_score
        )

    @allure.step('Create course "{course.title}"')
    def create_course(self, course: CourseData, image: Path):
        # Заполняет форму на открытой странице создания и сохраняет курс (редирект на список)
        self.fill_course_form(course, image)
        self.create_course_toolbar_view.click_create_course_button_and_check_redirect()

    @allure.step('Add {count} exercises')
    def add_exercises(self, count: int):
        for _ in range(count):
            self.create_course_exercises_toolbar_view.click_create_exercise_button()

    @allure.step('Check exercises count is {count}')
    def check_exercises_count(self, count: int):
        # Упражнения с индексами 0..count-1 видны, следующего за ними нет
        for index in range(count):
            self.create_course_exercise_form.subtitle.check_visible(index=index)
        self.create_course_exercise_form.check_not_visible(index=count)

    @allure.step("Check current url is create course page")
    def check_current_url_create_course(self):
        self.check_current_url(re.compile(r".*/#/courses/create$"))

    @allure.step("Check current url is edit course page")
    def check_current_url_edit_course(self):
        self.check_current_url(re.compile(r".*/#/courses/(?!create$)[^/]+$"))
