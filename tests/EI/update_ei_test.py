# файл з самим тестом
import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassCreateEi, GlobalClassUpdateEi
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.expected_release import ExpectedRelease
from tests.utils.functions import compare_actual_result_and_expected_result
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.prepared_payload import PreparePayload
from tests.utils.requests import Requests


@allure.parent_suite('Budgets')
@allure.suite('EI')
@allure.sub_suite('BPE: Update EI')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/edit#gid=0',
                 name='Google sheets: Update EI')
class TestUpdateEi:
    @allure.title('Check status code and message from Kafka topic after EI updating')
    def test_check_status_code_and_message_from_kafka_topic_after_ei_updating(self, environment, country, language,
                                                                              cassandra_username, cassandra_password):
        with allure.step('# 1. Authorization: create EI'):
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
        with allure.step('# 2. Send request to create EI'):
            payload = copy.deepcopy(PreparePayload())
            GlobalClassCreateEi.payload_for_create_ei = payload.create_ei_obligatory_data_model()
            GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
                host_of_request=GlobalClassCreateEi.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassCreateEi.country,
                language=GlobalClassCreateEi.language,
                payload=GlobalClassCreateEi.payload_for_create_ei
            )
            GlobalClassCreateEi.ei_ocid = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()["data"]["outcomes"]["ei"][0][
                    'id']
            GlobalClassCreateEi.ei_token = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()["data"]["outcomes"]["ei"][0][
                    'X-TOKEN']
        with allure.step('# 3. Authorization: update EI'):
            GlobalClassUpdateEi.cassandra_username = cassandra_username
            GlobalClassUpdateEi.cassandra_password = cassandra_password
            GlobalClassUpdateEi.environment = environment
            GlobalClassUpdateEi.hosts = Environment().choose_environment(GlobalClassUpdateEi.environment)
            GlobalClassUpdateEi.host_for_bpe = GlobalClassUpdateEi.hosts[1]
            GlobalClassUpdateEi.host_for_service = GlobalClassUpdateEi.hosts[2]
            GlobalClassUpdateEi.cassandra_cluster = GlobalClassUpdateEi.hosts[0]
            GlobalClassUpdateEi.access_token = PlatformAuthorization(
                GlobalClassUpdateEi.host_for_bpe).get_access_token_for_platform_one()
            GlobalClassUpdateEi.operation_id = PlatformAuthorization(
                GlobalClassUpdateEi.host_for_bpe).get_x_operation_id(
                GlobalClassUpdateEi.access_token)
        with allure.step('# 4. Send request to update EI'):
            GlobalClassUpdateEi.payload_for_update_ei = payload.update_ei_full_data_model(
                tender_classification_id=GlobalClassCreateEi.payload_for_create_ei['tender']['classification']['id']
            )
            GlobalClassUpdateEi.send_the_request_update_ei = Requests().update_ei(
                host_of_request=GlobalClassUpdateEi.host_for_bpe,
                access_token=GlobalClassUpdateEi.access_token,
                x_operation_id=GlobalClassUpdateEi.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                ei_token=GlobalClassCreateEi.ei_token,
                payload=GlobalClassUpdateEi.payload_for_update_ei
            )

        with allure.step('# 5. See result'):
            with allure.step('# 5.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=str(202),
                    actual_result=str(GlobalClassUpdateEi.send_the_request_update_ei.status_code)
                )
            with allure.step('# 5.2. Check message in feed point'):
                GlobalClassUpdateEi.message = KafkaMessage(GlobalClassUpdateEi.operation_id).get_message_from_kafka()
                GlobalClassUpdateEi.check_message = KafkaMessage(
                    GlobalClassUpdateEi.operation_id).update_ei_message_is_successful(
                    environment=GlobalClassUpdateEi.environment,
                    kafka_message=GlobalClassUpdateEi.message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid
                )
                allure.attach(str(GlobalClassUpdateEi.message), 'Message in feed point')

                try:
                    if GlobalClassUpdateEi.check_message is True:
                        database = CassandraSession(
                            cassandra_username=GlobalClassUpdateEi.cassandra_username,
                            cassandra_password=GlobalClassUpdateEi.cassandra_password,
                            cassandra_cluster=GlobalClassUpdateEi.cassandra_cluster
                        )
                        database.create_ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassUpdateEi.operation_id
                        )
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassUpdateEi.cassandra_username,
                                cassandra_password=GlobalClassUpdateEi.cassandra_password,
                                cassandra_cluster=GlobalClassUpdateEi.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassUpdateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(True),
                    actual_result=str(GlobalClassUpdateEi.check_message)
                )

    @allure.title('Check EI release after Ei updating on model without optional fields')
    def test_check_ei_release_after_ei_updating_on_model_without_optional_fields(self, environment, country, language,
                                                                                 cassandra_username,
                                                                                 cassandra_password):
        with allure.step('# 1. Authorization platform one: create EI'):
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
        with allure.step('# 2. Send request to create EI'):
            payload = copy.deepcopy(PreparePayload())
            GlobalClassCreateEi.payload_for_create_ei = payload.create_ei_full_data_model()
            GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
                host_of_request=GlobalClassCreateEi.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassCreateEi.country,
                language=GlobalClassCreateEi.language,
                payload=GlobalClassCreateEi.payload_for_create_ei
            )
            GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
            GlobalClassCreateEi.ei_ocid = GlobalClassCreateEi.message["data"]["outcomes"]["ei"][0]['id']
            GlobalClassCreateEi.ei_token = GlobalClassCreateEi.message["data"]["outcomes"]["ei"][0]['X-TOKEN']
            actual_ei_release_model_before_updating = requests.get(
                url=f"{GlobalClassCreateEi.message['data']['url']}/"
                    f"{GlobalClassCreateEi.message['data']['ocid']}").json()
        with allure.step('# 3. Authorization platform one: update EI'):
            GlobalClassUpdateEi.cassandra_username = cassandra_username
            GlobalClassUpdateEi.cassandra_password = cassandra_password
            GlobalClassUpdateEi.environment = environment
            GlobalClassUpdateEi.hosts = Environment().choose_environment(GlobalClassUpdateEi.environment)
            GlobalClassUpdateEi.host_for_bpe = GlobalClassUpdateEi.hosts[1]
            GlobalClassUpdateEi.host_for_service = GlobalClassUpdateEi.hosts[2]
            GlobalClassUpdateEi.cassandra_cluster = GlobalClassUpdateEi.hosts[0]
            GlobalClassUpdateEi.access_token = PlatformAuthorization(
                GlobalClassUpdateEi.host_for_bpe).get_access_token_for_platform_one()
            GlobalClassUpdateEi.operation_id = PlatformAuthorization(
                GlobalClassUpdateEi.host_for_bpe).get_x_operation_id(
                GlobalClassUpdateEi.access_token)
        with allure.step('# 4. Send request to update EI'):
            time.sleep(2)
            GlobalClassUpdateEi.payload_for_update_ei = payload.update_ei_obligatory_data_model(
                tender_classification_id=GlobalClassCreateEi.payload_for_create_ei['tender']['classification']['id']
            )
            GlobalClassUpdateEi.send_the_request_update_ei = Requests().update_ei(
                host_of_request=GlobalClassUpdateEi.host_for_bpe,
                access_token=GlobalClassUpdateEi.access_token,
                x_operation_id=GlobalClassUpdateEi.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                ei_token=GlobalClassCreateEi.ei_token,
                payload=GlobalClassUpdateEi.payload_for_update_ei
            )

        with allure.step('# 5. See result'):
            with allure.step('# 5.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=str(202),
                    actual_result=str(GlobalClassUpdateEi.send_the_request_update_ei.status_code)
                )
            with allure.step('# 5.2. Check message in feed point'):
                GlobalClassUpdateEi.message = KafkaMessage(GlobalClassUpdateEi.operation_id).get_message_from_kafka()
                GlobalClassUpdateEi.check_message = KafkaMessage(
                    GlobalClassUpdateEi.operation_id).update_ei_message_is_successful(
                    environment=GlobalClassUpdateEi.environment,
                    kafka_message=GlobalClassUpdateEi.message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid
                )
                allure.attach(str(GlobalClassUpdateEi.message), 'Message in feed point')
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
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(True),
                    actual_result=str(GlobalClassUpdateEi.check_message)
                )
            with allure.step('# 5.3. Check EI release before updating'):
                release = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassCreateEi.environment,
                    language=GlobalClassCreateEi.language
                ))
                expected_ei_release_model = copy.deepcopy(release.ei_release_full_data_model(
                    operation_date=GlobalClassCreateEi.message['data']['operationDate'],
                    release_id=actual_ei_release_model_before_updating['releases'][0]['id'],
                    tender_id=actual_ei_release_model_before_updating['releases'][0]['tender']['id'],
                    ei_id=GlobalClassCreateEi.message['data']['ocid'],
                    payload_for_create_ei=GlobalClassCreateEi.payload_for_create_ei,
                    actual_items_array=actual_ei_release_model_before_updating['releases'][0]['tender']['items']
                ))
                allure.attach(str(json.dumps(actual_ei_release_model_before_updating)),
                              "Actual Ei release before updating")
                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected Ei release")
                compare_releases = DeepDiff(
                    actual_ei_release_model_before_updating,
                    expected_ei_release_model)
                try:
                    if compare_releases == {}:
                        pass
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
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str({}),
                    actual_result=str(compare_releases)
                )
            with allure.step('# 5.4. Check EI release after updating'):
                actual_ei_release_model_after_updating = requests.get(
                    url=f"{GlobalClassUpdateEi.message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_ei_release_model_before_updating)),
                              "Actual Ei release before updating")
                allure.attach(str(json.dumps(actual_ei_release_model_after_updating)),
                              "Actual Ei release after updating")
                compare_releases = DeepDiff(actual_ei_release_model_before_updating,
                                            actual_ei_release_model_after_updating)
                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                expected_result = {
                    'dictionary_item_removed': "['releases'][0]['tender']['description'], "
                                               "['releases'][0]['tender']['items'], "
                                               "['releases'][0]['planning']['rationale']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value': f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_model_after_updating['releases'][0]['id'][29:42]}",
                            'old_value': f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_model_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateEi.message['data']['operationDate'],
                            'old_value': GlobalClassCreateEi.message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['title']": {
                            'new_value': GlobalClassUpdateEi.payload_for_update_ei['tender']['title'],
                            'old_value': GlobalClassCreateEi.payload_for_create_ei['tender']['title']
                        }
                    }
                }
                try:
                    if compare_releases == expected_result:
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
                        database = CassandraSession(
                            cassandra_username=GlobalClassUpdateEi.cassandra_username,
                            cassandra_password=GlobalClassUpdateEi.cassandra_password,
                            cassandra_cluster=GlobalClassUpdateEi.cassandra_cluster
                        )
                        database.create_ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassUpdateEi.message['data']['ocid']
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassUpdateEi.operation_id
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
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(expected_result),
                    actual_result=str(compare_releases)
                )

    @allure.title('Check EI release data after Ei updating with full data model')
    def test_check_ei_release_data_after_ei_updating_with_full_data_model(self, environment, country, language,
                                                                          cassandra_username, cassandra_password):
        with allure.step('# 1. Authorization platform one: create EI'):
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
        with allure.step('# 2. Send request to create EI'):
            payload = copy.deepcopy(PreparePayload())
            GlobalClassCreateEi.payload_for_create_ei = payload.create_ei_obligatory_data_model()
            GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
                host_of_request=GlobalClassCreateEi.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassCreateEi.country,
                language=GlobalClassCreateEi.language,
                payload=GlobalClassCreateEi.payload_for_create_ei
            )
            GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
            GlobalClassCreateEi.ei_ocid = GlobalClassCreateEi.message["data"]["outcomes"]["ei"][0]['id']
            GlobalClassCreateEi.ei_token = GlobalClassCreateEi.message["data"]["outcomes"]["ei"][0]['X-TOKEN']
            actual_ei_release_model_before_updating = requests.get(
                url=f"{GlobalClassCreateEi.message['data']['url']}/"
                    f"{GlobalClassCreateEi.message['data']['ocid']}").json()
        with allure.step('# 3. Authorization platform one: update EI'):
            GlobalClassUpdateEi.cassandra_username = cassandra_username
            GlobalClassUpdateEi.cassandra_password = cassandra_password
            GlobalClassUpdateEi.environment = environment
            GlobalClassUpdateEi.hosts = Environment().choose_environment(GlobalClassUpdateEi.environment)
            GlobalClassUpdateEi.host_for_bpe = GlobalClassUpdateEi.hosts[1]
            GlobalClassUpdateEi.host_for_service = GlobalClassUpdateEi.hosts[2]
            GlobalClassUpdateEi.cassandra_cluster = GlobalClassUpdateEi.hosts[0]
            GlobalClassUpdateEi.access_token = PlatformAuthorization(
                GlobalClassUpdateEi.host_for_bpe).get_access_token_for_platform_one()
            GlobalClassUpdateEi.operation_id = PlatformAuthorization(
                GlobalClassUpdateEi.host_for_bpe).get_x_operation_id(
                GlobalClassUpdateEi.access_token)
        with allure.step('# 4. Send request to update EI'):
            time.sleep(2)
            GlobalClassUpdateEi.payload_for_update_ei = payload.update_ei_full_data_model(
                tender_classification_id=GlobalClassCreateEi.payload_for_create_ei['tender']['classification']['id']
            )
            GlobalClassUpdateEi.send_the_request_update_ei = Requests().update_ei(
                host_of_request=GlobalClassUpdateEi.host_for_bpe,
                access_token=GlobalClassUpdateEi.access_token,
                x_operation_id=GlobalClassUpdateEi.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                ei_token=GlobalClassCreateEi.ei_token,
                payload=GlobalClassUpdateEi.payload_for_update_ei
            )
        with allure.step('# 5. See result'):
            with allure.step('# 5.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=str(202),
                    actual_result=str(GlobalClassUpdateEi.send_the_request_update_ei.status_code)
                )
            with allure.step('# 5.2. Check message in feed point'):
                GlobalClassUpdateEi.message = KafkaMessage(GlobalClassUpdateEi.operation_id).get_message_from_kafka()
                GlobalClassUpdateEi.check_message = KafkaMessage(
                    GlobalClassUpdateEi.operation_id).update_ei_message_is_successful(
                    environment=GlobalClassUpdateEi.environment,
                    kafka_message=GlobalClassUpdateEi.message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid
                )
                allure.attach(str(GlobalClassUpdateEi.message), 'Message in feed point')
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
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(True),
                    actual_result=str(GlobalClassUpdateEi.check_message)
                )
            with allure.step('# 5.3. Check EI release before updating'):
                release = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassCreateEi.environment,
                    language=GlobalClassCreateEi.language))
                expected_ei_release_model = copy.deepcopy(release.ei_release_obligatory_data_model(
                    operation_date=GlobalClassCreateEi.message['data']['operationDate'],
                    release_id=actual_ei_release_model_before_updating['releases'][0]['id'],
                    tender_id=actual_ei_release_model_before_updating['releases'][0]['tender']['id'],
                    ei_id=GlobalClassCreateEi.message['data']['ocid'],
                    payload_for_create_ei=GlobalClassCreateEi.payload_for_create_ei
                ))
                allure.attach(str(json.dumps(actual_ei_release_model_before_updating)),
                              "Actual Ei release before updating")
                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected Ei release")
                compare_releases = DeepDiff(actual_ei_release_model_before_updating,
                                            expected_ei_release_model)
                try:
                    if compare_releases == {}:
                        pass
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
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str({}),
                    actual_result=str(compare_releases)
                )
            with allure.step('# 5.4. Check EI release after updating'):
                actual_ei_release_model_after_updating = requests.get(
                    url=f"{GlobalClassUpdateEi.message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_ei_release_model_before_updating)),
                              "Actual Ei release before updating")
                allure.attach(str(json.dumps(actual_ei_release_model_after_updating)),
                              "Actual Ei release after updating")
                compare_releases = DeepDiff(actual_ei_release_model_before_updating,
                                            actual_ei_release_model_after_updating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                expected_result = {
                    'dictionary_item_added': "['releases'][0]['tender']['description'], "
                                             "['releases'][0]['tender']['items'], "
                                             "['releases'][0]['planning']['rationale']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value': f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_model_after_updating['releases'][0]['id'][29:42]}",
                            'old_value': f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_model_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateEi.message['data']['operationDate'],
                            'old_value': GlobalClassCreateEi.message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['title']": {
                            'new_value': GlobalClassUpdateEi.payload_for_update_ei['tender']['title'],
                            'old_value': GlobalClassCreateEi.payload_for_create_ei['tender']['title']
                        }
                    }
                }

                if actual_ei_release_model_after_updating['releases'][0]['tender']['description'] == \
                        GlobalClassUpdateEi.payload_for_update_ei['tender']['description']:
                    pass
                else:
                    raise ValueError('Check tender.description')
                if actual_ei_release_model_after_updating['releases'][0]['planning']['rationale'] == \
                        GlobalClassUpdateEi.payload_for_update_ei['planning']['rationale']:
                    pass
                else:
                    raise ValueError('Check planning.rationale')

                expected_items_array = release.ei_tender_items_array_release(
                    actual_items_array=actual_ei_release_model_after_updating['releases'][0]['tender']['items'],
                    payload=GlobalClassUpdateEi.payload_for_update_ei
                )
                if actual_ei_release_model_after_updating['releases'][0]['tender']['items'] == expected_items_array:
                    pass
                else:
                    raise ValueError('Check tender.items array')
                try:
                    if compare_releases == expected_result:
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
                        database = CassandraSession(
                            cassandra_username=GlobalClassUpdateEi.cassandra_username,
                            cassandra_password=GlobalClassUpdateEi.cassandra_password,
                            cassandra_cluster=GlobalClassUpdateEi.cassandra_cluster
                        )
                        database.create_ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassUpdateEi.message['data']['ocid']
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassUpdateEi.operation_id
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
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(expected_result),
                    actual_result=str(compare_releases)
                )

    @allure.title('Check EI release data after Ei updating based on full data model with 3 items objects')
    def test_check_ei_release_data_after_ei_updating_based_on_full_data_model_with_three_items_objects(
            self, environment, country, language, cassandra_username, cassandra_password):
        with allure.step('# 1. Authorization platform one: create EI'):
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
        with allure.step('# 2. Send request to create EI'):
            payload = copy.deepcopy(PreparePayload())
            GlobalClassCreateEi.payload_for_create_ei = payload.create_ei_full_data_model()
            GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
                host_of_request=GlobalClassCreateEi.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassCreateEi.country,
                language=GlobalClassCreateEi.language,
                payload=GlobalClassCreateEi.payload_for_create_ei
            )
            GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
            GlobalClassCreateEi.ei_ocid = GlobalClassCreateEi.message["data"]["outcomes"]["ei"][0]['id']
            GlobalClassCreateEi.ei_token = GlobalClassCreateEi.message["data"]["outcomes"]["ei"][0]['X-TOKEN']
            actual_ei_release_model_before_updating = requests.get(
                url=f"{GlobalClassCreateEi.message['data']['url']}/"
                    f"{GlobalClassCreateEi.message['data']['ocid']}").json()
        with allure.step('# 3. Authorization platform one: update EI'):
            GlobalClassUpdateEi.cassandra_username = cassandra_username
            GlobalClassUpdateEi.cassandra_password = cassandra_password
            GlobalClassUpdateEi.environment = environment
            GlobalClassUpdateEi.hosts = Environment().choose_environment(GlobalClassUpdateEi.environment)
            GlobalClassUpdateEi.host_for_bpe = GlobalClassUpdateEi.hosts[1]
            GlobalClassUpdateEi.host_for_service = GlobalClassUpdateEi.hosts[2]
            GlobalClassUpdateEi.cassandra_cluster = GlobalClassUpdateEi.hosts[0]
            GlobalClassUpdateEi.access_token = PlatformAuthorization(
                GlobalClassUpdateEi.host_for_bpe).get_access_token_for_platform_one()
            GlobalClassUpdateEi.operation_id = PlatformAuthorization(
                GlobalClassUpdateEi.host_for_bpe).get_x_operation_id(
                GlobalClassUpdateEi.access_token)
        with allure.step('# 4. Send request to update EI'):
            time.sleep(2)
            GlobalClassUpdateEi.payload_for_update_ei = payload.update_ei_full_data_model(
                tender_classification_id=GlobalClassCreateEi.payload_for_create_ei['tender']['classification']['id'],
                quantity_of_tender_item_object=3)
            GlobalClassUpdateEi.send_the_request_update_ei = Requests().update_ei(
                host_of_request=GlobalClassUpdateEi.host_for_bpe,
                access_token=GlobalClassUpdateEi.access_token,
                x_operation_id=GlobalClassUpdateEi.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                ei_token=GlobalClassCreateEi.ei_token,
                payload=GlobalClassUpdateEi.payload_for_update_ei
            )
        with allure.step('# 5. See result'):
            with allure.step('# 5.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=str(202),
                    actual_result=str(GlobalClassUpdateEi.send_the_request_update_ei.status_code)
                )
            with allure.step('# 5.2. Check message in feed point'):
                GlobalClassUpdateEi.message = KafkaMessage(GlobalClassUpdateEi.operation_id).get_message_from_kafka()
                GlobalClassUpdateEi.check_message = KafkaMessage(
                    GlobalClassUpdateEi.operation_id).update_ei_message_is_successful(
                    environment=GlobalClassUpdateEi.environment,
                    kafka_message=GlobalClassUpdateEi.message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid
                )
                allure.attach(str(GlobalClassUpdateEi.message), 'Message in feed point')
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
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(True),
                    actual_result=str(GlobalClassUpdateEi.check_message)
                )
            with allure.step('# 5.3. Check EI release before updating'):
                release = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassCreateEi.environment,
                    language=GlobalClassCreateEi.language
                ))
                expected_ei_release_model = copy.deepcopy(release.ei_release_full_data_model(
                    operation_date=GlobalClassCreateEi.message['data']['operationDate'],
                    release_id=actual_ei_release_model_before_updating['releases'][0]['id'],
                    tender_id=actual_ei_release_model_before_updating['releases'][0]['tender']['id'],
                    ei_id=GlobalClassCreateEi.message['data']['ocid'],
                    payload_for_create_ei=GlobalClassCreateEi.payload_for_create_ei,
                    actual_items_array=actual_ei_release_model_before_updating['releases'][0]['tender']['items']
                ))
                allure.attach(str(json.dumps(actual_ei_release_model_before_updating)),
                              "Actual Ei release before updating")
                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected Ei release")
                compare_releases = DeepDiff(
                    actual_ei_release_model_before_updating,
                    expected_ei_release_model)
                try:
                    if compare_releases == {}:
                        pass
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
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str({}),
                    actual_result=str(compare_releases)
                )
            with allure.step('# 5.4. Check EI release after updating'):
                actual_ei_release_model_after_updating = requests.get(
                    url=f"{GlobalClassUpdateEi.message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_ei_release_model_before_updating)),
                              "Actual Ei release before updating")
                allure.attach(str(json.dumps(actual_ei_release_model_after_updating)),
                              "Actual Ei release after updating")
                expected_items_array = release.ei_tender_items_array_release(
                    actual_items_array=actual_ei_release_model_after_updating['releases'][0]['tender']['items'],
                    payload=GlobalClassUpdateEi.payload_for_update_ei
                )
                if actual_ei_release_model_after_updating['releases'][0]['tender']['items'] == expected_items_array:
                    pass
                else:
                    raise ValueError('Check tender.items array')
                compare_releases = DeepDiff(
                    actual_ei_release_model_before_updating,
                    actual_ei_release_model_after_updating)
                try:
                    if GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0]['classification']['id'] != \
                            GlobalClassUpdateEi.payload_for_update_ei['tender']['items'][0]['classification']['id']:
                        expected_result = {
                            'values_changed': {
                                "root['releases'][0]['id']": {
                                    'new_value':
                                        f"{GlobalClassCreateEi.ei_ocid}-"
                                        f"{actual_ei_release_model_after_updating['releases'][0]['id'][29:42]}",
                                    'old_value':
                                        f"{GlobalClassCreateEi.ei_ocid}-"
                                        f"{actual_ei_release_model_before_updating['releases'][0]['id'][29:42]}"
                                },
                                "root['releases'][0]['date']": {
                                    'new_value': GlobalClassUpdateEi.message['data']['operationDate'],
                                    'old_value': GlobalClassCreateEi.message['data']['operationDate']
                                },
                                "root['releases'][0]['tender']['title']": {
                                    'new_value': GlobalClassUpdateEi.payload_for_update_ei['tender']['title'],
                                    'old_value': GlobalClassCreateEi.payload_for_create_ei['tender']['title']
                                },
                                "root['releases'][0]['tender']['description']": {
                                    'new_value': GlobalClassUpdateEi.payload_for_update_ei['tender']['description'],
                                    'old_value': GlobalClassCreateEi.payload_for_create_ei['tender']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['id']": {
                                    'new_value':
                                        expected_items_array[0]['id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'id']
                                },
                                "root['releases'][0]['tender']['items'][0]['description']": {
                                    'new_value':
                                        expected_items_array[0]['description'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'description']
                                },
                                "root['releases'][0]['tender']['items'][0]['classification']['id']": {
                                    "new_value": expected_items_array[0]['classification']['id'],
                                    "old_value":
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'classification']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['classification']['description']": {
                                    "new_value": expected_items_array[0]['classification']['description'],
                                    "old_value":
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'classification']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]['id']": {
                                    'new_value': expected_items_array[0]['additionalClassifications'][0]['id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'additionalClassifications'][0]['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]["
                                "'description']": {
                                    'new_value': expected_items_array[0]['additionalClassifications'][0]['description'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'additionalClassifications'][0]['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['quantity']": {
                                    'new_value': expected_items_array[0]['quantity'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'quantity']
                                },
                                "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                                    'new_value': expected_items_array[0]['unit']['name'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'unit'][
                                            'name']
                                },
                                "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                                    'new_value': expected_items_array[0]['unit']['id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'unit'][
                                            'id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['streetAddress']": {
                                    'new_value': expected_items_array[0]['deliveryAddress']['streetAddress'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['streetAddress']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['postalCode']": {
                                    'new_value': expected_items_array[0]['deliveryAddress']['postalCode'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['postalCode']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'region']['id']": {
                                    'new_value': expected_items_array[0]['deliveryAddress']['addressDetails']['region'][
                                        'id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'region']['description']": {
                                    'new_value': expected_items_array[0]['deliveryAddress']['addressDetails']['region'][
                                        'description'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'locality']['id']": {
                                    'new_value':
                                        expected_items_array[0]['deliveryAddress']['addressDetails']['locality'][
                                            'id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'locality']['description']": {
                                    'new_value':
                                        expected_items_array[0]['deliveryAddress']['addressDetails']['locality'][
                                            'description'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['description']
                                },
                                "root['releases'][0]['planning']['rationale']": {
                                    'new_value': GlobalClassUpdateEi.payload_for_update_ei['planning']['rationale'],
                                    'old_value': actual_ei_release_model_before_updating['releases'][0]['planning'][
                                        'rationale']
                                }
                            },
                            "iterable_item_added": {
                                "root['releases'][0]['tender']['items'][1]": expected_items_array[1],
                                "root['releases'][0]['tender']['items'][2]": expected_items_array[2]
                            }
                        }
                    elif GlobalClassCreateEi.payload_for_create_ei['tender']['items'][0]['classification']['id'] == \
                            GlobalClassUpdateEi.payload_for_update_ei['tender']['items'][0]['classification']['id']:
                        expected_result = {
                            'values_changed': {
                                "root['releases'][0]['id']": {
                                    'new_value':
                                        f"{GlobalClassCreateEi.ei_ocid}-"
                                        f"{actual_ei_release_model_after_updating['releases'][0]['id'][29:42]}",
                                    'old_value':
                                        f"{GlobalClassCreateEi.ei_ocid}-"
                                        f"{actual_ei_release_model_before_updating['releases'][0]['id'][29:42]}"
                                },
                                "root['releases'][0]['date']": {
                                    'new_value': GlobalClassUpdateEi.message['data']['operationDate'],
                                    'old_value': GlobalClassCreateEi.message['data']['operationDate']
                                },
                                "root['releases'][0]['tender']['title']": {
                                    'new_value': GlobalClassUpdateEi.payload_for_update_ei['tender']['title'],
                                    'old_value': GlobalClassCreateEi.payload_for_create_ei['tender']['title']
                                },
                                "root['releases'][0]['tender']['description']": {
                                    'new_value': GlobalClassUpdateEi.payload_for_update_ei['tender']['description'],
                                    'old_value': GlobalClassCreateEi.payload_for_create_ei['tender']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['id']": {
                                    'new_value':
                                        expected_items_array[0]['id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'id']
                                },
                                "root['releases'][0]['tender']['items'][0]['description']": {
                                    'new_value':
                                        expected_items_array[0]['description'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'description']
                                },
                                "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]['id']": {
                                    'new_value': expected_items_array[0]['additionalClassifications'][0]['id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'additionalClassifications'][0]['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]["
                                "'description']": {
                                    'new_value': expected_items_array[0]['additionalClassifications'][0]['description'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'additionalClassifications'][0]['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['quantity']": {
                                    'new_value': expected_items_array[0]['quantity'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'quantity']
                                },
                                "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                                    'new_value': expected_items_array[0]['unit']['name'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'unit'][
                                            'name']
                                },
                                "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                                    'new_value': expected_items_array[0]['unit']['id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'unit'][
                                            'id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['streetAddress']": {
                                    'new_value': expected_items_array[0]['deliveryAddress']['streetAddress'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['streetAddress']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['postalCode']": {
                                    'new_value': expected_items_array[0]['deliveryAddress']['postalCode'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['postalCode']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'region']['id']": {
                                    'new_value': expected_items_array[0]['deliveryAddress']['addressDetails']['region'][
                                        'id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'region']['description']": {
                                    'new_value': expected_items_array[0]['deliveryAddress']['addressDetails']['region'][
                                        'description'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'locality']['id']": {
                                    'new_value':
                                        expected_items_array[0]['deliveryAddress']['addressDetails']['locality'][
                                            'id'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'locality']['description']": {
                                    'new_value':
                                        expected_items_array[0]['deliveryAddress']['addressDetails']['locality'][
                                            'description'],
                                    'old_value':
                                        actual_ei_release_model_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['description']
                                },
                                "root['releases'][0]['planning']['rationale']": {
                                    'new_value': GlobalClassUpdateEi.payload_for_update_ei['planning']['rationale'],
                                    'old_value': actual_ei_release_model_before_updating['releases'][0]['planning'][
                                        'rationale']
                                }
                            },
                            'iterable_item_added': {
                                "root['releases'][0]['tender']['items'][1]": expected_items_array[1],
                                "root['releases'][0]['tender']['items'][2]": expected_items_array[2]
                            }
                        }
                except ValueError:
                    raise ValueError("Check your payloads")
                try:
                    if compare_releases == expected_result:
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
                        database = CassandraSession(
                            cassandra_username=GlobalClassUpdateEi.cassandra_username,
                            cassandra_password=GlobalClassUpdateEi.cassandra_password,
                            cassandra_cluster=GlobalClassUpdateEi.cassandra_cluster
                        )
                        database.create_ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassUpdateEi.message['data']['ocid']
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassUpdateEi.operation_id
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
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=str(expected_result),
                    actual_result=str(compare_releases)
                )
