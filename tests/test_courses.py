import pytest
from pages.courses_list_page import CoursesListPage
from pages.create_course_page import CreateCoursePage


@pytest.mark.courses
@pytest.mark.regression
def test_empty_courses_list(courses_list_page: CoursesListPage):
    courses_list_page.visit("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/courses")

    courses_list_page.navbar.check_visible("username")
    courses_list_page.sidebar.check_visible()
    courses_list_page.check_visible_courses_title()
    courses_list_page.check_visible_create_course_button()
    courses_list_page.check_visible_empty_view()


@pytest.mark.courses
@pytest.mark.regression
def test_create_course(
        create_course_page: CreateCoursePage,
        courses_list_page: CoursesListPage
):
    create_course_page.visit("https://nikita-filonov.github.io/qa-automation-engineer-ui-course/#/courses/create")
    create_course_page.navbar.check_visible("username")
    create_course_page.create_course_toolbar_view.check_visible(is_create_course_disabled=True)
    create_course_page.create_course_form.check_visible(
        title="",
        estimated_time="",
        description="",
        max_score="0",
        min_score="0"
    )
    create_course_page.create_course_exercises_toolbar_view.check_visible()
    create_course_page.check_visible_exercises_empty_view()

    create_course_page.upload_preview_image("./testdata/files/image.png")
    create_course_page.image_upload_widget.check_visible(is_image_uploaded=True)

    create_course_page.create_course_form.fill(
        title="Playwright",
        estimated_time="2 weeks",
        description="Playwright",
        max_score="100",
        min_score="10"
    )

    create_course_page.create_course_toolbar_view.check_visible(is_create_course_disabled=False)

    create_course_page.create_course_toolbar_view.click_create_course_button()

    courses_list_page.check_visible_courses_title()
    courses_list_page.check_visible_create_course_button()
