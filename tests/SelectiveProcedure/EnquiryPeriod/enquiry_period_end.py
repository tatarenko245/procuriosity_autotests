import copy
import json
import time
import allure
import requests
from deepdiff import DeepDiff
from tests.utils.PayloadModel.Budget.Ei.expenditure_item_payload import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModel.SelectiveProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.EnquiryPeriod.answer_prepared_payload import AnswerPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.EnquiryPeriod.enquiry_prepared_payload import EnquiryPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.date_class import Date
from tests.utils.functions_collection import time_bot
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestCreateEnquiry:
    @allure.title("Check Tp and MS releases if enquiryPeriodEnd was expired,"
                  "set tender status suspended. \n"
                  "------------------------------------------------\n"
                  "create Ei: obligatory data model without items array;\n"
                  "create Fs: obligatory data model, treasury money;\n"
                  "create Pn: obligatory data model, without lots and items;\n"
                  "create CnOnPn: obligatory data model, with lots and items;\n"
                  "create Enquiry: obligatory data model;\n")
    def test_check_pn_ms_releases_one(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                      connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        try:
            if parse_environment == "dev":
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"

            elif parse_environment == "sandbox":
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            ei_access_token = authorization.get_access_token_for_platform_one()
            ei_operation_id = authorization.get_x_operation_id(ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_obligatory_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=ei_access_token,
                x_operation_id=ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

            ei_feed_point_message = KafkaMessage(ei_operation_id).get_message_from_kafka()
            ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            fs_access_token = authorization.get_access_token_for_platform_one()
            fs_operation_id = authorization.get_x_operation_id(fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=create_ei_payload)

            Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=fs_access_token,
                x_operation_id=fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
                test_mode=True)

            fs_feed_point_message = KafkaMessage(fs_operation_id).get_message_from_kafka()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Pn'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            pn_access_token = authorization.get_access_token_for_platform_one()
            pn_operation_id = authorization.get_x_operation_id(pn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Pn'):
            """
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            And save in variable pn_ocid, pn_id, pn_token.
            """
            time.sleep(1)
            pn_payload_class = copy.deepcopy(PnPreparePayload(
                fs_payload=create_fs_payload,
                fs_feed_point_message=fs_feed_point_message))
            create_pn_payload = \
                pn_payload_class.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            Requests().createPn(
                host_of_request=get_hosts[1],
                access_token=pn_access_token,
                x_operation_id=pn_operation_id,
                country=parse_country,
                language=parse_language,
                pmd=parse_pmd,
                payload=create_pn_payload,
                test_mode=True)

            pn_feed_point_message = KafkaMessage(pn_operation_id).get_message_from_kafka()
            pn_ocid = pn_feed_point_message['data']['ocid']
            pn_id = pn_feed_point_message['data']['outcomes']['pn'][0]['id']
            pn_token = pn_feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
            pn_url = pn_feed_point_message['data']['url']
            actual_ei_release_before_cn_creation = requests.get(
                url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create tender phase process.
            As result get Tender platform's access token and process operation-id.
            """
            create_cn_access_token = authorization.get_access_token_for_platform_one()
            create_cn_operation_id = authorization.get_x_operation_id(create_cn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create CnOnPn'):
            """
            Send api request on BPE host for create tender phase process.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            try:
                """
                Get minSubmissionPeriodDuration value from dossier.rules for this testcase
                """
                min_submission_period_duration = int(connect_to_database.get_min_submission_period_duration_rules(
                    country=parse_country,
                    pmd=parse_pmd,
                    operation_type='all',
                    parameter='minSubmissionPeriodDuration'
                ))
            except Exception:
                raise Exception("Impossible to get minSubmissionPeriodDuration value from dossier.rules "
                                "for this testcase")
            min_submission_period_duration += 180

            cn_payload_class = copy.deepcopy(CnOnPnPreparePayload(host_for_services=get_hosts[2]))
            create_cn_payload = \
                cn_payload_class.create_cnonpn_obligatory_data_model(
                    actual_ei_release=actual_ei_release_before_cn_creation,
                    pre_qualification_period_end=min_submission_period_duration,
                    pn_payload=create_pn_payload)

            Requests().createCnOnPn(
                host_of_request=get_hosts[1],
                access_token=create_cn_access_token,
                x_operation_id=create_cn_operation_id,
                pn_ocid=pn_ocid,
                pn_id=pn_id,
                pn_token=pn_token,
                payload=create_cn_payload,
                test_mode=True)

            create_cn_feed_point_message = KafkaMessage(create_cn_operation_id).get_message_from_kafka()
            tp_id = create_cn_feed_point_message['data']['outcomes']['tp'][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Enquiry'):
            """
            Tender platform authorization for create enquiry process.
            As result get Tender platform's access token and process operation-id.
            """
            create_enquiry_access_token = authorization.get_access_token_for_platform_one()
            create_enquiry_operation_id = authorization.get_x_operation_id(create_enquiry_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Enquiry'):
            """
            Send api request on BPE host for create enquiry process.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            enquiry_payload_class = copy.deepcopy(EnquiryPreparePayload())
            create_enquiry_payload = \
                enquiry_payload_class.create_enquiry_obligatory_data_model()

            Requests().create_enquiry(
                host_of_request=get_hosts[1],
                access_token=create_enquiry_access_token,
                x_operation_id=create_enquiry_operation_id,
                pn_ocid=pn_ocid,
                tender_id=tp_id,
                payload=create_enquiry_payload,
                test_mode=True)

            create_enquiry_feed_point_message_bpe = KafkaMessage(create_enquiry_operation_id).get_message_from_kafka()
            enquiry_id = create_enquiry_feed_point_message_bpe['data']['outcomes']['enquiries'][0]['id']
            enquiry_token = create_enquiry_feed_point_message_bpe['data']['outcomes']['enquiries'][0]['X-TOKEN']
            actual_tp_release_before_enquiry_period_end_expired = requests.get(url=f"{pn_url}/{tp_id}").json()
            actual_ms_release_before_enquiry_period_end_expired = requests.get(url=f"{pn_url}/{pn_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step(f'# {step_number}.3. Check TP release'):
                """
                Compare actual TP release before enquiry period end expired and 
                actual TP release after enquiry period end expired.
                """
                allure.attach(str(json.dumps(actual_tp_release_before_enquiry_period_end_expired)),
                              "Actual TP release before before enquiry period end expired.")

                time_bot(expected_time=create_cn_payload['preQualification']['period']['endDate'])

                actual_tp_release_after_enquiry_period_end_expired = requests.get(url=f"{pn_url}/{tp_id}").json()
                allure.attach(str(json.dumps(actual_tp_release_after_enquiry_period_end_expired)),
                              "Actual TP release after enquiry period end expired.")

                compare_releases = DeepDiff(actual_tp_release_before_enquiry_period_end_expired,
                                            actual_tp_release_after_enquiry_period_end_expired)

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{tp_id}-"
                                f"{actual_tp_release_after_enquiry_period_end_expired['releases'][0]['id'][46:59]}",
                            "old_value":
                                f"{tp_id}-"
                                f"{actual_tp_release_before_enquiry_period_end_expired['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": create_cn_payload['preQualification']['period']['endDate'],
                            "old_value": actual_tp_release_before_enquiry_period_end_expired['releases'][0]['date']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "suspended",
                            "old_value": "submission"
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
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_enquiry_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Tp release before enquiry creating and '
                                 'Tp release after enquiry creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Tp releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Tp releases.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare actual Ms release before enquiry period end expired and 
                actual Ms release after enquiry period end expired.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_enquiry_period_end_expired)),
                              "Actual MS release before enquiry period end expired.")

                actual_ms_release_after_enquiry_period_end_expired = requests.get(url=f"{pn_url}/{pn_ocid}").json()
                allure.attach(str(json.dumps(actual_ms_release_after_enquiry_period_end_expired)),
                              "Actual MS release after enquiry period end expired.")

                compare_releases = dict(DeepDiff(actual_ms_release_before_enquiry_period_end_expired,
                                                 actual_ms_release_after_enquiry_period_end_expired))

                expected_result = {}

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)

                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)

                        connect_to_database.pn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.cnonpn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.enquiry_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=ei_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=fs_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=pn_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_cn_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_enquiry_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_cn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Ms release before enquiry creating and '
                                 'Ms release after enquiry creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing MS releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms releases.")
                    assert str(compare_releases) == str(expected_result)

    @allure.title("Check Tp and MS releases if enquiry period end was expired,"
                  "set tender status submission. \n"
                  "------------------------------------------------\n"
                  "create Ei: obligatory data model without items array;\n"
                  "create Fs: obligatory data model, treasury money;\n"
                  "create Pn: obligatory data model, without lots and items;\n"
                  "create CnOnPn: obligatory data model, with lots and items;\n"
                  "create Enquiry: obligatory data model;\n"
                  "create Answer: obligatory data model;\n")
    def test_check_pn_ms_releases_one(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                      connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        try:
            if parse_environment == "dev":
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"

            elif parse_environment == "sandbox":
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            ei_access_token = authorization.get_access_token_for_platform_one()
            ei_operation_id = authorization.get_x_operation_id(ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_obligatory_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=ei_access_token,
                x_operation_id=ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

            ei_feed_point_message = KafkaMessage(ei_operation_id).get_message_from_kafka()
            ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            fs_access_token = authorization.get_access_token_for_platform_one()
            fs_operation_id = authorization.get_x_operation_id(fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=create_ei_payload)

            Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=fs_access_token,
                x_operation_id=fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
                test_mode=True)

            fs_feed_point_message = KafkaMessage(fs_operation_id).get_message_from_kafka()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Pn'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            pn_access_token = authorization.get_access_token_for_platform_one()
            pn_operation_id = authorization.get_x_operation_id(pn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Pn'):
            """
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            And save in variable pn_ocid, pn_id, pn_token.
            """
            time.sleep(1)
            pn_payload_class = copy.deepcopy(PnPreparePayload(
                fs_payload=create_fs_payload,
                fs_feed_point_message=fs_feed_point_message))
            create_pn_payload = \
                pn_payload_class.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            Requests().createPn(
                host_of_request=get_hosts[1],
                access_token=pn_access_token,
                x_operation_id=pn_operation_id,
                country=parse_country,
                language=parse_language,
                pmd=parse_pmd,
                payload=create_pn_payload,
                test_mode=True)

            pn_feed_point_message = KafkaMessage(pn_operation_id).get_message_from_kafka()
            pn_ocid = pn_feed_point_message['data']['ocid']
            pn_id = pn_feed_point_message['data']['outcomes']['pn'][0]['id']
            pn_token = pn_feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
            pn_url = pn_feed_point_message['data']['url']
            actual_ei_release_before_cn_creation = requests.get(
                url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create tender phase process.
            As result get Tender platform's access token and process operation-id.
            """
            create_cn_access_token = authorization.get_access_token_for_platform_one()
            create_cn_operation_id = authorization.get_x_operation_id(create_cn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create CnOnPn'):
            """
            Send api request on BPE host for create tender phase process.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            try:
                """
                Get minSubmissionPeriodDuration value from dossier.rules for this testcase
                """
                min_submission_period_duration = int(connect_to_database.get_min_submission_period_duration_rules(
                    country=parse_country,
                    pmd=parse_pmd,
                    operation_type='all',
                    parameter='minSubmissionPeriodDuration'
                ))
            except Exception:
                raise Exception("Impossible to get minSubmissionPeriodDuration value from dossier.rules "
                                "for this testcase")
            min_submission_period_duration += 180

            cn_payload_class = copy.deepcopy(CnOnPnPreparePayload(host_for_services=get_hosts[2]))
            create_cn_payload = \
                cn_payload_class.create_cnonpn_obligatory_data_model(
                    actual_ei_release=actual_ei_release_before_cn_creation,
                    pre_qualification_period_end=min_submission_period_duration,
                    pn_payload=create_pn_payload)

            Requests().createCnOnPn(
                host_of_request=get_hosts[1],
                access_token=create_cn_access_token,
                x_operation_id=create_cn_operation_id,
                pn_ocid=pn_ocid,
                pn_id=pn_id,
                pn_token=pn_token,
                payload=create_cn_payload,
                test_mode=True)

            create_cn_feed_point_message = KafkaMessage(create_cn_operation_id).get_message_from_kafka()
            tp_id = create_cn_feed_point_message['data']['outcomes']['tp'][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Enquiry'):
            """
            Tender platform authorization for create enquiry process.
            As result get Tender platform's access token and process operation-id.
            """
            create_enquiry_access_token = authorization.get_access_token_for_platform_one()
            create_enquiry_operation_id = authorization.get_x_operation_id(create_enquiry_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Enquiry'):
            """
            Send api request on BPE host for create enquiry process.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            enquiry_payload_class = copy.deepcopy(EnquiryPreparePayload())
            create_enquiry_payload = \
                enquiry_payload_class.create_enquiry_obligatory_data_model()

            Requests().create_enquiry(
                host_of_request=get_hosts[1],
                access_token=create_enquiry_access_token,
                x_operation_id=create_enquiry_operation_id,
                pn_ocid=pn_ocid,
                tender_id=tp_id,
                payload=create_enquiry_payload,
                test_mode=True)

            create_enquiry_feed_point_message_bpe = KafkaMessage(create_enquiry_operation_id).get_message_from_kafka()
            enquiry_id = create_enquiry_feed_point_message_bpe['data']['outcomes']['enquiries'][0]['id']
            enquiry_token = create_enquiry_feed_point_message_bpe['data']['outcomes']['enquiries'][0]['X-TOKEN']
            time_bot(expected_time=create_cn_payload['preQualification']['period']['endDate'])
            actual_tp_release_after_suspended = requests.get(url=f"{pn_url}/{tp_id}").json()
            actual_ms_release_after_suspended = requests.get(url=f"{pn_url}/{pn_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Answer'):
            """
            Tender platform authorization for create answer process.
            As result get Tender platform's access token and process operation-id.
            """
            create_answer_access_token = authorization.get_access_token_for_platform_one()
            create_answer_operation_id = authorization.get_x_operation_id(create_answer_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Answer'):
            """
            Send api request on BPE host for create answer process.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            answer_payload_class = copy.deepcopy(AnswerPreparePayload())
            create_answer_payload = answer_payload_class.create_answer_obligatory_data_model()

            synchronous_result_of_sending_the_request = Requests().create_answer(
                host_of_request=get_hosts[1],
                access_token=create_answer_access_token,
                x_operation_id=create_answer_operation_id,
                pn_ocid=pn_ocid,
                tender_id=tp_id,
                enquiry_id=enquiry_id,
                enquiry_token=enquiry_token,
                payload=create_answer_payload,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step(f'# {step_number}.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                with allure.step('Compare actual status code of sending the request and '
                                 'expected status code of sending request.'):
                    allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                                  "Actual status code of sending the request.")
                    allure.attach(str(202), "Expected status code of sending request.")
                    assert str(synchronous_result_of_sending_the_request.status_code) == str(202)

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                create_answer_feed_point_message = KafkaMessage(create_answer_operation_id).get_message_from_kafka()

                allure.attach(str(create_answer_feed_point_message), 'Message in feed point where initiator bpe')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_answer_operation_id).create_answer_message_is_successful(
                    environment=parse_environment,
                    kafka_message=create_answer_feed_point_message,
                    pn_ocid=pn_ocid,
                    ev_id=tp_id)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_answer_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual asynchronous result of sending the request with BPE initiator and '
                                 'expected asynchronous result of sending the request with BPE initiator.'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual asynchronous result of sending the request with BPE initiator.")
                    allure.attach(str(True), "Expected asynchronous result of sending the request with BPE initiator.")
                    assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)

            with allure.step(f'# {step_number}.3. Check TP release'):
                """
                Compare actual TP release before enquiry period end expired and 
                actual TP release after enquiry period end expired.
                """
                allure.attach(str(json.dumps(actual_tp_release_after_suspended)),
                              "Actual Tp release after tender suspended.")

                actual_tp_release_after_unsuspended = requests.get(url=f"{pn_url}/{tp_id}").json()
                allure.attach(str(json.dumps(actual_tp_release_after_unsuspended)),
                              "Actual Tp release after tender unsuspended.")

                compare_releases = DeepDiff(actual_tp_release_after_suspended,
                                            actual_tp_release_after_unsuspended)

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned

                try:
                    """
                    Get period_shift value from clarification.rules for this testcase
                    """
                    period_shift = int(connect_to_database.get_period_shift_rules(
                        country=parse_country,
                        pmd=parse_pmd,
                        operation_type='all',
                        parameter='period_shift'
                    ))
                except Exception:
                    raise Exception("Impossible to get period_shift value from clarification.rules for this testcase")

                try:
                    """
                    Get extensionAfterUnsuspended value from dossier.rules for this testcase
                    """
                    extension_after_unsuspended = int(connect_to_database.get_min_submission_period_duration_rules(
                        country=parse_country,
                        pmd=parse_pmd,
                        operation_type='all',
                        parameter='extensionAfterUnsuspended'
                    ))
                except Exception:
                    raise Exception("Impossible to get extensionAfterUnsuspended value "
                                    "from clarification.rules for this testcase")

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['tender']['enquiries'][0]['answer'], "
                                             "['releases'][0]['tender']['enquiries'][0]['dateAnswered']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{tp_id}-{actual_tp_release_after_unsuspended['releases'][0]['id'][46:59]}",
                            "old_value":
                                f"{tp_id}-{actual_tp_release_after_suspended['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": create_answer_feed_point_message['data']['operationDate'],
                            "old_value": actual_tp_release_after_suspended['releases'][0]['date']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "submission",
                            "old_value": "suspended"
                        },
                        "root['releases'][0]['tender']['enquiryPeriod']['endDate']": {
                            "new_value": Date().selective_procedure_enquiry_period_end_date_after_unsuspended(
                                create_answer_date=create_answer_feed_point_message['data']['operationDate'],
                                interval_seconds=period_shift),
                            "old_value": actual_tp_release_after_suspended[
                                'releases'][0]['tender']['enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['preQualification']['period']['endDate']": {
                            "new_value": Date().selective_procedure_pre_qualification_period_end_date_after_unsuspended(
                                create_answer_date=create_answer_feed_point_message['data']['operationDate'],
                                interval_seconds=extension_after_unsuspended),
                            "old_value": actual_tp_release_after_suspended[
                                'releases'][0]['preQualification']['period']['endDate']
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
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_enquiry_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Tp release before enquiry creating and '
                                 'Tp release after enquiry creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Tp releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Tp releases.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare actual Ms release before enquiry period end expired and
                actual Ms release after enquiry period end expired.
                """
                allure.attach(str(json.dumps(actual_ms_release_after_suspended)),
                              "Actual Ms release after tender suspended.")

                actual_ms_release_after_unsuspended = requests.get(url=f"{pn_url}/{pn_ocid}").json()
                allure.attach(str(json.dumps(actual_ms_release_after_unsuspended)),
                              "Actual Ms release after tender unsuspended.")

                compare_releases = dict(DeepDiff(actual_ms_release_after_suspended,
                                                 actual_ms_release_after_unsuspended))

                expected_result = {}

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)

                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)

                        connect_to_database.pn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.cnonpn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.enquiry_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=ei_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=fs_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=pn_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_cn_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_enquiry_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_cn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Ms release before enquiry creating and '
                                 'Ms release after enquiry creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing MS releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms releases.")
                    assert str(compare_releases) == str(expected_result)
