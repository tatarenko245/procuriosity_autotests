import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
     GlobalClassCancelPn
from tests.utils.PayloadModel.Budget.Ei.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.OpenProcedure.Pn.pn_prepared_payload import PnPreparePayload

from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions import compare_actual_result_and_expected_result
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.my_requests import Requests


@allure.parent_suite('Planning')
@allure.suite('Pn')
@allure.sub_suite('BPE: Cancel Pn')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=671883180',
                 name='Google sheets: Cancel Pn')
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
        GlobalClassMetadata.host_for_services = GlobalClassMetadata.hosts[2]
        GlobalClassMetadata.cassandra_cluster = GlobalClassMetadata.hosts[0]
        GlobalClassMetadata.database = CassandraSession(
            cassandra_username=GlobalClassMetadata.cassandra_username,
            cassandra_password=GlobalClassMetadata.cassandra_password,
            cassandra_cluster=GlobalClassMetadata.cassandra_cluster)

    @allure.title('Check status code and message from Kafka topic after Pn canceling')
    def test_check_result_of_sending_the_request(self):
        with allure.step('# 1. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
        with allure.step('# 2. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model(quantity_of_tender_item_object=2)
            Requests().createEi(
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
        with allure.step('# 3. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)

        with allure.step('# 4. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload = copy.deepcopy(FsPreparePayload(ei_payload=GlobalClassCreateEi.payload))
            GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
            Requests().createFs(
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

        with allure.step('# 5. Authorization platform one: create Pn'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)

        with allure.step('# 6. Send request to create Pn'):
            """
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=3,
                    quantity_of_item_object=3)

            Requests().createPn(
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

            GlobalClassCreatePn.pn_token = \
                GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']

        with allure.step('# 7. Authorization platform one: cancel Pn'):
            """
            Tender platform authorization for cancel planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCancelPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCancelPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCancelPn.access_token)

        with allure.step('# 8. Send request to cancel Pn'):
            """
            Send api request on BPE host for planning notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            synchronous_result_of_sending_the_request = Requests().cancel_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCancelPn.access_token,
                x_operation_id=GlobalClassCancelPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token
            )

        with allure.step('# 9. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 9.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 9.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassCancelPn.feed_point_message = \
                    KafkaMessage(GlobalClassCancelPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCancelPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCancelPn.operation_id).cancel_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCancelPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid
                )
                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is True:
                        GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCancelPn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check Pn and MS releases data after Pn canceling, pn release with full data model '
                  'with 3 lots and 3 items')
    def test_check_pn_ms_releases_one(self):
        with allure.step('# 1. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
        with allure.step('# 2. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model(quantity_of_tender_item_object=2)
            Requests().createEi(
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
        with allure.step('# 3. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)

        with allure.step('# 4. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload = copy.deepcopy(FsPreparePayload(ei_payload=GlobalClassCreateEi.payload))
            GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
            Requests().createFs(
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

        with allure.step('# 5. Authorization platform one: create Pn'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)

        with allure.step('# 6. Send request to create Pn'):
            """
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=3,
                    quantity_of_item_object=3)

            Requests().createPn(
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

            GlobalClassCreatePn.pn_token = \
                GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']

            actual_pn_release_before_canceling = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()
            GlobalClassCreatePn.actual_pn_release = actual_pn_release_before_canceling

            actual_ms_release_before_canceling = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            actual_fs_release_before_canceling = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

            actual_ei_release_before_canceling = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

        with allure.step('# 7. Authorization platform one: cancel Pn'):
            """
            Tender platform authorization for cancel planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCancelPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCancelPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCancelPn.access_token)

        with allure.step('# 8. Send request to cancel Pn'):
            """
            Send api request on BPE host for planning notice canceling.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            synchronous_result_of_sending_the_request = Requests().cancel_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCancelPn.access_token,
                x_operation_id=GlobalClassCancelPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token
            )

        with allure.step('# 9. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 9.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 9.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassCancelPn.feed_point_message = \
                    KafkaMessage(GlobalClassCancelPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCancelPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCancelPn.operation_id).cancel_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCancelPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 9.3. Check Pn release'):
                """
                Compare actual planning notice release before canceling and actual planning release after canceling.
                """
                allure.attach(str(json.dumps(actual_pn_release_before_canceling)),
                              "Actual Pn release before canceling")

                actual_pn_release_after_canceling = requests.get(
                    url=f"{GlobalClassCancelPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_id}").json()

                allure.attach(str(json.dumps(actual_pn_release_after_canceling)),
                              "Actual Pn release after canceling")

                compare_releases = dict(DeepDiff(
                    actual_pn_release_before_canceling, actual_pn_release_after_canceling))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreatePn.pn_id}-"
                                f"{actual_pn_release_after_canceling['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreatePn.pn_id}-"
                                f"{actual_pn_release_before_canceling['releases'][0]['id'][46:59]}",
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassCancelPn.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreatePn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            'new_value': 'tenderCancellation',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['status']": {
                            'new_value': 'cancelled',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            'new_value': 'empty',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['lots'][0]['status']": {
                            'new_value': 'cancelled',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['lots'][1]['status']": {
                            'new_value': 'cancelled',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['lots'][2]['status']": {
                            'new_value': 'cancelled',
                            'old_value': 'planning'
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
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.4. Check MS release'):
                """
                Compare actual multistage release before canceling and actual multistage release after canceling.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_canceling)),
                              "Actual MS release before canceling")

                actual_ms_release_after_canceling = requests.get(
                    url=f"{GlobalClassCancelPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()
                allure.attach(str(json.dumps(actual_pn_release_after_canceling)),
                              "Actual MS release after canceling")

                compare_releases = dict(
                    DeepDiff(actual_ms_release_before_canceling, actual_ms_release_after_canceling))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_after_canceling['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_before_canceling['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCancelPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreatePn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            'new_value': 'tenderCancellation',
                            'old_value': 'compiled'
                        },
                        "root['releases'][0]['tender']['status']": {
                            'new_value': 'cancelled',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            'new_value': 'empty',
                            'old_value': 'planning'
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
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.5. Check Ei release'):
                """
                Compare actual expenditure item release before pn canceling and actual expenditure item release
                after pn canceling.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_canceling)),
                              "Actual Ei release before pn canceling")

                actual_ei_release_after_canceling = requests.get(
                    url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateEi.ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_canceling)),
                              "Actual Ei release after pn canceling")

                compare_releases = dict(
                    DeepDiff(actual_ei_release_before_canceling, actual_ei_release_after_canceling))

                expected_result = {}

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.6. Check Fs release'):
                """
                Compare actual financial source release before pn canceling and actual financial source release
                after pn canceling.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_canceling)),
                              "Actual Fs release before pn canceling")

                actual_fs_release_after_canceling = requests.get(
                    url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateFs.fs_id}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_canceling)),
                              "Actual Fs release after pn canceling")

                compare_releases = dict(
                    DeepDiff(actual_fs_release_before_canceling, actual_fs_release_after_canceling))

                expected_result = {}

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

            try:
                """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                if compare_releases == expected_result:
                    GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
                        ei_id=GlobalClassCreateEi.ei_ocid)

                    GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
                        ei_id=GlobalClassCreateEi.ei_ocid)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateEi.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateFs.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreatePn.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCancelPn.operation_id)
                else:
                    with allure.step('# Steps from Casandra DataBase'):
                        steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                            operation_id=GlobalClassCancelPn.operation_id)
                        allure.attach(steps, "Cassandra DataBase: steps of process")
            except ValueError:
                raise ValueError("Can not return BPE operation step")

            assert str(compare_actual_result_and_expected_result(
                expected_result=expected_result,
                actual_result=compare_releases
            )) == str(True)

    @allure.title('Check Pn and MS releases data after Pn canceling, pn release  without optional fields')
    def test_check_pn_ms_releases_two(self):
        with allure.step('# 1. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
        with allure.step('# 2. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_obligatory_data_model()
            Requests().createEi(
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
        with allure.step('# 3. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)

        with allure.step('# 4. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload = copy.deepcopy(FsPreparePayload(ei_payload=GlobalClassCreateEi.payload))
            GlobalClassCreateFs.payload = fs_payload.create_fs_obligatory_data_model_treasury_money(
                ei_payload=GlobalClassCreateEi.payload
            )
            Requests().createFs(
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

        with allure.step('# 5. Authorization platform one: create Pn'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)

        with allure.step('# 6. Send request to create Pn'):
            """
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            Requests().createPn(
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

            GlobalClassCreatePn.pn_token = \
                GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']

            actual_pn_release_before_canceling = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()
            GlobalClassCreatePn.actual_pn_release = actual_pn_release_before_canceling

            actual_ms_release_before_canceling = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            actual_fs_release_before_canceling = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

            actual_ei_release_before_canceling = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

        with allure.step('# 7. Authorization platform one: cancel Pn'):
            """
            Tender platform authorization for cancel planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCancelPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCancelPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCancelPn.access_token)

        with allure.step('# 8. Send request to cancel Pn'):
            """
            Send api request on BPE host for planning notice canceling.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            synchronous_result_of_sending_the_request = Requests().cancel_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCancelPn.access_token,
                x_operation_id=GlobalClassCancelPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token
            )

        with allure.step('# 9. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 9.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 9.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassCancelPn.feed_point_message = \
                    KafkaMessage(GlobalClassCancelPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCancelPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCancelPn.operation_id).cancel_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCancelPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 9.3. Check Pn release'):
                """
                Compare actual planning notice release before canceling and actual planning release after canceling.
                """
                allure.attach(str(json.dumps(actual_pn_release_before_canceling)),
                              "Actual Pn release before canceling")

                actual_pn_release_after_canceling = requests.get(
                    url=f"{GlobalClassCancelPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_id}").json()

                allure.attach(str(json.dumps(actual_pn_release_after_canceling)),
                              "Actual Pn release after canceling")

                compare_releases = dict(DeepDiff(
                    actual_pn_release_before_canceling, actual_pn_release_after_canceling))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreatePn.pn_id}-"
                                f"{actual_pn_release_after_canceling['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreatePn.pn_id}-"
                                f"{actual_pn_release_before_canceling['releases'][0]['id'][46:59]}",
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassCancelPn.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreatePn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            'new_value': 'tenderCancellation',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['status']": {
                            'new_value': 'cancelled',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            'new_value': 'empty',
                            'old_value': 'planning'
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
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.4. Check MS release'):
                """
                Compare actual multistage release before canceling and actual multistage release after canceling.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_canceling)),
                              "Actual MS release before canceling")

                actual_ms_release_after_canceling = requests.get(
                    url=f"{GlobalClassCancelPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()
                allure.attach(str(json.dumps(actual_pn_release_after_canceling)),
                              "Actual MS release after canceling")

                compare_releases = dict(
                    DeepDiff(actual_ms_release_before_canceling, actual_ms_release_after_canceling))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_after_canceling['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_before_canceling['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCancelPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreatePn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            'new_value': 'tenderCancellation',
                            'old_value': 'compiled'
                        },
                        "root['releases'][0]['tender']['status']": {
                            'new_value': 'cancelled',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            'new_value': 'empty',
                            'old_value': 'planning'
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
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.5. Check Ei release'):
                """
                Compare actual expenditure item release before pn canceling and actual expenditure item release
                after pn canceling.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_canceling)),
                              "Actual Ei release before pn canceling")

                actual_ei_release_after_canceling = requests.get(
                    url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateEi.ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_canceling)),
                              "Actual Ei release after pn canceling")

                compare_releases = dict(
                    DeepDiff(actual_ei_release_before_canceling, actual_ei_release_after_canceling))

                expected_result = {}

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.6. Check Fs release'):
                """
                Compare actual financial source release before pn canceling and actual financial source release
                after pn canceling.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_canceling)),
                              "Actual Fs release before pn canceling")

                actual_fs_release_after_canceling = requests.get(
                    url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateFs.fs_id}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_canceling)),
                              "Actual Fs release after pn canceling")

                compare_releases = dict(
                    DeepDiff(actual_fs_release_before_canceling, actual_fs_release_after_canceling))

                expected_result = {}

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCancelPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

            try:
                """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                if compare_releases == expected_result:
                    GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
                        ei_id=GlobalClassCreateEi.ei_ocid)

                    GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
                        ei_id=GlobalClassCreateEi.ei_ocid)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateEi.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateFs.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreatePn.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCancelPn.operation_id)
                else:
                    with allure.step('# Steps from Casandra DataBase'):
                        steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                            operation_id=GlobalClassCancelPn.operation_id)
                        allure.attach(steps, "Cassandra DataBase: steps of process")
            except ValueError:
                raise ValueError("Can not return BPE operation step")

            assert str(compare_actual_result_and_expected_result(
                expected_result=expected_result,
                actual_result=compare_releases
            )) == str(True)
