import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.PayloadModels.Budget.ExpenditureItem.expenditure_item_payload__ import EiPreparePayload
from tests.utils.PayloadModels.Budget.FinancialSource.deldete_financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModels.SelectiveProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModels.SelectiveProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.ReleaseModels.SelectiveProcedure.CnOnPn.cnonpn_prepared_release import CnOnPnExpectedRelease
from tests.utils.date_class import Date
from tests.utils.functions_collection import get_value_from_region_csv, \
    get_value_from_classification_unit_dictionary_csv

from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestUpdateCn:
    @allure.title("Check Ev and MS releases data after CnOnPn updating without optional fields. \n"
                  "------------------------------------------------\n"
                  "create ExpenditureItem: obligatory data model without items array;\n"
                  "create FinancialSource: obligatory data model, treasury money;\n"
                  "create PN_release: obligatory data model, without lots and items;\n"
                  "create CnOnPn: obligatory data model, with lots and items;\n"
                  "update CnOnPn: obligatory data model, with lots and items;\n")
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
            actual_tp_release_before_cn_updating = requests.get(url=f"{pn_url}/{tp_id}").json()
            actual_ms_release_before_cn_updating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update CnOnPn'):
            """
            Tender platform authorization for update tender phase process.
            As result get Tender platform's access token and process operation-id.
            """
            update_cn_access_token = authorization.get_access_token_for_platform_one()
            update_cn_operation_id = authorization.get_x_operation_id(update_cn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update CnOnPn'):
            """
            Send api request on BPE host for update tender phase process.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            cn_payload_class = copy.deepcopy(CnOnPnPreparePayload(host_for_services=get_hosts[2]))
            update_cn_payload = \
                cn_payload_class.update_cnonpn_obligatory_data_model(
                    actual_ei_release=actual_ei_release_before_cn_creation,
                    pre_qualification_period_end=min_submission_period_duration,
                    actual_tp_release=actual_tp_release_before_cn_updating,
                    quantity_of_items_object=1,
                    quantity_of_lots_object=1,
                    need_to_set_permanent_id_for_lots_array=True,
                    need_to_set_permanent_id_for_documents_array=True,
                    need_to_set_permanent_id_for_items_array=True)

            synchronous_result_of_sending_the_request = Requests().update_cnonpn(
                host_of_request=get_hosts[1],
                access_token=update_cn_access_token,
                x_operation_id=update_cn_operation_id,
                pn_ocid=pn_ocid,
                tender_id=tp_id,
                pn_token=pn_token,
                payload=update_cn_payload,
                test_mode=True)

            update_cn_feed_point_message = KafkaMessage(update_cn_operation_id).get_message_from_kafka()
            actual_tp_release_after_cn_updating = requests.get(url=f"{pn_url}/{tp_id}").json()
            actual_ms_release_after_cn_updating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
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
                allure.attach(str(update_cn_feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_cn_operation_id).update_cnonpn_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_cn_feed_point_message,
                    pn_ocid=pn_ocid,
                    tender_id=tp_id)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_cn_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual asynchronous result of sending the request and '
                                 'expected asynchronous result of sending request.'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual asynchronous result of sending the request.")
                    allure.attach(str(True), "Expected asynchronous result of sending the request.")
                    assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)

            with allure.step(f'# {step_number}.3. Check TP release'):
                """
                Compare actual tender phase release before updating and actual tender phase after updating.
                """
                allure.attach(str(json.dumps(actual_tp_release_before_cn_updating)),
                              "Actual TP release before updating")

                allure.attach(str(json.dumps(actual_tp_release_after_cn_updating)),
                              "Actual TP release after updating")

                compare_releases = DeepDiff(actual_tp_release_before_cn_updating,
                                            actual_tp_release_after_cn_updating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned

                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                unit_data = get_value_from_classification_unit_dictionary_csv(
                    unit_id=update_cn_payload['tender']['items'][0]['unit']['id'],
                    language=parse_language)

                try:
                    """
                    Get period_shift value from clarification.rules for this testcase
                    """
                    period_shift = int(connect_to_database.get_parameter_from_clarification_rules(
                        country=parse_country,
                        pmd=parse_pmd,
                        operation_type='all',
                        parameter='period_shift'
                    ))
                except Exception:
                    raise Exception(
                        "Impossible to get period_shift value from clarification.rules for this testcase")

                expected_release_class = copy.deepcopy(CnOnPnExpectedRelease(
                    environment=parse_environment,
                    period_shift=period_shift,
                    language=parse_language,
                    pmd=parse_pmd,
                    pn_ocid=pn_ocid,
                    pn_id=pn_id,
                    tender_id=tp_id,
                    cn_feed_point_message=update_cn_feed_point_message,
                    cn_payload=update_cn_payload,
                    actual_tp_release=actual_tp_release_after_cn_updating))

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['tender']['amendments']",
                    'dictionary_item_removed': "['releases'][0]['tender']['lots'][0]['placeOfPerformance']"
                                               "['address']['addressDetails']['locality']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value': f"{tp_id}-"
                                         f"{actual_tp_release_after_cn_updating['releases'][0]['id'][46:59]}",
                            'old_value': f"{tp_id}-"
                                         f"{actual_tp_release_before_cn_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_cn_feed_point_message['data']['operationDate'],
                            'old_value': create_cn_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            'new_value': 'tenderAmendment',
                            'old_value': 'tender'
                        },
                        "root['releases'][0]['tender']['items'][0]['description']": {
                            'new_value': update_cn_payload['tender']['items'][0]['description'],
                            'old_value': create_cn_payload['tender']['items'][0]['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['quantity']": {
                            'new_value': update_cn_payload['tender']['items'][0]['quantity'],
                            'old_value': create_cn_payload['tender']['items'][0]['quantity']
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                            'new_value': unit_data[1],
                            'old_value':
                                actual_tp_release_before_cn_updating['releases'][0]['tender']['items'][0]['unit'][
                                    'name']
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                            'new_value': unit_data[0],
                            'old_value':
                                actual_tp_release_before_cn_updating['releases'][0]['tender']['items'][0]['unit'][
                                    'id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['title']": {
                            'new_value': update_cn_payload['tender']['lots'][0]['title'],
                            'old_value': create_cn_payload['tender']['lots'][0]['title']
                        },
                        "root['releases'][0]['tender']['lots'][0]['description']": {
                            'new_value': update_cn_payload['tender']['lots'][0]['description'],
                            'old_value': create_cn_payload['tender']['lots'][0]['description']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['startDate']": {
                            'new_value': update_cn_payload['tender']['lots'][0]['contractPeriod']['startDate'],
                            'old_value': create_cn_payload['tender']['lots'][0]['contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['contractPeriod']['endDate']": {
                            'new_value': update_cn_payload['tender']['lots'][0]['contractPeriod']['endDate'],
                            'old_value': create_cn_payload['tender']['lots'][0]['contractPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress']": {
                            'new_value': update_cn_payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                'streetAddress'],
                            'old_value': create_cn_payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                'streetAddress']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['id']": {
                            'new_value': update_cn_payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                'addressDetails']['region']['id'],
                            'old_value': create_cn_payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                'addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['region']['description']": {
                            "new_value": get_value_from_region_csv(
                                region=update_cn_payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=parse_country,
                                language=parse_language)[1],
                            "old_value": get_value_from_region_csv(
                                region=create_cn_payload['tender']['lots'][0][
                                    'placeOfPerformance']['address']['addressDetails']['region']['id'],
                                country=parse_country,
                                language=parse_language)[1]
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['scheme']": {
                            'new_value': update_cn_payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['scheme'],
                            'old_value': actual_tp_release_before_cn_updating['releases'][0]['tender'][
                                'lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['id']": {
                            'new_value': update_cn_payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['id'],
                            'old_value': create_cn_payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']"
                        "['addressDetails']['locality']['description']": {
                            'new_value': update_cn_payload['tender']['lots'][0]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['description'],
                            'old_value': actual_tp_release_before_cn_updating['releases'][0]['tender'][
                                'lots'][0]['placeOfPerformance']['address']['addressDetails'][
                                'locality']['description']
                        },
                        "root['releases'][0]['tender']['enquiryPeriod']['endDate']": {
                            'new_value': Date().selectiveProcedure_enquiryPeriod_endDate(
                                preQualification_period_endDate=update_cn_payload['preQualification']['period'][
                                    'endDate'],
                                interval_seconds=period_shift),
                            'old_value': actual_tp_release_before_cn_updating['releases'][0]['tender'][
                                'enquiryPeriod']['endDate']
                        },
                        "root['releases'][0]['tender']['documents'][0]['title']": {
                            'new_value': update_cn_payload['tender']['documents'][0]['title'],
                            'old_value': create_cn_payload['tender']['documents'][0]['title']
                        },
                        "root['releases'][0]['tender']['documents'][0]['description']": {
                            'new_value': update_cn_payload['tender']['documents'][0]['description'],
                            'old_value': create_cn_payload['tender']['documents'][0]['description']
                        },
                        "root['releases'][0]['preQualification']['period']['endDate']": {
                            'new_value': update_cn_payload['preQualification']['period']['endDate'],
                            'old_value': create_cn_payload['preQualification']['period']['endDate']
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
                                operation_id=update_cn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Tp release before cn updating and '
                                 'Tp release after cn updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Tp releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Tp releases.")
                    assert str(compare_releases) == str(expected_result)

                with allure.step('Check a difference of comparing actual amendments array and '
                                 'expected amendments array.'):
                    allure.attach(str(actual_tp_release_after_cn_updating['releases'][0]['tender']['amendments']),
                                  "Actual result of comparing amendments array.")
                    allure.attach(str(expected_release_class.update_cn_amendments_array()),
                                  "Expected result of comparing amendments array.")
                    assert str(actual_tp_release_after_cn_updating['releases'][0]['tender']['amendments']) == str(
                        expected_release_class.update_cn_amendments_array())

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare actual multistage release before updating and actual multistage release after updating.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_cn_updating)),
                              "Actual Ms release before cn updating")

                allure.attach(str(json.dumps(actual_ms_release_after_cn_updating)),
                              "Actual Ms release after cn updating")

                compare_releases = dict(DeepDiff(actual_ms_release_before_cn_updating,
                                                 actual_ms_release_after_cn_updating))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{pn_ocid}-"
                                         f"{actual_ms_release_after_cn_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{pn_ocid}-"
                                         f"{actual_ms_release_before_cn_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": update_cn_feed_point_message['data']['operationDate'],
                            "old_value": create_cn_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['contractPeriod']['startDate']": {
                            "new_value": update_cn_payload['tender']['lots'][0]['contractPeriod']['startDate'],
                            "old_value": create_cn_payload['tender']['lots'][0]['contractPeriod']['startDate']
                        },
                        "root['releases'][0]['tender']['contractPeriod']['endDate']": {
                            "new_value": update_cn_payload['tender']['lots'][0]['contractPeriod']['endDate'],
                            "old_value": create_cn_payload['tender']['lots'][0]['contractPeriod']['endDate']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditureItem(cp_id=ei_ocid)

                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)

                        connect_to_database.pn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.cnonpn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_ei_operation_id)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_fs_operation_id)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_pn_operation_id)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_cn_operation_id)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=update_cn_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_cn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Ms release before cn updating and '
                                 'Ms release after cn updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing MS releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms releases.")
                    assert str(compare_releases) == str(expected_result)
