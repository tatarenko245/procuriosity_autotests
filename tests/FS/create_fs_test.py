# файл з самим тестом
import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassMetadata
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.expected_release import ExpectedRelease
from tests.utils.functions import compare_actual_result_and_expected_result
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.prepared_payload import PreparePayload
from tests.utils.requests import Requests


@allure.parent_suite('Budgets')
@allure.suite('FS')
@allure.sub_suite('BPE: Create FS')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=1455075741',
                 name='Google sheets: Create FS')
class TestCreateFs:
    @allure.title('Check status code and message from Kafka topic after FS creation')
    def test_check_status_code_and_message_from_kafka_topic_after_fs_creation(self, environment, country, language,
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
        with allure.step('# 3. Authorization: create FS'):
            GlobalClassCreateFs.language = language
            GlobalClassCreateFs.cassandra_username = cassandra_username
            GlobalClassCreateFs.cassandra_password = cassandra_password
            GlobalClassCreateFs.environment = environment
            GlobalClassCreateFs.hosts = Environment().choose_environment(GlobalClassCreateFs.environment)
            GlobalClassCreateFs.host_for_bpe = GlobalClassCreateFs.hosts[1]
            GlobalClassCreateFs.host_for_service = GlobalClassCreateFs.hosts[2]
            GlobalClassCreateFs.cassandra_cluster = GlobalClassCreateFs.hosts[0]
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassCreateFs.host_for_bpe).get_access_token_for_platform_one()
            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassCreateFs.host_for_bpe).get_x_operation_id(
                GlobalClassCreateFs.access_token)
        with allure.step('# 4. Send request to create FS'):
            GlobalClassCreateFs.payload_for_create_fs = payload.create_fs_full_data_model_own_money()
            GlobalClassCreateFs.send_the_request_create_fs = Requests().create_fs(
                host_of_request=GlobalClassCreateFs.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload_for_create_fs
            )

        with allure.step('# 5. See result'):
            with allure.step('# 5.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=GlobalClassCreateFs.send_the_request_create_fs.status_code
                )
            with allure.step('# 5.2. Check message in feed point'):
                GlobalClassCreateFs.message = KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()
                GlobalClassCreateFs.check_message = KafkaMessage(
                    GlobalClassCreateFs.operation_id).create_fs_message_is_successful(
                    environment=GlobalClassCreateFs.environment,
                    kafka_message=GlobalClassCreateFs.message
                )
                allure.attach(str(GlobalClassCreateFs.message), 'Message in feed point')
                try:
                    if GlobalClassCreateFs.check_message is True:
                        database = CassandraSession(
                            cassandra_username=GlobalClassCreateFs.cassandra_username,
                            cassandra_password=GlobalClassCreateFs.cassandra_password,
                            cassandra_cluster=GlobalClassCreateFs.cassandra_cluster
                        )
                        database.create_ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id
                        )
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassCreateFs.cassandra_username,
                                cassandra_password=GlobalClassCreateFs.cassandra_password,
                                cassandra_cluster=GlobalClassCreateFs.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Check the message in kafka topic")
                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=GlobalClassCreateFs.check_message
                )

    @allure.title('Check FS release data after FS creation:'
                  'ei -> model without optional fields '
                  'and fs -> full data model own money')
    def test_check_fs_release_data_after_fs_creation_ei_model_without_optional_fields_and_fs_full_data_model_own(
            self, environment, country, language, cassandra_username, cassandra_password):
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
            GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
            GlobalClassCreateEi.ei_ocid = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()["data"]["outcomes"]["ei"][0][
                    'id']
        with allure.step('# 3. Authorization: create FS'):
            GlobalClassCreateFs.language = language
            GlobalClassCreateFs.cassandra_username = cassandra_username
            GlobalClassCreateFs.cassandra_password = cassandra_password
            GlobalClassCreateFs.environment = environment
            GlobalClassCreateFs.hosts = Environment().choose_environment(GlobalClassCreateFs.environment)
            GlobalClassCreateFs.host_for_bpe = GlobalClassCreateFs.hosts[1]
            GlobalClassCreateFs.host_for_service = GlobalClassCreateFs.hosts[2]
            GlobalClassCreateFs.cassandra_cluster = GlobalClassCreateFs.hosts[0]
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassCreateFs.host_for_bpe).get_access_token_for_platform_one()
            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassCreateFs.host_for_bpe).get_x_operation_id(
                GlobalClassCreateFs.access_token)
        with allure.step('# 4. Send request to create FS'):
            time.sleep(2)
            GlobalClassCreateFs.payload_for_create_fs = payload.create_fs_full_data_model_own_money()
            GlobalClassCreateFs.send_the_request_create_fs = Requests().create_fs(
                host_of_request=GlobalClassCreateFs.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload_for_create_fs
            )
        with allure.step('# 5. See result'):
            with allure.step('# 5.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=GlobalClassCreateFs.send_the_request_create_fs.status_code
                )
            with allure.step('# 5.2. Check message in feed point'):
                GlobalClassCreateFs.message = KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()
                GlobalClassCreateFs.check_message = KafkaMessage(
                    GlobalClassCreateFs.operation_id).create_fs_message_is_successful(
                    environment=GlobalClassCreateFs.environment,
                    kafka_message=GlobalClassCreateFs.message
                )
                allure.attach(str(GlobalClassCreateFs.message), 'Message in feed point')
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
                    expected_result=True,
                    actual_result=GlobalClassCreateFs.check_message
                )
            with allure.step('# 5.3. Check FS release'):
                release = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassCreateFs.environment,
                    language=GlobalClassCreateFs.language
                ))
                actual_fs_release = requests.get(
                    url=f"{GlobalClassCreateFs.message['data']['url']}/"
                        f"{GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id']}").json()
                allure.attach(str(json.dumps(actual_fs_release)),
                              "Actual FS release")
                expected_fs_release = copy.deepcopy(
                    release.fs_release_full_data_model_own_money_payer_id_is_not_equal_funder_id(
                        operation_date=GlobalClassCreateFs.message['data']['operationDate'],
                        release_id=actual_fs_release['releases'][0]['id'],
                        tender_id=actual_fs_release['releases'][0]['tender']['id'],
                        related_processes_id=actual_fs_release['releases'][0]['relatedProcesses'][0]['id'],
                        ei_id=GlobalClassCreateEi.message['data']['ocid'],
                        fs_id=GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id'],
                        payload_for_create_fs=GlobalClassCreateFs.payload_for_create_fs
                    ))
                allure.attach(str(json.dumps(expected_fs_release)),
                              "Expected FS release")
                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release))

                expected_result = {}
                try:
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassCreateFs.cassandra_username,
                                cassandra_password=GlobalClassCreateFs.cassandra_password,
                                cassandra_cluster=GlobalClassCreateFs.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Check the message in kafka topic")
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 5.4. Check EI release'):
                actual_ei_release = requests.get(
                    url=f"{GlobalClassCreateEi.message['data']['url']}/"
                        f"{GlobalClassCreateEi.message['data']['ocid']}").json()
                release = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassCreateEi.environment,
                    language=GlobalClassCreateEi.language
                ))
                expected_ei_release_model = copy.deepcopy(release.ei_release_obligatory_data_model(
                    operation_date=GlobalClassCreateEi.message['data']['operationDate'],
                    release_id=actual_ei_release['releases'][0]['id'],
                    tender_id=actual_ei_release['releases'][0]['tender']['id'],
                    ei_id=GlobalClassCreateEi.message['data']['ocid'],
                    payload_for_create_ei=GlobalClassCreateEi.payload_for_create_ei
                ))
                allure.attach(str(json.dumps(actual_ei_release)),
                              "Actual Ei release")
                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected Ei release")
                compare_releases = DeepDiff(
                    expected_ei_release_model,
                    actual_ei_release
                )
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)
                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassCreateFs.message['data']['operationDate'],
                            'old_value': GlobalClassCreateEi.message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes = [{
                    "id": actual_ei_release['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id'],
                    "uri": f"{GlobalClassMetadata.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/"
                           f"{GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id']}"
                }]

                expected_budget_amount = {
                    "amount": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['amount']['amount'],
                    "currency": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['amount']['currency']
                }
                try:
                    if compare_releases == expected_result:
                        database = CassandraSession(
                            cassandra_username=GlobalClassCreateFs.cassandra_username,
                            cassandra_password=GlobalClassCreateFs.cassandra_password,
                            cassandra_cluster=GlobalClassCreateFs.cassandra_cluster
                        )
                        database.create_ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateFs.message['data']['ocid']
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id
                        )
                        database = CassandraSession(
                            cassandra_username=GlobalClassCreateFs.cassandra_username,
                            cassandra_password=GlobalClassCreateFs.cassandra_password,
                            cassandra_cluster=GlobalClassCreateFs.cassandra_cluster
                        )
                        database.create_ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.message['data']['ocid']
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id
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
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_related_processes,
                    actual_result=actual_ei_release['releases'][0]['relatedProcesses']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_budget_amount,
                    actual_result=actual_ei_release['releases'][0]['planning']['budget']['amount']
                )) == str(True)

    @allure.title('Check FS release data after FS creation:'
                  'ei -> full data model and '
                  'fs -> full data model treasury money')
    def test_check_fs_release_data_after_fs_creation_ei_full_data_model_and_fs_full_data_model_treasury(
            self, environment, country, language, cassandra_username, cassandra_password):
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
            GlobalClassCreateEi.ei_ocid = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()["data"]["outcomes"]["ei"][0][
                    'id']
            actual_ei_release = requests.get(
                url=f"{GlobalClassCreateEi.message['data']['url']}/"
                    f"{GlobalClassCreateEi.message['data']['ocid']}").json()
        with allure.step('# 3. Authorization: create FS'):
            GlobalClassCreateFs.language = language
            GlobalClassCreateFs.cassandra_username = cassandra_username
            GlobalClassCreateFs.cassandra_password = cassandra_password
            GlobalClassCreateFs.environment = environment
            GlobalClassCreateFs.hosts = Environment().choose_environment(GlobalClassCreateFs.environment)
            GlobalClassCreateFs.host_for_bpe = GlobalClassCreateFs.hosts[1]
            GlobalClassCreateFs.host_for_service = GlobalClassCreateFs.hosts[2]
            GlobalClassCreateFs.cassandra_cluster = GlobalClassCreateFs.hosts[0]
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassCreateFs.host_for_bpe).get_access_token_for_platform_one()
            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassCreateFs.host_for_bpe).get_x_operation_id(
                GlobalClassCreateFs.access_token)
        with allure.step('# 4. Send request to create FS'):
            time.sleep(2)
            GlobalClassCreateFs.payload_for_create_fs = payload.create_fs_full_data_model_treasury_money()
            GlobalClassCreateFs.send_the_request_create_fs = Requests().create_fs(
                host_of_request=GlobalClassCreateFs.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload_for_create_fs
            )
        with allure.step('# 5. See result'):
            with allure.step('# 5.1. Check status code'):
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=GlobalClassCreateFs.send_the_request_create_fs.status_code
                )
            with allure.step('# 5.2. Check message in feed point'):
                GlobalClassCreateFs.message = KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()
                GlobalClassCreateFs.check_message = KafkaMessage(
                    GlobalClassCreateFs.operation_id).create_fs_message_is_successful(
                    environment=GlobalClassCreateFs.environment,
                    kafka_message=GlobalClassCreateFs.message
                )
                allure.attach(str(GlobalClassCreateFs.message), 'Message in feed point')
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
                    expected_result=True,
                    actual_result=GlobalClassCreateFs.check_message
                )
            with allure.step('# 5.3. Check FS release'):
                release = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassCreateFs.environment,
                    language=GlobalClassCreateFs.language
                ))
                actual_fs_release = requests.get(
                    url=f"{GlobalClassCreateFs.message['data']['url']}/"
                        f"{GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id']}").json()
                allure.attach(str(json.dumps(actual_fs_release)),
                              "Actual FS release")
                expected_fs_release = copy.deepcopy(
                    release.fs_release_full_data_model_treasury_money(
                        operation_date=GlobalClassCreateFs.message['data']['operationDate'],
                        release_id=actual_fs_release['releases'][0]['id'],
                        tender_id=actual_fs_release['releases'][0]['tender']['id'],
                        related_processes_id=actual_fs_release['releases'][0]['relatedProcesses'][0]['id'],
                        ei_id=GlobalClassCreateEi.message['data']['ocid'],
                        fs_id=GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id'],
                        payload_for_create_fs=GlobalClassCreateFs.payload_for_create_fs,
                        buyer_section=actual_ei_release['releases'][0]['buyer']
                    ))
                allure.attach(str(json.dumps(expected_fs_release)),
                              "Expected FS release")
                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release))
                expected_result = {}
                try:
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = CassandraSession(
                                cassandra_username=GlobalClassCreateFs.cassandra_username,
                                cassandra_password=GlobalClassCreateFs.cassandra_password,
                                cassandra_cluster=GlobalClassCreateFs.cassandra_cluster
                            ).get_orchestrator_operation_step_by_x_operation_id(
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Check the message in kafka topic")
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 5.4. Check EI release'):
                actual_ei_release = requests.get(
                    url=f"{GlobalClassCreateEi.message['data']['url']}/"
                        f"{GlobalClassCreateEi.message['data']['ocid']}").json()
                release = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassCreateEi.environment,
                    language=GlobalClassCreateEi.language
                ))
                expected_ei_release_model = copy.deepcopy(release.ei_release_full_data_model(
                    operation_date=GlobalClassCreateEi.message['data']['operationDate'],
                    release_id=actual_ei_release['releases'][0]['id'],
                    tender_id=actual_ei_release['releases'][0]['tender']['id'],
                    ei_id=GlobalClassCreateEi.message['data']['ocid'],
                    payload_for_create_ei=GlobalClassCreateEi.payload_for_create_ei,
                    actual_items_array=actual_ei_release['releases'][0]['tender']['items']
                ))
                allure.attach(str(json.dumps(actual_ei_release)), "Actual Ei release")
                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected Ei release")
                compare_releases = DeepDiff(
                    expected_ei_release_model,
                    actual_ei_release
                )
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)
                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassCreateFs.message['data']['operationDate'],
                            'old_value': GlobalClassCreateEi.message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes = [{
                    "id": actual_ei_release['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id'],
                    "uri": f"{GlobalClassMetadata.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/"
                           f"{GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id']}"
                }]

                expected_budget_amount = {
                    "amount": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['amount']['amount'],
                    "currency": GlobalClassCreateFs.payload_for_create_fs['planning']['budget']['amount']['currency']
                }
                try:
                    if compare_releases == expected_result:
                        database = CassandraSession(
                            cassandra_username=GlobalClassCreateFs.cassandra_username,
                            cassandra_password=GlobalClassCreateFs.cassandra_password,
                            cassandra_cluster=GlobalClassCreateFs.cassandra_cluster
                        )
                        database.create_ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateFs.message['data']['ocid']
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id
                        )
                        database = CassandraSession(
                            cassandra_username=GlobalClassCreateFs.cassandra_username,
                            cassandra_password=GlobalClassCreateFs.cassandra_password,
                            cassandra_cluster=GlobalClassCreateFs.cassandra_cluster
                        )
                        database.create_ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.message['data']['ocid']
                        )
                        database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id
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
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_related_processes,
                    actual_result=actual_ei_release['releases'][0]['relatedProcesses']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_budget_amount,
                    actual_result=actual_ei_release['releases'][0]['planning']['budget']['amount']
                )) == str(True)
