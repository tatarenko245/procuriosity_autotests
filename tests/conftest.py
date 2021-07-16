# Содержит в себе фикстуры. Фикстуры - это функции, которые мы запускаем до или после теста
from uuid import UUID

import pytest


def pytest_addoption(parser):
    parser.addoption("--pmd", action="store", type=str)
    parser.addoption("--country", action="store", type=str)
    parser.addoption("--language", action="store", type=str)
    parser.addoption("--tag", action="store", type=str)
    parser.addoption("--environment", action="store", type=str)
    parser.addoption("--cassandra_username", action="store", type=str)
    parser.addoption("--cassandra_password", action="store", type=str)


@pytest.fixture(scope="session")
def country(request):
    """Handler for --additional_value parameter"""
    return request.config.getoption("--country")


@pytest.fixture(scope="session")
def language(request):
    """Handler for --additional_value parameter"""

    return request.config.getoption("--language")


@pytest.fixture(scope="session")
def environment(request):
    """Handler for --additional_value parameter"""
    return request.config.getoption("--environment")


@pytest.fixture(scope="session")
def cassandra_username(request):
    """Handler for --additional_value parameter"""
    return request.config.getoption("--cassandra_username")


@pytest.fixture(scope="session")
def cassandra_password(request):
    """Handler for --additional_value parameter"""
    return request.config.getoption("--cassandra_password")


@pytest.fixture(scope="session")
def pmd(request):
    """Handler for --additional_value parameter"""

    return request.config.getoption("--pmd")


@pytest.fixture(scope="session")
def tag(request):
    """Handler for --additional_value parameter"""

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
