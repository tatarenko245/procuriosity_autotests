import copy
import json
import time
import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn, GlobalClassUpdateCnOnPn
from tests.utils.PayloadModel.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.EI.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.FS.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.PN.pn_prepared_payload import PnPreparePayload

from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions import compare_actual_result_and_expected_result, \
    get_value_from_classification_unit_dictionary_csv, get_value_from_region_csv, get_value_from_locality_csv, \
    get_contract_period_for_ms_release, get_value_from_cpvs_dictionary_csv
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.my_requests import Requests


@allure.parent_suite('Tendering')
@allure.suite('EV')
@allure.sub_suite('BPE: Update CnOnPn')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=1433017847',
                 name='Google sheets: Update CnOnPn')
class TestCreateCnOnPn:
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
        if environment == "dev":
            GlobalClassMetadata.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
        elif environment == "sandbox":
            GlobalClassMetadata.metadata_document_url = "http://storage.eprocurement.systems/get"
        GlobalClassMetadata.database = CassandraSession(
            cassandra_username=GlobalClassMetadata.cassandra_username,
            cassandra_password=GlobalClassMetadata.cassandra_password,
            cassandra_cluster=GlobalClassMetadata.cassandra_cluster)

    @allure.title('Check status code and message from Kafka topic after CnOnPn creating')
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
            fs_payload = copy.deepcopy(FsPreparePayload())
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
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=2,
                    quantity_of_item_object=2)

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

            GlobalClassCreatePn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

        with allure.step('# 7. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
        with allure.step('# 8. Send request to create CnOnPn'):
            """
            Send api request on BPE host for contract notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True
                )

            Requests().create_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateCnOnPn.access_token,
                x_operation_id=GlobalClassCreateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassCreateCnOnPn.payload
            )
            GlobalClassCreateCnOnPn.feed_point_message = \
                KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()

            GlobalClassCreateCnOnPn.ev_id = \
                GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']

            GlobalClassCreateCnOnPn.actual_pn_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()

            GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

        with allure.step('# 9. Authorization platform one: update CnOnPn'):
            """
            Tender platform authorization for update contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateCnOnPn.access_token)
        with allure.step('# 10. Send request to update CnOnPn'):
            """
            Send api request on BPE host for contract notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassUpdateCnOnPn.payload = \
                cnonpn_payload_class.update_cnonpn_full_data_model_with_lots_items_documents_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True,
                    need_to_set_permanent_id_for_electronic_auction=True
                )

            synchronous_result_of_sending_the_request = Requests().update_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateCnOnPn.access_token,
                x_operation_id=GlobalClassUpdateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassUpdateCnOnPn.payload
            )
        with allure.step('# 11. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 11.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """

                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 11.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassUpdateCnOnPn.feed_point_message = \
                    KafkaMessage(GlobalClassUpdateCnOnPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassUpdateCnOnPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateCnOnPn.operation_id).update_cnonpn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateCnOnPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
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

                        GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassUpdateCnOnPn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check EV and MS releases data after CnOnPn updating with full data model with 2 lots and 2 '
                  'items criteria, conversions, documents, auction')
    def test_check_ev_ms_releases_one(self):
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
            fs_payload = copy.deepcopy(FsPreparePayload())
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
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=2,
                    quantity_of_item_object=2)

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

            GlobalClassCreatePn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()
        with allure.step('# 7. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
        with allure.step('# 8. Send request to create CnOnPn'):
            """
            Send api request on BPE host for contract notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True
                )

            Requests().create_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateCnOnPn.access_token,
                x_operation_id=GlobalClassCreateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassCreateCnOnPn.payload
            )

            GlobalClassCreateCnOnPn.feed_point_message = \
                KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()

            GlobalClassCreateCnOnPn.ev_id = \
                GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']

            GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

            GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()
        with allure.step('# 9. Authorization platform one: update CnOnPn'):
            """
            Tender platform authorization for update contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateCnOnPn.access_token)
        with allure.step('# 10. Send request to update CnOnPn'):
            """
            Send api request on BPE host for contract notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassUpdateCnOnPn.payload = \
                cnonpn_payload_class.update_cnonpn_full_data_model_with_lots_items_documents_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True,
                    need_to_set_permanent_id_for_electronic_auction=True
                )

            synchronous_result_of_sending_the_request = Requests().update_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateCnOnPn.access_token,
                x_operation_id=GlobalClassUpdateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassUpdateCnOnPn.payload
            )
        with allure.step('# 11. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 11.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 11.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassUpdateCnOnPn.feed_point_message = \
                    KafkaMessage(GlobalClassUpdateCnOnPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassUpdateCnOnPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateCnOnPn.operation_id).update_cnonpn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateCnOnPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")

                    GlobalClassUpdateCnOnPn.actual_ev_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreateCnOnPn.ev_id}").json()

                    GlobalClassUpdateCnOnPn.actual_ms_release = requests.get(
                        url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_ocid}").json()

                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 11.3. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
                              "Actual EV release before updating")

                allure.attach(str(json.dumps(GlobalClassUpdateCnOnPn.actual_ev_release)),
                              "Actual EV release after updating")

                compare_releases = DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, GlobalClassUpdateCnOnPn.actual_ev_release)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['tender']['amendments']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassUpdateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdateCnOnPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            "new_value": "tenderAmendment",
                            "old_value": "tender"
                        },
                        "root['releases'][0]['tender']['items'][0]['internalId']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['internalId'],
                            "old_value": GlobalClassCreatePn.payload['tender']['items'][0]['internalId']
                        },
                        "root['releases'][0]['tender']['items'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['description'],
                            "old_value": GlobalClassCreatePn.payload['tender']['items'][0]['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['quantity']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['quantity'],
                            "old_value": GlobalClassCreatePn.payload['tender']['items'][0]['quantity']
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                            "new_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassCreatePn.payload['tender']['items'][0]['unit']['id'],
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                            "old_value": GlobalClassCreatePn.payload['tender']['items'][0]['unit']['id']
                        },
                        "root['releases'][0]['tender']['items'][1]['internalId']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['internalId'],
                            "old_value": GlobalClassCreatePn.payload['tender']['items'][1]['internalId']
                        },
                        "root['releases'][0]['tender']['items'][1]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['description'],
                            "old_value": GlobalClassCreatePn.payload['tender']['items'][1]['description']
                        },
                        "root['releases'][0]['tender']['items'][1]['quantity']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['quantity'],
                            "old_value": GlobalClassCreatePn.payload['tender']['items'][1]['quantity']
                        },
                        "root['releases'][0]['tender']['items'][1]['unit']['name']": {
                            "new_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['unit']['id'],
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassCreatePn.payload['tender']['items'][1]['unit']['id'],
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['items'][1]['unit']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['unit']['id'],
                            "old_value": GlobalClassCreatePn.payload['tender']['items'][1]['unit']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['internalId']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0]['internalId'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0]['internalId']
                        },
                        "root['releases'][0]['tender']['lots'][0]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0]['title'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0]['title']
                        },
                        "root['releases'][0]['tender']['lots'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0]['description'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0]['description']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['startDate'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0][
                                'contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['endDate'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0][
                                'contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['streetAddress'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['postalCode']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['postalCode'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0]
                            ['placeOfPerformance']['address']['postalCode']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['region']['id'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['description']": {
                            "new_value": get_value_from_region_csv(
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_region_csv(
                                region=GlobalClassCreatePn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['description']": {
                            "new_value": get_value_from_locality_csv(
                                locality=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_locality_csv(
                                locality=GlobalClassCreatePn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassCreatePn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['description'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0][
                                'placeOfPerformance']['description']
                        },
                        "root['releases'][0]['tender']['lots'][1]['internalId']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1]['internalId'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][1]['internalId']
                        },
                        "root['releases'][0]['tender']['lots'][1]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1]['title'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][1]['title']
                        },
                        "root['releases'][0]['tender']['lots'][1]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1]['description'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][1]['description']
                        },
                        "root['releases'][0]['tender']['lots'][1]['contractPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['startDate'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][1][
                                'contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][1]['contractPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['endDate'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][1]
                            ['contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']['streetAddress']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['streetAddress'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']['postalCode']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['postalCode'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['postalCode']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['region']['id'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['description']": {
                            "new_value": get_value_from_region_csv(
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_region_csv(
                                region=GlobalClassCreatePn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['description']": {
                            "new_value": get_value_from_locality_csv(
                                locality=GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_locality_csv(
                                locality=GlobalClassCreatePn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['description'],
                            "old_value": GlobalClassCreatePn.payload['tender']['lots'][1][
                                'placeOfPerformance']['description']
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['tenderPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['enquiryPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['documents'][0]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][0]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][0]['title']
                        },
                        "root['releases'][0]['tender']['documents'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][0]['description']
                        },
                        "root['releases'][0]['tender']['documents'][1]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][1]['title']
                        },
                        "root['releases'][0]['tender']['documents'][1]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][1]['description']
                        },
                        "root['releases'][0]['tender']['documents'][1]['relatedLots'][0]": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['relatedLots'][0],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][1]['relatedLots'][0]
                        },
                        "root['releases'][0]['tender']['electronicAuctions']['details'][0]"
                        "['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['electronicAuctions'][
                                'details'][0]['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['electronicAuctions'][
                                'details'][0]['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount']
                        },
                        "root['releases'][0]['tender']['electronicAuctions']['details'][1]"
                        "['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['electronicAuctions'][
                                'details'][1]['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['electronicAuctions'][
                                'details'][1]['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount']
                        }
                    },
                    "iterable_item_added": {
                        "root['releases'][0]['tender']['items'][0]['additionalClassifications'][1]": {
                            "scheme": "CPVS",
                            "id": GlobalClassUpdateCnOnPn.payload['tender']['items'][0][
                                'additionalClassifications'][0]['id'],
                            "description": get_value_from_cpvs_dictionary_csv(
                                cpvs=GlobalClassUpdateCnOnPn.payload['tender']['items'][0][
                                    'additionalClassifications'][0]['id'],
                                language=GlobalClassMetadata.language)[2]
                        },
                        "root['releases'][0]['tender']['items'][1]['additionalClassifications'][1]": {
                            "scheme": "CPVS",
                            "id": GlobalClassUpdateCnOnPn.payload['tender']['items'][1][
                                'additionalClassifications'][0]['id'],
                            "description": get_value_from_cpvs_dictionary_csv(
                                cpvs=GlobalClassUpdateCnOnPn.payload['tender']['items'][1][
                                    'additionalClassifications'][0]['id'],
                                language=GlobalClassMetadata.language)[2]
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
                                operation_id=GlobalClassUpdateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
            with allure.step('# 11.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
                              "Actual MS release before CnOnPn updating")
                allure.attach(str(json.dumps(GlobalClassUpdateCnOnPn.actual_ms_release)),
                              "Actual MS release after CnOnPn updating")

                compare_releases = dict(DeepDiff(GlobalClassCreateCnOnPn.actual_ms_release,
                                                 GlobalClassUpdateCnOnPn.actual_ms_release))
                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassUpdateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdateCnOnPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['description']": {
                            'new_value': GlobalClassUpdateCnOnPn.payload['planning']['budget']['description'],
                            'old_value': GlobalClassCreatePn.payload['planning']['budget']['description']
                        },
                        "root['releases'][0]['planning']['rationale']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['planning']['rationale'],
                            "old_value": GlobalClassCreatePn.payload['planning']['rationale']
                        },
                        "root['releases'][0]['tender']['procurementMethodRationale']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['procurementMethodRationale'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['procurementMethodRationale']
                        },
                        "root['releases'][0]['tender']['contractPeriod']['startDate']": {
                            'new_value': get_contract_period_for_ms_release(
                                lots_array=GlobalClassUpdateCnOnPn.payload['tender']['lots'])[0],
                            'old_value': get_contract_period_for_ms_release(
                                lots_array=GlobalClassCreatePn.payload['tender']['lots'])[0]
                        },
                        "root['releases'][0]['tender']['contractPeriod']['endDate']": {
                            'new_value': get_contract_period_for_ms_release(
                                lots_array=GlobalClassUpdateCnOnPn.payload['tender']['lots'])[1],
                            'old_value': get_contract_period_for_ms_release(
                                lots_array=GlobalClassCreatePn.payload['tender']['lots'])[1]
                        },
                        "root['releases'][0]['tender']['procurementMethodAdditionalInfo']": {
                            'new_value': GlobalClassUpdateCnOnPn.payload['tender']['procurementMethodAdditionalInfo'],
                            'old_value': GlobalClassCreateCnOnPn.payload['tender']['procurementMethodAdditionalInfo']
                        }
                    }
                }

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

                        GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id)
                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check EV and MS releases data after CnOnPn updating with full data model with 2 lots and 2 '
                  'items criteria, conversions, documents, auction')
    def test_check_ev_ms_releases_two(self):
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
            fs_payload = copy.deepcopy(FsPreparePayload())
            GlobalClassCreateFs.payload = fs_payload.create_fs_obligatory_data_model_treasury_money()
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

            GlobalClassCreatePn.actual_pn_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()

            GlobalClassCreatePn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()
        with allure.step('# 7. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
        with allure.step('# 8. Send request to create CnOnPn'):
            """
            Send api request on BPE host for contract notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_obligatory_data_model_with_lots_items_documents(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=1,
                    quantity_of_items_object=1,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release,
                    need_to_set_permanent_id_for_lots_array=False,
                    need_to_set_permanent_id_for_items_array=False,
                    need_to_set_permanent_id_for_documents_array=False
                )

            Requests().create_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateCnOnPn.access_token,
                x_operation_id=GlobalClassCreateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassCreateCnOnPn.payload
            )

            GlobalClassCreateCnOnPn.feed_point_message = \
                KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()

            GlobalClassCreateCnOnPn.ev_id = \
                GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']

            GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

            GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()
        with allure.step('# 9. Authorization platform one: update CnOnPn'):
            """
            Tender platform authorization for update contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateCnOnPn.access_token)
        with allure.step('# 10. Send request to update CnOnPn'):
            """
            Send api request on BPE host for contract notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassUpdateCnOnPn.payload = \
                cnonpn_payload_class.update_cnonpn_obligatory_data_model_with_lots_items_documents_without_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=1,
                    quantity_of_items_object=1,
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True
                )

            synchronous_result_of_sending_the_request = Requests().update_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateCnOnPn.access_token,
                x_operation_id=GlobalClassUpdateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassUpdateCnOnPn.payload
            )

        with allure.step('# 11. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 11.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 11.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassUpdateCnOnPn.feed_point_message = \
                    KafkaMessage(GlobalClassUpdateCnOnPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassUpdateCnOnPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateCnOnPn.operation_id).update_cnonpn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateCnOnPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")

                    GlobalClassUpdateCnOnPn.actual_ev_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreateCnOnPn.ev_id}").json()

                    GlobalClassUpdateCnOnPn.actual_ms_release = requests.get(
                        url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_ocid}").json()

                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 11.3. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
                              "Actual EV release before updating")

                allure.attach(str(json.dumps(GlobalClassUpdateCnOnPn.actual_ev_release)),
                              "Actual EV release after updating")

                compare_releases = DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, GlobalClassUpdateCnOnPn.actual_ev_release)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['tender']['amendments']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassUpdateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdateCnOnPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            "new_value": "tenderAmendment",
                            "old_value": "tender"
                        },
                        "root['releases'][0]['tender']['items'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][0]['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['quantity']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['quantity'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][0]['quantity']
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                            "new_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassCreateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][0]['unit']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0]['title']
                        },
                        "root['releases'][0]['tender']['lots'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0]['description']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['startDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['streetAddress'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['region']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['description']": {
                            "new_value": get_value_from_region_csv(
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_region_csv(
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['description']": {
                            "new_value": get_value_from_locality_csv(
                                locality=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_locality_csv(
                                locality=GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['tenderPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['enquiryPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['documents'][0]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][0]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][0]['title']
                        },
                        "root['releases'][0]['tender']['documents'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][0]['description']
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
                                operation_id=GlobalClassUpdateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
            with allure.step('# 11.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
                              "Actual MS release before CnOnPn updating")
                allure.attach(str(json.dumps(GlobalClassUpdateCnOnPn.actual_ms_release)),
                              "Actual MS release after CnOnPn updating")

                compare_releases = dict(DeepDiff(GlobalClassCreateCnOnPn.actual_ms_release,
                                                 GlobalClassUpdateCnOnPn.actual_ms_release))
                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassUpdateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdateCnOnPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['contractPeriod']['startDate']": {
                            'new_value': get_contract_period_for_ms_release(
                                lots_array=GlobalClassUpdateCnOnPn.payload['tender']['lots'])[0],
                            'old_value': get_contract_period_for_ms_release(
                                lots_array=GlobalClassCreateCnOnPn.payload['tender']['lots'])[0]
                        },
                        "root['releases'][0]['tender']['contractPeriod']['endDate']": {
                            'new_value': get_contract_period_for_ms_release(
                                lots_array=GlobalClassUpdateCnOnPn.payload['tender']['lots'])[1],
                            'old_value': get_contract_period_for_ms_release(
                                lots_array=GlobalClassCreateCnOnPn.payload['tender']['lots'])[1]
                        }
                    }
                }

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

                        GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check EV and MS releases data after CnOnPn updating based on model without optional fields '
                  'for creating and full data model for updating')
    def test_check_ev_ms_releases_three(self):
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
            fs_payload = copy.deepcopy(FsPreparePayload())
            GlobalClassCreateFs.payload = fs_payload.create_fs_obligatory_data_model_treasury_money()
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

            GlobalClassCreatePn.actual_pn_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()

            GlobalClassCreatePn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()
        with allure.step('# 7. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
        with allure.step('# 8. Send request to create CnOnPn'):
            """
            Send api request on BPE host for contract notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_obligatory_data_model_with_lots_items_documents(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release,
                    need_to_set_permanent_id_for_lots_array=False,
                    need_to_set_permanent_id_for_items_array=False,
                    need_to_set_permanent_id_for_documents_array=False
                )

            Requests().create_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateCnOnPn.access_token,
                x_operation_id=GlobalClassCreateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassCreateCnOnPn.payload
            )

            GlobalClassCreateCnOnPn.feed_point_message = \
                KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()

            GlobalClassCreateCnOnPn.ev_id = \
                GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']

            GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

            GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()
        with allure.step('# 9. Authorization platform one: update CnOnPn'):
            """
            Tender platform authorization for update contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateCnOnPn.access_token)
        with allure.step('# 10. Send request to update CnOnPn'):
            """
            Send api request on BPE host for contract notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassUpdateCnOnPn.payload = \
                cnonpn_payload_class.update_cnonpn_full_data_model_with_lots_items_documents_without_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True
                )

            synchronous_result_of_sending_the_request = Requests().update_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateCnOnPn.access_token,
                x_operation_id=GlobalClassUpdateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassUpdateCnOnPn.payload
            )

        with allure.step('# 11. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 11.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 11.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassUpdateCnOnPn.feed_point_message = \
                    KafkaMessage(GlobalClassUpdateCnOnPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassUpdateCnOnPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateCnOnPn.operation_id).update_cnonpn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateCnOnPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")

                    GlobalClassUpdateCnOnPn.actual_ev_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreateCnOnPn.ev_id}").json()

                    GlobalClassUpdateCnOnPn.actual_ms_release = requests.get(
                        url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_ocid}").json()

                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 11.3. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
                              "Actual EV release before updating")

                allure.attach(str(json.dumps(GlobalClassUpdateCnOnPn.actual_ev_release)),
                              "Actual EV release after updating")

                compare_releases = DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, GlobalClassUpdateCnOnPn.actual_ev_release)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['tender']['amendments'], ['releases'][0]['tender']"
                                             "['items'][0]['internalId'], ['releases'][0]['tender']['items'][0]"
                                             "['additionalClassifications'], ['releases'][0]['tender']['items'][1]"
                                             "['internalId'], ['releases'][0]['tender']['items'][1]"
                                             "['additionalClassifications'], ['releases'][0]['tender']['lots'][0]"
                                             "['internalId'], ['releases'][0]['tender']['lots'][0]"
                                             "['placeOfPerformance']['description'], ['releases'][0]['tender']"
                                             "['lots'][0]['placeOfPerformance']['address']['postalCode'], "
                                             "['releases'][0]['tender']['lots'][1]['internalId'], "
                                             "['releases'][0]['tender']['lots'][1]['placeOfPerformance']"
                                             "['description'], ['releases'][0]['tender']['lots'][1]"
                                             "['placeOfPerformance']['address']['postalCode']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassUpdateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdateCnOnPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            "new_value": "tenderAmendment",
                            "old_value": "tender"
                        },
                        "root['releases'][0]['tender']['items'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][0]['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['quantity']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['quantity'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][0]['quantity']
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                            "new_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassCreateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][0]['unit']['id']
                        },
                        "root['releases'][0]['tender']['items'][1]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][1]['description']
                        },
                        "root['releases'][0]['tender']['items'][1]['quantity']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['quantity'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][1]['quantity']
                        },
                        "root['releases'][0]['tender']['items'][1]['unit']['name']": {
                            "new_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['unit']['id'],
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassCreateCnOnPn.payload['tender']['items'][1]['unit']['id'],
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['items'][1]['unit']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['unit']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][1]['unit']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0]['title']
                        },
                        "root['releases'][0]['tender']['lots'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0]['description']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['startDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['streetAddress'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['region']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['description']": {
                            "new_value": get_value_from_region_csv(
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_region_csv(
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['description']": {
                            "new_value": get_value_from_locality_csv(
                                locality=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_locality_csv(
                                locality=GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][1]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1]['title']
                        },
                        "root['releases'][0]['tender']['lots'][1]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1]['description']
                        },
                        "root['releases'][0]['tender']['lots'][1]['contractPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['startDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][1]['contractPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']['streetAddress']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['streetAddress'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['region']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['description']": {
                            "new_value": get_value_from_region_csv(
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_region_csv(
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['description']": {
                            "new_value": get_value_from_locality_csv(
                                locality=GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_locality_csv(
                                locality=GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['tenderPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['enquiryPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['documents'][0]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][0]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][0]['title']
                        },
                        "root['releases'][0]['tender']['documents'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][0]['description']
                        }
                    },
                    "iterable_item_added": {
                        "root['releases'][0]['tender']['documents'][1]": {
                            "id": GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['id'],
                            "documentType": GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['documentType'],
                            "title": GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['title'],
                            "description": GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['description'],
                            "url": f"{GlobalClassMetadata.metadata_document_url}/"
                                   f"{GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['id']}",
                            "datePublished": GlobalClassUpdateCnOnPn.feed_point_message['data']['operationDate'],
                            "relatedLots": [
                                GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['relatedLots'][0]]
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
                                operation_id=GlobalClassUpdateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
            with allure.step('# 11.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
                              "Actual MS release before CnOnPn updating")
                allure.attach(str(json.dumps(GlobalClassUpdateCnOnPn.actual_ms_release)),
                              "Actual MS release after CnOnPn updating")

                compare_releases = DeepDiff(GlobalClassCreateCnOnPn.actual_ms_release,
                                            GlobalClassUpdateCnOnPn.actual_ms_release)

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

            expected_result = {
                "dictionary_item_added": "['releases'][0]['planning']['rationale'], "
                                         "['releases'][0]['planning']['budget']['description'], "
                                         "['releases'][0]['tender']['procurementMethodRationale'], "
                                         "['releases'][0]['tender']['procurementMethodAdditionalInfo']",
                "values_changed": {
                    "root['releases'][0]['id']": {
                        "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                     f"{GlobalClassUpdateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}",
                        "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                     f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}"
                    },
                    "root['releases'][0]['date']": {
                        "new_value": GlobalClassUpdateCnOnPn.feed_point_message['data']['operationDate'],
                        "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                    },
                    "root['releases'][0]['tender']['contractPeriod']['startDate']": {
                        'new_value': get_contract_period_for_ms_release(
                            lots_array=GlobalClassUpdateCnOnPn.payload['tender']['lots'])[0],
                        'old_value': get_contract_period_for_ms_release(
                            lots_array=GlobalClassCreateCnOnPn.payload['tender']['lots'])[0]
                    },
                    "root['releases'][0]['tender']['contractPeriod']['endDate']": {
                        'new_value': get_contract_period_for_ms_release(
                            lots_array=GlobalClassUpdateCnOnPn.payload['tender']['lots'])[1],
                        'old_value': get_contract_period_for_ms_release(
                            lots_array=GlobalClassCreateCnOnPn.payload['tender']['lots'])[1]
                    }
                }
            }

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

                    GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                        pn_ocid=GlobalClassCreatePn.pn_ocid)

                    GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                        pn_ocid=GlobalClassCreatePn.pn_ocid)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateEi.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateFs.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreatePn.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateCnOnPn.operation_id)
                else:
                    with allure.step('# Steps from Casandra DataBase'):
                        steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)
                        allure.attach(steps, "Cassandra DataBase: steps of process")
            except ValueError:
                raise ValueError("Can not return BPE operation step")

            assert str(compare_actual_result_and_expected_result(
                expected_result=expected_result,
                actual_result=compare_releases
            )) == str(True)

            assert str(compare_actual_result_and_expected_result(
                expected_result=GlobalClassUpdateCnOnPn.payload['planning']['rationale'],
                actual_result=GlobalClassUpdateCnOnPn.actual_ms_release['releases'][0]['planning']['rationale']
            )) == str(True)

            assert str(compare_actual_result_and_expected_result(
                expected_result=GlobalClassUpdateCnOnPn.payload['planning']['budget']['description'],
                actual_result=GlobalClassUpdateCnOnPn.actual_ms_release['releases'][0]['planning']['budget'][
                    'description']
            )) == str(True)

            assert str(compare_actual_result_and_expected_result(
                expected_result=GlobalClassUpdateCnOnPn.payload['tender']['procurementMethodRationale'],
                actual_result=GlobalClassUpdateCnOnPn.actual_ms_release['releases'][0]['tender'][
                    'procurementMethodRationale']
            )) == str(True)

            assert str(compare_actual_result_and_expected_result(
                expected_result=GlobalClassUpdateCnOnPn.payload['tender']['procurementMethodAdditionalInfo'],
                actual_result=GlobalClassUpdateCnOnPn.actual_ms_release['releases'][0]['tender'][
                    'procurementMethodAdditionalInfo']
            )) == str(True)

    @allure.title('Check EV and MS releases data after CnOnPn updating based on full data model for creating and '
                  'model without optional fields for updating')
    def test_check_ev_ms_releases_four(self):
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
            fs_payload = copy.deepcopy(FsPreparePayload())
            GlobalClassCreateFs.payload = fs_payload.create_fs_obligatory_data_model_treasury_money()
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

            GlobalClassCreatePn.actual_pn_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_id}").json()

            GlobalClassCreatePn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()
        with allure.step('# 7. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
        with allure.step('# 8. Send request to create CnOnPn'):
            """
            Send api request on BPE host for contract notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release,
                    need_to_set_permanent_id_for_lots_array=False,
                    need_to_set_permanent_id_for_items_array=False,
                    need_to_set_permanent_id_for_documents_array=False
                )

            Requests().create_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateCnOnPn.access_token,
                x_operation_id=GlobalClassCreateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassCreateCnOnPn.payload
            )

            GlobalClassCreateCnOnPn.feed_point_message = \
                KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()

            GlobalClassCreateCnOnPn.ev_id = \
                GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']

            GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

            GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()
        with allure.step('# 9. Authorization platform one: update CnOnPn'):
            """
            Tender platform authorization for update contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassUpdateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassUpdateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassUpdateCnOnPn.access_token)
        with allure.step('# 10. Send request to update CnOnPn'):
            """
            Send api request on BPE host for contract notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassUpdateCnOnPn.payload = \
                cnonpn_payload_class.update_cnonpn_obligatory_data_model_with_lots_items_documents_with_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True,
                    need_to_set_permanent_id_for_electronic_auction=True
                )

            synchronous_result_of_sending_the_request = Requests().update_cnonpn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassUpdateCnOnPn.access_token,
                x_operation_id=GlobalClassUpdateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassUpdateCnOnPn.payload
            )

        with allure.step('# 11. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 11.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 11.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassUpdateCnOnPn.feed_point_message = \
                    KafkaMessage(GlobalClassUpdateCnOnPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassUpdateCnOnPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassUpdateCnOnPn.operation_id).update_cnonpn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassUpdateCnOnPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassUpdateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")

                    GlobalClassUpdateCnOnPn.actual_ev_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreateCnOnPn.ev_id}").json()

                    GlobalClassUpdateCnOnPn.actual_ms_release = requests.get(
                        url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_ocid}").json()

                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 11.3. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
                              "Actual EV release before updating")

                allure.attach(str(json.dumps(GlobalClassUpdateCnOnPn.actual_ev_release)),
                              "Actual EV release after updating")

                compare_releases = DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, GlobalClassUpdateCnOnPn.actual_ev_release)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned

                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['tender']['amendments']",
                    "dictionary_item_removed": "['releases'][0]['tender']['procurementMethodModalities'], "
                                               "['releases'][0]['tender']['lots'][0]['placeOfPerformance']"
                                               "['description'], ['releases'][0]['tender']['lots'][0]["
                                               "'placeOfPerformance']['address']['postalCode'], "
                                               "['releases'][0]['tender']['lots'][1]['placeOfPerformance']"
                                               "['description'], ['releases'][0]['tender']['lots'][1]"
                                               "['placeOfPerformance']['address']['postalCode']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassUpdateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassUpdateCnOnPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            "new_value": "tenderAmendment",
                            "old_value": "tender"
                        },
                        "root['releases'][0]['tender']['items'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][0]['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['quantity']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['quantity'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][0]['quantity']
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                            "new_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassCreateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][0]['unit']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][0]['unit']['id']
                        },
                        "root['releases'][0]['tender']['items'][1]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][1]['description']
                        },
                        "root['releases'][0]['tender']['items'][1]['quantity']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['quantity'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][1]['quantity']
                        },
                        "root['releases'][0]['tender']['items'][1]['unit']['name']": {
                            "new_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['unit']['id'],
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_classification_unit_dictionary_csv(
                                unit_id=GlobalClassCreateCnOnPn.payload['tender']['items'][1]['unit']['id'],
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['items'][1]['unit']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['items'][1]['unit']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['items'][1]['unit']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0]['title']
                        },
                        "root['releases'][0]['tender']['lots'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0]['description']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['startDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['streetAddress'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['region']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['description']": {
                            "new_value": get_value_from_region_csv(
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_region_csv(
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['description']": {
                            "new_value": get_value_from_locality_csv(
                                locality=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_locality_csv(
                                locality=GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][1]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1]['title']
                        },
                        "root['releases'][0]['tender']['lots'][1]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1]['description']
                        },
                        "root['releases'][0]['tender']['lots'][1]['contractPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['startDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][1]['contractPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']['streetAddress']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['streetAddress'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['region']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['description']": {
                            "new_value": get_value_from_region_csv(
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_region_csv(
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['id']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                'placeOfPerformance']['address']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][1]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['description']": {
                            "new_value": get_value_from_locality_csv(
                                locality=GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassUpdateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_locality_csv(
                                locality=GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['locality']['id'],
                                region=GlobalClassCreateCnOnPn.payload['tender']['lots'][1][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=GlobalClassMetadata.country,
                                language=GlobalClassMetadata.language)[1]
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['startDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['tenderPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['enquiryPeriod']['endDate']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['documents'][0]['title']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][0]['title'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][0]['title']
                        },
                        "root['releases'][0]['tender']['documents'][0]['description']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][0]['description'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['documents'][0]['description']
                        },
                        "root['releases'][0]['tender']['documents'][1]['relatedLots'][0]": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['documents'][1]['relatedLots'][0],
                            "old_value": GlobalClassCreateCnOnPn.actual_ev_release['releases'][0][
                                'tender']['documents'][1]['relatedLots'][0]
                        },
                        "root['releases'][0]['tender']['electronicAuctions']['details'][0]"
                        "['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['electronicAuctions'][
                                'details'][0]['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['electronicAuctions'][
                                'details'][0]['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount']
                        },
                        "root['releases'][0]['tender']['electronicAuctions']['details'][1]"
                        "['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount']": {
                            "new_value": GlobalClassUpdateCnOnPn.payload['tender']['electronicAuctions'][
                                'details'][1]['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount'],
                            "old_value": GlobalClassCreateCnOnPn.payload['tender']['electronicAuctions'][
                                'details'][1]['electronicAuctionModalities'][0]['eligibleMinimumDifference']['amount']
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
                                operation_id=GlobalClassUpdateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")
                print("Compare")
                print(json.dumps(compare_releases))
                print("Expected")
                print(json.dumps(expected_result))
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
            with allure.step('# 11.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
                              "Actual MS release before CnOnPn updating")
                allure.attach(str(json.dumps(GlobalClassUpdateCnOnPn.actual_ms_release)),
                              "Actual MS release after CnOnPn updating")

                compare_releases = dict(DeepDiff(GlobalClassCreateCnOnPn.actual_ms_release,
                                                 GlobalClassUpdateCnOnPn.actual_ms_release))

            expected_result = {
                "values_changed": {
                    "root['releases'][0]['id']": {
                        "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                     f"{GlobalClassUpdateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}",
                        "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                     f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}"
                    },
                    "root['releases'][0]['date']": {
                        "new_value": GlobalClassUpdateCnOnPn.feed_point_message['data']['operationDate'],
                        "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                    },
                    "root['releases'][0]['tender']['contractPeriod']['startDate']": {
                        'new_value': get_contract_period_for_ms_release(
                            lots_array=GlobalClassUpdateCnOnPn.payload['tender']['lots'])[0],
                        'old_value': get_contract_period_for_ms_release(
                            lots_array=GlobalClassCreateCnOnPn.payload['tender']['lots'])[0]
                    },
                    "root['releases'][0]['tender']['contractPeriod']['endDate']": {
                        'new_value': get_contract_period_for_ms_release(
                            lots_array=GlobalClassUpdateCnOnPn.payload['tender']['lots'])[1],
                        'old_value': get_contract_period_for_ms_release(
                            lots_array=GlobalClassCreateCnOnPn.payload['tender']['lots'])[1]
                    }
                }
            }

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

                    GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                        pn_ocid=GlobalClassCreatePn.pn_ocid)

                    GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                        pn_ocid=GlobalClassCreatePn.pn_ocid)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateEi.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateFs.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreatePn.operation_id)

                    GlobalClassMetadata.database.cleanup_steps_of_process(
                        operation_id=GlobalClassCreateCnOnPn.operation_id)
                else:
                    with allure.step('# Steps from Casandra DataBase'):
                        steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)
                        allure.attach(steps, "Cassandra DataBase: steps of process")
            except ValueError:
                raise ValueError("Can not return BPE operation step")

            assert str(compare_actual_result_and_expected_result(
                expected_result=expected_result,
                actual_result=compare_releases
            )) == str(True)
