# файл з самим тестом
import copy

import allure
import requests
from deepdiff import DeepDiff
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

    def test_check_status_code_of_request(self):
        assert compare_actual_result_and_expected_result(
            expected_result=str(202),
            actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
        )

    def test_check_message_in_kafka_topic(self):
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

    @allure.step('Check Ei release')
    def test_check_ei_release_in_public_point(self):
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
        ).obligatory_data_model()
        allure.attach(actual_ei_release_model, "Actual Ei release")
        allure.attach(expected_ei_release_model, "Expected Ei release")
        compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
        assert compare_actual_result_and_expected_result(
            expected_result=str({}),
            actual_result=str(compare_releases)
        )

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
                allure.attach("TestCase passed: Database is empty")
            else:
                CassandraSession(
                    cassandra_username=GlobalClassCreateEi.cassandra_username,
                    cassandra_password=GlobalClassCreateEi.cassandra_password,
                    cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                ).get_orchestrator_operation_step_by_x_operation_id(operation_id=GlobalClassCreateEi.operation_id)
        except ValueError:
            print("Check the message in kafka topic")


class TestCheckThePossibilityToCreateEIOnFullDataModel:
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
        payload = copy.deepcopy(EiPayload())
        GlobalClassCreateEi.payload_for_create_ei = payload.add_optionals_fields()
        GlobalClassCreateEi.payload_for_create_ei = payload.add_tender_items(quantity=4)
        GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
            host_of_request=host_for_bpe,
            access_token=access_token,
            x_operation_id=GlobalClassCreateEi.operation_id,
            country=GlobalClassCreateEi.country,
            language=GlobalClassCreateEi.language,
            payload=GlobalClassCreateEi.payload_for_create_ei
        )

    def test_check_status_code_of_request(self):
        assert compare_actual_result_and_expected_result(
            expected_result=str(202),
            actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
        )

    def test_check_message_in_kafka_topic(self):
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

    @allure.step('Check Ei release')
    def test_check_ei_release_in_public_point(self):
        actual_ei_release_model = requests.get(url=f"{GlobalClassCreateEi.message['data']['url']}/"
                                                   f"{GlobalClassCreateEi.message['data']['ocid']}").json()
        release = EiRelease(
            operation_date=GlobalClassCreateEi.message['data']['operationDate'],
            release_id=actual_ei_release_model['releases'][0]['id'],
            tender_id=actual_ei_release_model['releases'][0]['tender']['id'],
            ei_id=GlobalClassCreateEi.message['data']['ocid'],
            environment=GlobalClassCreateEi.environment,
            payload_for_create_ei=GlobalClassCreateEi.payload_for_create_ei,
            language=GlobalClassCreateEi.language
        )
        release.full_data_data_model()
        expected_ei_release_model = release.add_tender_with_items_array(
            actual_items_array=actual_ei_release_model['releases'][0]['tender']['items'])
        allure.attach(actual_ei_release_model, "Actual Ei release")
        allure.attach(expected_ei_release_model, "Expected Ei release")
        compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
        assert compare_actual_result_and_expected_result(
            expected_result=str({}),
            actual_result=str(compare_releases)
        )

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
