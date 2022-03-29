import copy
import json
import time
import allure
import requests
from deepdiff import DeepDiff
from tests.utils.PayloadModel.Budget.Ei.expenditure_item_payload__ import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.deldete_financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModel.SelectiveProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.Qualification.qualification_prepared_payload import \
    QualificationPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.QualificationDeclare.qualification_declare_prepared_payload import \
    DeclarePreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.Submission.submission_prepared_payload import SubmissionPreparePayload

from tests.utils.functions_collection import time_bot, get_id_token_of_qualification_in_pending_awaiting_state
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestQualification:
    @allure.title("Check Ev and MS releases data after qualificationDeclareNonConflictInterest creating "
                  "without optional fields. \n"
                  "------------------------------------------------\n"
                  "create Ei: obligatory data model without items array;\n"
                  "create Fs: obligatory data model, treasury money;\n"
                  "create Pn: obligatory data model, without lots and items;\n"
                  "create CnOnPn: obligatory data model, with lots and items;\n"
                  "create Submission from Moldova: obligatory data model contains 2 candidates. \n"
                  "create Submission from Belarus: obligatory data model contains 1 candidate \n"
                  "create QualificationDeclaration: obligatory data model. \n"
                  "create QualificationConsideration: payload is not needed. \n"
                  "create Qualification: obligatory data model. \n")
    def test_check_pn_ms_releases_one(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                      connect_to_database,
                                      queue_mapper):
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
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
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
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

            ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
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
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
                test_mode=True)

            fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Pn'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            create_pn_access_token = authorization.get_access_token_for_platform_one()
            create_pn_operation_id = authorization.get_x_operation_id(create_pn_access_token)
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

        time_bot(expected_time=create_cn_payload['preQualification']['period']['endDate'])
        kafka_message_class = KafkaMessage(ocid=tp_id,
                                           initiation="bpe")
        submission_period_end_feed_point_message = \
            kafka_message_class.get_message_from_kafka_by_ocid_and_initiator()[0]

        actual_tp_release_before_qualif_declaration_creation = requests.get(url=f"{pn_url}/{tp_id}").json()

        requirements_list = list()
        for c in actual_tp_release_before_qualif_declaration_creation['releases'][0]['tender']['criteria']:
            for c_1 in c:
                if c_1 == "source":
                    if c['source'] == "procuringEntity":
                        requirement_groups_list = list()
                        for rg in c['requirementGroups']:
                            for rg_1 in rg:
                                if rg_1 == "id":
                                    requirement_groups_list.append(rg['id'])

                        for x in range(len(requirement_groups_list)):
                            for rr in c['requirementGroups'][x]['requirements']:
                                for rr_1 in rr:
                                    if rr_1 == "id":
                                        requirements_list.append(rr['id'])
        candidates_list = list()
        for qu in actual_tp_release_before_qualif_declaration_creation['releases'][0]['qualifications']:
            if qu['status'] == "pending":
                if qu['statusDetails'] == "awaiting":
                    for s in actual_tp_release_before_qualif_declaration_creation[
                            'releases'][0]['submissions']['details']:
                        if s['id'] == qu['relatedSubmission']:
                            for cand in range(len(s['candidates'])):
                                candidate_dictionary = {
                                    "qualification_id": qu['id'],
                                    "candidates": s['candidates'][cand]
                                }
                                candidates_list.append(candidate_dictionary)
        qualification_list = list()
        qualifications = get_id_token_of_qualification_in_pending_awaiting_state(
            actual_qualifications_array=actual_tp_release_before_qualif_declaration_creation[
                'releases'][0]['qualifications'],
            feed_point_message=submission_period_end_feed_point_message)

        for q in qualifications:
            qualification_list.append(q)

        for x in range(len(requirements_list)):
            for y in range(len(candidates_list)):

                step_number += 1
                with allure.step(f'# {step_number}. Authorization platform one: create '
                                 f'QualificationDeclaration with {queue_mapper[y]} candidate and'
                                 f' {queue_mapper[x]} requirement.'):
                    """
                    Tender platform authorization for create QualificationDeclaration process.
                    As result get Tender platform's access token and process operation-id.
                    """
                    create_qualification_declaration_access_token = authorization.get_access_token_for_platform_one()
                    create_qualification_declaration_operation_id = authorization.get_x_operation_id(
                        create_qualification_declaration_access_token)

                step_number += 1
                with allure.step(f'# {step_number}. Send request to create '
                                 f'QualificationDeclaration with {queue_mapper[y]} candidate and'
                                 f' {queue_mapper[x]} requirement.'):
                    """
                    Send api request on BPE host for create QualificationDeclaration.
                    Save synchronous result of sending the request and asynchronous result of sending the request.
                    """
                    time.sleep(1)
                    qualification_declaration_payload_class = copy.deepcopy(DeclarePreparePayload(
                        host_for_services=get_hosts[2]))

                    for q in range(len(qualification_list)):
                        if qualification_list[q][0] == candidates_list[y]['qualification_id']:
                            create_qualification_declaration_payload = \
                                qualification_declaration_payload_class.create_declare_new_person_obligatory_data_model(
                                    requirement_id=requirements_list[x],
                                    tenderer_id=candidates_list[y]['candidates']['id']
                                )

                            Requests().create_declaration_qualification_non_conflict_interest(
                                host_of_request=get_hosts[1],
                                access_token=create_qualification_declaration_access_token,
                                x_operation_id=create_qualification_declaration_operation_id,
                                pn_ocid=pn_ocid,
                                tender_id=tp_id,
                                qualification_id=qualification_list[q][0],
                                qualification_token=qualification_list[q][1],
                                payload=create_qualification_declaration_payload,
                                test_mode=True)

        step_number += 1
        for q in range(len(qualification_list)):
            with allure.step(f'# {step_number}. Authorization platform one: create '
                             f'QualificationConsideration for {queue_mapper[q]} qualification.'):
                """
                Tender platform authorization for create QualificationConsideration process.
                As result get Tender platform's access token and process operation-id.
                """
                create_qualification_consideration_access_token = \
                    authorization.get_access_token_for_platform_one()
                create_qualification_consideration_operation_id = authorization.get_x_operation_id(
                    create_qualification_consideration_access_token)

            step_number += 1
            with allure.step(f'# {step_number}. Send request to create '
                             f'QualificationConsideration for {queue_mapper[q]} qualification.'):
                """
                Send api request on BPE host for create QualificationConsideration.
                Save synchronous result of sending the request and asynchronous result of sending the request.
                """
                time.sleep(1)

                Requests().create_consideration_qualification(
                    host_of_request=get_hosts[1],
                    access_token=create_qualification_declaration_access_token,
                    x_operation_id=create_qualification_consideration_operation_id,
                    pn_ocid=pn_ocid,
                    tender_id=tp_id,
                    qualification_id=qualification_list[q][0],
                    qualification_token=qualification_list[q][1],
                    test_mode=True)
        time.sleep(10)
        actual_tp_release_before_qualification_creation = requests.get(url=f"{pn_url}/{tp_id}").json()
        actual_ms_release_before_qualification_creation = requests.get(url=f"{pn_url}/{pn_ocid}").json()

        for q in range(len(qualification_list)):
            step_number += 1
            with allure.step(f'# {step_number}. Authorization platform one: create '
                             f'Qualification process for {queue_mapper[q]} qualification.'):
                """
                Tender platform authorization for create QualificationConsideration process.
                As result get Tender platform's access token and process operation-id.
                """
                create_qualification_access_token = authorization.get_access_token_for_platform_one()
                create_qualification_operation_id = authorization.get_x_operation_id(create_qualification_access_token)

            step_number += 1
            with allure.step(f'# {step_number}. Send request to create '
                             f'Qualification process for {queue_mapper[q]} qualification.'):
                """
                Send api request on BPE host for create QualificationConsideration.
                Save synchronous result of sending the request and asynchronous result of sending the request.
                """
                time.sleep(1)

                qualification_payload_class = copy.deepcopy(QualificationPreparePayload(host_for_services=get_hosts[2]))

                create_qualification_payload = qualification_payload_class.create_qualification_obligatory_data_model(
                    status="active"
                )

                synchronous_result_of_sending_the_request = \
                    Requests().create_qualification(
                        host_of_request=get_hosts[1],
                        access_token=create_qualification_access_token,
                        x_operation_id=create_qualification_operation_id,
                        pn_ocid=pn_ocid,
                        tender_id=tp_id,
                        qualification_id=qualification_list[q][0],
                        qualification_token=qualification_list[q][1],
                        payload=create_qualification_payload,
                        test_mode=True)

            step_number += 1
            with allure.step(f'# {step_number}. See result for {queue_mapper[q]} qualification.'):
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

                with allure.step(f'# {step_number}.2. Check message in feed point for Qualification process.'):
                    """
                    Check the asynchronous_result_of_sending_the_request.
                    """
                    kafka_message_class = KafkaMessage(create_qualification_operation_id)
                    create_qualification_feed_point_message = kafka_message_class.get_message_from_kafka()
                    allure.attach(str(create_qualification_feed_point_message), 'Message in feed point.')

                    asynchronous_result_of_sending_the_request_was_checked = \
                        kafka_message_class.qualification_process_message_is_successful(
                            environment=parse_environment,
                            kafka_message=create_qualification_feed_point_message,
                            pn_ocid=pn_ocid,
                            tender_id=tp_id)

                    try:
                        """
                        If asynchronous_result_of_sending_the_request was False,
                        then return process steps by operation-id.
                        """
                        if asynchronous_result_of_sending_the_request_was_checked is False:
                            with allure.step('# Steps from Casandra DataBase'):
                                steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                    operation_id=create_qualification_operation_id)
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
                    Compare actual Tp release before Qualification creating and
                    actual Tp release after Qualification creating.
                    """
                    allure.attach(str(json.dumps(actual_tp_release_before_qualification_creation)),
                                  "Actual TP release before Qualification creation.")

                    actual_tp_release_after_qualification_creation = \
                        requests.get(url=f"{pn_url}/{tp_id}").json()
                    allure.attach(str(json.dumps(actual_tp_release_after_qualification_creation)),
                                  "Actual TP release after Qualification creation.")

                    compare_releases = dict(
                        DeepDiff(actual_tp_release_before_qualification_creation,
                                 actual_tp_release_after_qualification_creation))

                    new_releases_timestamp = actual_tp_release_after_qualification_creation[
                                                 'releases'][0]['id'][46:59]
                    old_releases_timestamp = actual_tp_release_before_qualification_creation[
                                                 'releases'][0]['id'][46:59]

                    expected_result = {
                        "values_changed": {
                            "root['releases'][0]['id']": {
                                "new_value": f"{tp_id}-{new_releases_timestamp}",
                                "old_value": f"{tp_id}-{old_releases_timestamp}"
                            },
                            "root['releases'][0]['date']": {
                                "new_value": create_qualification_feed_point_message['data']['operationDate'],
                                "old_value": actual_tp_release_before_qualification_creation['releases'][0]['date']
                            },
                            f"root['releases'][0]['qualifications'][{q}]['date']": {
                                "new_value": create_qualification_feed_point_message['data']['operationDate'],
                                "old_value": actual_tp_release_before_qualification_creation[
                                    'releases'][0]['qualifications'][q]['date']
                            },
                            f"root['releases'][0]['qualifications'][{q}]['statusDetails']": {
                                "new_value": create_qualification_payload['qualification']['statusDetails'],
                                "old_value": actual_tp_release_before_qualification_creation[
                                    'releases'][0]['qualifications'][q]['statusDetails']
                            }
                        }
                    }

                    actual_tp_release_before_qualification_creation = requests.get(url=f"{pn_url}/{tp_id}").json()

                    try:
                        """
                            If compare_releases !=expected_result,
                            then return process steps by operation-id.
                            """
                        if compare_releases == expected_result:
                            pass
                        else:
                            with allure.step('# Steps from Casandra DataBase'):
                                steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                    operation_id=create_qualification_operation_id)
                                allure.attach(steps, "Cassandra DataBase: steps of process")
                    except ValueError:
                        raise ValueError("Can not return BPE operation step")

                    with allure.step(
                            'Check a difference of comparing Tp release before '
                            'Qualification creation and Tp release after Qualification creation.'):
                        allure.attach(json.dumps(compare_releases),
                                      "Actual result of comparing Tp releases.")
                        allure.attach(json.dumps(expected_result),
                                      "Expected result of comparing Tp releases.")
                        assert compare_releases == expected_result

                with allure.step(f'# {step_number}.4. Check MS release'):
                    """
                    Compare actual Ms release before Qualification creating and
                    actual Ms release after Qualification creating.
                    """
                    allure.attach(json.dumps(actual_ms_release_before_qualification_creation),
                                  "Actual MS release before Qualification creation")

                    actual_ms_release_after_qualification_creation = requests.get(url=f"{pn_url}/{pn_ocid}").json()
                    allure.attach(json.dumps(actual_ms_release_after_qualification_creation),
                                  "Actual MS release after Qualification creation")

                    compare_releases = dict(
                        DeepDiff(actual_ms_release_before_qualification_creation,
                                 actual_ms_release_after_qualification_creation))

                    expected_result = {}

                    actual_ms_release_before_qualification_creation = requests.get(url=f"{pn_url}/{pn_ocid}").json()

                    if q == 1:
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

                                connect_to_database.submission_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                                connect_to_database.qualification_declaration_process_cleanup_table_of_services(
                                    pn_ocid=pn_ocid)

                                connect_to_database.qualification_consideration_process_cleanup_table_of_services(
                                    pn_ocid=pn_ocid)

                                connect_to_database.qualification_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                                connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)

                                connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)

                                connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_pn_operation_id)

                                connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_cn_operation_id)

                                connect_to_database.cleanup_orchestrator_operation_step_by_operationid(
                                    operation_id=create_submission_belarus_operation_id)

                                connect_to_database.cleanup_orchestrator_operation_step_by_operationid(
                                    operation_id=create_submission_moldova_operation_id)

                                connect_to_database.cleanup_orchestrator_operation_step_by_operationid(
                                    operation_id=submission_period_end_feed_point_message['X-OPERATION-ID'])

                                connect_to_database.cleanup_orchestrator_operation_step_by_operationid(
                                    operation_id=create_qualification_declaration_operation_id)

                                connect_to_database.cleanup_orchestrator_operation_step_by_operationid(
                                    operation_id=create_qualification_consideration_operation_id)

                            else:
                                with allure.step('# Steps from Casandra DataBase'):
                                    steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                        operation_id=create_qualification_consideration_operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            raise ValueError("Can not return BPE operation step")

                    with allure.step('Check a difference of comparing Ms release before '
                                     'Qualification creating and Ms release after Qualification creating.'):
                        allure.attach(json.dumps(compare_releases),
                                      "Actual result of comparing MS releases.")
                        allure.attach(json.dumps(expected_result),
                                      "Expected result of comparing Ms releases.")
                        assert compare_releases == expected_result
