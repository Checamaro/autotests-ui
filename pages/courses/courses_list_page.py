import re

import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage
from components.navigation.navbar_component import NavbarComponent
from components.navigation.sidebar_component import SidebarComponent
from components.courses.courses_list_toolbar_view_component import CoursesListToolbarViewComponent
from components.courses.course_view_component import CourseViewComponent


class CoursesListPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        self.navbar = NavbarComponent(page)
        self.sidebar = SidebarComponent(page)
        self.toolbar_view = CoursesListToolbarViewComponent(page)
        self.course_view = CourseViewComponent(page)  # Добавить эту строку

        self.empty_view_icon = page.get_by_test_id('courses-list-empty-view-icon')
        self.empty_view_title = page.get_by_test_id('courses-list-empty-view-title-text')
        self.empty_view_description = page.get_by_test_id('courses-list-empty-view-description-text')

    def check_visible_empty_view(self):
        expect(self.empty_view_icon).to_be_visible()
        expect(self.empty_view_title).to_be_visible()
        expect(self.empty_view_title).to_have_text('There is no results')
        expect(self.empty_view_description).to_be_visible()
        expect(self.empty_view_description).to_have_text(
            'Results from the load test pipeline will be displayed here'
        )

    def click_edit_course(self, index: int):
        self.course_view.menu.click_edit(index=index)

    def click_delete_course(self, index: int):
        self.course_view.menu.click_delete(index=index)

    @allure.step('Check courses list contains exactly {count} courses')
    def check_courses_count(self, count: int):
        # Курс с индексом count отсутствует (курсов не больше count);
        # наличие курсов с индексами 0..count-1 проверяется отдельно через check_visible
        if count == 0:
            self.check_visible_empty_view()
        else:
            self.course_view.title.check_visible(nth=count - 1)
        self.course_view.check_not_visible(index=count)

    @allure.step("Check current url is courses list")
    def check_current_url_courses_list(self):
        self.check_current_url(re.compile(r".*/#/courses$"))
