# Содержит в себе фикстуры. Фикстуры - это функции, которые мы запускаем до или после теста
import allure
import pytest


def pytest_addoption(parser):
    parser.addoption("--pmd", action="store", type=str)
    parser.addoption("--country", action="store", type=str)
    parser.addoption("--language", action="store", type=str)
    parser.addoption("--tag", action="store", type=str)
    parser.addoption("--environment", action="store", type=str)
    parser.addoption("--cassandra_username", action="store", type=str)
    parser.addoption("--cassandra_password", action="store", type=str)


@allure.step('Set up: country')
@pytest.fixture(scope="session")
def country(request):
    """Handler for --additional_value parameter"""
    allure.attach(request.config.getoption("--country"), "Country")
    return request.config.getoption("--country")


@allure.step('Set up: language')
@pytest.fixture(scope="session")
def language(request):
    """Handler for --additional_value parameter"""
    allure.attach(request.config.getoption("--language"), "Language")
    return request.config.getoption("--language")


@allure.step('Set up: environment')
@pytest.fixture(scope="session")
def environment(request):
    """Handler for --additional_value parameter"""
    allure.attach(request.config.getoption("--environment"), "Environment")
    return request.config.getoption("--environment")


@allure.step('Set up: Cassandra username')
@pytest.fixture(scope="session")
def cassandra_username(request):
    """Handler for --additional_value parameter"""
    allure.attach(request.config.getoption("--cassandra_username"), "Cassandra username")
    return request.config.getoption("--cassandra_username")


@allure.step('Set up: Cassandra password')
@pytest.fixture(scope="session")
def cassandra_password(request):
    """Handler for --additional_value parameter"""
    allure.attach(request.config.getoption("--cassandra_password"), "Cassandra password")
    return request.config.getoption("--cassandra_password")


@allure.step('Set up: pmd')
@pytest.fixture(scope="session")
def pmd(request):
    """Handler for --additional_value parameter"""
    allure.attach(request.config.getoption("--pmd"), "pmd")
    return request.config.getoption("--pmd")


@allure.step('Set up: Tag')
@pytest.fixture(scope="session")
def tag(request):
    """Handler for --additional_value parameter"""
    allure.attach(request.config.getoption("--tag"), "tag")
    return request.config.getoption("--tag")


class GlobalClassCreateEi:
    environment = None
    operation_id = None
    hosts = None
    send_the_request_create_ei = None
    message = None
    host_for_service = None
    country = None
    language = None
    payload_for_create_ei = None
    cassandra_cluster = None
    cassandra_username = None
    cassandra_password = None
    access_token = None
    host_for_bpe = None
    check_message = None


class GlobalClassCreateFs:
    environment = None
    operation_id = None
    hosts = None
    send_the_request_create_fs = None
    message = None
    host_for_service = None
    country = None
    language = None
    payload_for_create_fs = None
    cassandra_cluster = None
    cassandra_username = None
    cassandra_password = None
    create_ei_process = None
