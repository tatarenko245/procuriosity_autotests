import copy
import json
import time
import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn, GlobalClassCreateEnquiry, GlobalClassCreateAnswer, GlobalClassEnquiryPeriodEnd
from tests.utils.PayloadModel.OpenProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.Budget.Ei.expenditure_item_payload import EiPreparePayload
from tests.utils.PayloadModel.OpenProcedure.EnquiryPeriod.answer_prepared_payload import AnswerPreparePayload
from tests.utils.PayloadModel.OpenProcedure.EnquiryPeriod.enquiry_prepared_payload import EnquiryPreparePayload
from tests.utils.PayloadModel.Budget.Fs.financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModel.OpenProcedure.Pn.pn_prepared_payload import PnPreparePayload

from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions_collection import compare_actual_result_and_expected_result, time_bot
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.platform_query_library import Requests


@allure.parent_suite('Clarification')
@allure.suite('EV')
@allure.sub_suite('BPE: Enquiry period end')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=5497041',
                 name='Google sheets: Enquiry period end')
class TestEnquiryPeriodEnd:
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
        if parse_environment == "dev":
            GlobalClassMetadata.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
        elif parse_environment == "sandbox":
            GlobalClassMetadata.metadata_document_url = "http://storage.eprocurement.systems/get"
        GlobalClassMetadata.database = CassandraSession(
            username=GlobalClassMetadata.cassandra_username,
            password=GlobalClassMetadata.cassandra_password,
            host=GlobalClassMetadata.cassandra_cluster)

    @allure.title('Check EV and MS releases data if Enquiry period end was expired,  set tender status suspended')
    def test_check_ev_ms_releases_one(self, parse_country, connect_to_database, parse_pmd):
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
            try:
                """
                Get offset interval from clarification.rules and from submission.rules for this testcase
                """
                interval_from_clarification_rules = int(connect_to_database.get_offset_from_clarification_rules(
                    country=parse_country,
                    pmd=parse_pmd,
                    operation_type='all',
                    parameter='interval'
                ))

                interval_from_submission_rules = int(connect_to_database.get_offset_from_clarification_rules(
                    country=parse_country,
                    pmd=parse_pmd,
                    operation_type='all',
                    parameter='interval'
                ))
            except Exception:
                raise Exception("Impossible to get interval value from clarification.rules and from submission.rules")

            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
                    enquiry_interval=interval_from_clarification_rules + 60,
                    tender_interval=interval_from_submission_rules + 60,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True
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

            Requests().create_enquiry(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEnquiry.access_token,
                x_operation_id=GlobalClassCreateEnquiry.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateEnquiry.payload
            )

            GlobalClassCreateEnquiry.feed_point_message_bpe = \
                KafkaMessage(GlobalClassCreateEnquiry.operation_id).get_message_from_kafka()

            GlobalClassCreateEnquiry.enquiry_id = \
                GlobalClassCreateEnquiry.feed_point_message_bpe['data']['outcomes']['enquiries'][0]['id']

            GlobalClassCreateEnquiry.enquiry_token = \
                GlobalClassCreateEnquiry.feed_point_message_bpe['data']['outcomes']['enquiries'][0]['X-TOKEN']

            GlobalClassCreateEnquiry.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassCreateEnquiry.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()
        with allure.step('# 11. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 11.1. Check EV release'):
                """
                Compare actual evaluation value release before enquiry period end expired and 
                actual evaluation value release after enquiry period end expired.
                """
                allure.attach(str(json.dumps(GlobalClassCreateEnquiry.actual_ev_release)),
                              "Actual EV release before enquiry period end expired")

                time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])

                GlobalClassEnquiryPeriodEnd.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()

                allure.attach(str(json.dumps(GlobalClassEnquiryPeriodEnd.actual_ev_release)),
                              "Actual EV release after enquiry period end expired")
                compare_releases = dict(DeepDiff(
                    GlobalClassCreateEnquiry.actual_ev_release, GlobalClassEnquiryPeriodEnd.actual_ev_release))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassEnquiryPeriodEnd.actual_ev_release['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateEnquiry.feed_point_message_bpe['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "suspended",
                            "old_value":
                                GlobalClassCreateEnquiry.actual_ev_release['releases'][0]['tender']['statusDetails']
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
                            GlobalClassEnquiryPeriodEnd.feed_point_message_bpe = \
                                KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                                             initiation="bpe").get_message_from_kafka_by_ocid_and_initiator(
                                )
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassEnquiryPeriodEnd.feed_point_message_bpe['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 11.2. Check MS release'):
                """
                Compare actual multistage release before enquiry period end expired and 
                actual multistage release after enquiry period end expired.
                """
                allure.attach(str(json.dumps(GlobalClassCreateEnquiry.actual_ms_release)),
                              "Actual MS release before enquiry period end expired")

                GlobalClassEnquiryPeriodEnd.actual_ms_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()

                allure.attach(str(json.dumps(GlobalClassEnquiryPeriodEnd.actual_ms_release)),
                              "Actual MS release after enquiry period end expired")

                compare_releases = dict(DeepDiff(GlobalClassCreateEnquiry.actual_ms_release,
                                                 GlobalClassEnquiryPeriodEnd.actual_ms_release))

                expected_result = {}

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        GlobalClassMetadata.database.cleanup_table_of_services_for_expenditure_item(
                            cp_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.enquiry_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEnquiry.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassEnquiryPeriodEnd.feed_point_message_bpe['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check EV and MS releases data if Enquiry period end was expired, '
                  'set tender statusDetails tendering')
    def test_check_ev_ms_releases_two(self, parse_country, connect_to_database, parse_pmd):
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
            try:
                """
                Get offset interval from clarification.rules and from submission.rules for this testcase
                """
                interval_from_clarification_rules = int(connect_to_database.get_offset_from_clarification_rules(
                    country=parse_country,
                    pmd=parse_pmd,
                    operation_type='all',
                    parameter='interval'
                ))

                interval_from_submission_rules = int(connect_to_database.get_offset_from_clarification_rules(
                    country=parse_country,
                    pmd=parse_pmd,
                    operation_type='all',
                    parameter='interval'
                ))
            except Exception:
                raise Exception("Impossible to get interval value from clarification.rules and from submission.rules")

            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
                    enquiry_interval=interval_from_clarification_rules + 60,
                    tender_interval=interval_from_submission_rules + 60,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True
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

            Requests().create_enquiry(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEnquiry.access_token,
                x_operation_id=GlobalClassCreateEnquiry.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateEnquiry.payload
            )

            GlobalClassCreateEnquiry.feed_point_message_bpe = \
                KafkaMessage(GlobalClassCreateEnquiry.operation_id).get_message_from_kafka()

            GlobalClassCreateEnquiry.enquiry_id = \
                GlobalClassCreateEnquiry.feed_point_message_bpe['data']['outcomes']['enquiries'][0]['id']

            GlobalClassCreateEnquiry.enquiry_token = \
                GlobalClassCreateEnquiry.feed_point_message_bpe['data']['outcomes']['enquiries'][0]['X-TOKEN']

        with allure.step('# 11. Authorization platform one: create Answer'):
            """
            Tender platform authorization for create answer process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateAnswer.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateAnswer.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateAnswer.access_token)

        with allure.step('# 12. Send request to create Answer'):
            """
            Send api request on BPE host for answer creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """

            time.sleep(1)
            answer_payload_class = copy.deepcopy(AnswerPreparePayload())
            GlobalClassCreateAnswer.payload = answer_payload_class.create_answer_full_data_model()

            Requests().create_answer(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateAnswer.access_token,
                x_operation_id=GlobalClassCreateAnswer.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                enquiry_id=GlobalClassCreateEnquiry.enquiry_id,
                enquiry_token=GlobalClassCreateEnquiry.enquiry_token,
                payload=GlobalClassCreateAnswer.payload
            )

            GlobalClassCreateAnswer.feed_point_message = \
                KafkaMessage(GlobalClassCreateAnswer.operation_id).get_message_from_kafka()

            allure.attach(str(GlobalClassCreateAnswer.feed_point_message), 'Message in feed point')

            GlobalClassCreateAnswer.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassCreateAnswer.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

        with allure.step('# 13. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 13.1. Check EV release'):
                """
                Compare actual evaluation value release before enquiry period end expired and 
                actual evaluation value release after enquiry period end expired.
                """
                allure.attach(str(json.dumps(GlobalClassCreateAnswer.actual_ev_release)),
                              "Actual EV release before enquiry period end expired")

                time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])

                GlobalClassEnquiryPeriodEnd.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()

                allure.attach(str(json.dumps(GlobalClassEnquiryPeriodEnd.actual_ev_release)),
                              "Actual EV release after enquiry period end expired")
                compare_releases = dict(DeepDiff(
                    GlobalClassCreateAnswer.actual_ev_release, GlobalClassEnquiryPeriodEnd.actual_ev_release))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassEnquiryPeriodEnd.actual_ev_release['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateAnswer.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'],
                            "old_value": GlobalClassCreateAnswer.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "tendering",
                            "old_value":
                                GlobalClassCreateAnswer.actual_ev_release['releases'][0]['tender']['statusDetails']
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
                            GlobalClassEnquiryPeriodEnd.feed_point_message_bpe = \
                                KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                                             initiation="bpe").get_message_from_kafka_by_ocid_and_initiator(
                                )
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassEnquiryPeriodEnd.feed_point_message_bpe['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

            with allure.step('# 11.2. Check MS release'):
                """
                Compare actual multistage release before enquiry period end expired and 
                actual multistage release after enquiry period end expired.
                """
                allure.attach(str(json.dumps(GlobalClassCreateAnswer.actual_ms_release)),
                              "Actual MS release before enquiry period end expired")

                GlobalClassEnquiryPeriodEnd.actual_ms_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()

                allure.attach(str(json.dumps(GlobalClassEnquiryPeriodEnd.actual_ms_release)),
                              "Actual MS release after enquiry period end expired")

                compare_releases = dict(DeepDiff(GlobalClassCreateAnswer.actual_ms_release,
                                                 GlobalClassEnquiryPeriodEnd.actual_ms_release))

                expected_result = {}

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        GlobalClassMetadata.database.cleanup_table_of_services_for_expenditure_item(
                            cp_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.enquiry_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEnquiry.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassEnquiryPeriodEnd.feed_point_message_bpe['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
