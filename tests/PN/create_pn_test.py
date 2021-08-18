import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn

from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.expected_release import ExpectedRelease
from tests.utils.functions import compare_actual_result_and_expected_result
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.prepared_payload import PreparePayload
from tests.utils.requests import Requests


@allure.parent_suite('Planning')
@allure.suite('PN')
@allure.sub_suite('BPE: Create PN')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=726248592',
                 name='Google sheets: Create PN')
class TestCreatePn:
    def test_setup(self, environment, country, language, pmd, cassandra_username, cassandra_password):
        """
        Get 'country', 'language', 'cassandra_username', 'cassandra_password', 'environment' parameters
        from test run command.
        Then choose BPE host.
        Then choose host for Database connection.
        """
        GlobalClassMetadata.country = country
        GlobalClassMetadata.language = language
        GlobalClassMetadata.pmd = pmd
        GlobalClassMetadata.cassandra_username = cassandra_username
        GlobalClassMetadata.cassandra_password = cassandra_password
        GlobalClassMetadata.environment = environment
        GlobalClassMetadata.hosts = Environment().choose_environment(GlobalClassMetadata.environment)
        GlobalClassMetadata.host_for_bpe = GlobalClassMetadata.hosts[1]
        GlobalClassMetadata.cassandra_cluster = GlobalClassMetadata.hosts[0]

    @allure.title('Check status code and message from Kafka topic after PN creating')
    def test_check_result_of_sending_the_request(self):
        with allure.step('# 1. Authorization platform one: create EI'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
        with allure.step('# 2. Send request to create EI'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            payload = copy.deepcopy(PreparePayload())
            GlobalClassCreateEi.payload = payload.create_ei_obligatory_data_model()
            Requests().create_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                payload=GlobalClassCreateEi.payload
            )

        with allure.step('# 3. Authorization platform one: create FS'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)

        with allure.step('# 4. Send request to create FS'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_obligatory_data_model_treasury_money()
            Requests().create_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload
            )

        with allure.step('# 5. Authorization platform one: create PN'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)

        with allure.step('# 6. Send request to create PN'):
            """
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassCreatePn.payload = \
                payload.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            synchronous_result_of_sending_the_request = Requests().create_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreatePn.access_token,
                x_operation_id=GlobalClassCreatePn.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                pmd=GlobalClassMetadata.pmd,
                payload=GlobalClassCreatePn.payload
            )
            GlobalClassCreatePn.feed_point_message = \
                KafkaMessage(GlobalClassCreatePn.operation_id).get_message_from_kafka()

            GlobalClassCreatePn.pn_ocid = \
                GlobalClassCreatePn.feed_point_message['data']['ocid']

        with allure.step('# 7. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 7.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 7.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                allure.attach(str(GlobalClassCreatePn.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreatePn.operation_id).create_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreatePn.feed_point_message
                )
                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is True:
                        database.ei_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.fs_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.pn_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateFs.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreatePn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check PN and MS releases data after PN creating without optional fields')
    def test_check_pn_ms_releases_one(self):
        with allure.step('# 1. Authorization platform one: create EI'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)

        with allure.step('# 2. Send request to create EI'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            payload = copy.deepcopy(PreparePayload())
            GlobalClassCreateEi.payload = payload.create_ei_obligatory_data_model()
            Requests().create_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                payload=GlobalClassCreateEi.payload
            )
            GlobalClassCreateEi.feed_point_message = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()

            GlobalClassCreateEi.ei_ocid = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

            GlobalClassCreateEi.actual_ei_release = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()
        with allure.step('# 3. Authorization platform one: create FS'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)

        with allure.step('# 4. Send request to create FS'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_obligatory_data_model_treasury_money()
            Requests().create_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload
            )

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']

            GlobalClassCreateFs.actual_fs_release = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: create PN'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)

        with allure.step('# 6. Send request to create PN'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            And save in variable pn_ocid, pn_id.
            """
            time.sleep(1)
            GlobalClassCreatePn.payload = \
                payload.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            synchronous_result_of_sending_the_request = Requests().create_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreatePn.access_token,
                x_operation_id=GlobalClassCreatePn.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                pmd=GlobalClassMetadata.pmd,
                payload=GlobalClassCreatePn.payload
            )
            GlobalClassCreatePn.feed_point_message = \
                KafkaMessage(GlobalClassCreatePn.operation_id).get_message_from_kafka()

            GlobalClassCreatePn.pn_ocid = \
                GlobalClassCreatePn.feed_point_message['data']['ocid']

            GlobalClassCreatePn.pn_id = \
                GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['id']

            GlobalClassCreatePn.actual_pn_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()

            GlobalClassCreatePn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

        with allure.step('# 7. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 7.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 7.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                allure.attach(str(GlobalClassCreatePn.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreatePn.operation_id).create_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreatePn.feed_point_message
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 7.3. Check PN release'):
                """
                Compare actual planning notice release with expected planning notice release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreatePn.actual_pn_release)), "Actual PN release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_pn_release_model = copy.deepcopy(
                    expected_release_class.pn_release_obligatory_data_model_without_lots_and_items_based_on_one_fs(
                        operation_date=GlobalClassCreatePn.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreatePn.feed_point_message['data']['operationDate']
                    ))
                allure.attach(str(json.dumps(expected_pn_release_model)), "Expected PN release")

                compare_releases = dict(DeepDiff(GlobalClassCreatePn.actual_pn_release, expected_pn_release_model))
                expected_result = {}
                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            database = CassandraSession(
                                cassandra_username=GlobalClassMetadata.cassandra_username,
                                cassandra_password=GlobalClassMetadata.cassandra_password,
                                cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreatePn.actual_ms_release)), "Actual MS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ms_release_model = copy.deepcopy(
                    expected_release_class.ms_release_obligatory_data_model_with_three_parties_object(
                        operation_date=GlobalClassCreatePn.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreatePn.feed_point_message['data']['operationDate']
                    ))

                allure.attach(str(json.dumps(expected_pn_release_model)), "Expected MS release")

                compare_releases = dict(DeepDiff(GlobalClassCreatePn.actual_ms_release, expected_ms_release_model))

                expected_result = {}
                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            database = CassandraSession(
                                cassandra_username=GlobalClassMetadata.cassandra_username,
                                cassandra_password=GlobalClassMetadata.cassandra_password,
                                cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if compare_releases == expected_result:
                        database.ei_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.fs_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateFs.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreatePn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check PN and MS releases data after PN creating without optional fields '
                  'and with lots and items (without optional fields).')
    def test_check_pn_ms_releases_two(self):
        with allure.step('# 1. Authorization platform one: create EI'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)

        with allure.step('# 2. Send request to create EI'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            payload = copy.deepcopy(PreparePayload())
            GlobalClassCreateEi.payload = payload.create_ei_full_data_model()
            Requests().create_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                payload=GlobalClassCreateEi.payload
            )
            GlobalClassCreateEi.feed_point_message = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()

            GlobalClassCreateEi.ei_ocid = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

            GlobalClassCreateEi.actual_ei_release = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()
        with allure.step('# 3. Authorization platform one: create FS'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)

        with allure.step('# 4. Send request to create FS'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_full_data_model_own_money()
            Requests().create_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload
            )

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']

            GlobalClassCreateFs.actual_fs_release = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: create PN'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)

        with allure.step('# 6. Send request to create PN'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            And save in variable pn_ocid, pn_id.
            """
            time.sleep(1)
            GlobalClassCreatePn.payload = \
                payload.create_pn_obligatory_data_model_with_one_lots_and_items_based_on_one_fs()

            synchronous_result_of_sending_the_request = Requests().create_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreatePn.access_token,
                x_operation_id=GlobalClassCreatePn.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                pmd=GlobalClassMetadata.pmd,
                payload=GlobalClassCreatePn.payload
            )

            GlobalClassCreatePn.feed_point_message = \
                KafkaMessage(GlobalClassCreatePn.operation_id).get_message_from_kafka()

            GlobalClassCreatePn.pn_ocid = \
                GlobalClassCreatePn.feed_point_message['data']['ocid']

            GlobalClassCreatePn.pn_id = \
                GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['id']

            GlobalClassCreatePn.actual_pn_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()

            GlobalClassCreatePn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

        with allure.step('# 7. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 7.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 7.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                allure.attach(str(GlobalClassCreatePn.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreatePn.operation_id).create_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreatePn.feed_point_message
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 7.3. Check PN release'):
                """
                Compare actual planning notice release with expected planning notice release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreatePn.actual_pn_release)), "Actual PN release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_pn_release_model = copy.deepcopy(
                    expected_release_class.pn_release_obligatory_data_model_with_lots_and_items_based_on_one_fs(
                        operation_date=GlobalClassCreatePn.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreatePn.feed_point_message['data']['operationDate']
                    ))
                allure.attach(str(json.dumps(expected_pn_release_model)), "Expected PN release")

                compare_releases = dict(DeepDiff(GlobalClassCreatePn.actual_pn_release, expected_pn_release_model))
                expected_result = {}
                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            database = CassandraSession(
                                cassandra_username=GlobalClassMetadata.cassandra_username,
                                cassandra_password=GlobalClassMetadata.cassandra_password,
                                cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreatePn.actual_ms_release)), "Actual MS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ms_release_model = copy.deepcopy(
                    expected_release_class.ms_release_obligatory_data_model_with_three_parties_object(
                        operation_date=GlobalClassCreatePn.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreatePn.feed_point_message['data']['operationDate']
                    ))

                allure.attach(str(json.dumps(expected_pn_release_model)), "Expected MS release")

                compare_releases = dict(DeepDiff(GlobalClassCreatePn.actual_ms_release, expected_ms_release_model))

                expected_result = {}
                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            database = CassandraSession(
                                cassandra_username=GlobalClassMetadata.cassandra_username,
                                cassandra_password=GlobalClassMetadata.cassandra_password,
                                cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")
                print()
                print(json.dumps(GlobalClassCreatePn.actual_ms_release))
                print(json.dumps(expected_ms_release_model))
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if compare_releases == expected_result:
                        database.ei_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.fs_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateFs.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreatePn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)