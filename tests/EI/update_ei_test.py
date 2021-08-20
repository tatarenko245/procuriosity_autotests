# файл з самим тестом
import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassCreateEi, GlobalClassUpdateEi, GlobalClassMetadata
from tests.utils.PayloadModel.EI.ei_prepared_payload import EiPreparePayload
from tests.utils.ReleaseModel.EI.ei_prepared_release import EiExpectedRelease
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment

from tests.utils.functions import compare_actual_result_and_expected_result
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization

from tests.utils.requests import Requests


@allure.parent_suite('Budgets')
@allure.suite('EI')
@allure.sub_suite('BPE: Update EI')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/edit#gid=0',
                 name='Google sheets: Update EI')
class TestUpdateEi:
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

    @allure.title('Check status code and message from Kafka topic after EI updating')
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
            And save in variable ei_ocid and ei_token.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_obligatory_data_model()
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

            GlobalClassCreateEi.ei_token = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['X-TOKEN']

        with allure.step('# 3. Authorization platform one: update EI'):
            """
            Tender platform authorization for update expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateEi.access_token)

        with allure.step('# 4. Send request to update EI'):
            """
            Send api request on BPE host for expenditure item updating.
            """
            time.sleep(1)
            GlobalClassUpdateEi.payload = ei_payload.update_ei_full_data_model(
                tender_classification_id=GlobalClassCreateEi.payload['tender']['classification']['id'])

            synchronous_result_of_sending_the_request = Requests().update_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateEi.access_token,
                x_operation_id=GlobalClassUpdateEi.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                ei_token=GlobalClassCreateEi.ei_token,
                payload=GlobalClassUpdateEi.payload
            )
            GlobalClassUpdateEi.feed_point_message = \
                KafkaMessage(GlobalClassUpdateEi.operation_id).get_message_from_kafka()

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
                allure.attach(str(GlobalClassUpdateEi.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateEi.operation_id).update_ei_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateEi.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid
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
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check EI release data after Ei updating with full data model')
    def test_check_ei_release_one(self):

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
            And save in variable ei_ocid and ei_token.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model()
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

            GlobalClassCreateEi.ei_token = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['X-TOKEN']

            actual_ei_release_before_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

        with allure.step('# 3. Authorization platform one: Update EI'):
            """
            Tender platform authorization for update expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateEi.access_token)

        with allure.step('# 4. Send request to update EI'):
            """
            Send api request on BPE host for expenditure item updating.
            """
            time.sleep(1)
            GlobalClassUpdateEi.payload = ei_payload.update_ei_obligatory_data_model()
            synchronous_result_of_sending_the_request = Requests().update_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateEi.access_token,
                x_operation_id=GlobalClassUpdateEi.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                ei_token=GlobalClassCreateEi.ei_token,
                payload=GlobalClassUpdateEi.payload
            )

            GlobalClassUpdateEi.feed_point_message = \
                KafkaMessage(GlobalClassUpdateEi.operation_id).get_message_from_kafka()

            actual_ei_release_after_updating = requests.get(
                url=f"{GlobalClassUpdateEi.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateEi.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateEi.operation_id).update_ei_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateEi.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid
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
                                operation_id=GlobalClassUpdateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 5.3. Check EI release before updating'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)), "Actual EI release before updating")
                GlobalClassCreateEi.actual_ei_release = actual_ei_release_before_updating
                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ei_release_model = copy.deepcopy(
                    expected_release_class.ei_release_full_data_model())

                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected EI release before updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_updating, expected_ei_release_model))
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
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 5.4. Check EI release after updating'):
                """
                Compare actual second expenditure item release after updating with
                first expenditure item release before updating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)),
                              "Actual Ei release before updating")
                allure.attach(str(json.dumps(actual_ei_release_after_updating)),
                              "Actual Ei release after updating")

                compare_releases = DeepDiff(actual_ei_release_before_updating, actual_ei_release_after_updating)
                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_removed': "['releases'][0]['tender']['description'], "
                                               "['releases'][0]['tender']['items'], "
                                               "['releases'][0]['planning']['rationale']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value': f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_updating['releases'][0]['id'][29:42]}",
                            'old_value': f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateEi.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateEi.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['title']": {
                            'new_value': GlobalClassUpdateEi.payload['tender']['title'],
                            'old_value': GlobalClassCreateEi.payload['tender']['title']
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
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check EI release after Ei updating on model without optional fields')
    def test_check_ei_release_two(self):
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
            And save in variable ei_ocid and ei_token.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_obligatory_data_model()
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

            GlobalClassCreateEi.ei_token = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['X-TOKEN']

            actual_ei_release_before_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

        with allure.step('# 3. Authorization platform one: Update EI'):
            """
            Tender platform authorization for update expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateEi.access_token)

        with allure.step('# 4. Send request to update EI'):
            """
            Send api request on BPE host for expenditure item updating.
            """
            time.sleep(1)
            GlobalClassUpdateEi.payload = ei_payload.update_ei_full_data_model(
                tender_classification_id=GlobalClassCreateEi.payload['tender']['classification']['id'])
            synchronous_result_of_sending_the_request = Requests().update_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateEi.access_token,
                x_operation_id=GlobalClassUpdateEi.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                ei_token=GlobalClassCreateEi.ei_token,
                payload=GlobalClassUpdateEi.payload
            )

            GlobalClassUpdateEi.feed_point_message = \
                KafkaMessage(GlobalClassUpdateEi.operation_id).get_message_from_kafka()

            actual_ei_release_after_updating = requests.get(
                url=f"{GlobalClassUpdateEi.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateEi.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateEi.operation_id).update_ei_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateEi.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid
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
                                operation_id=GlobalClassUpdateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 5.3. Check EI release before updating'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)), "Actual EI release before updating")
                GlobalClassCreateEi.actual_ei_release = actual_ei_release_before_updating
                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ei_release_model = copy.deepcopy(
                    expected_release_class.ei_release_obligatory_data_model())

                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected EI release before updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_updating, expected_ei_release_model))
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
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 5.4. Check EI release after updating'):
                """
                Compare actual second expenditure item release after updating with
                first expenditure item release before updating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)),
                              "Actual Ei release before updating")
                allure.attach(str(json.dumps(actual_ei_release_after_updating)),
                              "Actual Ei release after updating")

                compare_releases = DeepDiff(actual_ei_release_before_updating, actual_ei_release_after_updating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['tender']['description'], "
                                             "['releases'][0]['tender']['items'], "
                                             "['releases'][0]['planning']['rationale']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value': f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_after_updating['releases'][0]['id'][29:42]}",
                            'old_value': f"{GlobalClassCreateEi.ei_ocid}-"
                                         f"{actual_ei_release_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdateEi.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreateEi.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['title']": {
                            'new_value': GlobalClassUpdateEi.payload['tender']['title'],
                            'old_value': GlobalClassCreateEi.payload['tender']['title']
                        }
                    }
                }

                expected_items_array_model = expected_release_class.prepare_expected_items_array(
                    payload_items_array=GlobalClassUpdateEi.payload['tender']['items'],
                    release_items_array=actual_ei_release_after_updating['releases'][0]['tender']['items']
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
                    if compare_releases == expected_result:
                        database.ei_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateEi.payload['tender']['description'],
                    actual_result=actual_ei_release_after_updating['releases'][0]['tender']['description']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_items_array_model,
                    actual_result=actual_ei_release_after_updating['releases'][0]['tender']['items']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateEi.payload['planning']['rationale'],
                    actual_result=actual_ei_release_after_updating['releases'][0]['planning']['rationale']
                )) == str(True)

    @allure.title('Check EI release data after Ei updating based on full data model with 3 items objects')
    def test_check_ei_release_three(self):
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
            And save in variable ei_ocid and ei_token.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model()
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

            GlobalClassCreateEi.ei_token = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['X-TOKEN']

            actual_ei_release_before_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

        with allure.step('# 3. Authorization platform one: Update EI'):
            """
            Tender platform authorization for update expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateEi.access_token)

        with allure.step('# 4. Send request to update EI'):
            """
            Send api request on BPE host for expenditure item updating.
            """
            time.sleep(1)
            GlobalClassUpdateEi.payload = ei_payload.update_ei_full_data_model(
                tender_classification_id=GlobalClassCreateEi.payload['tender']['classification']['id'],
                quantity_of_tender_item_object=3)
            synchronous_result_of_sending_the_request = Requests().update_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateEi.access_token,
                x_operation_id=GlobalClassUpdateEi.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                ei_token=GlobalClassCreateEi.ei_token,
                payload=GlobalClassUpdateEi.payload
            )

            GlobalClassUpdateEi.feed_point_message = \
                KafkaMessage(GlobalClassUpdateEi.operation_id).get_message_from_kafka()

            actual_ei_release_after_updating = requests.get(
                url=f"{GlobalClassUpdateEi.feed_point_message['data']['url']}").json()

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
                allure.attach(str(GlobalClassUpdateEi.feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateEi.operation_id).update_ei_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateEi.feed_point_message,
                    ei_ocid=GlobalClassCreateEi.ei_ocid
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
                                operation_id=GlobalClassUpdateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 5.3. Check EI release before updating'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)), "Actual EI release before updating")
                GlobalClassCreateEi.actual_ei_release = actual_ei_release_before_updating
                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ei_release_model = copy.deepcopy(
                    expected_release_class.ei_release_full_data_model())

                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected EI release before updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_updating, expected_ei_release_model))
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
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 5.4. Check EI release after updating'):
                """
                Compare actual second expenditure item release after updating with
                first expenditure item release before updating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)),
                              "Actual Ei release before updating")
                allure.attach(str(json.dumps(actual_ei_release_after_updating)),
                              "Actual Ei release after updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_updating, actual_ei_release_after_updating))

                try:
                    """
                    Expected result depends on payload['tender']['items'][0]['classification']['id'].
                    """
                    expected_items_array_model = expected_release_class.prepare_expected_items_array(
                        payload_items_array=GlobalClassUpdateEi.payload['tender']['items'],
                        release_items_array=actual_ei_release_after_updating['releases'][0]['tender']['items']
                    )
                    if actual_ei_release_after_updating['releases'][0]['tender']['items'] == expected_items_array_model:
                        pass
                    else:
                        raise ValueError('Check tender.items array')
                    if GlobalClassCreateEi.payload['tender']['items'][0]['classification']['id'] != \
                            GlobalClassUpdateEi.payload['tender']['items'][0]['classification']['id']:
                        expected_result = {
                            'values_changed': {
                                "root['releases'][0]['id']": {
                                    'new_value':
                                        f"{GlobalClassCreateEi.ei_ocid}-"
                                        f"{actual_ei_release_after_updating['releases'][0]['id'][29:42]}",
                                    'old_value':
                                        f"{GlobalClassCreateEi.ei_ocid}-"
                                        f"{actual_ei_release_before_updating['releases'][0]['id'][29:42]}"
                                },
                                "root['releases'][0]['date']": {
                                    'new_value': GlobalClassUpdateEi.feed_point_message['data']['operationDate'],
                                    'old_value': GlobalClassCreateEi.feed_point_message['data']['operationDate']
                                },
                                "root['releases'][0]['tender']['title']": {
                                    'new_value': GlobalClassUpdateEi.payload['tender']['title'],
                                    'old_value': GlobalClassCreateEi.payload['tender']['title']
                                },
                                "root['releases'][0]['tender']['description']": {
                                    'new_value': GlobalClassUpdateEi.payload['tender']['description'],
                                    'old_value': GlobalClassCreateEi.payload['tender']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['id']": {
                                    'new_value':
                                        expected_items_array_model[0]['id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'id']
                                },
                                "root['releases'][0]['tender']['items'][0]['description']": {
                                    'new_value':
                                        expected_items_array_model[0]['description'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'description']
                                },
                                "root['releases'][0]['tender']['items'][0]['classification']['id']": {
                                    "new_value": expected_items_array_model[0]['classification']['id'],
                                    "old_value":
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'classification']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['classification']['description']": {
                                    "new_value": expected_items_array_model[0]['classification']['description'],
                                    "old_value":
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'classification']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]['id']": {
                                    'new_value': expected_items_array_model[0]['additionalClassifications'][0]['id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'additionalClassifications'][0]['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]["
                                "'description']": {
                                    'new_value': expected_items_array_model[0]['additionalClassifications'][0][
                                        'description'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'additionalClassifications'][0]['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['quantity']": {
                                    'new_value': expected_items_array_model[0]['quantity'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'quantity']
                                },
                                "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                                    'new_value': expected_items_array_model[0]['unit']['name'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'unit']['name']
                                },
                                "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                                    'new_value': expected_items_array_model[0]['unit']['id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'unit']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['streetAddress']": {
                                    'new_value': expected_items_array_model[0]['deliveryAddress']['streetAddress'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['streetAddress']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['postalCode']": {
                                    'new_value': expected_items_array_model[0]['deliveryAddress']['postalCode'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['postalCode']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'region']['id']": {
                                    'new_value':
                                        expected_items_array_model[0]['deliveryAddress']['addressDetails']['region'][
                                            'id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'region']['description']": {
                                    'new_value':
                                        expected_items_array_model[0]['deliveryAddress']['addressDetails']['region'][
                                            'description'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'locality']['id']": {
                                    'new_value':
                                        expected_items_array_model[0]['deliveryAddress']['addressDetails']['locality'][
                                            'id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'locality']['description']": {
                                    'new_value':
                                        expected_items_array_model[0]['deliveryAddress']['addressDetails']['locality'][
                                            'description'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['description']
                                },
                                "root['releases'][0]['planning']['rationale']": {
                                    'new_value': GlobalClassUpdateEi.payload['planning']['rationale'],
                                    'old_value': actual_ei_release_before_updating['releases'][0]['planning'][
                                        'rationale']
                                }
                            },
                            "iterable_item_added": {
                                "root['releases'][0]['tender']['items'][1]": expected_items_array_model[1],
                                "root['releases'][0]['tender']['items'][2]": expected_items_array_model[2]
                            }
                        }
                    elif GlobalClassCreateEi.payload['tender']['items'][0]['classification']['id'] == \
                            GlobalClassUpdateEi.payload['tender']['items'][0]['classification']['id']:
                        expected_result = {
                            'values_changed': {
                                "root['releases'][0]['id']": {
                                    'new_value':
                                        f"{GlobalClassCreateEi.ei_ocid}-"
                                        f"{actual_ei_release_after_updating['releases'][0]['id'][29:42]}",
                                    'old_value':
                                        f"{GlobalClassCreateEi.ei_ocid}-"
                                        f"{actual_ei_release_before_updating['releases'][0]['id'][29:42]}"
                                },
                                "root['releases'][0]['date']": {
                                    'new_value': GlobalClassUpdateEi.feed_point_message['data']['operationDate'],
                                    'old_value': GlobalClassCreateEi.feed_point_message['data']['operationDate']
                                },
                                "root['releases'][0]['tender']['title']": {
                                    'new_value': GlobalClassUpdateEi.payload['tender']['title'],
                                    'old_value': GlobalClassCreateEi.payload['tender']['title']
                                },
                                "root['releases'][0]['tender']['description']": {
                                    'new_value': GlobalClassUpdateEi.payload['tender']['description'],
                                    'old_value': GlobalClassCreateEi.payload['tender']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['id']": {
                                    'new_value':
                                        expected_items_array_model[0]['id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0]['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['description']": {
                                    'new_value':
                                        expected_items_array_model[0]['description'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'description']
                                },
                                "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]['id']": {
                                    'new_value': expected_items_array_model[0]['additionalClassifications'][0]['id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'additionalClassifications'][0]['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]["
                                "'description']": {
                                    'new_value': expected_items_array_model[0]['additionalClassifications'][0][
                                        'description'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'additionalClassifications'][0]['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['quantity']": {
                                    'new_value': expected_items_array_model[0]['quantity'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'quantity']
                                },
                                "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                                    'new_value': expected_items_array_model[0]['unit']['name'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'unit']['name']
                                },
                                "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                                    'new_value': expected_items_array_model[0]['unit']['id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'unit']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['streetAddress']": {
                                    'new_value': expected_items_array_model[0]['deliveryAddress']['streetAddress'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['streetAddress']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['postalCode']": {
                                    'new_value': expected_items_array_model[0]['deliveryAddress']['postalCode'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['postalCode']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'region']['id']": {
                                    'new_value':
                                        expected_items_array_model[0]['deliveryAddress']['addressDetails']['region'][
                                            'id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'region']['description']": {
                                    'new_value':
                                        expected_items_array_model[0]['deliveryAddress']['addressDetails']['region'][
                                            'description'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['region']['description']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'locality']['id']": {
                                    'new_value':
                                        expected_items_array_model[0]['deliveryAddress']['addressDetails']['locality'][
                                            'id'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['id']
                                },
                                "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                                "'locality']['description']": {
                                    'new_value':
                                        expected_items_array_model[0]['deliveryAddress']['addressDetails']['locality'][
                                            'description'],
                                    'old_value':
                                        actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                            'deliveryAddress']['addressDetails']['locality']['description']
                                },
                                "root['releases'][0]['planning']['rationale']": {
                                    'new_value': GlobalClassUpdateEi.payload['planning']['rationale'],
                                    'old_value': actual_ei_release_before_updating['releases'][0]['planning'][
                                        'rationale']
                                }
                            },
                            'iterable_item_added': {
                                "root['releases'][0]['tender']['items'][1]": expected_items_array_model[1],
                                "root['releases'][0]['tender']['items'][2]": expected_items_array_model[2]
                            }
                        }
                except ValueError:
                    raise ValueError("Check your payloads")

                expected_items_array_model = expected_release_class.prepare_expected_items_array(
                    payload_items_array=GlobalClassUpdateEi.payload['tender']['items'],
                    release_items_array=actual_ei_release_after_updating['releases'][0]['tender']['items']
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
                    if compare_releases == expected_result:
                        database.ei_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateEi.payload['tender']['description'],
                    actual_result=actual_ei_release_after_updating['releases'][0]['tender']['description']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_items_array_model,
                    actual_result=actual_ei_release_after_updating['releases'][0]['tender']['items']
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=GlobalClassUpdateEi.payload['planning']['rationale'],
                    actual_result=actual_ei_release_after_updating['releases'][0]['planning']['rationale']
                )) == str(True)
