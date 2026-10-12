import allure
import pytest
from allure_commons.types import Severity
from qase.pytest import qase

from config import settings
from pages.courses.courses_list_page import CoursesListPage
from pages.courses.create_course_page import CreateCoursePage
from tools.allure.epics import AllureEpic
from tools.allure.features import AllureFeature
from tools.allure.stories import AllureStory
from tools.allure.tags import AllureTag
from tools.courses import BASE_COURSE
from tools.routes import AppRoute

# Упражнения для кейсов UI-20, UI-22: (title, description)
EXERCISES = [("Ex 1", "Desc 1"), ("Ex 2", "Desc 2"), ("Ex 3", "Desc 3")]


@pytest.mark.courses
@pytest.mark.regression
@allure.tag(AllureTag.REGRESSION, AllureTag.COURSES)
@allure.epic(AllureEpic.LMS)
@allure.feature(AllureFeature.COURSES)
@allure.story(AllureStory.COURSES)
@allure.parent_suite(AllureEpic.LMS)
@allure.suite(AllureFeature.COURSES)
@allure.sub_suite(AllureStory.COURSES)
class TestCourses:
    @allure.title('Check displaying of empty courses list')
    @allure.severity(Severity.NORMAL)
    def test_empty_courses_list(self, courses_list_page: CoursesListPage):
        courses_list_page.visit(AppRoute.COURSES)

        courses_list_page.navbar.check_visible(settings.test_user.username)
        courses_list_page.sidebar.check_visible()
        courses_list_page.toolbar_view.check_visible()
        courses_list_page.check_visible_empty_view()

    # ---------------------------------------------------------------- Создание курса

    @qase.id(1)
    @allure.title('Create course form is opened in initial state')
    @allure.severity(Severity.CRITICAL)
    def test_create_course_form_initial_state(
            self, courses_list_page: CoursesListPage, create_course_page: CreateCoursePage
    ):
        courses_list_page.visit(AppRoute.COURSES)
        courses_list_page.toolbar_view.click_create_course_button()

        create_course_page.check_visible_initial_state()

    @qase.id(2)
    @allure.title('Create course')
    @allure.severity(Severity.BLOCKER)
    def test_create_course(self, courses_list_page: CoursesListPage, create_course_page: CreateCoursePage):
        create_course_page.visit(AppRoute.CREATE_COURSES)

        create_course_page.create_course_toolbar_view.check_visible()
        create_course_page.image_upload_widget.check_visible(is_image_uploaded=False)
        create_course_page.create_course_form.check_visible(
            title="", max_score="0", min_score="0", description="", estimated_time=""
        )

        create_course_page.create_course_exercises_toolbar_view.check_visible()
        create_course_page.check_visible_exercises_empty_view()

        create_course_page.image_upload_widget.upload_preview_image(settings.test_data.image_png_file)
        create_course_page.image_upload_widget.check_visible(is_image_uploaded=True)
        create_course_page.create_course_form.fill(
            title="Playwright",
            max_score="100",
            min_score="10",
            description="Playwright",
            estimated_time="2 weeks"
        )
        create_course_page.create_course_toolbar_view.click_create_course_button()

        courses_list_page.toolbar_view.check_visible()
        courses_list_page.course_view.check_visible(
            index=0, title="Playwright", max_score="100", min_score="10", estimated_time="2 weeks"
        )

    @qase.id(3)
    @pytest.mark.parametrize(
        "not_filled_field",
        ["title", "description", "estimated_time", "min_score", "max_score"],
        ids=["no-title", "no-description", "no-estimated-time", "min-score-zero", "max-score-zero"]
    )
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Save course button is disabled when one of the fields is not filled')
    @allure.severity(Severity.NORMAL)
    def test_save_button_disabled_with_not_filled_field(self, create_course_page: CreateCoursePage, not_filled_field: str):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.image_upload_widget.upload_preview_image(settings.test_data.image_png_file)
        create_course_page.image_upload_widget.check_visible(is_image_uploaded=True)
        create_course_page.create_course_form.fill(**BASE_COURSE.model_dump(exclude={not_filled_field}))

        create_course_page.create_course_toolbar_view.check_disabled_create_course_button()

    @qase.id(3)
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Save course button is disabled when preview is not uploaded')
    @allure.severity(Severity.NORMAL)
    def test_save_button_disabled_without_preview(self, create_course_page: CreateCoursePage):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.create_course_form.fill(**BASE_COURSE.model_dump())

        create_course_page.image_upload_widget.check_visible(is_image_uploaded=False)
        create_course_page.create_course_toolbar_view.check_disabled_create_course_button()

    @qase.id(4)
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Save course button is enabled when form is completely filled')
    @allure.severity(Severity.NORMAL)
    def test_save_button_enabled_with_filled_form(self, create_course_page: CreateCoursePage):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.fill_course_form(BASE_COURSE, settings.test_data.image_png_file)

        create_course_page.create_course_toolbar_view.check_enabled_create_course_button()

    @qase.id(5)
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Remove image removes preview and disables save course button')
    @allure.severity(Severity.NORMAL)
    def test_remove_image_disables_save_button(self, create_course_page: CreateCoursePage):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.fill_course_form(BASE_COURSE, settings.test_data.image_png_file)
        create_course_page.create_course_toolbar_view.check_enabled_create_course_button()

        create_course_page.image_upload_widget.click_remove_image_button()

        create_course_page.image_upload_widget.check_visible(is_image_uploaded=False)
        create_course_page.create_course_toolbar_view.check_disabled_create_course_button()

    @qase.id(6)
    @pytest.mark.parametrize(
        "min_score, max_score, is_enabled",
        [("0", "2", False), ("1", "2", True), ("1", "0", False)],
        ids=["min0-max2-disabled", "min1-max2-enabled", "min1-max0-disabled"]
    )
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Save course button state on min and max score boundaries near zero')
    @allure.severity(Severity.NORMAL)
    def test_save_button_state_on_scores_boundary(
            self, create_course_page: CreateCoursePage, min_score: str, max_score: str, is_enabled: bool
    ):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.fill_course_form(BASE_COURSE, settings.test_data.image_png_file)

        create_course_page.create_course_form.fill(min_score=min_score, max_score=max_score)

        create_course_page.create_course_toolbar_view.check_create_course_button_state(is_enabled)

    @qase.id(7)
    @pytest.mark.parametrize(
        "cleared_field, min_score, max_score",
        [("min_score", "0", "100"), ("max_score", "10", "0")],
        ids=["clear-min-score", "clear-max-score"]
    )
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Clearing numeric field returns value 0 and disables save course button')
    @allure.severity(Severity.MINOR)
    def test_clear_score_field_returns_zero(
            self, create_course_page: CreateCoursePage, cleared_field: str, min_score: str, max_score: str
    ):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.fill_course_form(BASE_COURSE, settings.test_data.image_png_file)

        create_course_page.create_course_form.clear_score(cleared_field)

        create_course_page.create_course_form.check_visible(
            title=BASE_COURSE.title,
            estimated_time=BASE_COURSE.estimated_time,
            description=BASE_COURSE.description,
            max_score=max_score,
            min_score=min_score
        )
        create_course_page.create_course_toolbar_view.check_disabled_create_course_button()

    @qase.id(8)
    @pytest.mark.xfail(reason="#2", strict=True)
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Course with min score greater than max score is not saved on create')
    @allure.severity(Severity.CRITICAL)
    def test_create_course_with_min_score_greater_than_max_score(self, create_course_page: CreateCoursePage):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.fill_course_form(
            BASE_COURSE.model_copy(update={"min_score": "100", "max_score": "10"}),
            settings.test_data.image_png_file
        )

        # Баг #2: кнопка остаётся активной, и курс с min > max сохраняется
        create_course_page.create_course_toolbar_view.check_disabled_create_course_button()

    @qase.id(12)
    @allure.tag(AllureTag.SECURITY)
    @allure.title('HTML markup in course title is displayed as plain text')
    @allure.severity(Severity.MINOR)
    def test_html_markup_in_course_title_displayed_as_text(
            self, courses_list_page: CoursesListPage, create_course_page: CreateCoursePage
    ):
        html_title = "<b>bold</b><img src=x onerror=alert(1)>"

        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.create_course(
            BASE_COURSE.model_copy(update={"title": html_title}), settings.test_data.image_png_file
        )

        courses_list_page.course_view.check_visible(
            index=0,
            title=html_title,
            max_score=BASE_COURSE.max_score,
            min_score=BASE_COURSE.min_score,
            estimated_time=BASE_COURSE.estimated_time
        )

    @qase.id(13)
    @allure.tag(AllureTag.NAVIGATION)
    @allure.title('Leaving create course page without saving does not create course')
    @allure.severity(Severity.NORMAL)
    def test_leave_create_course_page_without_saving(
            self, courses_list_page: CoursesListPage, create_course_page: CreateCoursePage
    ):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.fill_course_form(BASE_COURSE, settings.test_data.image_png_file)

        create_course_page.sidebar.click_courses()

        courses_list_page.check_current_url_courses_list()
        courses_list_page.check_visible_empty_view()

    @qase.id(14)
    @allure.tag(AllureTag.NAVIGATION)
    @allure.title('Browser back from create course page returns to courses list')
    @allure.severity(Severity.MINOR)
    def test_browser_back_from_create_course_page(
            self, courses_list_page: CoursesListPage, create_course_page: CreateCoursePage
    ):
        courses_list_page.visit(AppRoute.COURSES)
        courses_list_page.toolbar_view.click_create_course_button()
        create_course_page.check_current_url_create_course()

        create_course_page.go_back()

        courses_list_page.check_current_url_courses_list()
        courses_list_page.toolbar_view.check_visible()
        courses_list_page.check_visible_empty_view()
        courses_list_page.navbar.check_visible(settings.test_user.username)

    @qase.id(15)
    @allure.tag(AllureTag.SESSION)
    @allure.title('Create course draft is kept after page reload')
    @allure.severity(Severity.NORMAL)
    def test_create_course_draft_kept_after_reload(self, create_course_page: CreateCoursePage):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.create_course_form.fill(title="Playwright draft", description="Draft")

        create_course_page.reload()

        create_course_page.check_current_url_create_course()
        create_course_page.create_course_toolbar_view.check_visible(title="Create course")
        create_course_page.create_course_form.check_visible(
            title="Playwright draft", estimated_time="", description="Draft", max_score="0", min_score="0"
        )

    @qase.id(15)
    @allure.tag(AllureTag.SESSION)
    @allure.title('Edit course draft is kept after page reload')
    @allure.severity(Severity.NORMAL)
    def test_edit_course_draft_kept_after_reload(
            self, courses_list_page_with_course: CoursesListPage, create_course_page_with_course: CreateCoursePage
    ):
        courses_list_page_with_course.visit(AppRoute.COURSES)
        courses_list_page_with_course.click_edit_course(index=0)
        create_course_page_with_course.create_course_form.fill(title="Playwright draft", description="Draft")

        create_course_page_with_course.reload()

        create_course_page_with_course.check_current_url_edit_course()
        create_course_page_with_course.create_course_toolbar_view.check_visible(title="Update course")
        create_course_page_with_course.create_course_form.check_visible(
            title="Playwright draft",
            estimated_time=BASE_COURSE.estimated_time,
            description="Draft",
            max_score=BASE_COURSE.max_score,
            min_score=BASE_COURSE.min_score
        )

    @qase.id(16)
    @allure.tag(AllureTag.SESSION)
    @allure.title('Created course is kept after courses list reload')
    @allure.severity(Severity.CRITICAL)
    def test_created_course_kept_after_reload(
            self, courses_list_page: CoursesListPage, create_course_page: CreateCoursePage
    ):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.create_course(BASE_COURSE, settings.test_data.image_png_file)
        courses_list_page.course_view.check_visible(
            index=0,
            title=BASE_COURSE.title,
            max_score=BASE_COURSE.max_score,
            min_score=BASE_COURSE.min_score,
            estimated_time=BASE_COURSE.estimated_time
        )

        courses_list_page.reload()

        courses_list_page.check_current_url_courses_list()
        courses_list_page.navbar.check_visible(settings.test_user.username)
        courses_list_page.course_view.check_visible(
            index=0,
            title=BASE_COURSE.title,
            max_score=BASE_COURSE.max_score,
            min_score=BASE_COURSE.min_score,
            estimated_time=BASE_COURSE.estimated_time
        )
        courses_list_page.check_courses_count(1)

    @qase.id(17)
    @allure.tag(AllureTag.NAVIGATION)
    @allure.title('Create course button opens empty form after edit draft was left')
    @allure.severity(Severity.NORMAL)
    def test_create_course_button_opens_empty_form_after_edit_draft(
            self, courses_list_page_with_course: CoursesListPage, create_course_page_with_course: CreateCoursePage
    ):
        courses_list_page_with_course.visit(AppRoute.COURSES)
        courses_list_page_with_course.click_edit_course(index=0)
        create_course_page_with_course.create_course_form.fill(title="Playwright draft")
        create_course_page_with_course.sidebar.click_courses()
        courses_list_page_with_course.check_current_url_courses_list()

        courses_list_page_with_course.toolbar_view.click_create_course_button()

        create_course_page_with_course.check_visible_initial_state()

    # ---------------------------------------------------------------- Упражнения курса

    @qase.id(19)
    @allure.title('Create exercise adds exercise block with default values')
    @allure.severity(Severity.NORMAL)
    def test_create_exercise(self, create_course_page: CreateCoursePage):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.check_visible_exercises_empty_view()

        create_course_page.create_course_exercises_toolbar_view.click_create_exercise_button()

        create_course_page.check_hidden_exercises_empty_view()
        create_course_page.create_course_exercise_form.check_visible(
            index=0, title="Exercise title", description="Exercise description"
        )
        create_course_page.check_exercises_count(1)

    @qase.id(20)
    @pytest.mark.parametrize("deleted_index", [0, 1, 2], ids=["first", "middle", "last"])
    @allure.title('Delete exercise recalculates numbering of remaining exercises')
    @allure.severity(Severity.NORMAL)
    def test_delete_exercise_recalculates_numbering(self, create_course_page: CreateCoursePage, deleted_index: int):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.add_exercises(count=len(EXERCISES))
        for index, (title, description) in enumerate(EXERCISES):
            create_course_page.create_course_exercise_form.fill_create_exercise_form(
                index=index, title=title, description=description
            )

        create_course_page.create_course_exercise_form.click_delete_exercise_button(index=deleted_index)

        remaining_exercises = [exercise for index, exercise in enumerate(EXERCISES) if index != deleted_index]
        create_course_page.check_exercises_count(len(remaining_exercises))
        for index, (title, description) in enumerate(remaining_exercises):
            create_course_page.create_course_exercise_form.check_visible(
                index=index, title=title, description=description
            )

    @qase.id(21)
    @allure.title('Delete the only exercise returns exercises empty view')
    @allure.severity(Severity.MINOR)
    def test_delete_single_exercise(self, create_course_page: CreateCoursePage):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.add_exercises(count=1)
        create_course_page.check_exercises_count(1)

        create_course_page.create_course_exercise_form.click_delete_exercise_button(index=0)

        create_course_page.check_visible_exercises_empty_view()
        create_course_page.check_exercises_count(0)

    @qase.id(22)
    @allure.title('Course exercises are saved and displayed on edit')
    @allure.severity(Severity.CRITICAL)
    def test_course_exercises_saved_and_displayed_on_edit(
            self, courses_list_page: CoursesListPage, create_course_page: CreateCoursePage
    ):
        exercises = EXERCISES[:2]

        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.fill_course_form(BASE_COURSE, settings.test_data.image_png_file)
        create_course_page.add_exercises(count=len(exercises))
        for index, (title, description) in enumerate(exercises):
            create_course_page.create_course_exercise_form.fill_create_exercise_form(
                index=index, title=title, description=description
            )
        create_course_page.create_course_toolbar_view.click_create_course_button_and_check_redirect()

        courses_list_page.click_edit_course(index=0)

        create_course_page.check_exercises_count(len(exercises))
        for index, (title, description) in enumerate(exercises):
            create_course_page.create_course_exercise_form.check_visible(
                index=index, title=title, description=description
            )

    # ---------------------------------------------------------------- Редактирование курса

    @qase.id(23)
    @allure.title('Edit course form is prefilled and has Update course title')
    @allure.severity(Severity.CRITICAL)
    def test_edit_course_form_prefilled(
            self, courses_list_page_with_course: CoursesListPage, create_course_page_with_course: CreateCoursePage
    ):
        courses_list_page_with_course.visit(AppRoute.COURSES)

        courses_list_page_with_course.click_edit_course(index=0)

        create_course_page_with_course.check_current_url_edit_course()
        create_course_page_with_course.check_visible_course_form(BASE_COURSE, title="Update course")
        create_course_page_with_course.image_upload_widget.check_visible(is_image_uploaded=True)
        create_course_page_with_course.create_course_toolbar_view.check_enabled_create_course_button()

    @qase.id(24)
    @allure.title('Edit course')
    @allure.severity(Severity.BLOCKER)
    def test_edit_course(self, courses_list_page: CoursesListPage, create_course_page: CreateCoursePage):
        create_course_page.visit(AppRoute.CREATE_COURSES)
        create_course_page.image_upload_widget.upload_preview_image(settings.test_data.image_png_file)
        create_course_page.image_upload_widget.check_visible(is_image_uploaded=True)
        create_course_page.create_course_form.fill(
            title="Playwright",
            estimated_time="2 weeks",
            description="Playwright",
            max_score="100",
            min_score="10"
        )
        create_course_page.create_course_toolbar_view.click_create_course_button()

        courses_list_page.toolbar_view.check_visible()
        courses_list_page.course_view.check_visible(
            index=0, title="Playwright", max_score="100", min_score="10", estimated_time="2 weeks"
        )
        courses_list_page.course_view.menu.click_edit(index=0)

        create_course_page.create_course_form.fill(
            title="New Playwright",
            estimated_time="3 weeks",
            description="New Playwright",
            max_score="1000",
            min_score="100"
        )
        create_course_page.create_course_toolbar_view.click_create_course_button()

        courses_list_page.toolbar_view.check_visible()
        courses_list_page.course_view.check_visible(
            index=0, title="New Playwright", max_score="1000", min_score="100", estimated_time="3 weeks"
        )
        # Дубликат курса не создаётся: в списке ровно один курс
        courses_list_page.check_courses_count(1)

    @qase.id(25)
    @allure.title('Editing one course does not affect other courses')
    @allure.severity(Severity.NORMAL)
    def test_edit_one_course_does_not_affect_other_courses(
            self, courses_list_page_with_course: CoursesListPage, create_course_page_with_course: CreateCoursePage
    ):
        course_b = BASE_COURSE.model_copy(update={"title": "Course B"})

        courses_list_page_with_course.visit(AppRoute.COURSES)
        courses_list_page_with_course.toolbar_view.click_create_course_button()
        create_course_page_with_course.create_course(course_b, settings.test_data.image_png_file)
        courses_list_page_with_course.check_courses_count(2)

        courses_list_page_with_course.click_edit_course(index=1)
        create_course_page_with_course.create_course_form.fill(title="Course B edited")
        create_course_page_with_course.create_course_toolbar_view.click_create_course_button_and_check_redirect()

        courses_list_page_with_course.check_courses_count(2)
        courses_list_page_with_course.course_view.check_visible(
            index=0,
            title=BASE_COURSE.title,
            max_score=BASE_COURSE.max_score,
            min_score=BASE_COURSE.min_score,
            estimated_time=BASE_COURSE.estimated_time
        )
        courses_list_page_with_course.course_view.check_visible(
            index=1,
            title="Course B edited",
            max_score=course_b.max_score,
            min_score=course_b.min_score,
            estimated_time=course_b.estimated_time
        )

    @qase.id(26)
    @pytest.mark.parametrize(
        "changed_fields",
        [{"title": ""}, {"description": ""}, {"estimated_time": ""}, {"min_score": "0"}, {"max_score": "0"}],
        ids=["clear-title", "clear-description", "clear-estimated-time", "min-score-zero", "max-score-zero"]
    )
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Save course button is disabled on edit when one of the conditions is violated')
    @allure.severity(Severity.NORMAL)
    def test_edit_course_save_button_disabled(
            self,
            courses_list_page_with_course: CoursesListPage,
            create_course_page_with_course: CreateCoursePage,
            changed_fields: dict
    ):
        courses_list_page_with_course.visit(AppRoute.COURSES)
        courses_list_page_with_course.click_edit_course(index=0)

        create_course_page_with_course.create_course_form.fill(**changed_fields)

        create_course_page_with_course.create_course_toolbar_view.check_disabled_create_course_button()

        create_course_page_with_course.sidebar.click_courses()
        courses_list_page_with_course.course_view.check_visible(
            index=0,
            title=BASE_COURSE.title,
            max_score=BASE_COURSE.max_score,
            min_score=BASE_COURSE.min_score,
            estimated_time=BASE_COURSE.estimated_time
        )

    @qase.id(26)
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Save course button is disabled on edit after preview removal')
    @allure.severity(Severity.NORMAL)
    def test_edit_course_save_button_disabled_after_remove_preview(
            self, courses_list_page_with_course: CoursesListPage, create_course_page_with_course: CreateCoursePage
    ):
        courses_list_page_with_course.visit(AppRoute.COURSES)
        courses_list_page_with_course.click_edit_course(index=0)
        create_course_page_with_course.image_upload_widget.check_visible(is_image_uploaded=True)

        create_course_page_with_course.image_upload_widget.click_remove_image_button()

        create_course_page_with_course.image_upload_widget.check_visible(is_image_uploaded=False)
        create_course_page_with_course.create_course_toolbar_view.check_disabled_create_course_button()

        create_course_page_with_course.sidebar.click_courses()
        courses_list_page_with_course.course_view.check_visible(
            index=0,
            title=BASE_COURSE.title,
            max_score=BASE_COURSE.max_score,
            min_score=BASE_COURSE.min_score,
            estimated_time=BASE_COURSE.estimated_time
        )

    @qase.id(27)
    @pytest.mark.xfail(reason="#2", strict=True)
    @allure.tag(AllureTag.VALIDATION)
    @allure.title('Course with min score greater than max score is not saved on edit')
    @allure.severity(Severity.CRITICAL)
    def test_edit_course_with_min_score_greater_than_max_score(
            self, courses_list_page_with_course: CoursesListPage, create_course_page_with_course: CreateCoursePage
    ):
        courses_list_page_with_course.visit(AppRoute.COURSES)
        courses_list_page_with_course.click_edit_course(index=0)

        create_course_page_with_course.create_course_form.fill(min_score="100", max_score="10")

        # Баг #2: кнопка остаётся активной, и курс с min > max сохраняется
        create_course_page_with_course.create_course_toolbar_view.check_disabled_create_course_button()

    @qase.id(28)
    @allure.tag(AllureTag.NAVIGATION)
    @allure.title('Leaving edit course page without saving does not change course')
    @allure.severity(Severity.NORMAL)
    def test_leave_edit_course_page_without_saving(
            self, courses_list_page_with_course: CoursesListPage, create_course_page_with_course: CreateCoursePage
    ):
        courses_list_page_with_course.visit(AppRoute.COURSES)
        courses_list_page_with_course.click_edit_course(index=0)
        create_course_page_with_course.create_course_form.fill(title="Not saved")

        create_course_page_with_course.sidebar.click_courses()

        courses_list_page_with_course.check_current_url_courses_list()
        courses_list_page_with_course.course_view.check_visible(
            index=0,
            title=BASE_COURSE.title,
            max_score=BASE_COURSE.max_score,
            min_score=BASE_COURSE.min_score,
            estimated_time=BASE_COURSE.estimated_time
        )
        courses_list_page_with_course.check_courses_count(1)
