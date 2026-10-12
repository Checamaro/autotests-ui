from pydantic import BaseModel


class CourseData(BaseModel):
    """Данные курса для формы создания/редактирования (значения полей — строки, как в UI)."""
    title: str
    estimated_time: str
    description: str
    max_score: str
    min_score: str


# Базовый курс «D-base» из docs/test-cases/courses.md
BASE_COURSE = CourseData(
    title="Playwright",
    estimated_time="2 weeks",
    description="Playwright",
    max_score="100",
    min_score="10"
)
