# файл з самим тестом
import copy
import requests
from deepdiff import DeepDiff
from pytest_testrail.plugin import pytestrail
from tests.conftest import GlobalClassCreateEi
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions import compare_actual_result_and_expected_result
from tests.utils.payloads import EiPayload
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.releases_models import EiRelease
from tests.utils.requests import Requests


class TestCheckThePossibilityToCreateEIOnObligatoryDataModel:
    @pytestrail.case('22133')
    def test_setup(self, environment, country, language, cassandra_username, cassandra_password):
        GlobalClassCreateEi.country = country
        GlobalClassCreateEi.language = language
        GlobalClassCreateEi.cassandra_username = cassandra_username
        GlobalClassCreateEi.cassandra_password = cassandra_password
        GlobalClassCreateEi.environment = environment
        GlobalClassCreateEi.hosts = Environment().choose_environment(GlobalClassCreateEi.environment)
        host_for_bpe = GlobalClassCreateEi.hosts[1]
        GlobalClassCreateEi.host_for_service = GlobalClassCreateEi.hosts[2]
        GlobalClassCreateEi.cassandra_cluster = GlobalClassCreateEi.hosts[0]
        access_token = PlatformAuthorization(host_for_bpe).get_access_token_for_platform_one()
        GlobalClassCreateEi.operation_id = PlatformAuthorization(host_for_bpe).get_x_operation_id(access_token)
        GlobalClassCreateEi.payload_for_create_ei = copy.deepcopy(EiPayload().obligatory_model_of_payload())
        GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
            host_of_request=host_for_bpe,
            access_token=access_token,
            x_operation_id=GlobalClassCreateEi.operation_id,
            country=GlobalClassCreateEi.country,
            language=GlobalClassCreateEi.language,
            payload=GlobalClassCreateEi.payload_for_create_ei
        )

    @pytestrail.case('22133')
    def test_check_status_code_of_request_22133_1(self):
        assert compare_actual_result_and_expected_result(
            expected_result=str(202),
            actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
        )

    @pytestrail.case('22133')
    def test_check_message_in_kafka_topic_22133_2(self):
        GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
        GlobalClassCreateEi.check_message = KafkaMessage(
            GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
            environment=GlobalClassCreateEi.environment,
            kafka_message=GlobalClassCreateEi.message
        )
        assert compare_actual_result_and_expected_result(
            expected_result=str(True),
            actual_result=str(GlobalClassCreateEi.check_message)
        )

    @pytestrail.case('22133')
    def test_check_ei_release_in_public_point_22133_3(self):
        actual_ei_release_model = requests.get(url=f"{GlobalClassCreateEi.message['data']['url']}/"
                                                   f"{GlobalClassCreateEi.message['data']['ocid']}").json()
        expected_ei_release_model = EiRelease(
            operation_date=GlobalClassCreateEi.message['data']['operationDate'],
            release_id=actual_ei_release_model['releases'][0]['id'],
            tender_id=actual_ei_release_model['releases'][0]['tender']['id'],
            ei_id=GlobalClassCreateEi.message['data']['ocid'],
            environment=GlobalClassCreateEi.environment,
            payload_for_create_ei=GlobalClassCreateEi.payload_for_create_ei,
            language=GlobalClassCreateEi.language
        ).for_create_ei_obligatory_data_model()
        compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
        assert compare_actual_result_and_expected_result(
            expected_result=str({}),
            actual_result=str(compare_releases)
        )

    @pytestrail.case('22133')
    def test_teardown(self):
        try:
            if GlobalClassCreateEi.check_message is True:
                database = CassandraSession(
                    cassandra_username=GlobalClassCreateEi.cassandra_username,
                    cassandra_password=GlobalClassCreateEi.cassandra_password,
                    cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                )
                database.create_ei_process_cleanup_table_of_services(
                    ei_id=GlobalClassCreateEi.message['data']['ocid']
                )
                database.cleanup_steps_of_process(
                    operation_id=GlobalClassCreateEi.operation_id
                )
            else:
                pass
        except ValueError:
            print("Check the message in kafka topic")


