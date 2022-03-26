import copy
import json
import time
import allure
import requests
from deepdiff import DeepDiff
from tests.utils.PayloadModel.Budget.Ei.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.Qualification.qualification_prepared_payload import \
    QualificationPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.QualificationDeclare.qualification_declare_prepared_payload import \
    DeclarePreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.StartSecondStage.start_second_stage_prepared_payload import \
    StartSecondStagePreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.Submission.submission_prepared_payload import SubmissionPreparePayload
from tests.utils.PayloadModel.SelectiveProcedure.SubmitBid.bid_prepared_payload import BidPreparePayload
from tests.utils.ReleaseModel.SelectiveProcedure.TenderPeriodEnd.tender_period_end_release import \
    TenderPeriodExpectedChanges
from tests.utils.functions import time_bot, get_id_token_of_qualification_in_pending_awaiting_state, check_uuid_version
from tests.utils.message_for_platform import MessageForPlatform
from tests.utils.my_requests import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestTenderPeriodEnd:
    @allure.title("Check TP and MS releases data if TenderPeriodEnd was expired\n"
                  "------------------------------------------------\n"
                  "create Ei: obligatory data model without items array;\n"
                  "create Fs: obligatory data model, treasury money;\n"
                  "create Pn: obligatory data model, without lots and items;\n"
                  "create CnOnPn: obligatory data model, with lots and items;\n"
                  "create Submission from Moldova: obligatory data model contains 2 candidates. \n"
                  "create Submission from Belarus: obligatory data model contains 1 candidate \n"
                  "create QualificationDeclaration: obligatory data model. \n"
                  "create QualificationConsideration: payload is not needed. \n"
                  "create Qualification: obligatory data model. \n"
                  "create QualificationProtocol: payload is not needed. \n"
                  "startSecondStage: obligatory data model;\n"
                  "submit bid by first tenderer: obligatory data model;\n"
                  "submit bid by second tenderer: obligatory data model;\n"
                  "tender period end: payload is not needed\n")
    def test_check_tp_ms_releases_one(self, get_hosts, country, language, pmd, environment, connection_to_database,
                                      queue_mapper):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        try:
            if environment == "dev":
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"

            elif environment == "sandbox":
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
                country=country,
                language=language,
                payload=create_ei_payload,
                test_mode=True)

            ei_feed_point_message = MessageForPlatform(create_ei_operation_id).get_message_from_kafka_topic()
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
            fs_payload_class = copy.deepcopy(FsPreparePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=create_ei_payload)

            Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
                test_mode=True)

            fs_feed_point_message = MessageForPlatform(create_fs_operation_id).get_message_from_kafka_topic()
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
                country=country,
                language=language,
                pmd=pmd,
                payload=create_pn_payload,
                test_mode=True)

            pn_feed_point_message = MessageForPlatform(create_pn_operation_id).get_message_from_kafka_topic()
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
                min_submission_period_duration = int(connection_to_database.get_min_submission_period_duration_rules(
                    country=country,
                    pmd=pmd,
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

            cn_feed_point_message = MessageForPlatform(create_cn_operation_id).get_message_from_kafka_topic()
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
        kafka_message_class = MessageForPlatform(ocid=tp_id,
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

                step_number += 1
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

                create_qualification_payload = \
                    qualification_payload_class.create_qualification_obligatory_data_model(status="active")

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

        with allure.step(f'# {step_number}. Authorization platform one: create QualificationProtocol process.'):
            """
            Tender platform authorization for create QualificationProtocol process.
            As result get Tender platform's access token and process operation-id.
            """
            create_qualification_protocol_access_token = authorization.get_access_token_for_platform_one()
            create_qualification_protocol_operation_id = \
                authorization.get_x_operation_id(create_qualification_protocol_access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send request to create QualificationProtocol process.'):
            """
            Send api request on BPE host for create QualificationProtocol.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            Requests().create_qualification_protocol(
                host_of_request=get_hosts[1],
                access_token=create_qualification_protocol_access_token,
                x_operation_id=create_qualification_protocol_operation_id,
                pn_ocid=pn_ocid,
                pn_token=pn_token,
                tender_id=tp_id,
                test_mode=True)

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create StartSecondStage process.'):
            """
            Tender platform authorization for create StartSecondStage process.
            As result get Tender platform's access token and process operation-id.
            """
            create_start_second_stage_access_token = authorization.get_access_token_for_platform_one()
            create_start_second_stage_operation_id = \
                authorization.get_x_operation_id(create_start_second_stage_access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send request to create StartSecondStage process.'):
            """
            Send api request on BPE host for create StartSecondStage.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            start_second_stage_payload_class = copy.deepcopy(StartSecondStagePreparePayload(tender_period_interval=60))
            start_second_stage_payload = start_second_stage_payload_class.create_start_second_stage_data_model()

            Requests().do_second_stage(
                host_of_request=get_hosts[1],
                access_token=create_start_second_stage_access_token,
                x_operation_id=create_start_second_stage_operation_id,
                pn_ocid=pn_ocid,
                pn_token=pn_token,
                tender_id=tp_id,
                test_mode=True,
                payload=start_second_stage_payload)

        time.sleep(10)
        actual_tp_release_before_submit_bid = requests.get(url=f"{pn_url}/{tp_id}").json()

        time_bot(expected_time=actual_tp_release_before_submit_bid['releases'][0]['tender']['enquiryPeriod']['endDate'])

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: SubmitBid process by first tenderer.'):
            """
            Tender platform authorization for SubmitBid process by first tenderer.
            As result get Tender platform's access token and process operation-id.
            """
            submit_bid_access_token_for_first_invitation = authorization.get_access_token_for_platform_one()
            submit_bid_operation_id_for_first_invitation = \
                authorization.get_x_operation_id(create_start_second_stage_access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send request to create SubmitBid process by first tenderer.'):
            """
            Send api request on BPE host for SubmitBid process by first tenderer.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            submit_bid_payload_class = copy.deepcopy(BidPreparePayload(host_for_services=get_hosts[2]))
            submit_bid_payload_for_first_invitation = submit_bid_payload_class.create_bid_obligatory_data_model(
                based_stage_release=actual_tp_release_before_submit_bid,
                submission_payload=create_submission_moldova_payload
            )

            Requests().submit_bid(
                host_of_request=get_hosts[1],
                access_token=submit_bid_access_token_for_first_invitation,
                x_operation_id=submit_bid_operation_id_for_first_invitation,
                pn_ocid=pn_ocid,
                tender_id=tp_id,
                test_mode=True,
                payload=submit_bid_payload_for_first_invitation
            )

            time.sleep(5)
            kafka_message_class = MessageForPlatform(submit_bid_operation_id_for_first_invitation)
            submit_bid_feed_point_message_by_first_tenderer = kafka_message_class.get_message_from_kafka_topic()

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: SubmitBid process by second tenderer.'):
            """
            Tender platform authorization for SubmitBid process by second tenderer.
            As result get Tender platform's access token and process operation-id.
            """
            submit_bid_access_token_for_second_invitation = authorization.get_access_token_for_platform_one()
            submit_bid_operation_id_for_second_invitation = \
                authorization.get_x_operation_id(create_start_second_stage_access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send request to create SubmitBid process by second tenderer.'):
            """
            Send api request on BPE host for SubmitBid process by second tenderer.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            submit_bid_payload_for_second_invitation = submit_bid_payload_class.create_bid_obligatory_data_model(
                based_stage_release=actual_tp_release_before_submit_bid,
                submission_payload=create_submission_belarus_payload
            )

            Requests().submit_bid(
                host_of_request=get_hosts[1],
                access_token=submit_bid_access_token_for_second_invitation,
                x_operation_id=submit_bid_operation_id_for_second_invitation,
                pn_ocid=pn_ocid,
                tender_id=tp_id,
                test_mode=True,
                payload=submit_bid_payload_for_second_invitation
            )

            kafka_message_class = MessageForPlatform(submit_bid_operation_id_for_second_invitation)
            submit_bid_feed_point_message_by_second_tenderer = kafka_message_class.get_message_from_kafka_topic()

        actual_tp_release_before_tender_period_end_expired = requests.get(url=f"{pn_url}/{tp_id}").json()
        actual_ms_release_before_tender_period_end_expired = requests.get(url=f"{pn_url}/{pn_ocid}").json()

        time_bot(expected_time=actual_tp_release_before_tender_period_end_expired[
            'releases'][0]['tender']['tenderPeriod']['endDate']
                 )

        step_number += 1
        with allure.step(f'# {step_number}.  See results if tender period end was expired.'):
            """
            Check the results of TestCase.
            """

            with allure.step(f'# {step_number}.1. Check message in feed point.'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                kafka_message_class = MessageForPlatform(ocid=tp_id,
                                                         initiation="bpe")

                tender_period_end_feed_point_message = \
                    kafka_message_class.get_message_from_kafka_by_ocid_and_initiator()[1]

                allure.attach(str(tender_period_end_feed_point_message), 'Message in feed point.')

                asynchronous_result_of_tender_period_end_was_checked = \
                    kafka_message_class.tender_period_end_no_auction_message_is_successful(
                        environment=environment,
                        kafka_message=tender_period_end_feed_point_message,
                        pn_ocid=pn_ocid,
                        tender_id=tp_id
                    )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False,
                    then return process steps by operation-id.
                    """
                    if asynchronous_result_of_tender_period_end_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=tender_period_end_feed_point_message['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual asynchronous result of sending the request and '
                                 'expected asynchronous result of sending request.'):
                    allure.attach(str(asynchronous_result_of_tender_period_end_was_checked),
                                  "Actual asynchronous result of sending the request.")
                    allure.attach(str(True), "Expected asynchronous result of sending the request.")
                    assert asynchronous_result_of_tender_period_end_was_checked is True

            with allure.step(f'# {step_number}.2. Check TP release'):
                """
                Compare actual Tp release before TenderPeriodEnd expiring and
                actual Tp release after TenderPeriodEnd expiring.
                """
                allure.attach(str(json.dumps(actual_tp_release_before_tender_period_end_expired)),
                              "Actual TP release before TenderPeriodEnd expiring.")

                actual_tp_release_after_tender_period_end_expired = requests.get(url=f"{pn_url}/{tp_id}").json()
                allure.attach(str(json.dumps(actual_tp_release_after_tender_period_end_expired)),
                              "Actual TP release after TenderPeriodEnd expiring.")

                compare_releases = dict(
                    DeepDiff(actual_tp_release_before_tender_period_end_expired,
                             actual_tp_release_after_tender_period_end_expired))

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added":
                        "['releases'][0]['awards'], "
                        "['releases'][0]['bids'], "
                        "['releases'][0]['tender']['awardPeriod']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{tp_id}-"
                                f"{actual_tp_release_after_tender_period_end_expired['releases'][0]['id'][46:59]}",
                            "old_value":
                                f"{tp_id}-"
                                f"{actual_tp_release_before_tender_period_end_expired['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": tender_period_end_feed_point_message['data']['operationDate'],
                            "old_value": actual_tp_release_before_tender_period_end_expired['releases'][0]['date']
                        },
                        "root['releases'][0]['tag'][0]": {
                            "new_value": "award",
                            "old_value": "tender"
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "awarding",
                            "old_value": "tendering"
                        }
                    },
                    "iterable_item_added": {
                        "root['releases'][0]['parties'][0]['roles'][2]": "tenderer",
                        "root['releases'][0]['parties'][0]['roles'][3]": "supplier",
                        "root['releases'][0]['parties'][1]['roles'][2]": "tenderer",
                        "root['releases'][0]['parties'][1]['roles'][3]": "supplier",
                        "root['releases'][0]['parties'][2]['roles'][2]": "tenderer",
                        "root['releases'][0]['parties'][2]['roles'][3]": "supplier"
                    }
                }

                try:
                    """
                    Prepare expected award array
                    """
                    final_expected_awards_array = list()

                    list_of_awards_id_from_release = list()
                    for i in actual_tp_release_after_tender_period_end_expired['releases'][0]['awards']:
                        for i_1 in i:
                            if i_1 == "id":
                                list_of_awards_id_from_release.append(i['id'])
                    quantity_of_object_into_list_of_awards_id_from_release = \
                        len(list_of_awards_id_from_release)

                    list_of_awards_suppliers_from_release = list()
                    for i in actual_tp_release_after_tender_period_end_expired['releases'][0]['awards']:
                        for i_1 in i:
                            if i_1 == "suppliers":
                                list_of_awards_suppliers_from_release.append(i['suppliers'])

                    expected_awards_array_first = TenderPeriodExpectedChanges(
                        environment=environment,
                        language=language,
                        host_for_services=get_hosts[2]
                    ).prepare_array_of_awards_mapper(
                        bid_payload=submit_bid_payload_for_first_invitation,
                        actual_tp_release_after_tender_period_end=actual_tp_release_after_tender_period_end_expired,
                        tender_period_end_feed_point_message=tender_period_end_feed_point_message
                    )

                    expected_awards_array_second = TenderPeriodExpectedChanges(
                        environment=environment,
                        language=language,
                        host_for_services=get_hosts[2]
                    ).prepare_array_of_awards_mapper(
                        bid_payload=submit_bid_payload_for_second_invitation,
                        actual_tp_release_after_tender_period_end=actual_tp_release_after_tender_period_end_expired,
                        tender_period_end_feed_point_message=tender_period_end_feed_point_message
                    )

                    expected_awards_array = expected_awards_array_first + expected_awards_array_second

                    list_of_awards_suppliers_from_expected_awards_array = list()
                    for i in expected_awards_array:
                        for i_1 in i:
                            if i_1 == "suppliers":
                                list_of_awards_suppliers_from_expected_awards_array.append(i['suppliers'])
                    quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array = \
                        len(list_of_awards_suppliers_from_expected_awards_array)

                    if quantity_of_object_into_list_of_awards_id_from_release == \
                            quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array:
                        for q in range(quantity_of_object_into_list_of_awards_id_from_release):
                            for q_1 in range(
                                    quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array):
                                if expected_awards_array[q_1]['suppliers'] == \
                                        list_of_awards_suppliers_from_release[q]:
                                    final_expected_awards_array.append(expected_awards_array[q_1]['value'])
                    else:
                        raise Exception("Error: quantity_of_object_into_list_of_awards_id_from_release !="
                                        "quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array")
                    try:
                        """
                        Check id into award array and set permanent id for 'final_expected_awards_array'.
                        """
                        for award in range(quantity_of_object_into_list_of_awards_id_from_release):
                            try:
                                """
                                Check that actual_ev_release['releases'][0]['awards'][0]['id'] is uuid version 4
                                """
                                check_award_id = check_uuid_version(
                                    uuid_to_test=actual_tp_release_after_tender_period_end_expired[
                                        'releases'][0]['awards'][award]['id'],
                                    version=4
                                )
                                if check_award_id is True:
                                    final_expected_awards_array[award]['id'] = \
                                        actual_tp_release_after_tender_period_end_expired[
                                            'releases'][0]['awards'][award]['id']
                                else:
                                    raise Exception("actual_ev_release['releases'][0]['awards'][0]['id'] "
                                                    "must be uuid version 4")
                            except Exception:
                                raise Exception("Impossible to check that actual_ev_release['releases'][0]"
                                                "['awards'][0]['id'] is uuid version 4")
                    except Exception:
                        raise Exception("Impossible to check id into award array and set permanent id "
                                        "for 'final_expected_awards_array'.")
                    try:
                        """
                        Set 'statusDetails' for award, according with rule FReq-1.4.1.8.
                        """
                        if actual_tp_release_after_tender_period_end_expired['releases'][0]['tender'][
                            'awardCriteria'] == "ratedCriteria" or \
                                actual_tp_release_after_tender_period_end_expired['releases'][0]['tender'][
                                    'awardCriteria'] == "qualityOnly" or \
                                actual_tp_release_after_tender_period_end_expired['releases'][0]['tender'][
                                    'awardCriteria'] == "costOnly":
                            weight_values_list = list()

                            for award in range(quantity_of_object_into_list_of_awards_id_from_release):
                                weight_values_list.append(final_expected_awards_array[award]['weightedValue'][
                                                              'amount'])
                            min_weight_value = min(weight_values_list)
                            if final_expected_awards_array[award]['weightedValue']['amount'] == min_weight_value:
                                final_expected_awards_array[award]['statusDetails'] = "awaiting"
                            else:
                                final_expected_awards_array[award]['statusDetails'] = "empty"
                            awards_status_details_list = list()
                            try:
                                """
                                Check how many awards have statusDetails 'awaiting'.
                                """
                                for award in range(quantity_of_object_into_list_of_awards_id_from_release):
                                    if final_expected_awards_array[award]['statusDetails'] == "awaiting":
                                        awards_status_details_list.append(
                                            final_expected_awards_array[award]['relatedBid'])
                            except Exception:
                                raise Exception(
                                    "Impossible to check how many awards have statusDetails 'awaiting'.")
                            try:
                                """
                                Check 'statusDetails' into final_expected_awards_array.
                                """
                                if len(awards_status_details_list) > 1:
                                    for award in range(quantity_of_object_into_list_of_awards_id_from_release):
                                        if final_expected_awards_array[award]['relatedBid'] == \
                                                submit_bid_feed_point_message_by_first_tenderer['data']['outcomes'][
                                                    'bids'][0]['id']:
                                            final_expected_awards_array[award]['statusDetails'] = "awaiting"
                                        else:
                                            final_expected_awards_array[award]['statusDetails'] = "empty"
                            except Exception:
                                raise Exception("Impossible to check 'statusDetails' into "
                                                "final_expected_awards_array.")
                        else:
                            try:
                                """
                                Check 'statusDetails' into final_expected_awards_array.
                                """
                                for award in range(quantity_of_object_into_list_of_awards_id_from_release):
                                    if final_expected_awards_array[award]['relatedBid'] == \
                                            submit_bid_feed_point_message_by_first_tenderer['data']['outcomes'][
                                                'bids'][0]['id']:
                                        final_expected_awards_array[award]['statusDetails'] = "awaiting"
                                    else:
                                        final_expected_awards_array[award]['statusDetails'] = "empty"
                            except Exception:
                                raise Exception("Impossible to check 'statusDetails' into "
                                                "final_expected_awards_array.")
                    except Exception:
                        raise Exception("Impossible to set 'statusDetails' for award, "
                                        "according with rule FReq-1.4.1.8.")
                except Exception:
                    raise Exception("Impossible to prepare expected awards array")

                try:
                    """
                    Prepare expected bid object
                    """
                    final_expected_bids_object = {"details": []}
                    expected_bids_array = list()

                    expected_bids_object_first = TenderPeriodExpectedChanges(
                        environment=environment,
                        language=language,
                        host_for_services=get_hosts[2]
                    ).prepare_bid_details_mapper(
                        bid_payload=submit_bid_payload_for_first_invitation,
                        bid_feed_point_message=submit_bid_feed_point_message_by_first_tenderer,
                        actual_tp_release_after_tender_period_end=actual_tp_release_after_tender_period_end_expired,
                        tender_period_end_feed_point_message=tender_period_end_feed_point_message
                    )
                    expected_bids_array.append(expected_bids_object_first)

                    expected_bids_object_second = TenderPeriodExpectedChanges(
                        environment=environment,
                        language=language,
                        host_for_services=get_hosts[2]
                    ).prepare_bid_details_mapper(
                        bid_payload=submit_bid_payload_for_second_invitation,
                        bid_feed_point_message=submit_bid_feed_point_message_by_second_tenderer,
                        actual_tp_release_after_tender_period_end=actual_tp_release_after_tender_period_end_expired,
                        tender_period_end_feed_point_message=tender_period_end_feed_point_message
                    )
                    expected_bids_array.append(expected_bids_object_second)
                    try:
                        """
                        Check how many quantity of object into expected_bids_array.
                        """
                        list_of_expected_bids_array_tenderers = list()
                        for i in expected_bids_array:
                            for i_1 in i:
                                if i_1 == "tenderers":
                                    list_of_expected_bids_array_tenderers.append(i_1)
                        quantity_of_list_of_expected_bids_array_tenderers = len(list_of_expected_bids_array_tenderers)
                    except Exception:
                        raise Exception("Impossible to check how many quantity of object into expected_bids_array.")
                    try:
                        """
                        Check how many quantity of object into
                        GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]'bids']['details'].
                        """
                        list_of_releases_bids_details_tenderers = list()
                        for i in \
                                actual_tp_release_after_tender_period_end_expired['releases'][0]['bids']['details']:
                            for i_1 in i:
                                if i_1 == "tenderers":
                                    list_of_releases_bids_details_tenderers.append(i['tenderers'])
                        quantity_of_list_of_releases_bids_details_tenderers = \
                            len(list_of_releases_bids_details_tenderers)
                    except Exception:
                        raise Exception("Impossible to calculate how many quantity of object into "
                                        "expected_bids_array['details']['tenderers']")
                    if quantity_of_list_of_expected_bids_array_tenderers == \
                            quantity_of_list_of_releases_bids_details_tenderers:
                        for q in range(quantity_of_list_of_releases_bids_details_tenderers):
                            for q_1 in range(quantity_of_list_of_expected_bids_array_tenderers):
                                if expected_bids_array[q_1]['tenderers'] == \
                                        list_of_releases_bids_details_tenderers[q]:
                                    final_expected_bids_object['details'].append(
                                        expected_bids_array[q_1]['value'])
                    else:
                        raise Exception("Error: quantity_of_details_id_into_expected_bids !="
                                        "quantity_of_details_id_into_releases_bids")
                    try:
                        """
                        Set permanent id for 'details' into expected_bids_array['details'].
                        """
                        for d in range(quantity_of_list_of_expected_bids_array_tenderers):
                            final_expected_bids_object['details'][d]['id'] = \
                                actual_tp_release_after_tender_period_end_expired['releases'][0]['bids'][
                                    'details'][d]['id']
                    except Exception:
                        raise Exception("Impossible to set permanent id for 'details', "
                                        "'evidences', 'requirementResponses' into expected_bids_array['details'].")
                except Exception:
                    raise Exception("Impossible to prepare expected bids object")

                try:
                    """
                    Prepare expected awardPeriod object.
                    """
                    final_expected_award_period_object = {
                        "startDate": actual_tp_release_after_tender_period_end_expired['releases'][0]['tender'][
                            'tenderPeriod']['endDate']
                    }
                except Exception:
                    raise Exception("Prepare expected awardPeriod object.")

                try:
                    """
                        If compare_releases !=expected_result,
                        then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=tender_period_end_feed_point_message['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step(
                        'Check a difference of comparing Tp release before '
                        'TenderPeriodEnd expiring and Tp release after TenderPeriodEnd expiring.'):
                    allure.attach(json.dumps(compare_releases),
                                  "Actual result of comparing Tp releases.")
                    allure.attach(json.dumps(expected_result),
                                  "Expected result of comparing Tp releases.")
                    assert compare_releases == expected_result

                with allure.step(
                        'Check a difference of comparing actual awards array and '
                        'expected awards array.'):
                    allure.attach(json.dumps(actual_tp_release_after_tender_period_end_expired[
                                                 'releases'][0]['awards']), "Actual awards array.")
                    allure.attach(json.dumps(final_expected_awards_array),
                                  "Expected awards array")
                    assert actual_tp_release_after_tender_period_end_expired[
                                                 'releases'][0]['awards'] == final_expected_awards_array

                with allure.step(
                        'Check a difference of comparing actual bids object and '
                        'expected bids object.'):
                    allure.attach(json.dumps(actual_tp_release_after_tender_period_end_expired[
                                                 'releases'][0]['bids']), "Actual bids object.")
                    allure.attach(json.dumps(final_expected_bids_object),
                                  "Expected bids object")
                    assert actual_tp_release_after_tender_period_end_expired[
                                                 'releases'][0]['bids'] == final_expected_bids_object

                with allure.step(
                        'Check a difference of comparing actual awardPeriod object and '
                        'expected awardPeriod object.'):
                    allure.attach(json.dumps(actual_tp_release_after_tender_period_end_expired[
                                                 'releases'][0]['tender']['awardPeriod']), "Actual awardPeriod object.")
                    allure.attach(json.dumps(final_expected_award_period_object),
                                  "Expected awardPeriod object")
                    assert actual_tp_release_after_tender_period_end_expired[
                               'releases'][0]['tender']['awardPeriod'] == final_expected_award_period_object

            with allure.step(f'# {step_number}.3. Check MS release'):
                """
                Compare actual Tp release before TenderPeriodEnd expiring and
                actual Tp release after TenderPeriodEnd expiring.
                """
                allure.attach(json.dumps(actual_ms_release_before_tender_period_end_expired),
                              "Actual MS release before TenderPeriodEnd expiring")

                actual_ms_release_after_tender_period_end_expired = requests.get(url=f"{pn_url}/{pn_ocid}").json()
                allure.attach(json.dumps(actual_ms_release_after_tender_period_end_expired),
                              "Actual MS release after TenderPeriodEnd expiring")

                compare_releases = dict(
                    DeepDiff(actual_ms_release_before_tender_period_end_expired,
                             actual_ms_release_after_tender_period_end_expired))

                expected_result = {}

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:

                        connection_to_database.ei_process_cleanup_table_of_services(ei_id=ei_ocid)

                        connection_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)

                        connection_to_database.pn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connection_to_database.cnonpn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connection_to_database.submission_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connection_to_database.qualification_declaration_process_cleanup_table_of_services(
                            pn_ocid=pn_ocid)

                        connection_to_database.qualification_consideration_process_cleanup_table_of_services(
                            pn_ocid=pn_ocid)

                        connection_to_database.qualification_protocol_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connection_to_database.qualification_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connection_to_database.cleanup_steps_of_process(operation_id=create_ei_operation_id)

                        connection_to_database.cleanup_steps_of_process(operation_id=create_fs_operation_id)

                        connection_to_database.cleanup_steps_of_process(operation_id=create_pn_operation_id)

                        connection_to_database.cleanup_steps_of_process(operation_id=create_cn_operation_id)

                        connection_to_database.cleanup_steps_of_process_from_orchestrator(
                            pn_ocid=pn_ocid)

                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=tender_period_end_feed_point_message['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Ms release before '
                                 'TenderPeriodEnd expiring and Ms release after TenderPeriodEnd expiring.'):
                    allure.attach(json.dumps(compare_releases),
                                  "Actual result of comparing MS releases.")
                    allure.attach(json.dumps(expected_result),
                                  "Expected result of comparing Ms releases.")
                    assert compare_releases == expected_result
