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
from tests.utils.PayloadModels.SelectiveProcedure.Submission.submission_prepared_payload import SubmissionPreparePayload
from tests.utils.ReleaseModels.SelectiveProcedure.SubmissionPeriodEnd.submission_period_end_release import \
    SubmissionPeriodEndExpectedRelease
from tests.utils.functions_collection import time_bot
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestSubmissionPeriodEnd:
    @allure.title("Check Ev and MS releases data if submissionPeriodEnd was expired. \n"
                  "------------------------------------------------\n"
                  "create ExpenditureItem: obligatory data model without items array;\n"
                  "create FinancialSource: obligatory data model, treasury money;\n"
                  "create PlanningNotice: obligatory data model, without lots and items;\n"
                  "create CnOnPn: obligatory data model, with lots and items;\n"
                  "create Submission from Moldova: obligatory data model contains 2 candidates. \n"
                  "create Submission from Belarus: obligatory data model contains 1 candidate. \n")
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

        with allure.step(f'# {step_number}. Authorization platform one: create PlanningNotice'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            create_pn_access_token = authorization.get_access_token_for_platform_one()
            create_pn_operation_id = authorization.get_x_operation_id(create_pn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create PlanningNotice'):
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

            cn_feed_point_message = KafkaMessage(create_cn_operation_id).get_message_from_kafka()
            tp_id = cn_feed_point_message['data']['outcomes']['tp'][0]['id']
            actual_tp_release_before_submission_creating = requests.get(url=f"{pn_url}/{tp_id}").json()
            actual_ms_release_before_submission_creating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Submission from Moldova'):
            """
            Tender platform authorization for create tender phase process.
            As result get Tender platform's access token and process operation-id.
            """
            create_submission_moldova_access_token = authorization.get_access_token_for_platform_one()
            create_submission_moldova_operation_id = authorization.get_x_operation_id(
                create_submission_moldova_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Submission from Moldova'):
            """
            Send api request on BPE host for create submission.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            submission_payload_class = copy.deepcopy(SubmissionPreparePayload())
            create_submission_moldova_payload = \
                submission_payload_class.create_submission_moldova_obligatory_data_model()

            Requests().create_submission(
                host_of_request=get_hosts[1],
                access_token=create_submission_moldova_access_token,
                x_operation_id=create_submission_moldova_operation_id,
                pn_ocid=pn_ocid,
                tender_id=tp_id,
                payload=create_submission_moldova_payload,
                test_mode=True)

            create_submission_moldova_feed_point_message = KafkaMessage(
                create_submission_moldova_operation_id).get_message_from_kafka()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Submission from Belarus'):
            """
            Tender platform authorization for create tender phase process.
            As result get Tender platform's access token and process operation-id.
            """
            create_submission_belarus_access_token = authorization.get_access_token_for_platform_one()
            create_submission_belarus_operation_id = authorization.get_x_operation_id(
                create_submission_belarus_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Submission from Belarus'):
            """
            Send api request on BPE host for create submission.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            create_submission_belarus_payload = \
                submission_payload_class.create_submission_belarus_obligatory_data_model()

            Requests().create_submission(
                host_of_request=get_hosts[1],
                access_token=create_submission_belarus_access_token,
                x_operation_id=create_submission_belarus_operation_id,
                pn_ocid=pn_ocid,
                tender_id=tp_id,
                payload=create_submission_belarus_payload,
                test_mode=True)

            create_submission_belarus_feed_point_message = KafkaMessage(
                create_submission_belarus_operation_id).get_message_from_kafka()
            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                time_bot(expected_time=create_cn_payload['preQualification']['period']['endDate'])
                kafka_message_class = KafkaMessage(ocid=tp_id,
                                                   initiation="bpe")
                submission_period_end_feed_point_message = \
                    kafka_message_class.get_message_from_kafka_by_ocid_and_initiator()[0]
                allure.attach(str(submission_period_end_feed_point_message), 'Message in feed point')

                asynchronous_result_of_expired_submission_period_end = \
                    kafka_message_class.submission_period_end_no_auction_message_is_successful(
                        environment=parse_environment,
                        kafka_message=submission_period_end_feed_point_message,
                        pn_ocid=pn_ocid,
                        tender_id=tp_id)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_expired_submission_period_end is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=submission_period_end_feed_point_message['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual asynchronous result of sending the request and '
                                 'expected asynchronous result of sending request.'):
                    allure.attach(str(asynchronous_result_of_expired_submission_period_end),
                                  "Actual asynchronous result of sending the request.")
                    allure.attach(str(True), "Expected asynchronous result of sending the request.")
                    assert str(asynchronous_result_of_expired_submission_period_end) == str(True)

            with allure.step(f'# {step_number}.3. Check TP release'):
                """
                Compare actual Tp release before submission creating and actual Tp release after submission creating.
                """
                allure.attach(str(json.dumps(actual_tp_release_before_submission_creating)),
                              "Actual TP release before submission creating")

                actual_tp_release_after_submission_period_end_expired = requests.get(url=f"{pn_url}/{tp_id}").json()
                allure.attach(str(json.dumps(actual_tp_release_after_submission_period_end_expired)),
                              "Actual TP release after submissionPeriodEnd expired.")

                submission_period_end_release_class = SubmissionPeriodEndExpectedRelease(
                    language=parse_language,
                    country=parse_country,
                    pmd=parse_pmd,
                    phase="qualification",
                    actual_tp_release=actual_tp_release_after_submission_period_end_expired,
                    host_for_service=get_hosts[2])
                try:
                    """
                    Prepare expected criteria array, where source == procuringEntity.
                    """
                    final_expected_criteria_array_source_procuring_entity = \
                        [submission_period_end_release_class.prepare_criteria_object_source_procuring_entity()]
                except Exception:
                    raise Exception("Impossible to prepare expected criteria array, where source == procuringEntity.")

                try:
                    """
                    Prepare expected submission object.
                    """
                    final_expected_submissions_object = {
                        "details": []
                    }
                    expected_submissions_array = []

                    submission_details_object_from_moldova = \
                        submission_period_end_release_class.prepare_submission_object(
                            submission_payload=create_submission_moldova_payload,
                            create_submission_feed_point_message=create_submission_moldova_feed_point_message)

                    expected_submissions_array.append(submission_details_object_from_moldova)

                    submission_details_object_from_belarus = \
                        submission_period_end_release_class.prepare_submission_object(
                            submission_payload=create_submission_belarus_payload,
                            create_submission_feed_point_message=create_submission_belarus_feed_point_message)

                    expected_submissions_array.append(submission_details_object_from_belarus)

                    quantity_of_object_into_expected_submissions_details_object = \
                        len(expected_submissions_array)

                    quantity_of_object_into_release_submissions_details_object = len(
                        actual_tp_release_after_submission_period_end_expired['releases'][0]['submissions']['details'])

                    if quantity_of_object_into_expected_submissions_details_object == \
                            quantity_of_object_into_release_submissions_details_object:
                        for q in range(quantity_of_object_into_release_submissions_details_object):
                            for q_1 in range(quantity_of_object_into_expected_submissions_details_object):
                                if actual_tp_release_after_submission_period_end_expired[
                                    'releases'][0]['submissions']['details'][q]['id'] == \
                                        expected_submissions_array[q_1]['id']:

                                    final_expected_submissions_object['details'].append(
                                        expected_submissions_array[q_1]['value'])
                except Exception:
                    raise Exception("Impossible to prepare expected submission object.")

                try:
                    """
                    Prepare expected qualifications array.
                    """
                    final_expected_qualifications_array = []
                    expected_qualifications_array = []

                    qualification_object_for_first_submission = \
                        submission_period_end_release_class.prepare_qualification_object(
                            cn_payload=create_cn_payload,
                            submission_id=create_submission_moldova_feed_point_message[
                                'data']['outcomes']['submissions'][0]['id'],
                            submission_period_end_feed_point_message=submission_period_end_feed_point_message
                        )
                    expected_qualifications_array.append(qualification_object_for_first_submission)

                    qualification_object_for_second_submission = \
                        submission_period_end_release_class.prepare_qualification_object(
                            cn_payload=create_cn_payload,
                            submission_id=create_submission_belarus_feed_point_message[
                                'data']['outcomes']['submissions'][0]['id'],
                            submission_period_end_feed_point_message=submission_period_end_feed_point_message
                        )

                    expected_qualifications_array.append(qualification_object_for_second_submission)

                    quantity_of_object_into_final_expected_qualifications_array = len(expected_qualifications_array)

                    quantity_of_object_into_release_qualifications_array = len(
                        actual_tp_release_after_submission_period_end_expired['releases'][0]['qualifications'])

                    if quantity_of_object_into_final_expected_qualifications_array == \
                            quantity_of_object_into_release_qualifications_array:
                        for q in range(quantity_of_object_into_release_qualifications_array):
                            for q_1 in range(quantity_of_object_into_final_expected_qualifications_array):
                                if actual_tp_release_after_submission_period_end_expired[
                                            'releases'][0]['qualifications'][q]['id'] == \
                                        expected_qualifications_array[q_1]['id']:
                                    final_expected_qualifications_array.append(
                                        expected_qualifications_array[q_1]['value'])
                except Exception:
                    raise Exception("Impossible to prepare expected qualifications array.")

                compare_releases = dict(DeepDiff(actual_tp_release_before_submission_creating,
                                                 actual_tp_release_after_submission_period_end_expired))

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned

                try:
                    """
                    Prepare expected parties array.
                    """
                    final_expected_parties_array = []

                    parties_object_from_moldova = submission_period_end_release_class.prepare_parties_object(
                        submission_payload=create_submission_moldova_payload
                    )

                    parties_object_from_belarus = submission_period_end_release_class.prepare_parties_object(
                        submission_payload=create_submission_belarus_payload
                    )

                    expected_parties_array = parties_object_from_moldova + parties_object_from_belarus

                    quantity_of_object_into_final_expected_parties_array = len(expected_parties_array)

                    quantity_of_object_into_release_parties_array = len(
                        actual_tp_release_after_submission_period_end_expired['releases'][0]['parties'])

                    if quantity_of_object_into_final_expected_parties_array == \
                            quantity_of_object_into_release_parties_array:
                        for q in range(quantity_of_object_into_release_parties_array):
                            for q_1 in range(quantity_of_object_into_final_expected_parties_array):
                                if actual_tp_release_after_submission_period_end_expired[
                                            'releases'][0]['parties'][q]['id'] == expected_parties_array[q_1]['id']:
                                    final_expected_parties_array.append(expected_parties_array[q_1]['value'])

                except Exception:
                    raise Exception("Impossible to prepare expected parties array.")

                try:
                    """
                    Prepare expected preQualification.qualificationPeriod object.
                    """
                    final_expected_pre_qualification_qualification_period_object = \
                        submission_period_end_release_class.prepare_pre_qualification_qualification_period_object(
                            submission_period_end_feed_point_message=submission_period_end_feed_point_message
                        )
                except Exception:
                    raise Exception("Impossible to prepare expected preQualification.qualificationPeriod object.")

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['parties'], "
                                             "['releases'][0]['submissions'], "
                                             "['releases'][0]['qualifications'], "
                                             "['releases'][0]['tender']['criteria'], "
                                             "['releases'][0]['preQualification']['qualificationPeriod']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{tp_id}-"
                                f"{actual_tp_release_after_submission_period_end_expired['releases'][0]['id'][46:59]}",
                            "old_value": f"{tp_id}-"
                                         f"{actual_tp_release_before_submission_creating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": submission_period_end_feed_point_message['data']['operationDate'],
                            "old_value": actual_tp_release_before_submission_creating['releases'][0]['date']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "qualification",
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
                                operation_id=final_expected_pre_qualification_qualification_period_object[
                                    'X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing actual Tp release and expected Tp release.'):
                    allure.attach(json.dumps(compare_releases),
                                  "Actual result of comparing Tp releases.")
                    allure.attach(json.dumps(expected_result),
                                  "Expected result of comparing Tp releases.")
                    assert compare_releases == expected_result

                with allure.step('Compare actual parties array and expected parties array.'):
                    allure.attach(json.dumps(actual_tp_release_after_submission_period_end_expired[
                                                 'releases'][0]['parties']), "Actual parties array.")
                    allure.attach(json.dumps(final_expected_parties_array),
                                  "Expected parties array.")
                    assert actual_tp_release_after_submission_period_end_expired['releases'][0]['parties'] == \
                           final_expected_parties_array

                with allure.step('Compare actual submissions object and expected submissions object.'):
                    allure.attach(json.dumps(actual_tp_release_after_submission_period_end_expired['releases'][0][
                                          'submissions']), "Actual submissions object.")
                    allure.attach(json.dumps(final_expected_submissions_object),
                                  "Expected submissions object.")
                    assert actual_tp_release_after_submission_period_end_expired['releases'][0]['submissions'] == \
                           final_expected_submissions_object

                with allure.step('Compare actual qualifications array and expected qualifications array'):
                    allure.attach(json.dumps(actual_tp_release_after_submission_period_end_expired['releases'][0][
                                          'qualifications']), "Actual qualifications array.")
                    allure.attach(json.dumps(final_expected_qualifications_array), "Expected qualifications array.")
                    assert actual_tp_release_after_submission_period_end_expired['releases'][0]['qualifications'] == \
                           final_expected_qualifications_array

                with allure.step('Compare actual tender.criteria array and expected tender.criteria array'):
                    allure.attach(json.dumps(actual_tp_release_after_submission_period_end_expired['releases'][0][
                                          'tender']['criteria']), "Actual tender.criteria array.")
                    allure.attach(json.dumps(final_expected_criteria_array_source_procuring_entity),
                                  "Expected qualifications array.")
                    assert actual_tp_release_after_submission_period_end_expired['releases'][0]['tender'][
                               'criteria'] == final_expected_criteria_array_source_procuring_entity

                with allure.step('Compare actual preQualification.qualificationPeriod object and '
                                 'expected preQualification.qualificationPeriod object'):
                    allure.attach(json.dumps(actual_tp_release_after_submission_period_end_expired['releases'][0][
                                          'preQualification']['qualificationPeriod']),
                                  "Actual preQualification.qualificationPeriod object.")
                    allure.attach(json.dumps(final_expected_pre_qualification_qualification_period_object),
                                  "Expected preQualification.qualificationPeriod object.")
                    assert actual_tp_release_after_submission_period_end_expired['releases'][0]['preQualification'][
                               'qualificationPeriod'] == final_expected_pre_qualification_qualification_period_object

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare actual Ms release before submission creating and actual Ms release after submission creating.
                """
                allure.attach(json.dumps(actual_ms_release_before_submission_creating),
                              "Actual Ms release before submission creating")

                actual_ms_release_after_submission_period_end_expired = requests.get(url=f"{pn_url}/{pn_ocid}").json()
                allure.attach(json.dumps(actual_ms_release_after_submission_period_end_expired),
                              "Actual Ms release after submissionPeriodEnd expired.")

                compare_releases = dict(DeepDiff(actual_ms_release_before_submission_creating,
                                                 actual_ms_release_after_submission_period_end_expired))

                expected_result = {}

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

                        connect_to_database.submission_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_ei_operation_id)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_fs_operation_id)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_pn_operation_id)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_cn_operation_id)

                        connect_to_database.cleanup_orchestrator_steps_by_cpid(
                            cpid=pn_ocid)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=submission_period_end_feed_point_message['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Ms release before submissionPeriodEnd expired and '
                                 'Ms release after submissionPeriodEnd expired.'):
                    allure.attach(json.dumps(compare_releases), "Actual result of comparing MS releases.")
                    allure.attach(json.dumps(expected_result), "Expected result of comparing Ms releases.")
                    assert compare_releases == expected_result
