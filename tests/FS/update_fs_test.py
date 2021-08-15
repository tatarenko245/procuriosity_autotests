# файл з самим тестом
import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassMetadata, GlobalClassUpdateFs
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
@allure.sub_suite('BPE: Update FS')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=344712387',
                 name='Google sheets: Update FS')
class TestUpdateFs:
    def test_setup(self, environment, country, language, cassandra_username, cassandra_password):
        """
        Get 'country', 'language', 'cassandra_username', 'cassandra_password', 'environment' parameters
        from test run command.
        Then choose BPE host.
        Then choose host for Database connection.
        """
        GlobalClassMetadata.country = country
        GlobalClassMetadata.language = language
        GlobalClassMetadata.cassandra_username = cassandra_username
        GlobalClassMetadata.cassandra_password = cassandra_password
        GlobalClassMetadata.environment = environment
        GlobalClassMetadata.hosts = Environment().choose_environment(GlobalClassMetadata.environment)
        GlobalClassMetadata.host_for_bpe = GlobalClassMetadata.hosts[1]
        GlobalClassMetadata.cassandra_cluster = GlobalClassMetadata.hosts[0]

    @allure.title('Check status code and message from Kafka topic after FS updating')
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
            GlobalClassCreateEi.feed_point_message = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()

            GlobalClassCreateEi.ei_ocid = GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']
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
            And save in variable fs_id and fs_token.
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

            GlobalClassCreateFs.fs_id = GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)
        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_obligatory_data_model_treasury_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()
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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
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
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateFs.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload without optional fields treasury money,'
                  'update fs: payload without optional fields treasury money ')
    def test_check_fs_release_one(self):
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
            And save in variable fs_id and fs_token.
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
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()
        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)
        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_obligatory_data_model_treasury_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()
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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_treasury_money(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id,
                        ei_buyer_id=f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
                                    f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}",
                        ei_buyer_name=GlobalClassCreateEi.payload['buyer']['name']))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating))
                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.fs_id}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.fs_id}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }
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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(actual_ei_release_after_fs_creating,
                                            actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }
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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload full data model treasury money, '
                  'update fs: payload full data model treasury money ')
    def test_check_fs_release_two(self):
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_full_data_model_treasury_money()
            Requests().create_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload
            )
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_full_data_model_treasury_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, 
                        then return process steps by operation-id.
                        """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_full_data_model_treasury_money(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id,
                        ei_buyer_id=f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
                                    f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}",
                        ei_buyer_name=GlobalClassCreateEi.payload['buyer']['name']))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                    Compare actual second financial source release after updating with
                    first financial source release before updating.
                    """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating))
                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.fs_id}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.fs_id}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['id']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['budget']['id'],
                            "old_value": GlobalClassCreateFs.payload['planning']['budget']['id']
                        },
                        "root['releases'][0]['planning']['budget']['description']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['budget']['description'],
                            "old_value": GlobalClassCreateFs.payload['planning']['budget']['description']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['projectIdentifier']": {
                            "new_value":
                                GlobalClassUpdateFs.payload['planning']['budget']['europeanUnionFunding'][
                                    'projectIdentifier'],
                            "old_value":
                                GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding'][
                                    'projectIdentifier']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['projectName']": {
                            "new_value":
                                GlobalClassUpdateFs.payload['planning']['budget']['europeanUnionFunding'][
                                    'projectName'],
                            "old_value":
                                GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding'][
                                    'projectName']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['uri']": {
                            "new_value":
                                GlobalClassUpdateFs.payload['planning']['budget']['europeanUnionFunding'][
                                    'uri'],
                            "old_value":
                                GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding'][
                                    'uri']
                        },
                        "root['releases'][0]['planning']['budget']['project']": {
                            "new_value":
                                GlobalClassUpdateFs.payload['planning']['budget']['project'],
                            "old_value":
                                GlobalClassCreateFs.payload['planning']['budget']['project']
                        },
                        "root['releases'][0]['planning']['budget']['projectID']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['budget']['projectID'],
                            "old_value": GlobalClassCreateFs.payload['planning']['budget']['projectID']
                        },
                        "root['releases'][0]['planning']['budget']['uri']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['budget']['uri'],
                            "old_value": GlobalClassCreateFs.payload['planning']['budget']['uri']
                        },
                        "root['releases'][0]['planning']['rationale']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['rationale'],
                            "old_value": GlobalClassCreateFs.payload['planning']['rationale']
                        }
                    }
                }
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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating,
                    actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }
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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload without optional fields treasury money, '
                  'update fs: payload full data model treasury money ')
    def test_check_fs_release_three(self):
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
            And save in variable fs_id and fs_token.
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
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_full_data_model_treasury_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_treasury_money(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id,
                        ei_buyer_id=f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
                                    f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}",
                        ei_buyer_name=GlobalClassCreateEi.payload['buyer']['name']))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added':
                        "['releases'][0]['planning']['rationale'], "
                        "['releases'][0]['planning']['budget']['id'], "
                        "['releases'][0]['planning']['budget']['description'], "
                        "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                        "['releases'][0]['planning']['budget']['project'], "
                        "['releases'][0]['planning']['budget']['projectID'], "
                        "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': True,
                            'old_value': False
                        }
                    }
                }

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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['rationale'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['rationale']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['id'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['id']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['description'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['description']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget'][
                        'europeanUnionFunding'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget'][
                        'europeanUnionFunding']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['project'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['project']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['projectID'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['projectID']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['uri'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['uri']
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating, actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }

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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload full data model treasury money, '
                  'update fs: payload without optional fields treasury money')
    def test_check_fs_release_four(self):
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_full_data_model_treasury_money()
            Requests().create_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload
            )
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
        GlobalClassUpdateFs.access_token = PlatformAuthorization(
            GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

        GlobalClassUpdateFs.operation_id = PlatformAuthorization(
            GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_obligatory_data_model_treasury_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                            If asynchronous_result_of_sending_the_request was False, 
                            then return process steps by operation-id.
                            """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_full_data_model_treasury_money(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id,
                        ei_buyer_id=f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
                                    f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}",
                        ei_buyer_name=GlobalClassCreateEi.payload['buyer']['name']))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating)
                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_removed': "['releases'][0]['planning']['rationale'], "
                                               "['releases'][0]['planning']['budget']['id'], "
                                               "['releases'][0]['planning']['budget']['description'], "
                                               "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                               "['releases'][0]['planning']['budget']['project'], "
                                               "['releases'][0]['planning']['budget']['projectID'], "
                                               "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': False,
                            'old_value': True
                        }
                    }
                }

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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating, actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }

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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload without optional fields own money,'
                  'update fs: payload without optional fields own money ')
    def test_check_fs_release_five(self):
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_obligatory_data_model_own_money()
            Requests().create_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload
            )
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_obligatory_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_own_money_payer_id_is_not_equal_funder_id(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }

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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating, actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }

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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload full data model own money, '
                  'update fs: payload full data model own money ')
    def test_check_fs_release_six(self):
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
            And save in variable fs_id and fs_token.
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
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_full_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_full_data_model_own_money_payer_id_is_not_equal_funder_id(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['description']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['budget']['description'],
                            "old_value": GlobalClassCreateFs.payload['planning']['budget']['description']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['projectIdentifier']": {
                            "new_value":
                                GlobalClassUpdateFs.payload['planning']['budget'][
                                    'europeanUnionFunding']['projectIdentifier'],
                            "old_value":
                                GlobalClassCreateFs.payload['planning']['budget'][
                                    'europeanUnionFunding']['projectIdentifier']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['projectName']": {
                            "new_value":
                                GlobalClassUpdateFs.payload['planning']['budget']['europeanUnionFunding'][
                                    'projectName'],
                            "old_value":
                                GlobalClassCreateFs.payload['planning']['budget'][
                                    'europeanUnionFunding']['projectName']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['uri']": {
                            "new_value":
                                GlobalClassUpdateFs.payload['planning']['budget']['europeanUnionFunding']['uri'],
                            "old_value":
                                GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding']['uri']
                        },
                        "root['releases'][0]['planning']['budget']['project']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['budget']['project'],
                            "old_value": GlobalClassCreateFs.payload['planning']['budget']['project']
                        },
                        "root['releases'][0]['planning']['budget']['projectID']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['budget']['projectID'],
                            "old_value": GlobalClassCreateFs.payload['planning']['budget']['projectID']
                        },
                        "root['releases'][0]['planning']['budget']['uri']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['budget']['uri'],
                            "old_value": GlobalClassCreateFs.payload['planning']['budget']['uri']
                        },
                        "root['releases'][0]['planning']['rationale']": {
                            "new_value": GlobalClassUpdateFs.payload['planning']['rationale'],
                            "old_value": GlobalClassCreateFs.payload['planning']['rationale']
                        }
                    }
                }

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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating, actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }

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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload without optional fields own money, '
                  'update fs: payload full data model own money ')
    def test_check_fs_release_seven(self):
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_obligatory_data_model_own_money()
            Requests().create_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload
            )
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_full_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_own_money_payer_id_is_not_equal_funder_id(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['planning']['rationale'], "
                                             "['releases'][0]['planning']['budget']['description'], "
                                             "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                             "['releases'][0]['planning']['budget']['project'], "
                                             "['releases'][0]['planning']['budget']['projectID'], "
                                             "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': GlobalClassUpdateFs.payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': GlobalClassCreateFs.payload['planning']['budget']['isEuropeanUnionFunded']
                        }
                    }
                }

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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['description'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['description']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget'][
                        'europeanUnionFunding'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget'][
                        'europeanUnionFunding']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['project'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['project']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['projectID'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['projectID']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['uri'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['uri']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['rationale'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['rationale']
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating, actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }

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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload full data model own money, '
                  'update fs: payload without optional fields own money')
    def test_check_fs_release_eight(self):
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
            And save in variable fs_id and fs_token.
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
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_obligatory_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_full_data_model_own_money_payer_id_is_not_equal_funder_id(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating)
                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_removed': "['releases'][0]['planning']['rationale'], "
                                               "['releases'][0]['planning']['budget']['description'], "
                                               "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                               "['releases'][0]['planning']['budget']['project'], "
                                               "['releases'][0]['planning']['budget']['projectID'], "
                                               "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': GlobalClassUpdateFs.payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': GlobalClassCreateFs.payload['planning']['budget']['isEuropeanUnionFunded']
                        }
                    }
                }

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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating, actual_ei_release_after_fs_updating)

                expected_result = {
                        'values_changed': {
                            "root['releases'][0]['id']": {
                                "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                             f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                                "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                             f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                            },
                            "root['releases'][0]['date']": {
                                'new_value':
                                    GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                                'old_value':
                                    GlobalClassCreateFs.feed_point_message['data']['operationDate']
                            },
                            "root['releases'][0]['planning']['budget']['amount']['amount']": {
                                'new_value':
                                    GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                                'old_value':
                                    GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                            }
                        }
                }

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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload without optional fields treasury money, '
                  'update fs: payload full data model own money ')
    def test_check_fs_release_nine(self):
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
            And save in variable fs_id and fs_token.
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
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_full_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_treasury_money(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id,
                        ei_buyer_id=f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
                                    f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}",
                        ei_buyer_name=GlobalClassCreateEi.payload['buyer']['name']
                    ))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['planning']['rationale'], "
                                             "['releases'][0]['planning']['budget']['id'], "
                                             "['releases'][0]['planning']['budget']['description'], "
                                             "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                             "['releases'][0]['planning']['budget']['project'], "
                                             "['releases'][0]['planning']['budget']['projectID'], "
                                             "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': GlobalClassUpdateFs.payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': GlobalClassCreateFs.payload['planning']['budget']['isEuropeanUnionFunded']
                        }
                    }
                }

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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['id'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['id']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['description'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['description']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget'][
                        'europeanUnionFunding'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget'][
                        'europeanUnionFunding']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['project'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['project']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['projectID'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['projectID']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['uri'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['uri']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['rationale'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['rationale']
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating, actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }

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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  'create fs: payload without optional fields own money, '
                  'update fs: payload full data modeltreasury money ')
    def test_check_fs_release_ten(self):
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_obligatory_data_model_own_money()
            Requests().create_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload
            )
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_full_data_model_treasury_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_own_money_payer_id_is_not_equal_funder_id(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['planning']['rationale'], "
                                             "['releases'][0]['planning']['budget']['description'], "
                                             "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                             "['releases'][0]['planning']['budget']['project'], "
                                             "['releases'][0]['planning']['budget']['projectID'], "
                                             "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': GlobalClassUpdateFs.payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': GlobalClassCreateFs.payload['planning']['budget']['isEuropeanUnionFunded']
                        }
                    }
                }

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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['description'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['description']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget'][
                        'europeanUnionFunding'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget'][
                        'europeanUnionFunding']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['project'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['project']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['projectID'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['projectID']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['budget']['uri'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['budget']['uri']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateFs.payload['planning']['rationale'],
                    actual_result=actual_fs_release_after_updating['releases'][0]['planning']['rationale']
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating, actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }

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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check FS release data after FS updating:'
                  ' create fs: payload full data model treasury money, '
                  'update fs: payload without optional fields own money')
    def test_check_fs_release_twelve(self):
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_full_data_model_treasury_money()
            Requests().create_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload
            )
            actual_ei_release_after_fs_creating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            GlobalClassCreateFs.feed_point_message = \
                KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()

            GlobalClassCreateFs.fs_id = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['id']

            GlobalClassCreateFs.fs_token = \
                GlobalClassCreateFs.feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. Authorization platform one: update FS'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateFs.access_token)

        with allure.step('# 6. Send request to update FS'):
            """
            Send api request on BPE host for financial source updating. 
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            GlobalClassUpdateFs.payload = payload.update_fs_obligatory_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateFs.access_token,
                x_operation_id=GlobalClassUpdateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                fs_id=GlobalClassCreateFs.fs_id,
                fs_token=GlobalClassCreateFs.fs_token,
                payload=GlobalClassUpdateFs.payload
            )
            GlobalClassUpdateFs.feed_point_message = \
                KafkaMessage(GlobalClassUpdateFs.operation_id).get_message_from_kafka()

            actual_ei_release_after_fs_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

            actual_fs_release_after_updating = \
                requests.get(url=f"{GlobalClassUpdateFs.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateFs.operation_id).update_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateFs.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid,
                    fs_id=GlobalClassCreateFs.fs_id
                )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by operation-id.
                    """
                    database = CassandraSession(
                        cassandra_username=GlobalClassMetadata.cassandra_username,
                        cassandra_password=GlobalClassMetadata.cassandra_password,
                        cassandra_cluster=GlobalClassMetadata.cassandra_cluster)
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 7.3. Check FS release before updating'):
                """
                Compare actual first financial source release before updating with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_full_data_model_treasury_money(
                        actual_fs_release=actual_fs_release_before_updating,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id,
                        ei_buyer_id=f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
                                    f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}",
                        ei_buyer_name=GlobalClassCreateEi.payload['buyer']['name']))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release_before_updating, expected_fs_release_model))
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.4. Check FS release after updating'):
                """
                Compare actual second financial source release after updating with
                first financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)), "Actual FS release before updating")
                allure.attach(str(json.dumps(actual_fs_release_after_updating)), "Actual FS release after updating")

                compare_releases = DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating)
                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_removed': "['releases'][0]['planning']['rationale'], "
                                               "['releases'][0]['planning']['budget']['id'], "
                                               "['releases'][0]['planning']['budget']['description'], "
                                               "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                               "['releases'][0]['planning']['budget']['project'], "
                                               "['releases'][0]['planning']['budget']['projectID'], "
                                               "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']}-"
                                f"{actual_fs_release_before_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['startDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['period']['endDate'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': GlobalClassUpdateFs.payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': GlobalClassCreateFs.payload['planning']['budget']['isEuropeanUnionFunded']
                        }
                    }
                }

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
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 7.5. Check EI release after FS updating'):
                """
                Compare actual third expenditure item release after fs updating with
                second expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after fs updating")

                compare_releases = DeepDiff(
                    actual_ei_release_after_fs_creating, actual_ei_release_after_fs_updating)

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassUpdateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value':
                                GlobalClassUpdateFs.payload['planning']['budget']['amount']['amount'],
                            'old_value':
                                GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        }
                    }
                }

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
                        database.cleanup_steps_of_process(operation_id=GlobalClassUpdateFs.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
