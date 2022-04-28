
import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.PayloadModels.Budget.ExpenditureItem.expenditure_item_payload__ import EiPreparePayload
from tests.utils.PayloadModels.Budget.FinancialSource.deldete_financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModels.LimitedProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModels.LimitedProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.ReleaseModels.LimitedProcedure.CnOnPn.cnonpn_prepared_release import CnOnPnExpectedRelease
from tests.utils.functions_collection import get_value_from_classification_cpv_dictionary_xls, \
    generate_tender_classification_id, get_contract_period_for_ms_release

from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestCreateCn:
    @allure.title("Check Ev and MS releases data after CnOnPn creating without optional fields. \n"
                  "------------------------------------------------\n"
                  "create ExpenditureItem: obligatory data model without items array;\n"
                  "create FinancialSource: obligatory data model, treasury money;\n"
                  "create PN_release: obligatory data model, without lots and items;\n"
                  "create CnOnPn: obligatory data model, with lots and items;\n")
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

        with allure.step(f'# {step_number}. Authorization platform one: create ExpenditureItem'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create ExpenditureItem'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_obligatory_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

            ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create FinancialSource'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create FinancialSource'):
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
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
                test_mode=True)

            fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create PN_release'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            create_pn_access_token = authorization.get_access_token_for_platform_one()
            create_pn_operation_id = authorization.get_x_operation_id(create_pn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create PN_release'):
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
                access_token=create_pn_access_token,
                x_operation_id=create_pn_operation_id,
                country=parse_country,
                language=parse_language,
                pmd=parse_pmd,
                payload=create_pn_payload,
                test_mode=True)

            pn_feed_point_message = KafkaMessage(create_pn_operation_id).get_message_from_kafka()
            pn_ocid = pn_feed_point_message['data']['ocid']
            pn_id = pn_feed_point_message['data']['outcomes']['pn'][0]['id']
            pn_token = pn_feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
            pn_url = pn_feed_point_message['data']['url']
            actual_ms_release_before_cn_creating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
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

            cn_payload_class = copy.deepcopy(CnOnPnPreparePayload(host_for_services=get_hosts[2]))
            create_cn_payload = \
                cn_payload_class.create_cnonpn_obligatory_data_model(
                    actual_ei_release=actual_ei_release_before_cn_creation,
                    pn_payload=create_pn_payload)

            synchronous_result_of_sending_the_request = Requests().createCnOnPn(
                host_of_request=get_hosts[1],
                access_token=create_cn_access_token,
                x_operation_id=create_cn_operation_id,
                pn_ocid=pn_ocid,
                pn_id=pn_id,
                pn_token=pn_token,
                payload=create_cn_payload,
                test_mode=True)

            cn_feed_point_message = KafkaMessage(create_cn_operation_id).get_message_from_kafka()
            np_id = cn_feed_point_message['data']['outcomes']['np'][0]['id']
            actual_np_release_after_cn_creating = requests.get(url=f"{pn_url}/{np_id}").json()
            actual_ms_release_after_cn_creating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
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
                allure.attach(str(cn_feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_cn_operation_id).create_cnonpn_message_is_successful(
                    environment=parse_environment,
                    kafka_message=cn_feed_point_message,
                    pn_ocid=pn_ocid,
                    pmd=parse_pmd)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_cn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual asynchronous result of sending the request and '
                                 'expected asynchronous result of sending request.'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual asynchronous result of sending the request.")
                    allure.attach(str(True), "Expected asynchronous result of sending the request.")
                    assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)

            with allure.step(f'# {step_number}.3. Check NP release'):
                """
                Compare actual NP release with expected NP release model.
                """
                allure.attach(str(json.dumps(actual_np_release_after_cn_creating)), "Actual NP release")

                expected_release_class = copy.deepcopy(CnOnPnExpectedRelease(
                    environment=parse_environment,
                    language=parse_language,
                    pmd=parse_pmd,
                    pn_ocid=pn_ocid,
                    pn_id=pn_id,
                    tender_id=np_id,
                    cn_feed_point_message=cn_feed_point_message,
                    cn_payload=create_cn_payload,
                    actual_np_release=actual_np_release_after_cn_creating))

                expected_cn_release_model = \
                    expected_release_class.cn_release_obligatory_data_model_without_lots_and_items_based_on_one_fs()

                allure.attach(str(json.dumps(expected_cn_release_model)), "Expected NP release")

                compare_releases = dict(DeepDiff(actual_np_release_after_cn_creating, expected_cn_release_model))
                expected_result = {}

                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_cn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing actual NP release and expected NP release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing NP releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing NP releases.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare actual multistage release before cn creating and actual multistage release after cn creating.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_cn_creating)),
                              "Actual Ms release before cn creating")

                allure.attach(str(json.dumps(actual_ms_release_after_cn_creating)),
                              "Actual Ms release after cn creating")

                compare_releases = dict(DeepDiff(actual_ms_release_before_cn_creating,
                                                 actual_ms_release_after_cn_creating))

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['tender']['contractPeriod']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{pn_ocid}-"
                                         f"{actual_ms_release_after_cn_creating['releases'][0]['id'][29:42]}",
                            "old_value": f"{pn_ocid}-"
                                         f"{actual_ms_release_before_cn_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": cn_feed_point_message['data']['operationDate'],
                            "old_value": pn_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['status']": {
                            "new_value": "active",
                            "old_value": "planning"
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "negotiation",
                            "old_value": "planning"
                        },
                        "root['releases'][0]['tender']['classification']['id']": {
                            "new_value": get_value_from_classification_cpv_dictionary_xls(
                                cpv=generate_tender_classification_id(
                                    items_array=create_cn_payload['tender']['items']),
                                language=parse_language)[0],
                            "old_value": create_ei_payload['tender']['classification']['id']
                        },
                        "root['releases'][0]['tender']['classification']['description']": {
                            "new_value": get_value_from_classification_cpv_dictionary_xls(
                                cpv=generate_tender_classification_id(
                                    items_array=create_cn_payload['tender']['items']), language=parse_language)[1],
                            "old_value": get_value_from_classification_cpv_dictionary_xls(
                                cpv=create_ei_payload['tender']['classification']['id'], language=parse_language)[1]
                        }
                    },
                    'iterable_item_added': {
                        "root['releases'][0]['relatedProcesses'][3]": {
                            'id': actual_ms_release_after_cn_creating['releases'][0]['relatedProcesses'][3]['id'],
                            'relationship': ['x_negotiation'],
                            'scheme': 'ocid',
                            'identifier': np_id,
                            'uri': f"{self.metadata_tender_url}/{pn_ocid}/{np_id}"
                        }
                    }
                }

                expected_contract_period_object = {
                    'startDate': get_contract_period_for_ms_release(
                        lots_array=create_cn_payload['tender']['lots'])[0],
                    'endDate': get_contract_period_for_ms_release(
                        lots_array=create_cn_payload['tender']['lots'])[1]
                }

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

                        connect_to_database.cleanup_ocds_orchestrator_operation_step_by_operation_id(operation_id=create_ei_operation_id)

                        connect_to_database.cleanup_ocds_orchestrator_operation_step_by_operation_id(operation_id=create_fs_operation_id)

                        connect_to_database.cleanup_ocds_orchestrator_operation_step_by_operation_id(operation_id=create_pn_operation_id)

                        connect_to_database.cleanup_ocds_orchestrator_operation_step_by_operation_id(operation_id=create_cn_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_cn_operation_id)
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
                    allure.attach(str(actual_ms_release_after_cn_creating['releases'][0]['tender']['contractPeriod']),
                                  "Actual result of comparing contract period object.")
                    allure.attach(str(expected_contract_period_object),
                                  "Expected result of comparing contract period object.")
                    assert str(actual_ms_release_after_cn_creating['releases'][0]['tender']['contractPeriod']) == \
                           str(expected_contract_period_object)
