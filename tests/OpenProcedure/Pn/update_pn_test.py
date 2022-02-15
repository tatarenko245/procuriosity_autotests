import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassUpdatePn
from tests.utils.PayloadModel.Budget.Ei.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.OpenProcedure.Pn.pn_prepared_payload import PnPreparePayload

from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions import compare_actual_result_and_expected_result, get_value_from_region_csv, \
    get_value_from_locality_csv, is_it_uuid, get_value_from_country_csv, \
    get_value_from_classification_cpv_dictionary_xls, get_value_from_classification_unit_dictionary_csv
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.my_requests import Requests


@allure.parent_suite('Planning')
@allure.suite('Pn')
@allure.sub_suite('BPE: Update Pn')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=425197057',
                 name='Google sheets: Update Pn')
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

    @allure.title('Check status code and message from Kafka topic after Pn updating')
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

            Requests().create_pn(
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

            GlobalClassCreatePn.actual_pn_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()

        with allure.step('# 7. Authorization platform one: update Pn'):
            """
            Tender platform authorization for update planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdatePn.access_token)

        with allure.step('# 8. Send request to update Pn'):
            """
            Send api request on BPE host for planning notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassUpdatePn.payload = \
                pn_payload.update_pn_full_data_model_with_lots_and_items_full(
                    quantity_of_lot_object=3,
                    quantity_of_item_object=3,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True
                )
            synchronous_result_of_sending_the_request = Requests().update_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdatePn.access_token,
                x_operation_id=GlobalClassUpdatePn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassUpdatePn.payload
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
                GlobalClassUpdatePn.feed_point_message = \
                    KafkaMessage(GlobalClassUpdatePn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassUpdatePn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdatePn.operation_id).update_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdatePn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    pn_id=GlobalClassCreatePn.pn_id
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
                            operation_id=GlobalClassUpdatePn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check Pn and MS releases data after Pn updating with full data model with 3 lots and 3 items')
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

            Requests().create_pn(
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

            actual_pn_release_before_updating = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()
            GlobalClassCreatePn.actual_pn_release = actual_pn_release_before_updating

            actual_ms_release_before_updating = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

            actual_ei_release_before_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

        with allure.step('# 7. Authorization platform one: update Pn'):
            """
            Tender platform authorization for update planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdatePn.access_token)

        with allure.step('# 8. Send request to update Pn'):
            """
            Send api request on BPE host for planning notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassUpdatePn.payload = \
                pn_payload.update_pn_full_data_model_with_lots_and_items_full(
                    quantity_of_lot_object=3,
                    quantity_of_item_object=3,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True
                )
            synchronous_result_of_sending_the_request = Requests().update_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdatePn.access_token,
                x_operation_id=GlobalClassUpdatePn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassUpdatePn.payload
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
                GlobalClassUpdatePn.feed_point_message = \
                    KafkaMessage(GlobalClassUpdatePn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassUpdatePn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdatePn.operation_id).update_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdatePn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    pn_id=GlobalClassCreatePn.pn_id
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 9.3. Check Pn release'):
                """
                Compare actual planning notice release before updating and actual planning release after updating.
                """
                allure.attach(str(json.dumps(actual_pn_release_before_updating)),
                              "Actual Pn release before updating")

                actual_pn_release_after_updating = requests.get(
                    url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_id}").json()

                allure.attach(str(json.dumps(actual_pn_release_after_updating)),
                              "Actual Pn release after updating")

                compare_releases = dict(DeepDiff(
                    actual_pn_release_before_updating, actual_pn_release_after_updating))

                region_data = get_value_from_region_csv(
                    region=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['region']['id'],
                    country=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['country']['id'],
                    language=GlobalClassMetadata.language
                )

                locality_data = get_value_from_locality_csv(
                    locality=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['locality']['id'],
                    region=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['region']['id'],
                    country=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['country']['id'],
                    language=GlobalClassMetadata.language
                )

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{GlobalClassCreatePn.pn_id}-"
                                f"{actual_pn_release_after_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{GlobalClassCreatePn.pn_id}-"
                                f"{actual_pn_release_before_updating['releases'][0]['id'][46:59]}",
                        },
                        "root['releases'][0]['date']": {
                            'new_value': GlobalClassUpdatePn.feed_point_message['data']['operationDate'],
                            'old_value': GlobalClassCreatePn.actual_pn_release['releases'][0]['date']
                        },
                        "root['releases'][0]['tag'][0]": {
                            'new_value': 'planningUpdate',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['items'][0]['internalId']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['items'][0]['internalId'],
                            'old_value': GlobalClassCreatePn.payload['tender']['items'][0]['internalId']
                        },
                        "root['releases'][0]['tender']['items'][0]['description']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['items'][0]['description'],
                            'old_value': GlobalClassCreatePn.payload['tender']['items'][0]['description']
                        },
                        "root['releases'][0]['tender']['items'][1]['internalId']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['items'][1]['internalId'],
                            'old_value': GlobalClassCreatePn.payload['tender']['items'][1]['internalId']
                        },
                        "root['releases'][0]['tender']['items'][1]['description']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['items'][1]['description'],
                            'old_value': GlobalClassCreatePn.payload['tender']['items'][1]['description']
                        },
                        "root['releases'][0]['tender']['items'][2]['internalId']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['items'][2]['internalId'],
                            'old_value': GlobalClassCreatePn.payload['tender']['items'][2]['internalId']
                        },
                        "root['releases'][0]['tender']['items'][2]['description']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['items'][2]['description'],
                            'old_value': GlobalClassCreatePn.payload['tender']['items'][2]['description']
                        },
                        "root['releases'][0]['tender']['lots'][0]['internalId']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][0]['internalId'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][0]['internalId']
                        },
                        "root['releases'][0]['tender']['lots'][0]['title']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][0]['title'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][0]['title']
                        },
                        "root['releases'][0]['tender']['lots'][0]['description']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][0]['description'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][0]['description']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['startDate']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][0]['contractPeriod']['startDate'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][0]['contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['endDate']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][0]['contractPeriod']['endDate'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][0]['contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                    'streetAddress'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                    'streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['postalCode']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                    'postalCode'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                    'postalCode']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']["
                        "'region']['id']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                    'addressDetails']['region']['id'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                    'addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']["
                        "'region']['description']": {
                            'new_value': region_data[1],
                            'old_value': actual_pn_release_before_updating['releases'][0]['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['region']['description']

                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']["
                        "'locality']['id']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                    'addressDetails']['locality']['id'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                    'addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']["
                        "'addressDetails']['locality']['description']": {
                            'new_value': locality_data[1],
                            'old_value':
                                actual_pn_release_before_updating['releases'][0]['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['description']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['description']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['description'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][0]['placeOfPerformance']['description']
                        },
                        "root['releases'][0]['tender']['lots'][1]['internalId']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][1]['internalId'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][1]['internalId']
                        },
                        "root['releases'][0]['tender']['lots'][1]['title']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][1]['title'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][1]['title']
                        },
                        "root['releases'][0]['tender']['lots'][1]['description']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][1]['description'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][1]['description']
                        },
                        "root['releases'][0]['tender']['lots'][1]['contractPeriod']['startDate']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][1]['contractPeriod']['startDate'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][1]['contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][1]['contractPeriod']['endDate']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][1]['contractPeriod']['endDate'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][1]['contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']['streetAddress']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][1]['placeOfPerformance'][
                                    'address']['streetAddress'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][1]['placeOfPerformance'][
                                    'address']['streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']['postalCode']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][1]['placeOfPerformance'][
                                    'address']['postalCode'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][1]['placeOfPerformance'][
                                    'address']['postalCode']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']["
                        "'addressDetails']['region']['id']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][1]['placeOfPerformance'][
                                    'address']['addressDetails']['region']['id'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][1]['placeOfPerformance'][
                                    'address']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']["
                        "'addressDetails']['region']['description']": {
                            'new_value': region_data[1],
                            'old_value':
                                actual_pn_release_before_updating['releases'][0]['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['description']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']["
                        "'addressDetails']['locality']['id']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][1]['placeOfPerformance'][
                                    'address']['addressDetails']['locality']['id'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][1]['placeOfPerformance'][
                                    'address']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']["
                        "'addressDetails']['locality']['description']": {
                            'new_value': locality_data[1],
                            'old_value':
                                actual_pn_release_before_updating['releases'][0]['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['description']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['description']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][1]['placeOfPerformance']['description'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][1]['placeOfPerformance']['description']
                        },
                        "root['releases'][0]['tender']['lots'][2]['internalId']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][2]['internalId'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][2]['internalId']
                        },
                        "root['releases'][0]['tender']['lots'][2]['title']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][2]['title'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][2]['title']
                        },
                        "root['releases'][0]['tender']['lots'][2]['description']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][2]['description'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][2]['description']
                        },
                        "root['releases'][0]['tender']['lots'][2]['contractPeriod']['startDate']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][2]['contractPeriod']['startDate'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][2]['contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][2]['contractPeriod']['endDate']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][2]['contractPeriod']['endDate'],
                            'old_value': GlobalClassCreatePn.payload['tender']['lots'][2]['contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][2]['placeOfPerformance']['address']['streetAddress']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][2]['placeOfPerformance'][
                                    'address']['streetAddress'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][2]['placeOfPerformance'][
                                    'address']['streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][2]['placeOfPerformance']['address']['postalCode']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][2]['placeOfPerformance'][
                                    'address']['postalCode'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][2]['placeOfPerformance'][
                                    'address']['postalCode']
                        },
                        "root['releases'][0]['tender']['lots'][2]['placeOfPerformance']['address']["
                        "'addressDetails']['region']['id']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['lots'][2]['placeOfPerformance'][
                                'address']['addressDetails']['region']['id'],
                            'old_value':
                                actual_pn_release_before_updating['releases'][0]['tender']['lots'][2][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][2]['placeOfPerformance']['address']["
                        "'addressDetails']['region']['description']": {
                            'new_value': region_data[1],
                            'old_value':
                                actual_pn_release_before_updating['releases'][0]['tender']['lots'][2][
                                    'placeOfPerformance']['address']['addressDetails']['region']['description']
                        },
                        "root['releases'][0]['tender']['lots'][2]['placeOfPerformance']['address']["
                        "'addressDetails']['locality']['id']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][2]['placeOfPerformance'][
                                    'address']['addressDetails']['locality']['id'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][2]['placeOfPerformance'][
                                    'address']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][2]['placeOfPerformance']['address']["
                        "'addressDetails']['locality']['description']": {
                            'new_value': locality_data[1],
                            'old_value':
                                actual_pn_release_before_updating['releases'][0]['tender']['lots'][2][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['description']
                        },
                        "root['releases'][0]['tender']['lots'][2]['placeOfPerformance']['description']": {
                            'new_value':
                                GlobalClassUpdatePn.payload['tender']['lots'][2]['placeOfPerformance']['description'],
                            'old_value':
                                GlobalClassCreatePn.payload['tender']['lots'][2]['placeOfPerformance']['description']
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['startDate']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['tenderPeriod']['startDate'],
                            'old_value': GlobalClassCreatePn.payload['tender']['tenderPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['documents'][0]['title']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['documents'][0]['title'],
                            'old_value': GlobalClassCreatePn.payload['tender']['documents'][0]['title']
                        },
                        "root['releases'][0]['tender']['documents'][0]['description']": {
                            'new_value': GlobalClassUpdatePn.payload['tender']['documents'][0]['description'],
                            'old_value': GlobalClassCreatePn.payload['tender']['documents'][0]['description']
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
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.4. Check MS release'):
                """
                Compare actual multistage release before updating and actual multistage release after updating.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_updating)),
                              "Actual MS release before updating")

                actual_ms_release_after_updating = requests.get(
                    url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()
                allure.attach(str(json.dumps(actual_pn_release_after_updating)),
                              "Actual MS release after updating")

                compare_releases = dict(
                    DeepDiff(actual_ms_release_before_updating, actual_ms_release_after_updating))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_after_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdatePn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreatePn.actual_ms_release['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['description']": {
                            "new_value": GlobalClassUpdatePn.payload['planning']['budget']['description'],
                            "old_value": GlobalClassCreatePn.payload['planning']['budget']['description']
                        },
                        "root['releases'][0]['planning']['rationale']": {
                            "new_value": GlobalClassUpdatePn.payload['planning']['rationale'],
                            "old_value": GlobalClassCreatePn.payload['planning']['rationale']
                        },
                        "root['releases'][0]['tender']['title']": {
                            "new_value": GlobalClassUpdatePn.payload['tender']['title'],
                            "old_value": GlobalClassCreatePn.payload['tender']['title']
                        },
                        "root['releases'][0]['tender']['description']": {
                            "new_value": GlobalClassUpdatePn.payload['tender']['description'],
                            "old_value": GlobalClassCreatePn.payload['tender']['description']
                        },
                        "root['releases'][0]['tender']['procurementMethodRationale']": {
                            "new_value": GlobalClassUpdatePn.payload['tender']['procurementMethodRationale'],
                            "old_value": GlobalClassCreatePn.payload['tender']['procurementMethodRationale']
                        },
                        "root['releases'][0]['tender']['procurementMethodAdditionalInfo']": {
                            "new_value": GlobalClassUpdatePn.payload['tender']['procurementMethodAdditionalInfo'],
                            "old_value": GlobalClassCreatePn.payload['tender']['procurementMethodAdditionalInfo']
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
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.5. Check Ei release'):
                """
                Compare actual expenditure item release before updating and actual expenditure item release
                after updating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)),
                              "Actual Ei release before pn updating")

                actual_ei_release_after_updating = requests.get(
                    url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateEi.ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_updating)),
                              "Actual Ei release after pn updating")

                compare_releases = dict(
                    DeepDiff(actual_ei_release_before_updating, actual_ei_release_after_updating))

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
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.6. Check Fs release'):
                """
                Compare actual financial source release before updating and actual financial source release
                after updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)),
                              "Actual Fs release after pn creating")

                actual_fs_release_after_updating = requests.get(
                    url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateFs.fs_id}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_updating)),
                              "Actual Fs release after pn updating")

                compare_releases = dict(
                    DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating))

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
                                operation_id=GlobalClassUpdatePn.operation_id)
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
                            operation_id=GlobalClassUpdatePn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check Pn and MS releases data after Pn updating without optional fields, but '
                  'with lot and item (without optional fields).')
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

            Requests().create_pn(
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

            actual_pn_release_before_updating = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()
            GlobalClassCreatePn.actual_pn_release = actual_pn_release_before_updating

            actual_ms_release_before_updating = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

            actual_ei_release_before_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

        with allure.step('# 7. Authorization platform one: update Pn'):
            """
            Tender platform authorization for update planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdatePn.access_token)

        with allure.step('# 8. Send request to update Pn'):
            """
            Send api request on BPE host for planning notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassUpdatePn.payload = \
                pn_payload.update_pn_obligatory_data_model_with_lots_and_items_obligatory(
                    quantity_of_lot_object=1,
                    quantity_of_item_object=1,
                    need_to_set_permanent_id_for_lots_array=False,
                    need_to_set_permanent_id_for_items_array=False
                )
            synchronous_result_of_sending_the_request = Requests().update_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdatePn.access_token,
                x_operation_id=GlobalClassUpdatePn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassUpdatePn.payload
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
                GlobalClassUpdatePn.feed_point_message = \
                    KafkaMessage(GlobalClassUpdatePn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassUpdatePn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdatePn.operation_id).update_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdatePn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    pn_id=GlobalClassCreatePn.pn_id
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 9.3. Check Pn release'):
                """
                Compare actual planning notice release before updating and actual planning release after updating.
                """
                allure.attach(str(json.dumps(actual_pn_release_before_updating)),
                              "Actual Pn release before updating")

                actual_pn_release_after_updating = requests.get(
                    url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_id}").json()

                allure.attach(str(json.dumps(actual_pn_release_after_updating)),
                              "Actual Pn release after updating")

                compare_releases = DeepDiff(
                    actual_pn_release_before_updating, actual_pn_release_after_updating)

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                country_data = get_value_from_country_csv(
                    country=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['country']['id'],
                    language=GlobalClassMetadata.language
                )

                region_data = get_value_from_region_csv(
                    region=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['region']['id'],
                    country=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['country']['id'],
                    language=GlobalClassMetadata.language
                )

                locality_data = get_value_from_locality_csv(
                    locality=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['locality']['id'],
                    region=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['region']['id'],
                    country=GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance']['address'][
                        'addressDetails']['country']['id'],
                    language=GlobalClassMetadata.language
                )

                cpv_data = get_value_from_classification_cpv_dictionary_xls(
                    cpv=GlobalClassUpdatePn.payload['tender']['items'][0]['classification']['id'],
                    language=GlobalClassMetadata.language
                )

                unit_data = get_value_from_classification_unit_dictionary_csv(
                    unit_id=GlobalClassUpdatePn.payload['tender']['items'][0]['unit']['id'],
                    language=GlobalClassMetadata.language
                )

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['tender']['items'], ['releases'][0]['tender']['lots']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_id}-"
                                         f"{actual_pn_release_after_updating['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreatePn.pn_id}-"
                                         f"{actual_pn_release_before_updating['releases'][0]['id'][46:59]}",
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdatePn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreatePn.actual_pn_release['releases'][0]['date']
                        },
                        "root['releases'][0]['tag'][0]": {
                            "new_value": "planningUpdate",
                            "old_value": "planning"
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['startDate']": {
                            "new_value": GlobalClassUpdatePn.payload['tender']['tenderPeriod']['startDate'],
                            "old_value": GlobalClassCreatePn.payload['tender']['tenderPeriod']['startDate']
                        }
                    }
                }

                try:
                    """
                    Check on 'releases.tender.lots.id' is uuid.
                    """
                    is_it_uuid(
                        uuid_to_test=actual_pn_release_after_updating['releases'][0]['tender']['lots'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your 'releases.tender.lots.id' in Pn release: 'releases.tender.lots.id' "
                        "in Pn release must be uuid version 1")

                try:
                    """
                    Check on 'releases.tender.items.id' is uuid.
                    """
                    is_it_uuid(
                        uuid_to_test=actual_pn_release_after_updating['releases'][0]['tender']['items'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your 'releases.tender.items.id' in Pn release: 'releases.tender.lots.id' "
                        "in Pn release must be uuid version 1")

                expected_lots_array = [
                    {
                        "id": actual_pn_release_after_updating['releases'][0]['tender']['lots'][0]['id'],
                        "title": GlobalClassUpdatePn.payload['tender']['lots'][0]['title'],
                        "description": GlobalClassUpdatePn.payload['tender']['lots'][0]['description'],
                        "status": "planning",
                        "statusDetails": "empty",
                        "value": {
                            "amount": GlobalClassUpdatePn.payload['tender']['lots'][0]['value']['amount'],
                            "currency": GlobalClassUpdatePn.payload['tender']['lots'][0]['value']['currency']
                        },
                        "recurrentProcurement": [
                            {
                                "isRecurrent": False
                            }],
                        "renewals": [
                            {
                                "hasRenewals": False
                            }],
                        "variants": [
                            {
                                "hasVariants": False
                            }],
                        "contractPeriod": {
                            "startDate":
                                GlobalClassUpdatePn.payload['tender']['lots'][0]['contractPeriod']['startDate'],
                            "endDate":
                                GlobalClassUpdatePn.payload['tender']['lots'][0]['contractPeriod']['endDate']
                        },
                        "placeOfPerformance": {
                            "address": {
                                "streetAddress":
                                    GlobalClassUpdatePn.payload['tender']['lots'][0]['placeOfPerformance'][
                                        'address']['streetAddress'],
                                "addressDetails": {
                                    "country": {
                                        "scheme": country_data[2],
                                        "id": country_data[0],
                                        "description": country_data[1],
                                        "uri": country_data[3]
                                    },
                                    "region": {
                                        "scheme": region_data[2],
                                        "id": region_data[0],
                                        "description": region_data[1],
                                        "uri": region_data[3]
                                    },
                                    "locality": {
                                        "scheme": locality_data[2],
                                        "id": locality_data[0],
                                        "description": locality_data[1],
                                        "uri": locality_data[3]
                                    }}
                            }
                        },
                        "options": [{
                            "hasOptions": False
                        }]
                    }
                ]

                expected_items_array = [
                    {
                        "id": actual_pn_release_after_updating['releases'][0]['tender']['items'][0]['id'],
                        "description": GlobalClassUpdatePn.payload['tender']['items'][0]['description'],
                        "classification": {
                            "scheme": "CPV",
                            "id": cpv_data[0],
                            "description": cpv_data[1]
                        },
                        "quantity": GlobalClassUpdatePn.payload['tender']['items'][0]['quantity'],
                        "unit": {
                            "name": unit_data[1],
                            "id": unit_data[0]
                        },
                        "relatedLot": actual_pn_release_after_updating['releases'][0]['tender']['lots'][0]['id']
                    }
                ]
                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_lots_array,
                    actual_result=actual_pn_release_after_updating['releases'][0]['tender']['lots']
                )) == str(True)

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_items_array,
                    actual_result=actual_pn_release_after_updating['releases'][0]['tender']['items']
                )) == str(True)

            with allure.step('# 9.4. Check MS release'):
                """
                Compare actual multistage release before updating and actual multistage release after updating.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_updating)),
                              "Actual MS release before updating")

                actual_ms_release_after_updating = requests.get(
                    url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()
                allure.attach(str(json.dumps(actual_pn_release_after_updating)),
                              "Actual MS release after updating")

                compare_releases = dict(
                    DeepDiff(actual_ms_release_before_updating, actual_ms_release_after_updating))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_after_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdatePn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreatePn.actual_ms_release['releases'][0]['date']
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
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.5. Check Ei release'):
                """
                Compare actual expenditure item release before updating and actual expenditure item release
                after updating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)),
                              "Actual Ei release before pn updating")

                actual_ei_release_after_updating = requests.get(
                    url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateEi.ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_updating)),
                              "Actual Ei release after pn updating")

                compare_releases = dict(
                    DeepDiff(actual_ei_release_before_updating, actual_ei_release_after_updating))

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
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.6. Check Fs release'):
                """
                Compare actual financial source release before updating and actual financial source release
                after updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)),
                              "Actual Fs release after pn creating")

                actual_fs_release_after_updating = requests.get(
                    url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateFs.fs_id}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_updating)),
                              "Actual Fs release after pn updating")

                compare_releases = dict(
                    DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating))

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
                                operation_id=GlobalClassUpdatePn.operation_id)
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
                            operation_id=GlobalClassUpdatePn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check Pn and MS releases data after Pn updating without optional fields.')
    def test_check_pn_ms_releases_three(self):
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

            Requests().create_pn(
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

            actual_pn_release_before_updating = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()
            GlobalClassCreatePn.actual_pn_release = actual_pn_release_before_updating

            actual_ms_release_before_updating = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            actual_fs_release_before_updating = requests.get(
                url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateFs.fs_id}").json()

            actual_ei_release_before_updating = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()

        with allure.step('# 7. Authorization platform one: update Pn'):
            """
            Tender platform authorization for update planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdatePn.access_token)

        with allure.step('# 8. Send request to update Pn'):
            """
            Send api request on BPE host for planning notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassUpdatePn.payload = \
                pn_payload.update_pn_obligatory_data_model_without_lots_and_items()
            synchronous_result_of_sending_the_request = Requests().update_pn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdatePn.access_token,
                x_operation_id=GlobalClassUpdatePn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassUpdatePn.payload
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
                GlobalClassUpdatePn.feed_point_message = \
                    KafkaMessage(GlobalClassUpdatePn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassUpdatePn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdatePn.operation_id).update_pn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdatePn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    pn_id=GlobalClassCreatePn.pn_id
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 9.3. Check Pn release'):
                """
                Compare actual planning notice release before updating and actual planning release after updating.
                """
                allure.attach(str(json.dumps(actual_pn_release_before_updating)),
                              "Actual Pn release before updating")

                actual_pn_release_after_updating = requests.get(
                    url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_id}").json()

                allure.attach(str(json.dumps(actual_pn_release_after_updating)),
                              "Actual Pn release after updating")

                compare_releases = dict(DeepDiff(
                    actual_pn_release_before_updating, actual_pn_release_after_updating))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_id}-"
                                         f"{actual_pn_release_after_updating['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreatePn.pn_id}-"
                                         f"{actual_pn_release_before_updating['releases'][0]['id'][46:59]}",
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdatePn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreatePn.actual_pn_release['releases'][0]['date']
                        },
                        "root['releases'][0]['tag'][0]": {
                            "new_value": "planningUpdate",
                            "old_value": "planning"
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['startDate']": {
                            "new_value": GlobalClassUpdatePn.payload['tender']['tenderPeriod']['startDate'],
                            "old_value": GlobalClassCreatePn.payload['tender']['tenderPeriod']['startDate']
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
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.4. Check MS release'):
                """
                Compare actual multistage release before updating and actual multistage release after updating.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_updating)),
                              "Actual MS release before updating")

                actual_ms_release_after_updating = requests.get(
                    url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()
                allure.attach(str(json.dumps(actual_pn_release_after_updating)),
                              "Actual MS release after updating")

                compare_releases = dict(
                    DeepDiff(actual_ms_release_before_updating, actual_ms_release_after_updating))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_after_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{actual_ms_release_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdatePn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreatePn.actual_ms_release['releases'][0]['date']
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
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.5. Check Ei release'):
                """
                Compare actual expenditure item release before updating and actual expenditure item release 
                after updating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)),
                              "Actual Ei release before pn updating")

                actual_ei_release_after_updating = requests.get(
                    url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateEi.ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_updating)),
                              "Actual Ei release after pn updating")

                compare_releases = dict(
                    DeepDiff(actual_ei_release_before_updating, actual_ei_release_after_updating))

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
                                operation_id=GlobalClassUpdatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 9.6. Check Fs release'):
                """
                Compare actual financial source release before updating and actual financial source release 
                after updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_updating)),
                              "Actual Fs release after pn creating")

                actual_fs_release_after_updating = requests.get(
                    url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateFs.fs_id}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_updating)),
                              "Actual Fs release after pn updating")

                compare_releases = dict(
                    DeepDiff(actual_fs_release_before_updating, actual_fs_release_after_updating))

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
                                operation_id=GlobalClassUpdatePn.operation_id)
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
                            operation_id=GlobalClassUpdatePn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreatePn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
