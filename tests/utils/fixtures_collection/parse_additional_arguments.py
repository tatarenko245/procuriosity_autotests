import allure
import pytest


def pytest_addoption(parser):
    parser.addoption("--country", action="store", type=str)
    parser.addoption("--language", action="store", type=str)
    parser.addoption("--environment", action="store", type=str)
    parser.addoption("--pmd", action="store", type=str)
    parser.addoption("--cassandra_username", action="store", type=str)
    parser.addoption("--cassandra_password", action="store", type=str)


@allure.step('Set up: country')
@pytest.fixture(scope="session")
def parse_country(request):
    """Handler for --additional_value parameter"""
    country = request.config.getoption("--country")
    allure.attach(country, "Country")
    return country


@allure.step('Set up: language')
@pytest.fixture(scope="session")
def parse_language(request):
    """Handler for --additional_value parameter"""
    language = request.config.getoption("--language")
    allure.attach(language, "Language")
    return language


@allure.step('Set up: environment')
@pytest.fixture(scope="session")
# @pytest.fixture(autouse=True)
def parse_environment(request):
    """Handler for --additional_value parameter"""
    environment = request.config.getoption("--environment")
    allure.attach(environment, "Environment")
    return environment


@allure.step('Set up: pmd')
@pytest.fixture(scope="session")
def parse_pmd(request):
    """Handler for --additional_value parameter"""
    allure.attach(request.config.getoption("--pmd"), "pmd")
    return request.config.getoption("--pmd")


@allure.step('Set up: Cassandra username')
@pytest.fixture(scope="session")
def parse_cassandra_username(request):
    """Handler for --additional_value parameter"""
    cassandra_username = request.config.getoption("--cassandra_username")
    allure.attach(cassandra_username, "Cassandra username")
    return cassandra_username


@allure.step('Set up: Cassandra password')
@pytest.fixture(scope="session")
def parse_cassandra_password(request):
    """Handler for --additional_value parameter"""
    cassandra_password = request.config.getoption("--cassandra_password")
    allure.attach(cassandra_password, "Cassandra password")
    return cassandra_password