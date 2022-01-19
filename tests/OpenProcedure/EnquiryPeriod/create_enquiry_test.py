import copy
import json
import time
import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn, GlobalClassCreateEnquiry
from tests.utils.PayloadModel.OpenProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.Budget.Ei.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.OpenProcedure.EnquiryPeriod.enquiry_prepared_payload import EnquiryPreparePayload
from tests.utils.PayloadModel.Budget.Fs.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.OpenProcedure.Pn.pn_prepared_payload import PnPreparePayload

from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions import compare_actual_result_and_expected_result, is_it_uuid
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.my_requests import Requests


@allure.parent_suite('Clarification')
@allure.suite('EV')
@allure.sub_suite('BPE: Create enquiry')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=118033600',
                 name='Google sheets: Create enquiry')
class TestCreateEnquiry:
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

    @allure.title('Check status code and message from Kafka topic after Enquiry creating')
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

        with allure.step('# 9. Authorization platform one: create Enquiry'):
            """
            Tender platform authorization for create enquiry process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEnquiry.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEnquiry.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEnquiry.access_token)
        with allure.step('# 10. Send request to create Enquiry'):
            """
            Send api request on BPE host for enquiry creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            enquiry_payload_class = copy.deepcopy(EnquiryPreparePayload())
            GlobalClassCreateEnquiry.payload = \
                enquiry_payload_class.create_enquiry_full_data_model(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release
                )

            synchronous_result_of_sending_the_request = Requests().create_enquiry(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEnquiry.access_token,
                x_operation_id=GlobalClassCreateEnquiry.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateEnquiry.payload
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

                GlobalClassCreateEnquiry.feed_point_message_platform = \
                    KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                                 initiation="platform").get_message_from_kafka_by_ocid_and_initiator(
                    )

                GlobalClassCreateEnquiry.feed_point_message_bpe = \
                    KafkaMessage(GlobalClassCreateEnquiry.operation_id).get_message_from_kafka()

                allure.attach(str(GlobalClassCreateEnquiry.feed_point_message_platform),
                              'Message in feed point where initiator platform')
                allure.attach(str(GlobalClassCreateEnquiry.feed_point_message_bpe),
                              'Message in feed point where initiator bpe')

                asynchronous_result_of_sending_the_request_was_checked_bpe_initiator = KafkaMessage(
                    GlobalClassCreateEnquiry.operation_id).create_enquiry_message_initiator_bpe_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEnquiry.feed_point_message_bpe,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
                )

                asynchronous_result_of_sending_the_request_was_checked_platform_initiator = KafkaMessage(
                    GlobalClassCreateEnquiry.operation_id).create_enquiry_message_initiator_platform_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEnquiry.feed_point_message_platform[0],
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
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
                    if asynchronous_result_of_sending_the_request_was_checked_bpe_initiator is True \
                            and asynchronous_result_of_sending_the_request_was_checked_platform_initiator is True:
                        database.ei_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.fs_process_cleanup_table_of_services(ei_id=GlobalClassCreateEi.ei_ocid)
                        database.pn_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.cnonpn_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.enquiry_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateFs.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreatePn.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateCnOnPn.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEnquiry.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEnquiry.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked_bpe_initiator
                )

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked_platform_initiator
                )

    @allure.title('Check EV and MS releases data after Enquiry creating with full data model')
    def test_check_ev_ms_releases_one(self):
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

        with allure.step('# 9. Authorization platform one: create Enquiry'):
            """
            Tender platform authorization for create enquiry process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEnquiry.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEnquiry.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEnquiry.access_token)
        with allure.step('# 10. Send request to create Enquiry'):
            """
            Send api request on BPE host for enquiry creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            enquiry_payload_class = copy.deepcopy(EnquiryPreparePayload())
            GlobalClassCreateEnquiry.payload = \
                enquiry_payload_class.create_enquiry_full_data_model(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release
                )

            synchronous_result_of_sending_the_request = Requests().create_enquiry(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEnquiry.access_token,
                x_operation_id=GlobalClassCreateEnquiry.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateEnquiry.payload
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
                GlobalClassCreateEnquiry.feed_point_message_platform = \
                    KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                                 initiation="platform").get_message_from_kafka_by_ocid_and_initiator(
                    )

                GlobalClassCreateEnquiry.feed_point_message_bpe = \
                    KafkaMessage(GlobalClassCreateEnquiry.operation_id).get_message_from_kafka()

                allure.attach(str(GlobalClassCreateEnquiry.feed_point_message_platform),
                              'Message in feed point where initiator platform')
                allure.attach(str(GlobalClassCreateEnquiry.feed_point_message_bpe),
                              'Message in feed point where initiator bpe')

                asynchronous_result_of_sending_the_request_was_checked_bpe_initiator = KafkaMessage(
                    GlobalClassCreateEnquiry.operation_id).create_enquiry_message_initiator_bpe_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEnquiry.feed_point_message_bpe,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
                )

                asynchronous_result_of_sending_the_request_was_checked_platform_initiator = KafkaMessage(
                    GlobalClassCreateEnquiry.operation_id).create_enquiry_message_initiator_platform_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEnquiry.feed_point_message_platform[0],
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
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
                    if asynchronous_result_of_sending_the_request_was_checked_bpe_initiator is False \
                            or asynchronous_result_of_sending_the_request_was_checked_platform_initiator is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEnquiry.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")

                    GlobalClassCreateEnquiry.actual_ms_release = requests.get(
                        url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_ocid}").json()

                    GlobalClassCreateEnquiry.actual_ev_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreateCnOnPn.ev_id}").json()

                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked_bpe_initiator
                )

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked_platform_initiator
                )
            with allure.step('# 11.3. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
                              "Actual EV release before enquiry creating")

                allure.attach(str(json.dumps(GlobalClassCreateEnquiry.actual_ev_release)),
                              "Actual EV release after enquiry creating")

                compare_releases = DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, GlobalClassCreateEnquiry.actual_ev_release)

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['tender']['enquiries']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCreateEnquiry.feed_point_message_bpe['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['hasEnquiries']": {
                            'new_value': True,
                            'old_value': False
                        }
                    }
                }

                try:
                    is_it_uuid(
                        uuid_to_test=GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['tender'][
                            'enquiries'][0]['id'],
                        version=4
                    )

                except ValueError:
                    raise ValueError("release.tender.enquiries.id is not UUID 4.")
                expected_enquiries_array = [
                    {
                        "id": GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['tender']['enquiries'][0][
                            'id'],
                        "date": GlobalClassCreateEnquiry.feed_point_message_bpe['data']['operationDate'],
                        "title": GlobalClassCreateEnquiry.payload['enquiry']['title'],
                        "description": GlobalClassCreateEnquiry.payload['enquiry']['description'],
                        "relatedLot": GlobalClassCreateEnquiry.payload['enquiry']['relatedLot']
                    }]
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
                                operation_id=GlobalClassCreateEnquiry.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_enquiries_array,
                    actual_result=GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['tender']['enquiries']
                ))
            with allure.step('# 11.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
                              "Actual MS release before Enquiry updating")
                allure.attach(str(json.dumps(GlobalClassCreateEnquiry.actual_ms_release)),
                              "Actual MS release after Enquiry updating")

                compare_releases = dict(DeepDiff(GlobalClassCreateCnOnPn.actual_ms_release,
                                                 GlobalClassCreateEnquiry.actual_ms_release))
                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreateEnquiry.actual_ms_release['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCreateEnquiry.feed_point_message_bpe['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['hasEnquiries']": {
                            'new_value': True,
                            'old_value': False
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
                        database.pn_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.cnonpn_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.enquiry_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateFs.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreatePn.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateCnOnPn.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEnquiry.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEnquiry.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check EV and MS releases data after Enquiry creating based on data model without optional fields')
    def test_check_ev_ms_releases_two(self):
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

        with allure.step('# 9. Authorization platform one: create Enquiry'):
            """
            Tender platform authorization for create enquiry process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEnquiry.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEnquiry.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEnquiry.access_token)
        with allure.step('# 10. Send request to create Enquiry'):
            """
            Send api request on BPE host for enquiry creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            enquiry_payload_class = copy.deepcopy(EnquiryPreparePayload())
            GlobalClassCreateEnquiry.payload = \
                enquiry_payload_class.create_enquiry_obligatory_data_model()

            synchronous_result_of_sending_the_request = Requests().create_enquiry(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEnquiry.access_token,
                x_operation_id=GlobalClassCreateEnquiry.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateEnquiry.payload
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
                GlobalClassCreateEnquiry.feed_point_message_platform = \
                    KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                                 initiation="platform").get_message_from_kafka_by_ocid_and_initiator(
                    )

                GlobalClassCreateEnquiry.feed_point_message_bpe = \
                    KafkaMessage(GlobalClassCreateEnquiry.operation_id).get_message_from_kafka()

                allure.attach(str(GlobalClassCreateEnquiry.feed_point_message_platform),
                              'Message in feed point where initiator platform')
                allure.attach(str(GlobalClassCreateEnquiry.feed_point_message_bpe),
                              'Message in feed point where initiator bpe')

                asynchronous_result_of_sending_the_request_was_checked_bpe_initiator = KafkaMessage(
                    GlobalClassCreateEnquiry.operation_id).create_enquiry_message_initiator_bpe_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEnquiry.feed_point_message_bpe,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
                )

                asynchronous_result_of_sending_the_request_was_checked_platform_initiator = KafkaMessage(
                    GlobalClassCreateEnquiry.operation_id).create_enquiry_message_initiator_platform_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEnquiry.feed_point_message_platform[0],
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id
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
                    if asynchronous_result_of_sending_the_request_was_checked_bpe_initiator is False \
                            or asynchronous_result_of_sending_the_request_was_checked_platform_initiator is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEnquiry.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")

                    GlobalClassCreateEnquiry.actual_ms_release = requests.get(
                        url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_ocid}").json()

                    GlobalClassCreateEnquiry.actual_ev_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreateCnOnPn.ev_id}").json()

                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked_bpe_initiator
                )

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked_platform_initiator
                )
            with allure.step('# 11.3. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
                              "Actual EV release before enquiry creating")

                allure.attach(str(json.dumps(GlobalClassCreateEnquiry.actual_ev_release)),
                              "Actual EV release after enquiry creating")

                compare_releases = DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, GlobalClassCreateEnquiry.actual_ev_release)

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['tender']['enquiries']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCreateEnquiry.feed_point_message_bpe['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['hasEnquiries']": {
                            'new_value': True,
                            'old_value': False
                        }
                    }
                }

                try:
                    is_it_uuid(
                        uuid_to_test=GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['tender'][
                            'enquiries'][0]['id'],
                        version=4
                    )
                except ValueError:
                    raise ValueError("release.tender.enquiries.id is not UUID 4.")

                expected_enquiries_array = [
                    {
                        "id": GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['tender']['enquiries'][0][
                            'id'],
                        "date": GlobalClassCreateEnquiry.feed_point_message_bpe['data']['operationDate'],
                        "title": GlobalClassCreateEnquiry.payload['enquiry']['title'],
                        "description": GlobalClassCreateEnquiry.payload['enquiry']['description']
                    }]
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
                                operation_id=GlobalClassCreateEnquiry.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_enquiries_array,
                    actual_result=GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['tender']['enquiries']
                ))
            with allure.step('# 11.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
                              "Actual MS release before Enquiry updating")
                allure.attach(str(json.dumps(GlobalClassCreateEnquiry.actual_ms_release)),
                              "Actual MS release after Enquiry updating")

                compare_releases = dict(DeepDiff(GlobalClassCreateCnOnPn.actual_ms_release,
                                                 GlobalClassCreateEnquiry.actual_ms_release))
                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreateEnquiry.actual_ms_release['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCreateEnquiry.feed_point_message_bpe['data']['operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['hasEnquiries']": {
                            'new_value': True,
                            'old_value': False
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
                        database.pn_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.cnonpn_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.enquiry_process_cleanup_table_of_services(pn_ocid=GlobalClassCreatePn.pn_ocid)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEi.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateFs.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreatePn.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateCnOnPn.operation_id)
                        database.cleanup_steps_of_process(operation_id=GlobalClassCreateEnquiry.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEnquiry.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
