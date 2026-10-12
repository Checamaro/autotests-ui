import allure
from playwright.sync_api import Page

from components.base_component import BaseComponent
from elements.input import Input
from elements.textarea import Textarea


class CreateCourseFormComponent(BaseComponent):
    def __init__(self, page: Page):
        super().__init__(page)

        self.title_input = Input(page, 'create-course-form-title-input', 'Title')
        self.estimated_time_input = Input(
            page, 'create-course-form-estimated-time-input', 'Estimated time'
        )
        self.description_textarea = Textarea(page, 'create-course-form-description-input', 'Description')
        self.max_score_input = Input(page, 'create-course-form-max-score-input', 'Max score')
        self.min_score_input = Input(page, 'create-course-form-min-score-input', 'Min score')

    @allure.step("Check visible course form")
    def check_visible(self, title: str, estimated_time: str, description: str, max_score: str, min_score: str):
        self.title_input.check_visible()
        self.title_input.check_have_value(title)

        self.estimated_time_input.check_visible()
        self.estimated_time_input.check_have_value(estimated_time)

        self.description_textarea.check_visible()
        self.description_textarea.check_have_value(description)

        self.max_score_input.check_visible()
        self.max_score_input.check_have_value(max_score)

        self.min_score_input.check_visible()
        self.min_score_input.check_have_value(min_score)

    @allure.step('Fill create course form')
    def fill(
            self,
            title: str | None = None,
            estimated_time: str | None = None,
            description: str | None = None,
            max_score: str | None = None,
            min_score: str | None = None
    ):
        # Заполняются только переданные поля (None — поле не трогаем)
        if title is not None:
            self.title_input.fill(title)
            self.title_input.check_have_value(title)

        if estimated_time is not None:
            self.estimated_time_input.fill(estimated_time)
            self.estimated_time_input.check_have_value(estimated_time)

        if description is not None:
            self.description_textarea.fill(description)
            self.description_textarea.check_have_value(description)

        if max_score is not None:
            self.max_score_input.fill(max_score)
            self.max_score_input.check_have_value(max_score)

        if min_score is not None:
            self.min_score_input.fill(min_score)
            self.min_score_input.check_have_value(min_score)

    @allure.step('Clear numeric field "{field}" (field returns to value 0)')
    def clear_score(self, field: str):
        # field: "min_score" или "max_score". Числовое поле при пустой строке получает значение 0,
        # поэтому значение сразу после fill("") здесь не проверяем
        scores = {"min_score": self.min_score_input, "max_score": self.max_score_input}
        scores[field].fill("")
