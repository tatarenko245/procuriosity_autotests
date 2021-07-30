# файл з самим тестом
import copy
import json
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


@allure.parent_suite('Budgets')
@allure.suite('EI')
@allure.sub_suite('BPE: Create EI')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/edit#gid=0',
                 name='Google sheets: Create EI')
class TestCreateEi:
    @allure.title('Check status code and message from Kafka topic after EI creation')
    def test_check_status_code_and_message_from_kafka_topic_after_ei_creation(self, environment, country, language,
                                                                              cassandra_username, cassandra_password):
        with allure.step('# 1. Authorization'):
            GlobalClassCreateEi.country = country
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
            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassCreateEi.host_for_bpe).get_x_operation_id(
                GlobalClassCreateEi.access_token)
        with allure.step('# 2. Take EI payload based on full data model'):
            GlobalClassCreateEi.payload_for_create_ei = copy.deepcopy(EiPayload().add_optionals_fields())
            allure.attach(str(json.dumps(GlobalClassCreateEi.payload_for_create_ei)), 'Payload')

        with allure.step('# 3. Send request to create EI'):
            GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
                host_of_request=GlobalClassCreateEi.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassCreateEi.country,
                language=GlobalClassCreateEi.language,
                payload=GlobalClassCreateEi.payload_for_create_ei
            )

        with allure.step('# 4. See result'):
            with allure.step('# 4.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=str(202),
                    actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
                )
            GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
            GlobalClassCreateEi.check_message = KafkaMessage(
                GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
                environment=GlobalClassCreateEi.environment,
                kafka_message=GlobalClassCreateEi.message
            )

            with allure.step('# 4.2. Check message in feed point'):
                allure.attach(str(GlobalClassCreateEi.message), 'Message in feed point')
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
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassCreateEi.cassandra_username,
                                cassandra_password=GlobalClassCreateEi.cassandra_password,
                                cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    print("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(True),
                    actual_result=str(GlobalClassCreateEi.check_message)
                )

    @allure.title('Check EI release data after Ei creation based on full data model')
    def test_check_ei_release_data_after_ei_creation_based_on_full_data_model(self, environment, country, language,
                                                                              cassandra_username, cassandra_password):

        with allure.step('# 1. Authorization'):
            GlobalClassCreateEi.country = country
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
            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassCreateEi.host_for_bpe).get_x_operation_id(
                GlobalClassCreateEi.access_token)
        with allure.step('# 2. Take EI payload based on full data model'):
            payload = copy.deepcopy(EiPayload())
            GlobalClassCreateEi.payload_for_create_ei = payload.add_optionals_fields()
            allure.attach(str(GlobalClassCreateEi.payload_for_create_ei), 'Payload')

        with allure.step('# 3. Send request to create EI'):
            GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
                host_of_request=GlobalClassCreateEi.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassCreateEi.country,
                language=GlobalClassCreateEi.language,
                payload=GlobalClassCreateEi.payload_for_create_ei
            )

        with allure.step('# 4. See result'):
            with allure.step('# 4.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=str(202),
                    actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
                )
            GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
            GlobalClassCreateEi.check_message = KafkaMessage(
                GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
                environment=GlobalClassCreateEi.environment,
                kafka_message=GlobalClassCreateEi.message
            )
            with allure.step('# 4.2. Check message in feed point'):
                allure.attach(str(GlobalClassCreateEi.message), 'Message in feed point')
                try:
                    if GlobalClassCreateEi.check_message is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassCreateEi.cassandra_username,
                                cassandra_password=GlobalClassCreateEi.cassandra_password,
                                cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    print("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(True),
                    actual_result=str(GlobalClassCreateEi.check_message)
                )
            with allure.step('# 4.3. Check EI release'):
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
                allure.attach(str(json.dumps(actual_ei_release_model)), "Actual Ei release")
                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected Ei release")
                compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
                try:
                    if compare_releases is {}:
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
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassCreateEi.cassandra_username,
                                cassandra_password=GlobalClassCreateEi.cassandra_password,
                                cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    print("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str({}),
                    actual_result=str(compare_releases)
                )

    @allure.title('Check EI release after Ei creation on model without optional fields')
    def test_check_ei_release_data_after_ei_creation_based_on_model_without_optional_fields(self, environment, country,
                                                                                            language,
                                                                                            cassandra_username,
                                                                                            cassandra_password):

        with allure.step('# 1. Authorization'):
            GlobalClassCreateEi.country = country
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
            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassCreateEi.host_for_bpe).get_x_operation_id(
                GlobalClassCreateEi.access_token)
        with allure.step('# 2. Take EI payload based on full data model'):
            GlobalClassCreateEi.payload_for_create_ei = copy.deepcopy(EiPayload().obligatory_model_of_payload())
            allure.attach(str(GlobalClassCreateEi.payload_for_create_ei), 'Payload')

        with allure.step('# 3. Send request to create EI'):
            GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
                host_of_request=GlobalClassCreateEi.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassCreateEi.country,
                language=GlobalClassCreateEi.language,
                payload=GlobalClassCreateEi.payload_for_create_ei
            )

        with allure.step('# 4. See result'):
            with allure.step('# 4.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=str(202),
                    actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
                )
            GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
            GlobalClassCreateEi.check_message = KafkaMessage(
                GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
                environment=GlobalClassCreateEi.environment,
                kafka_message=GlobalClassCreateEi.message
            )
            with allure.step('# 4.2. Check message in feed point'):
                allure.attach(str(GlobalClassCreateEi.message), 'Message in feed point')
                try:
                    if GlobalClassCreateEi.check_message is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassCreateEi.cassandra_username,
                                cassandra_password=GlobalClassCreateEi.cassandra_password,
                                cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    print("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(True),
                    actual_result=str(GlobalClassCreateEi.check_message)
                )
            with allure.step('# 4.3. Check EI release'):
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
                expected_ei_release_model = release.obligatory_data_model()

                allure.attach(str(json.dumps(actual_ei_release_model)), "Actual Ei release")
                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected Ei release")
                compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
                try:
                    if compare_releases is {}:
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
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassCreateEi.cassandra_username,
                                cassandra_password=GlobalClassCreateEi.cassandra_password,
                                cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    print("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str({}),
                    actual_result=str(compare_releases)
                )

    # ----------------------
    @allure.title('Check EI release data after Ei creation based on full data model with 3 items objects')
    def test_check_ei_release_data_after_ei_creation_based_on_full_data_model_with_3_items_objects(self, environment,
                                                                                                   country,
                                                                                                   language,
                                                                                                   cassandra_username,
                                                                                                   cassandra_password):

        with allure.step('# 1. Authorization'):
            GlobalClassCreateEi.country = country
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
            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassCreateEi.host_for_bpe).get_x_operation_id(
                GlobalClassCreateEi.access_token)
        with allure.step('# 2. Take EI payload based on full data model'):
            payload = EiPayload()
            GlobalClassCreateEi.payload_for_create_ei = payload.add_optionals_fields()
            GlobalClassCreateEi.payload_for_create_ei = payload.add_tender_items(3)
            allure.attach(str(GlobalClassCreateEi.payload_for_create_ei), 'Payload')

        with allure.step('# 3. Send request to create EI'):
            GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
                host_of_request=GlobalClassCreateEi.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassCreateEi.country,
                language=GlobalClassCreateEi.language,
                payload=GlobalClassCreateEi.payload_for_create_ei
            )

        with allure.step('# 4. See result'):
            with allure.step('# 4.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=str(202),
                    actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
                )
            GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
            GlobalClassCreateEi.check_message = KafkaMessage(
                GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
                environment=GlobalClassCreateEi.environment,
                kafka_message=GlobalClassCreateEi.message
            )
            with allure.step('# 4.2. Check message in feed point'):
                allure.attach(str(GlobalClassCreateEi.message), 'Message in feed point')
                try:
                    if GlobalClassCreateEi.check_message is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassCreateEi.cassandra_username,
                                cassandra_password=GlobalClassCreateEi.cassandra_password,
                                cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    print("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(True),
                    actual_result=str(GlobalClassCreateEi.check_message)
                )
            with allure.step('# 4.3. Check EI release'):
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

            allure.attach(str(json.dumps(actual_ei_release_model)), "Actual Ei release")
            allure.attach(str(json.dumps(expected_ei_release_model)), "Expected Ei release")
            compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
            try:
                if compare_releases is {}:
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
                    with allure.step('# Steps from Casandra DataBase'):
                        steps = CassandraSession(
                            cassandra_username=GlobalClassCreateEi.cassandra_username,
                            cassandra_password=GlobalClassCreateEi.cassandra_password,
                            cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
                        ).get_orchestrator_operation_step_by_x_operation_id(
                            operation_id=GlobalClassCreateEi.operation_id)
                        allure.attach(steps, "Cassandra DataBase: steps of process")
            except ValueError:
                print("Check the message in kafka topic")
            assert compare_actual_result_and_expected_result(
                expected_result=str({}),
                actual_result=str(compare_releases)
            )
