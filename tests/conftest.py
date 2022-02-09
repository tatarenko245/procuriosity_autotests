# Содержит в себе фикстуры. Фикстуры - это функции, которые мы запускаем до или после теста
import allure
import pytest

from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment


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
# @pytest.fixture(autouse=True)
def country(request):
    """Handler for --additional_value parameter"""
    country = request.config.getoption("--country")
    allure.attach(country, "Country")
    return country


@allure.step('Set up: language')
@pytest.fixture(scope="session")
# @pytest.fixture(autouse=True)
def language(request):
    """Handler for --additional_value parameter"""
    language = request.config.getoption("--language")
    allure.attach(language, "Language")
    return language


@allure.step('Set up: environment')
@pytest.fixture(scope="session")
# @pytest.fixture(autouse=True)
def environment(request):
    """Handler for --additional_value parameter"""
    environment = request.config.getoption("--environment")
    allure.attach(environment, "Environment")
    return environment


@pytest.fixture(scope="session")
def metadata_budget_url(environment):
    metadata_budget_url = None
    if environment == "dev":
        metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
    elif environment == "sandbox":
        metadata_budget_url = "http://public.eprocurement.systems/budgets"
    return metadata_budget_url

@allure.step('Set up: Cassandra username')
@pytest.fixture(scope="session")
# @pytest.fixture(autouse=True)
def cassandra_username(request):
    """Handler for --additional_value parameter"""
    cassandra_username = request.config.getoption("--cassandra_username")
    allure.attach(cassandra_username, "Cassandra username")
    return cassandra_username


@allure.step('Set up: Cassandra password')
@pytest.fixture(scope="session")
# @pytest.fixture(autouse=True)
def cassandra_password(request):
    """Handler for --additional_value parameter"""
    cassandra_password = request.config.getoption("--cassandra_password")
    allure.attach(cassandra_password, "Cassandra password")
    return cassandra_password


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


@pytest.fixture(scope="class")
def get_hosts(environment):
    hosts = Environment().choose_environment(environment)
    database_host = hosts[0]
    bpe_host = hosts[1]
    service_host = hosts[2]
    return database_host, bpe_host, service_host


@pytest.fixture(scope="class")
def connection_to_database(get_hosts, cassandra_username, cassandra_password):
    connection = CassandraSession(
        cassandra_username=cassandra_username,
        cassandra_password=cassandra_password,
        cassandra_cluster=get_hosts[0])
    return connection


@pytest.fixture(scope="function")
def queue_mapper():
    queue_mapper = {
        0: "first",
        1: "second",
        2: "third",
        3: "fourth",
        4: "fifth",
        5: "sixth",
        6: "seventh",
        7: "eighth",
        8: "ninth",
        9: "tenth"
    }
    return queue_mapper


class GlobalClassCreateEi:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    ei_ocid = None
    ei_token = None
    actual_ei_release = None


class GlobalClassUpdateEi:
    environment = None
    operation_id = None
    hosts = None
    send_the_request_create_ei = None
    feed_point_message = None
    host_for_service = None
    country = None
    language = None
    payload = None
    cassandra_cluster = None
    cassandra_username = None
    cassandra_password = None
    access_token = None
    host_for_bpe = None
    check_message = None


class GlobalClassCreateFs:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    fs_id = None
    actual_fs_release = None
    actual_ei_release = None


class GlobalClassMetadata:
    environment = None
    country = None
    language = None
    pmd = None
    cassandra_cluster = None
    cassandra_username = None
    cassandra_password = None
    host_for_bpe = None
    host_for_services = None
    metadata_budget_url = None
    metadata_tender_url = None
    metadata_document_url = None
    database = None
    document_url = None


class GlobalClassUpdateFs:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None


class GlobalClassCreatePn:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    pn_id = None
    pn_ocid = None
    pn_token = None
    actual_ms_release = None
    actual_pn_release = None


class GlobalClassUpdatePn:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_pn_release = None


class GlobalClassCancelPn:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_pn_release = None


class GlobalClassCreateCnOnPn:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_pn_release = None
    actual_ev_release = None
    ev_id = None


class GlobalClassUpdateCnOnPn:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None
    ev_id = None


class GlobalClassCreateEnquiry:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message_platform = None
    feed_point_message_bpe = None
    actual_ms_release = None
    actual_ev_release = None
    enquiry_id = None
    enquiry_token = None


class GlobalClassCreateAnswer:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None


class GlobalClassEnquiryPeriodEnd:
    feed_point_message_bpe = None
    actual_ms_release = None
    actual_ev_release = None


class GlobalClassCreateFirstBid:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None
    bid_id = None
    bid_token = None


class GlobalClassCreateSecondBid:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None
    bid_id = None
    bid_token = None


class GlobalClassWithdrawBid:
    access_token = None
    operation_id = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None


class GlobalClassTenderPeriodEndNoAuction:
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None
    award_id = None
    award_token = None


class GlobalClassTenderPeriodEndAuction:
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None
    award_id = None
    award_token = None


class GlobalClassCreateDeclareNonConflict:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None


class GlobalClassUpdateDeclareNonConflict:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None
    previous_value_of_iterable_item_object = None


class GlobalClassAwardConsideration:
    access_token = None
    operation_id = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None


class GlobalClassCreateEvaluateAward:
    access_token = None
    operation_id = None
    payload = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None


class GlobalClassProtocol:
    access_token = None
    operation_id = None
    feed_point_message = None
    actual_ms_release = None
    actual_ev_release = None

