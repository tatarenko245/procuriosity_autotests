import copy
import fnmatch
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn
from tests.utils.PayloadModels.OpenProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModels.Budget.Ei.expenditure_item_payload__ import EiPreparePayload
from tests.utils.PayloadModels.Budget.Fs.deldete_financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModels.OpenProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.ReleaseModels.OpenProcedure.CnOnPn.cnonpn_prepared_release import CnOnPnExpectedRelease

from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions_collection import compare_actual_result_and_expected_result, \
    get_value_from_classification_cpv_dictionary_xls, get_sum_of_lot, \
    get_contract_period_for_ms_release, generate_tender_classification_id
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.platform_query_library import Requests


@allure.parent_suite('Tendering')
@allure.suite('EV')
@allure.sub_suite('BPE: Create CnOnPn')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=532628427',
                 name='Google sheets: Create CnOnPn')
class TestCreateCnOnPn:
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

        if parse_environment == "dev":
            GlobalClassMetadata.document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
        elif parse_environment == "sandbox":
            GlobalClassMetadata.document_url = "http://storage.eprocurement.systems/get"

    @allure.title('Check status code and message from Kafka topic after CnOnPn creating')
    def test_check_result_of_sending_the_request(self, connect_to_database, parse_country, parse_pmd):
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
                    enquiry_interval=interval_from_clarification_rules + 1,
                    tender_interval=interval_from_submission_rules + 1,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release
                )

            synchronous_result_of_sending_the_request = Requests().createCnOnPn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateCnOnPn.access_token,
                x_operation_id=GlobalClassCreateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassCreateCnOnPn.payload
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
                GlobalClassCreateCnOnPn.feed_point_message = \
                    KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCreateCnOnPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateCnOnPn.operation_id).create_cnonpn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateCnOnPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    pmd=GlobalClassMetadata.pmd
                )
                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is True:
                        GlobalClassMetadata.database.cleanup_table_of_services_for_expenditure_item(
                            cp_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check EV and MS releases data after CnOnPn creating with full data model with 2 lots and 2 '
                  'items criteria, conversions, documents, auction')
    def test_check_ev_ms_releases_one(self, connect_to_database, parse_country, parse_pmd):
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
                    enquiry_interval=interval_from_clarification_rules + 1,
                    tender_interval=interval_from_submission_rules + 1,
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_items_array=True,
                    need_to_set_permanent_id_for_documents_array=True,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release
                )

            synchronous_result_of_sending_the_request = Requests().createCnOnPn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateCnOnPn.access_token,
                x_operation_id=GlobalClassCreateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassCreateCnOnPn.payload
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
                GlobalClassCreateCnOnPn.feed_point_message = \
                    KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCreateCnOnPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateCnOnPn.operation_id).create_cnonpn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateCnOnPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    pmd=GlobalClassMetadata.pmd
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")

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

                    GlobalClassCreateCnOnPn.actual_pn_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_id}").json()
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 9.3. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)), "Actual EV release")

                expected_release_class = copy.deepcopy(CnOnPnExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ev_release_model = copy.deepcopy(
                    expected_release_class.ev_release_full_data_model_with_auction_criteria_conversions(
                        payload=GlobalClassCreatePn.payload,
                        actual_release=GlobalClassCreatePn.actual_pn_release
                    ))
                allure.attach(str(json.dumps(expected_ev_release_model)), "Expected EV release")

                compare_releases = dict(DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, expected_ev_release_model))
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
                                operation_id=GlobalClassCreateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing actual Tp release and expected Tp release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Tp releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Tp releases.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step('# 9.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreatePn.actual_ms_release)),
                              "Actual MS release before CnOnPn creating")
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
                              "Actual MS release after CnOnPn creating")

                compare_releases = DeepDiff(GlobalClassCreatePn.actual_ms_release,
                                            GlobalClassCreateCnOnPn.actual_ms_release)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['parties'][3]['persones']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreatePn.actual_ms_release['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreatePn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['status']": {
                            "new_value": "active",
                            "old_value": "planning"
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "evaluation",
                            "old_value": "planning"
                        },
                        "root['releases'][0]['tender']['procurementMethodRationale']": {
                            "new_value": GlobalClassCreateCnOnPn.payload['tender']['procurementMethodRationale'],
                            "old_value": GlobalClassCreatePn.payload['tender']['procurementMethodRationale']
                        },
                        "root['releases'][0]['tender']['procurementMethodAdditionalInfo']": {
                            "new_value": GlobalClassCreateCnOnPn.payload['tender']['procurementMethodAdditionalInfo'],
                            "old_value": GlobalClassCreatePn.payload['tender']['procurementMethodAdditionalInfo']
                        }
                    },
                    'iterable_item_added': {
                        "root['releases'][0]['relatedProcesses'][3]": {
                            'id': GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['relatedProcesses'][3]['id'],
                            'relationship': ['x_evaluation'],
                            'scheme': 'ocid',
                            'identifier': GlobalClassCreateCnOnPn.ev_id,
                            'uri': f"{GlobalClassMetadata.__metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}"
                                   f"/{GlobalClassCreateCnOnPn.ev_id}"
                        }
                    }
                }

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

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                try:
                    """
                    Prepare expected businessFunctions.persones array"""
                    persones_scheme = GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                        'identifier']['scheme']
                    persones_id = GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                        'identifier']['id']
                    document_id = GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                        'businessFunctions'][0]['documents'][0]['id']
                    final_expected_persones_array = [{
                        "id": f"{persones_scheme}-{persones_id}",
                        "title": GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0]['title'],
                        "name": GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0]['name'],
                        "identifier": {
                            "scheme": persones_scheme,
                            "id": persones_id,
                            "uri": GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                                'identifier']['uri']
                        },
                        "businessFunctions": [
                            {
                                "id": GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                                    'businessFunctions'][0]['id'],
                                "type": GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                                    'businessFunctions'][0]['type'],
                                "jobTitle": GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                                    'businessFunctions'][0]['jobTitle'],
                                "period": {
                                    "startDate":
                                        GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                                            'businessFunctions'][0]['period']['startDate']
                                },
                                "documents": [
                                    {
                                        "id":
                                            GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                                                'businessFunctions'][0]['documents'][0]['id'],
                                        "documentType":
                                            GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                                                'businessFunctions'][0]['documents'][0]['documentType'],
                                        "title":
                                            GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                                                'businessFunctions'][0]['documents'][0]['title'],
                                        "description":
                                            GlobalClassCreateCnOnPn.payload['tender']['procuringEntity']['persones'][0][
                                                'businessFunctions'][0]['documents'][0]['description'],
                                        "url": f"{GlobalClassMetadata.document_url}/{document_id}",
                                        "datePublished": GlobalClassCreateCnOnPn.feed_point_message[
                                            'data']['operationDate']
                                    }]
                            }]
                    }]
                except Exception:
                    raise Exception("Impossible to prepare expected businessFunctions.persones array")

                with allure.step('Check a difference of comparing Ms release before cn creating and '
                                 'Ms release after cn creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing MS releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms releases.")
                    assert str(compare_releases) == str(expected_result)

                with allure.step('Check a difference of comparing persones array before cn creating'
                                 ' and persones araray after cn creating.'):
                    allure.attach(str(GlobalClassCreateCnOnPn.actual_ms_release[
                                          'releases'][0]['parties'][3]['persones']),
                                  "Actual result of comparing contract period object.")
                    allure.attach(str(final_expected_persones_array),
                                  "Expected result of comparing contract period object.")
                    assert str(GlobalClassCreateCnOnPn.actual_ms_release[
                                   'releases'][0]['parties'][3]['persones']) == str(final_expected_persones_array)

    @allure.title('Check EV and MS releases data after CnONPn creating without optional fields')
    def test_check_ev_ms_releases_two(self, connect_to_database, parse_country, parse_pmd):
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
                cnonpn_payload_class.create_cnonpn_obligatory_data_model_with_lots_items_documents(
                    pmd=parse_pmd,
                    enquiry_interval=interval_from_clarification_rules + 1,
                    tender_interval=interval_from_submission_rules + 1,
                    quantity_of_lots_object=1,
                    quantity_of_items_object=1,
                    need_to_set_permanent_id_for_lots_array=False,
                    need_to_set_permanent_id_for_items_array=False,
                    need_to_set_permanent_id_for_documents_array=False,
                    based_stage_release=GlobalClassCreatePn.actual_pn_release
                )

            synchronous_result_of_sending_the_request = Requests().createCnOnPn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateCnOnPn.access_token,
                x_operation_id=GlobalClassCreateCnOnPn.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_id=GlobalClassCreatePn.pn_id,
                pn_token=GlobalClassCreatePn.pn_token,
                payload=GlobalClassCreateCnOnPn.payload
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
                GlobalClassCreateCnOnPn.feed_point_message = \
                    KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCreateCnOnPn.feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateCnOnPn.operation_id).create_cnonpn_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateCnOnPn.feed_point_message,
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    pmd=GlobalClassMetadata.pmd
                )
                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")

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

                    GlobalClassCreateCnOnPn.actual_pn_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_id}").json()
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )
            with allure.step('# 9.3. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)), "Actual EV release")

                expected_release_class = copy.deepcopy(CnOnPnExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ev_release_model = copy.deepcopy(
                    expected_release_class.ev_release_obligatory_data_model_without_auction_criteria_conversions(
                        payload=GlobalClassCreateCnOnPn.payload,
                        actual_release=GlobalClassCreateCnOnPn.actual_ev_release
                    ))
                allure.attach(str(json.dumps(expected_ev_release_model)), "Expected EV release")

                compare_releases = dict(DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, expected_ev_release_model))

                # VR-1.0.1.7.7
                if parse_pmd == "SV" or parse_pmd == "TEST_SV" and GlobalClassCreateCnOnPn.payload[
                                                           'tender']['items'][0]['classification']['id'][0:3] != "451":
                    dictionary_item_removed_was_cleaned = \
                        str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                    compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                    compare_releases = dict(compare_releases)

                    expected_result = {
                        'dictionary_item_removed': "['releases'][0]['tender']['auctionPeriod'], "
                                                   "['releases'][0]['tender']['procurementMethodModalities'], "
                                                   "['releases'][0]['tender']['electronicAuctions']"
                    }

                    expected_auction_period_start_date = fnmatch.fnmatch(
                        GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['electronicAuctions'][
                            'details'][0]['auctionPeriod']['startDate'], "202*-*-*T*:*:*Z")
                    if expected_auction_period_start_date is True:
                        expected_auction_period_object = {
                            "startDate": GlobalClassCreateCnOnPn.actual_ev_release[
                                'releases'][0]['tender']['electronicAuctions']['details'][0]['auctionPeriod'][
                                'startDate']
                        }

                    expected_electronic_auctions_details = copy.deepcopy(
                        expected_release_class.prepare_expected_electronic_auction_details_array(
                            payload_electronic_auction_details_array=GlobalClassCreateCnOnPn.payload[
                                'tender']['electronicAuctions']['details'],
                            release_electronic_auction_details_array=GlobalClassCreateCnOnPn.actual_ev_release[
                                'releases'][0]['tender']['electronicAuctions']['details']
                        ))

                    expected_electronic_procurement_method_modalities = ["electronicAuction"]

                    try:
                        """
                            If compare_releases !=expected_result, then return process steps by operation-id.
                            """
                        if compare_releases == expected_result:
                            pass
                        else:
                            with allure.step('# Steps from Casandra DataBase'):
                                steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                    operation_id=GlobalClassCreateCnOnPn.operation_id)
                                allure.attach(steps, "Cassandra DataBase: steps of process")
                    except ValueError:
                        raise ValueError("Can not return BPE operation step")

                    with allure.step('Check a difference of comparing Ms release before cn creating and '
                                     'Ms release after cn creating.'):
                        allure.attach(str(compare_releases),
                                      "Actual result of comparing MS releases.")
                        allure.attach(str(expected_result),
                                      "Expected result of comparing Ms releases.")
                        assert str(compare_releases) == str(expected_result)

                    with allure.step('Check actual releases.tender.auctionPeriod object '
                                     'and expected releases.tender.auctionPeriod object.'):
                        allure.attach(str(GlobalClassCreateCnOnPn.actual_ev_release[
                                              'releases'][0]['tender']['auctionPeriod']),
                                      "Actual releases.tender.auctionPeriod object.")
                        allure.attach(str(expected_auction_period_object),
                                      "Expected releases.tender.auctionPeriod object.")
                        assert str(GlobalClassCreateCnOnPn.actual_ev_release[
                                              'releases'][0]['tender']['auctionPeriod']) == str(
                            expected_auction_period_object)

                    with allure.step('Compare actual releases.tender.procurementMethodModalities array '
                                     'and expected releases.tender.procurementMethodModalities array.'):
                        allure.attach(str(GlobalClassCreateCnOnPn.actual_ev_release[
                                              'releases'][0]['tender']['procurementMethodModalities']),
                                      "Actual releases.tender.procurementMethodModalities array.")
                        allure.attach(str(expected_electronic_procurement_method_modalities),
                                      "Expected releases.tender.procurementMethodModalities array.")
                        assert str(GlobalClassCreateCnOnPn.actual_ev_release[
                                       'releases'][0]['tender']['procurementMethodModalities']) == str(
                            expected_electronic_procurement_method_modalities)

                    with allure.step('Compare actual releases.tender.electronicAuctions_details array '
                                     'and expected releases.tender.electronicAuctions.details array.'):
                        allure.attach(str(GlobalClassCreateCnOnPn.actual_ev_release[
                                              'releases'][0]['tender']['electronicAuctions']['details']),
                                      "Actual releases.tender.electronicAuctions.details array.")
                        allure.attach(str(expected_electronic_auctions_details),
                                      "Expected releases.tender.electronicAuctions.details array.")
                        assert str(GlobalClassCreateCnOnPn.actual_ev_release[
                                       'releases'][0]['tender']['electronicAuctions']['details']) == str(
                            expected_electronic_auctions_details)

                else:
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
                                    operation_id=GlobalClassCreateCnOnPn.operation_id)
                                allure.attach(steps, "Cassandra DataBase: steps of process")
                    except ValueError:
                        raise ValueError("Can not return BPE operation step")

                    with allure.step('Check a difference of comparing Ms release before cn creating and '
                                     'Ms release after cn creating.'):
                        allure.attach(str(compare_releases),
                                      "Actual result of comparing MS releases.")
                        allure.attach(str(expected_result),
                                      "Expected result of comparing Ms releases.")
                        assert str(compare_releases) == str(expected_result)

            with allure.step('# 9.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreatePn.actual_ms_release)),
                              "Actual MS release before CnOnPn creating")
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
                              "Actual MS release after CnOnPn creating")

                compare_releases = DeepDiff(GlobalClassCreatePn.actual_ms_release,
                                            GlobalClassCreateCnOnPn.actual_ms_release)

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['tender']['contractPeriod']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreatePn.actual_ms_release['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate'],
                            "old_value": GlobalClassCreatePn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['status']": {
                            "new_value": "active",
                            "old_value": "planning"
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "evaluation",
                            "old_value": "planning"
                        },
                        "root['releases'][0]['tender']['value']['amount']": {
                            "new_value": get_sum_of_lot(lots_array=GlobalClassCreateCnOnPn.payload['tender']['lots']),
                            "old_value": GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['tender']['classification']['id']": {
                            "new_value": get_value_from_classification_cpv_dictionary_xls(
                                cpv=generate_tender_classification_id(
                                    items_array=GlobalClassCreateCnOnPn.payload['tender']['items']),
                                language=GlobalClassMetadata.language)[0],
                            "old_value": GlobalClassCreateEi.payload['tender']['classification']['id']
                        },
                        "root['releases'][0]['tender']['classification']['description']": {
                            "new_value": get_value_from_classification_cpv_dictionary_xls(
                                cpv=generate_tender_classification_id(
                                    items_array=GlobalClassCreateCnOnPn.payload['tender']['items']),
                                language=GlobalClassMetadata.language)[1],
                            "old_value": get_value_from_classification_cpv_dictionary_xls(
                                cpv=GlobalClassCreateEi.payload['tender']['classification']['id'],
                                language=GlobalClassMetadata.language)[1]
                        }
                    },
                    'iterable_item_added': {
                        "root['releases'][0]['relatedProcesses'][3]": {
                            'id': GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['relatedProcesses'][3]['id'],
                            'relationship': ['x_evaluation'],
                            'scheme': 'ocid',
                            'identifier': GlobalClassCreateCnOnPn.ev_id,
                            'uri': f"{GlobalClassMetadata.__metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}"
                                   f"/{GlobalClassCreateCnOnPn.ev_id}"
                        }
                    }
                }

                expected_contract_period_object = {
                    'startDate': get_contract_period_for_ms_release(
                        lots_array=GlobalClassCreateCnOnPn.payload['tender']['lots'])[0],
                    'endDate': get_contract_period_for_ms_release(
                        lots_array=GlobalClassCreateCnOnPn.payload['tender']['lots'])[1]
                }

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

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateCnOnPn.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Ms release before cn creating and '
                                 'Ms release after cn creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing MS releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms releases.")
                    assert str(compare_releases) == str(expected_result)

                with allure.step('Check a difference of comparing contract period object before cn creating'
                                 ' and contract period object after cn creating.'):
                    allure.attach(str(GlobalClassCreateCnOnPn.actual_ms_release[
                                          'releases'][0]['tender']['contractPeriod']),
                                  "Actual result of comparing contract period object.")
                    allure.attach(str(expected_contract_period_object),
                                  "Expected result of comparing contract period object.")
                    assert str(GlobalClassCreateCnOnPn.actual_ms_release[
                                   'releases'][0]['tender']['contractPeriod']) == str(expected_contract_period_object)
