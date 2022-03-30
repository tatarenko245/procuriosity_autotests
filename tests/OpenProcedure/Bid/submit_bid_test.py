import copy
import time
import allure
import requests
from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn, GlobalClassCreateFirstBid
from tests.utils.PayloadModels.OpenProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModels.Budget.Ei.expenditure_item_payload__ import EiPreparePayload
from tests.utils.PayloadModels.Budget.Fs.deldete_financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModels.OpenProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.PayloadModels.OpenProcedure.SubmitBid.bid_prepared_payload import BidPreparePayload
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions_collection import compare_actual_result_and_expected_result, time_bot
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.platform_query_library import Requests


@allure.parent_suite('Tendering')
@allure.suite('Bid')
@allure.sub_suite('BPE: Submit Bid')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=666193675',
                 name='Google sheets: Submit Bid')
class TestCreateBid:
    def test_setup(self, parse_environment, parse_country, parse_language, parse_pmd, parse_cassandra_username,
                   parse_cassandra_password):
        """
        Get 'country', 'language', 'cassandra_username', 'cassandra_password', 'environment' parameters
        from test run command.
        Then choose BPE host.
        Then choose host for Database connection.
        """
        GlobalClassMetadata.country = parse_country
        GlobalClassMetadata.language = parse_language
        GlobalClassMetadata.pmd = parse_pmd
        GlobalClassMetadata.cassandra_username = parse_cassandra_username
        GlobalClassMetadata.cassandra_password = parse_cassandra_password
        GlobalClassMetadata.environment = parse_environment
        GlobalClassMetadata.hosts = Environment().choose_environment(GlobalClassMetadata.environment)
        GlobalClassMetadata.host_for_bpe = GlobalClassMetadata.hosts[1]
        GlobalClassMetadata.host_for_services = GlobalClassMetadata.hosts[2]
        GlobalClassMetadata.cassandra_cluster = GlobalClassMetadata.hosts[0]
        GlobalClassMetadata.database = CassandraSession(
            username=GlobalClassMetadata.cassandra_username,
            password=GlobalClassMetadata.cassandra_password,
            host=GlobalClassMetadata.cassandra_cluster)

    @allure.title('Check status code and message from Kafka topic after Bid creating, based on full data model')
    def test_check_result_of_sending_the_request_one(self):
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
            fs_payload = copy.deepcopy(FinancialSourcePayload(ei_payload=GlobalClassCreateEi.payload))
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
                    quantity_of_lot_object=2,
                    quantity_of_item_object=2)

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
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release
                )

            Requests().createCnOnPn(
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

        with allure.step('# 9. Authorization platform one: create Bid'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)

        with allure.step('# 10. Send request to create Bid'):
            """
            Send api request on BPE host for contract notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateFirstBid.payload = \
                bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release
                )

            synchronous_result_of_sending_the_request = Requests().submit_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFirstBid.access_token,
                x_operation_id=GlobalClassCreateFirstBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateFirstBid.payload
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
                GlobalClassCreateFirstBid.feed_point_message = \
                    KafkaMessage(GlobalClassCreateFirstBid.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCreateFirstBid.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateFirstBid.operation_id).create_bid_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateFirstBid.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    tender_id=GlobalClassCreateCnOnPn.ev_id
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateFirstBid.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

            with allure.step('# 11.3. Check status into database'):
                """
                Check status into database by cpid into submission.bids.
                """
                bid_status_from_database = GlobalClassMetadata.database.get_bid_status_from_submission_bids_by_on_ocid(
                    pn_ocid=GlobalClassCreatePn.pn_ocid
                )
                allure.attach(bid_status_from_database, "Cassandra DataBase: actual status of bid")
                allure.attach("pending", " Expected status of bid")
                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if bid_status_from_database == "pending":
                        GlobalClassMetadata.database.cleanup_table_of_services_for_expenditure_item(
                            cp_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_by_cpid(
                            operation_id=GlobalClassCreateFirstBid.operation_id)
                    else:
                        print(GlobalClassCreateFirstBid.operation_id)
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = \
                                GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                    operation_id=GlobalClassCreateFirstBid.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check status code and message from Kafka topic after Bid creating, based on '
                  'data model without optional fields')
    def test_check_result_of_sending_the_request_two(self):
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
            fs_payload = copy.deepcopy(FinancialSourcePayload(ei_payload=GlobalClassCreateEi.payload))
            GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_treasury_money()
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
                    need_to_set_permanent_id_for_lots_array=False,
                    need_to_set_permanent_id_for_items_array=False,
                    need_to_set_permanent_id_for_documents_array=False,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release
                )

            Requests().createCnOnPn(
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

        with allure.step('# 9. Authorization platform one: create Bid'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)

        with allure.step('# 10. Send request to create Bid'):
            """
            Send api request on BPE host for contract notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateFirstBid.payload = \
                bid_payload_class.create_first_bid_obligatory_data_model(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release
                )

            synchronous_result_of_sending_the_request = Requests().submit_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFirstBid.access_token,
                x_operation_id=GlobalClassCreateFirstBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateFirstBid.payload
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
                GlobalClassCreateFirstBid.feed_point_message = \
                    KafkaMessage(GlobalClassCreateFirstBid.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCreateFirstBid.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateFirstBid.operation_id).create_bid_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateFirstBid.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    tender_id=GlobalClassCreateCnOnPn.ev_id
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateFirstBid.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

            with allure.step('# 11.3. Check status into database'):
                """
                Check status into database by cpid into submission.bids.
                """
                bid_status_from_database = GlobalClassMetadata.database.get_bid_status_from_submission_bids_by_on_ocid(
                    pn_ocid=GlobalClassCreatePn.pn_ocid
                )
                allure.attach(bid_status_from_database, "Cassandra DataBase: actual status of bid")
                allure.attach("pending", " Expected status of bid")
                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if bid_status_from_database == "pending":
                        GlobalClassMetadata.database.cleanup_table_of_services_for_expenditure_item(
                            cp_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_by_cpid(
                            operation_id=GlobalClassCreateFirstBid.operation_id)
                    else:
                        print(GlobalClassCreateFirstBid.operation_id)
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = \
                                GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                    operation_id=GlobalClassCreateFirstBid.operation_id)
                            print(steps)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