class TestCheckOnTenderItemsInRelease:
    @pytestrail.case('24012')
    def test_setup(self, environment, country, language, cassandra_username, cassandra_password):
        GlobalClassCreateEi.country = country
        GlobalClassCreateEi.language = language
        GlobalClassCreateEi.language = language
        GlobalClassCreateEi.cassandra_username = cassandra_username
        GlobalClassCreateEi.cassandra_password = cassandra_password
        GlobalClassCreateEi.environment = environment
        GlobalClassCreateEi.hosts = Environment().choose_environment(GlobalClassCreateEi.environment)
        host_for_bpe = GlobalClassCreateEi.hosts[1]
        GlobalClassCreateEi.host_for_service = GlobalClassCreateEi.hosts[2]
        GlobalClassCreateEi.cassandra_cluster = GlobalClassCreateEi.hosts[0]
        access_token = PlatformAuthorization(host_for_bpe).get_access_token_for_platform_one()
        GlobalClassCreateEi.operation_id = PlatformAuthorization(host_for_bpe).get_x_operation_id(access_token)
        GlobalClassCreateEi.payload_for_create_ei = copy.deepcopy(EiPayload().add_tender_items(quantity=3))
        GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
            host_of_request=host_for_bpe,
            access_token=access_token,
            x_operation_id=GlobalClassCreateEi.operation_id,
            country=GlobalClassCreateEi.country,
            language=GlobalClassCreateEi.language,
            payload=GlobalClassCreateEi.payload_for_create_ei
        )

    @pytestrail.case('24012')
    def test_check_status_code_of_request_24012_1(self):
        assert compare_actual_result_and_expected_result(
            expected_result=str(202),
            actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
        )

    @pytestrail.case('24012')
    def test_check_message_in_kafka_topic_24012_2(self):
        GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
        check_message = KafkaMessage(GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
            environment=GlobalClassCreateEi.environment,
            kafka_message=GlobalClassCreateEi.message
        )
        assert compare_actual_result_and_expected_result(
            expected_result=str(True),
            actual_result=str(check_message)
        )

    @pytestrail.case('24012')
    def test_check_ei_release_in_public_point_24012_3(self):
        actual_ei_release_model = requests.get(url=f"{GlobalClassCreateEi.message['data']['url']}/"
                                                   f"{GlobalClassCreateEi.message['data']['ocid']}").json()
        expected_ei_release_model = EiRelease(
            operation_date=GlobalClassCreateEi.message['data']['operationDate'],
            release_id=actual_ei_release_model['releases'][0]['id'],
            tender_id=actual_ei_release_model['releases'][0]['tender']['id'],
            ei_id=GlobalClassCreateEi.message['data']['ocid'],
            environment=GlobalClassCreateEi.environment,
            payload_for_create_ei=GlobalClassCreateEi.payload_for_create_ei,
            language=GlobalClassCreateEi.language
        ).for_create_ei_obligatory_data_model_with_items_array(
            actual_items_array=actual_ei_release_model['releases'][0]['tender']['items']
        )
        compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
        assert compare_actual_result_and_expected_result(
            expected_result=str({}),
            actual_result=str(compare_releases)
        )

    @pytestrail.case('24012')
    def test_teardown(self):
        try:
            if GlobalClassCreateEi.check_message is True:
                database = CassandraSession(
                    cassandra_username=GlobalClassCreateEi.cassandra_username,
                    cassandra_password=GlobalClassCreateEi.cassandra_password,
                    cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                )
                database.create_ei_process_cleanup_table_of_services(
                    ei_id=GlobalClassCreateEi.message['data']['ocid']
                )
                database.cleanup_steps_of_process(
                    operation_id=GlobalClassCreateEi.operation_id
                )
            else:
                pass
        except ValueError:
            print("Check the message in kafka topic")


