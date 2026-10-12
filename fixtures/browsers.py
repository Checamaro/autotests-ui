from config import settings
import pytest
from _pytest.fixtures import SubRequest
from playwright.sync_api import Playwright, Page
from pages.authentication.registration_page import RegistrationPage
from pages.dashboard.dashboard_page import DashboardPage
from tools.routes import AppRoute
from tools.playwright.pages import initialize_playwright_page


@pytest.fixture(params=settings.browsers)
def chromium_page(request: SubRequest, playwright: Playwright) -> Page:
    yield from initialize_playwright_page(playwright, test_name=request.node.name, browser_type=request.param )


@pytest.fixture(scope="session")
def initialize_browser_state(playwright: Playwright):
    browser = playwright.chromium.launch(headless=settings.headless)
    context = browser.new_context(base_url=settings.get_base_url())
    page = context.new_page()

    registration_page = RegistrationPage(page=page)
    registration_page.visit(AppRoute.REGISTRATION)
    registration_page.registration_form.fill(
        email=settings.test_user.email,
        username=settings.test_user.username,
        password=settings.test_user.password
    )
    registration_page.click_registration_button()

    context.storage_state(path=settings.browser_state_file)
    browser.close()


@pytest.fixture(params=settings.browsers)
def chromium_page_with_state(initialize_browser_state, request: SubRequest, playwright: Playwright) -> Page:
    yield from initialize_playwright_page(
        playwright,
        test_name=request.node.name,
        browser_type=request.param,
        storage_state=settings.browser_state_file
    )


@pytest.fixture(scope="session")
def initialize_logged_out_browser_state(initialize_browser_state, playwright: Playwright):
    # Состояние «пользователь зарегистрирован, но вышел из системы»:
    # берём состояние после регистрации и выполняем logout через сайдбар.
    # Пользователи хранятся в localStorage приложения, поэтому без этого шага
    # в новом браузере войти существующим пользователем невозможно.
    browser = playwright.chromium.launch(headless=settings.headless)
    context = browser.new_context(base_url=settings.get_base_url(), storage_state=settings.browser_state_file)
    page = context.new_page()

    dashboard_page = DashboardPage(page=page)
    dashboard_page.visit(AppRoute.DASHBOARD)
    dashboard_page.sidebar.click_logout()

    context.storage_state(path=settings.logged_out_browser_state_file)
    browser.close()


@pytest.fixture(params=settings.browsers)
def chromium_page_with_logged_out_state(
        initialize_logged_out_browser_state,
        request: SubRequest,
        playwright: Playwright
) -> Page:
    yield from initialize_playwright_page(
        playwright,
        test_name=request.node.name,
        browser_type=request.param,
        storage_state=settings.logged_out_browser_state_file
    )
