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
from tests.utils.functions import compare_actual_result_and_expected_result, is_it_uuid
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

    @allure.title('Check status code and message from Kafka topic after FS creating')
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
            GlobalClassCreateFs.payload = payload.create_fs_full_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().create_fs(
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

        with allure.step('# 5. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 5.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 5.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                allure.attach(str(GlobalClassCreateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateFs.operation_id).create_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateFs.feed_point_message
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
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check FS release data after FS creation:'
                  'ei -> model without optional fields '
                  'and fs -> full data model own money')
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

            actual_ei_release_before_fs_creating = requests.get(
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_full_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().create_fs(
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

            actual_fs_release = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 5.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 5.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                allure.attach(str(GlobalClassCreateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateFs.operation_id).create_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateFs.feed_point_message
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 5.3. Check FS release'):
                """
                Compare actual first financial source release with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_full_data_model_own_money_payer_id_is_not_equal_funder_id(
                        actual_fs_release=actual_fs_release,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release_model))
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

            with allure.step('# 5.4. Check EI release after FS creating'):
                """
                Compare actual second expenditure item release after fs creating with
                first expenditure item release before fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_creating)),
                              "Actual Ei release before fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")

                compare_releases = DeepDiff(actual_ei_release_before_fs_creating, actual_ei_release_after_fs_creating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_before_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateEi.feed_point_message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes_model = [{
                    "id": actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": GlobalClassCreateFs.fs_id,
                    "uri": f"{GlobalClassMetadata.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}"
                           f"/{GlobalClassCreateFs.fs_id}"
                }]

                try:
                    """
                    Check actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'].
                    If actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'] is uuid v.1,
                    then pass.
                    ELSE return exception.
                    """
                    is_it_uuid(
                        uuid_to_test=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your relatedProcesses.id in EI release: relatedProcesses.id in Ei release "
                        "must be uuid version 1")

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
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassCreateFs.payload['planning']['budget']['amount'],
                    actual_result=actual_ei_release_after_fs_creating['releases'][0]['planning']['budget']['amount']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_related_processes_model,
                    actual_result=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses']
                )) == str(True)

    @allure.title('Check FS release data after FS creation:'
                  'ei -> full data model and '
                  'fs -> full data model treasury money')
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

            actual_ei_release_before_fs_creating = requests.get(
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_full_data_model_treasury_money()
            synchronous_result_of_sending_the_request = Requests().create_fs(
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

            actual_fs_release = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 5.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 5.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                allure.attach(str(GlobalClassCreateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateFs.operation_id).create_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateFs.feed_point_message
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 5.3. Check FS release'):
                """
                Compare actual first financial source release with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_full_data_model_treasury_money(
                        actual_fs_release=actual_fs_release,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id,
                        ei_buyer_id=f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
                                    f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}",
                        ei_buyer_name=GlobalClassCreateEi.payload['buyer']['name']))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release_model))
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

            with allure.step('# 5.4. Check EI release after FS creating'):
                """
                Compare actual second expenditure item release after fs creating with
                first expenditure item release before fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_creating)),
                              "Actual Ei release before fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")

                compare_releases = DeepDiff(actual_ei_release_before_fs_creating, actual_ei_release_after_fs_creating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_before_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateEi.feed_point_message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes_model = [{
                    "id": actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": GlobalClassCreateFs.fs_id,
                    "uri": f"{GlobalClassMetadata.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}"
                           f"/{GlobalClassCreateFs.fs_id}"
                }]

                try:
                    """
                    Check actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'].
                    If actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'] is uuid v.1,
                    then pass.
                    ELSE return exception.
                    """
                    is_it_uuid(
                        uuid_to_test=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your relatedProcesses.id in EI release: relatedProcesses.id in Ei release "
                        "must be uuid version 1")

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
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassCreateFs.payload['planning']['budget']['amount'],
                    actual_result=actual_ei_release_after_fs_creating['releases'][0]['planning']['budget']['amount']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_related_processes_model,
                    actual_result=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses']
                )) == str(True)

    @allure.title('Check FS release data after FS creation:'
                  'ei -> full data model and '
                  'fs -> model without optional fields own money')
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

            actual_ei_release_before_fs_creating = requests.get(
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_obligatory_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().create_fs(
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

            actual_fs_release = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 5.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 5.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                allure.attach(str(GlobalClassCreateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateFs.operation_id).create_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateFs.feed_point_message
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 5.3. Check FS release'):
                """
                Compare actual first financial source release with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_own_money_payer_id_is_not_equal_funder_id(
                        actual_fs_release=actual_fs_release,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release_model))
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

            with allure.step('# 5.4. Check EI release after FS creating'):
                """
                Compare actual second expenditure item release after fs creating with
                first expenditure item release before fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_creating)),
                              "Actual Ei release before fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")

                compare_releases = DeepDiff(actual_ei_release_before_fs_creating, actual_ei_release_after_fs_creating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_before_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateEi.feed_point_message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes_model = [{
                    "id": actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": GlobalClassCreateFs.fs_id,
                    "uri": f"{GlobalClassMetadata.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}"
                           f"/{GlobalClassCreateFs.fs_id}"
                }]

                try:
                    """
                    Check actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'].
                    If actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'] is uuid v.1,
                    then pass.
                    ELSE return exception.
                    """
                    is_it_uuid(
                        uuid_to_test=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your relatedProcesses.id in EI release: relatedProcesses.id in Ei release "
                        "must be uuid version 1")

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
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassCreateFs.payload['planning']['budget']['amount'],
                    actual_result=actual_ei_release_after_fs_creating['releases'][0]['planning']['budget']['amount']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_related_processes_model,
                    actual_result=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses']
                )) == str(True)

    @allure.title('Check FS release data after FS creation:'
                  'ei -> model without optional fields and '
                  'fs -> model without optional fields treasury money')
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

            actual_ei_release_before_fs_creating = requests.get(
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
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            GlobalClassCreateFs.payload = payload.create_fs_obligatory_data_model_treasury_money()
            synchronous_result_of_sending_the_request = Requests().create_fs(
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

            actual_fs_release = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

        with allure.step('# 5. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 5.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 5.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                allure.attach(str(GlobalClassCreateFs.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateFs.operation_id).create_fs_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateFs.feed_point_message
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
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 5.3. Check FS release'):
                """
                Compare actual first financial source release with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release)), "Actual FS release")

                expected_release_class = copy.deepcopy(ExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_treasury_money(
                        actual_fs_release=actual_fs_release,
                        payload_for_create_fs=GlobalClassCreateFs.payload,
                        operation_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        release_date=GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                        ei_id=GlobalClassCreateEi.ei_ocid,
                        fs_id=GlobalClassCreateFs.fs_id,
                        ei_buyer_id=f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
                                    f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}",
                        ei_buyer_name=GlobalClassCreateEi.payload['buyer']['name']))
                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected FS release")

                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release_model))
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

            with allure.step('# 5.4. Check EI release after FS creating'):
                """
                Compare actual second expenditure item release after fs creating with
                first expenditure item release before fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_creating)),
                              "Actual Ei release before fs creating")
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")

                compare_releases = DeepDiff(actual_ei_release_before_fs_creating, actual_ei_release_after_fs_creating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_before_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value':
                                GlobalClassCreateFs.feed_point_message['data']['operationDate'],
                            'old_value':
                                GlobalClassCreateEi.feed_point_message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes_model = [{
                    "id": actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": GlobalClassCreateFs.fs_id,
                    "uri": f"{GlobalClassMetadata.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}"
                           f"/{GlobalClassCreateFs.fs_id}"
                }]

                try:
                    """
                    Check actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'].
                    If actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'] is uuid v.1, 
                    then pass.
                    ELSE return exception.
                    """
                    is_it_uuid(
                        uuid_to_test=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your relatedProcesses.id in EI release: relatedProcesses.id in Ei release "
                        "must be uuid version 1")

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
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateFs.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassCreateFs.payload['planning']['budget']['amount'],
                    actual_result=actual_ei_release_after_fs_creating['releases'][0]['planning']['budget']['amount']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_related_processes_model,
                    actual_result=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses']
                )) == str(True)