class TestCheckThePossibilityToCreateEiWithoutOptionalData:
    @pytestrail.case('27619')
    def test_setup(self, environment, country, language, cassandra_username, cassandra_password):
        GlobalClassCreateEi.country = country
        GlobalClassCreateEi.language = language
        GlobalClassCreateEi.language = language
        GlobalClassCreateEi.cassandra_username = cassandra_username
        GlobalClassCreateEi.cassandra_password = cassandra_password
        GlobalClassCreateEi.environment = environment
        GlobalClassCreateEi.hosts = Environment().choose_environment(GlobalClassCreateEi.environment)
        GlobalClassCreateEi.host_for_bpe = GlobalClassCreateEi.hosts[1]
        GlobalClassCreateEi.host_for_service = GlobalClassCreateEi.hosts[2]
        GlobalClassCreateEi.cassandra_cluster = GlobalClassCreateEi.hosts[0]
        GlobalClassCreateEi.access_token = PlatformAuthorization(
            GlobalClassCreateEi.host_for_bpe).get_access_token_for_platform_one()

    @pytestrail.case('C27619')
    def test_check_ei_release_without_one_attribute_in_buyer_details__27619_1(self):
        payload_for_create_ei = copy.deepcopy(EiPayload().add_buyer_details())
        del payload_for_create_ei['buyer']['details']['typeOfBuyer']
        host_for_bpe = copy.deepcopy(GlobalClassCreateEi.host_for_bpe)
        access_token = copy.deepcopy(GlobalClassCreateEi.access_token)
        operation_id = PlatformAuthorization(GlobalClassCreateEi.host_for_bpe).get_x_operation_id(access_token)
        country = copy.deepcopy(GlobalClassCreateEi.country)
        language = copy.deepcopy(GlobalClassCreateEi.language)
        send_the_request_create_ei = Requests().create_ei(
            host_of_request=host_for_bpe,
            access_token=access_token,
            x_operation_id=operation_id,
            country=country,
            language=language,
            payload=payload_for_create_ei
        )
        message = KafkaMessage(operation_id).get_message_from_kafka()
        check_message = KafkaMessage(operation_id).create_ei_message_is_successful(
            environment=GlobalClassCreateEi.environment,
            kafka_message=message
        )
        actual_ei_release_model = requests.get(url=f"{message['data']['url']}/"
                                                   f"{message['data']['ocid']}").json()
        expected_ei_release_model = EiRelease(
            operation_date=message['data']['operationDate'],
            release_id=actual_ei_release_model['releases'][0]['id'],
            tender_id=actual_ei_release_model['releases'][0]['tender']['id'],
            ei_id=message['data']['ocid'],
            environment=GlobalClassCreateEi.environment,
            payload_for_create_ei=payload_for_create_ei,
            language=language
        ).for_create_ei_obligatory_data_model_with_buyer_details()
        compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
        assert compare_actual_result_and_expected_result(
            expected_result=str(202),
            actual_result=str(send_the_request_create_ei.status_code)
        )
        assert compare_actual_result_and_expected_result(
            expected_result=str(True),
            actual_result=str(check_message)
        )
        assert compare_actual_result_and_expected_result(
            expected_result=str({}),
            actual_result=str(compare_releases)
        )

    @pytestrail.case('27619')
    def test_check_ei_release_without_two_attribute_in_buyer_details_27619_2(self):
        payload_for_create_ei = copy.deepcopy(EiPayload().add_buyer_details())
        del payload_for_create_ei['buyer']['details']['mainGeneralActivity']
        del payload_for_create_ei['buyer']['details']['mainSectoralActivity']
        host_for_bpe = copy.deepcopy(GlobalClassCreateEi.host_for_bpe)
        access_token = copy.deepcopy(GlobalClassCreateEi.access_token)
        operation_id = PlatformAuthorization(GlobalClassCreateEi.host_for_bpe).get_x_operation_id(access_token)
        country = copy.deepcopy(GlobalClassCreateEi.country)
        language = copy.deepcopy(GlobalClassCreateEi.language)
        send_the_request_create_ei = Requests().create_ei(
            host_of_request=host_for_bpe,
            access_token=access_token,
            x_operation_id=operation_id,
            country=country,
            language=language,
            payload=payload_for_create_ei
        )
        message = KafkaMessage(operation_id).get_message_from_kafka()
        check_message = KafkaMessage(operation_id).create_ei_message_is_successful(
            environment=GlobalClassCreateEi.environment,
            kafka_message=message
        )
        actual_ei_release_model = requests.get(url=f"{message['data']['url']}/"
                                                   f"{message['data']['ocid']}").json()
        expected_ei_release_model = EiRelease(
            operation_date=message['data']['operationDate'],
            release_id=actual_ei_release_model['releases'][0]['id'],
            tender_id=actual_ei_release_model['releases'][0]['tender']['id'],
            ei_id=message['data']['ocid'],
            environment=GlobalClassCreateEi.environment,
            payload_for_create_ei=payload_for_create_ei,
            language=language
        ).for_create_ei_obligatory_data_model_with_buyer_details()
        compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
        assert compare_actual_result_and_expected_result(
            expected_result=str(202),
            actual_result=str(send_the_request_create_ei.status_code)
        )
        assert compare_actual_result_and_expected_result(
            expected_result=str(True),
            actual_result=str(check_message)
        )
        assert compare_actual_result_and_expected_result(
            expected_result=str({}),
            actual_result=str(compare_releases)
        )

    @pytestrail.case('27619')
    def test_teardown(self):
        try:
            if GlobalClassCreateEi.check_message is True:
                database = CassandraSession(
                    cassandra_username=GlobalClassCreateEi.cassandra_username,
                    cassandra_password=GlobalClassCreateEi.cassandra_password,
                    cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                )
                database.create_ei_process_cleanup_table_of_services(
                    ei_id=GlobalClassCreateEi.message['data']['ocid']
                )
                database.cleanup_steps_of_process(
                    operation_id=GlobalClassCreateEi.operation_id
                )
            else:
                pass
        except ValueError:
            print("Check the message in kafka topic")
