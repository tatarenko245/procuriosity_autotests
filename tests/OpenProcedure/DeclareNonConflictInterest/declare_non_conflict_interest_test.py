import copy
import datetime
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn, GlobalClassCreateFirstBid, GlobalClassTenderPeriodEndAuction, \
    GlobalClassCreateDeclareNonConflict, GlobalClassCreateSecondBid, GlobalClassUpdateDeclareNonConflict
from tests.utils.PayloadModel.OpenProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.OpenProcedure.DeclareNonConflictInterest.declare_non_conflict_interest_prepared_payload import \
    DeclarePreparePayload
from tests.utils.PayloadModel.Budget.Ei.expenditure_item_payload import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModel.OpenProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.PayloadModel.OpenProcedure.SubmitBid.bid_prepared_payload import BidPreparePayload
from tests.utils.ReleaseModel.OpenProcedure.DeclareNonConflictInterest.declare_non_conflict_prepared_release import \
    DeclareExpectedRelease
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions_collection import get_project_root, time_bot, get_id_token_of_award_in_pending_awaiting_state
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Awarding')
@allure.suite('Declare non conflict interest')
@allure.sub_suite('BPE: ')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1Q9MdmSbP88PQ18Jx28qXT_'
                     'akIPQ1uoUgnBg3fg8Ry8A/edit#gid=1095206362',
                 name='Google sheets: Declare non conflict interest.')
class TestDeclareNonConflictInterest:
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
            GlobalClassMetadata.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"

        elif parse_environment == "sandbox":
            GlobalClassMetadata.metadata_document_url = "http://storage.eprocurement.systems/get"

    @allure.title("Проверить подачу декларации персоной PE, которая существует в БД без изменений (полная модель)\n"
                  "------------------------------------------------\n"
                  "Ei: full data model with items array;\n"
                  "Fs: full data model, own money;\n"
                  "Pn: full data model, 1 lots, 1 items;\n"
                  "CnOnPn: full data model with auction, 1 lots, 1 items, criteria, conversions;\n"
                  "First Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "QualificationDeclaration non conflict interest: full data model with old person.\n"
                  )
    def test_check_result_of_sending_the_request_one(self):
        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Ei'):
            """
            Send api request to BPE host for expenditure item creation.
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
                payload=GlobalClassCreateEi.payload,
                test_mode=True
            )
            GlobalClassCreateEi.feed_point_message = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()

            GlobalClassCreateEi.ei_ocid = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

            GlobalClassCreateEi.actual_ei_release = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Fs'):
            """
            Send api request to BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload = copy.deepcopy(FinancialSourcePayload(ei_payload=GlobalClassCreateEi.payload))
            GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
            Requests().createFs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Pn'):
            """
            Send api request to BPE host for planning notice creating.
            Save asynchronous result of sending the request.
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=1,
                    quantity_of_item_object=1)

            Requests().createPn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreatePn.access_token,
                x_operation_id=GlobalClassCreatePn.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                pmd=GlobalClassMetadata.pmd,
                payload=GlobalClassCreatePn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create CnOnPn'):
            """
            Send api request to BPE host for contract notice creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=1,
                    quantity_of_items_object=1,
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
                payload=GlobalClassCreateCnOnPn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create first Bid'):
            """
            Tender platform authorization for create first bid.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create first Bid'):
            """
            Send api request to BPE host for first bid creating.
            Save asynchronous result of sending the request.
            """
            try:
                """
                Set specific value into submission.rules for this testcase.
                """
                min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_submission_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_one -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into submission.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into submission.rules")
            try:
                """
                Set specific value into evaluation.rules for this testcase.
                """
                min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_evaluation_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_one -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into evaluation.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into evaluation.rules")

            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateFirstBid.payload = \
                bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)

            Requests().submit_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFirstBid.access_token,
                x_operation_id=GlobalClassCreateFirstBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateFirstBid.payload,
                test_mode=True
            )
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])

            GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()
            GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()
            while "awardPeriod" not in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']:
                GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()
            time_bot(
                expected_time=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0][
                    'tender']['awardPeriod']['startDate'])

            GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassTenderPeriodEndAuction.feed_point_message = \
                KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                             initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()

            GlobalClassCreateDeclareNonConflict.award_id = \
                GlobalClassTenderPeriodEndAuction.feed_point_message[0]['data']['outcomes']['awards'][0]['id']
            GlobalClassCreateDeclareNonConflict.award_token = \
                GlobalClassTenderPeriodEndAuction.feed_point_message[0]['data']['outcomes']['awards'][0][
                    'X-TOKEN']
        step_number += 1
        requirements_list = list()
        for c in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']['criteria']:
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
        tenderers_list = list()
        for aw in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
            if aw['status'] == "pending":
                if aw['statusDetails'] == "awaiting":
                    for s in aw['suppliers']:
                        for s_1 in s:
                            if s_1 == "id":
                                tenderers_list.append(s['id'])

        for x in range(len(requirements_list)):
            for y in range(len(tenderers_list)):
                x_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                y_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                with allure.step(f'# {step_number}.Authorization platform one: create declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Tender platform authorization for create declare non conflict interest.
                    As result get Tender platform's access token and process operation-id.
                    """
                    GlobalClassCreateDeclareNonConflict.access_token = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

                    GlobalClassCreateDeclareNonConflict.operation_id = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                        GlobalClassCreateDeclareNonConflict.access_token)
                    step_number += 1
                with allure.step(f'# {step_number}. Send request: create declaration non conflict interest '
                                 f'with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Send api request to BPE host for declare non conflict interest creating.
                    Save asynchronous result of sending the request.
                    """
                    time.sleep(1)
                    declare_payload_class = copy.deepcopy(DeclarePreparePayload())
                    GlobalClassCreateDeclareNonConflict.payload = \
                        declare_payload_class.create_declare_old_person_full_data_model(
                            requirement_id=requirements_list[x],
                            tenderer_id=tenderers_list[y],
                            actual_ms_release=GlobalClassTenderPeriodEndAuction.actual_ms_release)

                    Requests().create_declare_non_conflict_interest(
                        host_of_request=GlobalClassMetadata.host_for_bpe,
                        access_token=GlobalClassCreateDeclareNonConflict.access_token,
                        x_operation_id=GlobalClassCreateDeclareNonConflict.operation_id,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        tender_id=GlobalClassCreateCnOnPn.ev_id,
                        payload=GlobalClassCreateDeclareNonConflict.payload,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        award_token=GlobalClassCreateDeclareNonConflict.award_token,
                        test_mode=True
                    )
                    GlobalClassCreateDeclareNonConflict.feed_point_message = \
                        KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                    step_number += 1

                with allure.step(f'# {step_number}. See result: create declaration declaration with'
                                 f'{y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Check the results of test case running.
                    """
                    with allure.step(f'# {step_number}.1. Check message in feed point.'):
                        """
                        Check the asynchronous_result_of_sending_the_request.
                        """
                        time.sleep(1)
                        GlobalClassCreateDeclareNonConflict.feed_point_message = \
                            KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                        allure.attach(str(GlobalClassCreateDeclareNonConflict.feed_point_message),
                                      'Message in feed point')

                        asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                            GlobalClassCreateDeclareNonConflict.operation_id).declare_non_confl_message_is_successful(
                            environment=GlobalClassMetadata.environment,
                            kafka_message=GlobalClassCreateDeclareNonConflict.feed_point_message,
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
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                          f"Step: # {step_number}.1. Check message in feed point.\n" \
                                          f"Message: Could not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Could not return BPE operation step")
                        with allure.step('Compare actual message from feed point and expected pattern'):
                            allure.attach(str(json.dumps(asynchronous_result_of_sending_the_request_was_checked)),
                                          "Actual result of comparing the message from feed point.")
                            allure.attach(str(True), "Expected result of comparing the message from feed point.")
                            assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)
                        step_number += 1

                    with allure.step(f'# {step_number}.2. Check EV release.'):
                        """
                        Compare actual evaluation value release with expected evaluation value release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
                                      "Actual EV release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ev_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreateCnOnPn.ev_id}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ev_release)),
                                      "Actual EV release after declaration creation.")

                        compare_releases = dict(DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ev_release,
                            GlobalClassCreateDeclareNonConflict.actual_ev_release))
                        dictionary_item_added_was_cleaned = \
                            str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                        compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                        compare_releases = dict(compare_releases)

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        expected_result = {
                            "dictionary_item_added": "['releases'][0]['awards'][0]['requirementResponses']",
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                            'operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['date']
                                }
                            }
                        }

                        actual_awards_array = GlobalClassCreateDeclareNonConflict.actual_ev_release['releases'][0][
                            'awards']
                        try:
                            """
                            Prepare actual awards.requirementResponses array.
                            """
                            actual_awards_requirement_responses_array = list()
                            for a in actual_awards_array:
                                if a['status'] == "pending":
                                    if a['statusDetails'] == "awaiting":
                                        for a_1 in a:
                                            if a_1 == "requirementResponses":
                                                for a_2 in a['requirementResponses']:
                                                    if a_2['requirement']['id'] == \
                                                            GlobalClassCreateDeclareNonConflict.payload[
                                                                'requirementResponse']['requirement']['id']:
                                                        if a_2['relatedTenderer']['id'] == \
                                                                GlobalClassCreateDeclareNonConflict.payload[
                                                                    'requirementResponse'][
                                                                    'relatedTenderer']['id']:
                                                            actual_awards_requirement_responses_array.append(a_2)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare actual awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare actual awards.requirementResponses.")

                        try:
                            """
                            Prepare expected awards.requirementResponses array.
                            """
                            expected_requirement_response_array = list()
                            expected_requirement_response_object = DeclareExpectedRelease(
                                environment=GlobalClassMetadata.environment,
                                language=GlobalClassMetadata.language
                            ).awards_requirement_responses_array(
                                actual_awards_array=actual_awards_array,
                                declare_payload=GlobalClassCreateDeclareNonConflict.payload)
                            expected_requirement_response_array.append(expected_requirement_response_object)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare expected awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare expected awards.requirementResponses.")

                        try:
                            """
                                If compare_releases !=expected_result, then return process steps by operation-id.
                                """
                            if compare_releases == expected_result and \
                                    expected_requirement_response_array == actual_awards_requirement_responses_array:
                                pass
                            else:
                                with allure.step('# Steps from Casandra DataBase'):
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TTestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Can not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Can not return BPE operation step.")

                        with allure.step('Compare actual EV release and expected EV release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases

                        with allure.step('Compare actual requirementResponse and '
                                         'expected requirementResponse into awards array'):
                            allure.attach(str(json.dumps(actual_awards_requirement_responses_array)),
                                          "Actual requirementResponse")
                            allure.attach(str(json.dumps(expected_requirement_response_array)),
                                          "Expected requirementResponse")
                            assert actual_awards_requirement_responses_array == \
                                   expected_requirement_response_array

                    with allure.step(f'# {step_number}.3. Check MS release.'):
                        """
                        Compare multistage release with expected multistage release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
                                      "Actual MS release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ms_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreatePn.pn_ocid}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ms_release)),
                                      "Actual MS release after declaration creation.")

                        compare_releases = DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ms_release,
                            GlobalClassCreateDeclareNonConflict.actual_ms_release)

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ms_release[
                                                       'releases'][0]['id'][29:42]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ms_release[
                                                       'releases'][0]['id'][29:42]

                        expected_result = {
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreatePn.pn_ocid}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreatePn.pn_ocid}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassCreateDeclareNonConflict.feed_point_message['data']['operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['date']
                                }
                            }
                        }
                        with allure.step('Compare actual MS release and expected MS release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases

        try:
            """
            Rollback specific value into submission.rules
            """
            GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                value=min_bids_from_submission_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_one -> \n" \
                          f"Step: Rollback specific value into submission.rules.\n" \
                          f"Message: Impossible to rollback specific value into submission.rules.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into submission.rules.")
        try:
            """
            Rollback specific value into evaluation.rules
            """
            GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                value=min_bids_from_evaluation_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_one -> \n" \
                          f"Step: Rollback specific value into evaluation.rules.\n" \
                          f"Message: Impossible to rollback specific value into evaluation.rules\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into evaluation.rules")

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

                GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.declaration_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id)

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

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[0][
                        'X-OPERATION-ID'])

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassCreateDeclareNonConflict.feed_point_message[
                        'X-OPERATION-ID'])
            else:
                with allure.step('# Steps from Casandra DataBase'):
                    database = GlobalClassMetadata.database
                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                    allure.attach(steps, "Cassandra DataBase: steps of process")
        except ValueError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_one -> \n" \
                          f"Step:Clean up database.\n" \
                          f"Message: Impossible to cLean up the database.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise ValueError("Can not return BPE operation step.")

    @allure.title("Проверить подачу декларации новой персоной PE\n"
                  "------------------------------------------------\n"
                  "Ei: full data model with items array;\n"
                  "Fs: full data model, own money;\n"
                  "Pn: full data model, 1 lots, 1 items;\n"
                  "CnOnPn: full data model with auction, 1 lots, 1 items, criteria, conversions;\n"
                  "First Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "Second Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "QualificationDeclaration non conflict interest: full data model with old person.\n"
                  )
    def test_check_result_of_sending_the_request_two(self):
        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Ei'):
            """
            Send api request to BPE host for expenditure item creation.
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
                payload=GlobalClassCreateEi.payload,
                test_mode=True
            )
            GlobalClassCreateEi.feed_point_message = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()

            GlobalClassCreateEi.ei_ocid = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

            GlobalClassCreateEi.actual_ei_release = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Fs'):
            """
            Send api request to BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload = copy.deepcopy(FinancialSourcePayload(ei_payload=GlobalClassCreateEi.payload))
            GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
            Requests().createFs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Pn'):
            """
            Send api request to BPE host for planning notice creating.
            Save asynchronous result of sending the request.
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=1,
                    quantity_of_item_object=1)

            Requests().createPn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreatePn.access_token,
                x_operation_id=GlobalClassCreatePn.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                pmd=GlobalClassMetadata.pmd,
                payload=GlobalClassCreatePn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create CnOnPn'):
            """
            Send api request to BPE host for contract notice creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=1,
                    quantity_of_items_object=1,
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
                payload=GlobalClassCreateCnOnPn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create first Bid'):
            """
            Tender platform authorization for create first bid.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create first Bid'):
            """
            Send api request to BPE host for first bid creating.
            Save asynchronous result of sending the request.
            """
            try:
                """
                Set specific value into submission.rules for this testcase.
                """
                min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_submission_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_two -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into submission.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into submission.rules")
            try:
                """
                Set specific value into evaluation.rules for this testcase.
                """
                min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_evaluation_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_two -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into evaluation.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into evaluation.rules")

            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateFirstBid.payload = \
                bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)

            Requests().submit_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFirstBid.access_token,
                x_operation_id=GlobalClassCreateFirstBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateFirstBid.payload,
                test_mode=True
            )
        with allure.step(f'# {step_number}. Authorization platform one: create second Bid'):
            """
            Tender platform authorization for create second bid.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateSecondBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateSecondBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateSecondBid.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create second Bid'):
            """
            Send api request to BPE host for second bid creating.
            Save asynchronous result of sending the request.
            """
            try:
                """
                Set specific value into submission.rules for this testcase.
                """
                min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_submission_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_two -> \n" \
                              f"Step: # {step_number}. Send request for create second Bid.\n" \
                              f"Message: Impossible to set specific value into submission.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into submission.rules")
            try:
                """
                Set specific value into evaluation.rules for this testcase.
                """
                min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_evaluation_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_two -> \n" \
                              f"Step: # {step_number}. Send request for create second Bid.\n" \
                              f"Message: Impossible to set specific value into evaluation.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into evaluation.rules")

            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateSecondBid.payload = \
                bid_payload_class.create_second_bid_full_data_model_with_requirement_responses(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)

            Requests().submit_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateSecondBid.access_token,
                x_operation_id=GlobalClassCreateSecondBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateSecondBid.payload,
                test_mode=True
            )

            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])

            GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()
            while "awardPeriod" not in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']:
                GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()
            time_bot(
                expected_time=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0][
                    'tender']['awardPeriod']['startDate'])
            time.sleep(2)
            GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassTenderPeriodEndAuction.feed_point_message = \
                KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                             initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()

            GlobalClassCreateDeclareNonConflict.award_id = get_id_token_of_award_in_pending_awaiting_state(
                actual_awards_array=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'],
                feed_point_message=GlobalClassTenderPeriodEndAuction.feed_point_message[1])[0]

            GlobalClassCreateDeclareNonConflict.award_token = get_id_token_of_award_in_pending_awaiting_state(
                actual_awards_array=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'],
                feed_point_message=GlobalClassTenderPeriodEndAuction.feed_point_message[1])[1]

        step_number += 1
        requirements_list = list()
        for c in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']['criteria']:
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
        tenderers_list = list()
        for aw in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
            if aw['status'] == "pending":
                if aw['statusDetails'] == "awaiting":
                    for s in aw['suppliers']:
                        for s_1 in s:
                            if s_1 == "id":
                                tenderers_list.append(s['id'])
        n = 1
        for x in range(len(requirements_list)):
            for y in range(len(tenderers_list)):
                x_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                y_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                with allure.step(f'# {step_number}.Authorization platform one: create declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Tender platform authorization for create declare non conflict interest.
                    As result get Tender platform's access token and process operation-id.
                    """
                    GlobalClassCreateDeclareNonConflict.access_token = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

                    GlobalClassCreateDeclareNonConflict.operation_id = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                        GlobalClassCreateDeclareNonConflict.access_token)
                    step_number += 1
                with allure.step(f'# {step_number}. Send request: create declaration non conflict interest '
                                 f'with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Send api request to BPE host for declare non conflict interest creating.
                    Save asynchronous result of sending the request.
                    """
                    time.sleep(1)
                    declare_payload_class = copy.deepcopy(DeclarePreparePayload())
                    GlobalClassCreateDeclareNonConflict.payload = \
                        declare_payload_class.create_declare_new_person_full_data_model(
                            requirement_id=requirements_list[x],
                            tenderer_id=tenderers_list[y],
                            number_of_iteration=step_number)

                    Requests().create_declare_non_conflict_interest(
                        host_of_request=GlobalClassMetadata.host_for_bpe,
                        access_token=GlobalClassCreateDeclareNonConflict.access_token,
                        x_operation_id=GlobalClassCreateDeclareNonConflict.operation_id,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        tender_id=GlobalClassCreateCnOnPn.ev_id,
                        payload=GlobalClassCreateDeclareNonConflict.payload,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        award_token=GlobalClassCreateDeclareNonConflict.award_token,
                        test_mode=True
                    )
                    GlobalClassCreateDeclareNonConflict.feed_point_message = \
                        KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                    step_number += 1

                with allure.step(f'# {step_number}. See result: create declaration declaration with '
                                 f'{y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Check the results of test case running.
                    """
                    with allure.step(f'# {step_number}.1. Check message in feed point.'):
                        """
                        Check the asynchronous_result_of_sending_the_request.
                        """
                        time.sleep(1)
                        GlobalClassCreateDeclareNonConflict.feed_point_message = \
                            KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                        allure.attach(str(GlobalClassCreateDeclareNonConflict.feed_point_message),
                                      'Message in feed point')

                        asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                            GlobalClassCreateDeclareNonConflict.operation_id).declare_non_confl_message_is_successful(
                            environment=GlobalClassMetadata.environment,
                            kafka_message=GlobalClassCreateDeclareNonConflict.feed_point_message,
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
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_two -> \n" \
                                          f"Step: # {step_number}.1. Check message in feed point.\n" \
                                          f"Message: Could not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Could not return BPE operation step")
                        with allure.step('Compare actual message from feed point and expected pattern'):
                            allure.attach(str(json.dumps(asynchronous_result_of_sending_the_request_was_checked)),
                                          "Actual result of comparing the message from feed point.")
                            allure.attach(str(True), "Expected result of comparing the message from feed point.")
                            assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)
                        step_number += 1

                    with allure.step(f'# {step_number}.1. Check EV release.'):
                        """
                        Compare actual evaluation value release with expected evaluation value release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
                                      "Actual EV release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ev_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreateCnOnPn.ev_id}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ev_release)),
                                      "Actual EV release after declaration creation.")

                        compare_releases = DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ev_release,
                            GlobalClassCreateDeclareNonConflict.actual_ev_release)

                        dictionary_item_added_was_cleaned = \
                            str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                        compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                        compare_releases = dict(compare_releases)

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        expected_result = {
                            "dictionary_item_added": "['releases'][0]['awards'][0]['requirementResponses']",
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                            'operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['date']
                                }
                            }
                        }

                        actual_awards_array = GlobalClassCreateDeclareNonConflict.actual_ev_release['releases'][0][
                            'awards']
                        try:
                            """
                            Prepare actual awards.requirementResponses array.
                            """
                            actual_awards_requirement_responses_array = list()
                            for a in actual_awards_array:
                                if a['status'] == "pending":
                                    if a['statusDetails'] == "awaiting":
                                        for a_1 in a:
                                            if a_1 == "requirementResponses":
                                                for a_2 in a['requirementResponses']:
                                                    if a_2['requirement']['id'] == \
                                                            GlobalClassCreateDeclareNonConflict.payload[
                                                                'requirementResponse']['requirement']['id']:
                                                        if a_2['relatedTenderer']['id'] == \
                                                                GlobalClassCreateDeclareNonConflict.payload[
                                                                    'requirementResponse'][
                                                                    'relatedTenderer']['id']:
                                                            actual_awards_requirement_responses_array.append(a_2)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_two -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare actual awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare actual awards.requirementResponses.")

                        try:
                            """
                            Prepare expected awards.requirementResponses array.
                            """
                            expected_requirement_response_array = list()
                            expected_requirement_response_object = DeclareExpectedRelease(
                                environment=GlobalClassMetadata.environment,
                                language=GlobalClassMetadata.language
                            ).awards_requirement_responses_array(
                                actual_awards_array=actual_awards_array,
                                declare_payload=GlobalClassCreateDeclareNonConflict.payload)
                            expected_requirement_response_array.append(expected_requirement_response_object)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_two -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare expected awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare expected awards.requirementResponses.")

                        try:
                            """
                                If compare_releases !=expected_result, then return process steps by operation-id.
                                """
                            if compare_releases == expected_result and \
                                    expected_requirement_response_array == actual_awards_requirement_responses_array:
                                pass
                            else:
                                with allure.step('# Steps from Casandra DataBase'):
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TTestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_two -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Can not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Can not return BPE operation step.")

                        with allure.step('Compare actual EV release and expected EV release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases

                        with allure.step('Compare actual requirementResponse and '
                                         'expected requirementResponse into awards array'):
                            allure.attach(str(json.dumps(actual_awards_requirement_responses_array)),
                                          "Actual requirementResponse")
                            allure.attach(str(json.dumps(expected_requirement_response_array)),
                                          "Expected requirementResponse")
                            assert actual_awards_requirement_responses_array == \
                                   expected_requirement_response_array

                    with allure.step(f'# {step_number}.3. Check MS release.'):
                        """
                        Compare multistage release with expected multistage release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
                                      "Actual MS release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ms_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreatePn.pn_ocid}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ms_release)),
                                      "Actual MS release after declaration creation.")

                        compare_releases = dict(DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ms_release,
                            GlobalClassCreateDeclareNonConflict.actual_ms_release))

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ms_release[
                                                       'releases'][0]['id'][29:42]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ms_release[
                                                       'releases'][0]['id'][29:42]

                        new_responder_identifier_from_payload = GlobalClassCreateDeclareNonConflict.payload[
                            'requirementResponse']['responder']['identifier']

                        new_responder_documents_from_payload = GlobalClassCreateDeclareNonConflict.payload[
                            'requirementResponse']['responder']['businessFunctions'][0]['documents']

                        iterable_item_added_object = {
                            f"root['releases'][0]['parties'][3]['persones'][{n}]": {
                                'id': f"{new_responder_identifier_from_payload['scheme']}-"
                                      f"{new_responder_identifier_from_payload['id']}",
                                'title': GlobalClassCreateDeclareNonConflict.payload[
                                    'requirementResponse']['responder']['title'],
                                'name': GlobalClassCreateDeclareNonConflict.payload[
                                    'requirementResponse']['responder']['name'],
                                'identifier': {
                                    'scheme': new_responder_identifier_from_payload['scheme'],
                                    'id': new_responder_identifier_from_payload['id'],
                                    'uri': new_responder_identifier_from_payload['uri']
                                },
                                'businessFunctions': [{
                                    'id': GlobalClassCreateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['businessFunctions'][0]['id'],
                                    'type': GlobalClassCreateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['businessFunctions'][0]['type'],
                                    'jobTitle': GlobalClassCreateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['businessFunctions'][0]['jobTitle'],
                                    'period': {
                                        'startDate': GlobalClassCreateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0][
                                            'period']['startDate']
                                    },
                                    'documents': [{
                                        'id': new_responder_documents_from_payload[0]['id'],
                                        'documentType': new_responder_documents_from_payload[0]['documentType'],
                                        'title': new_responder_documents_from_payload[0]['title'],
                                        'description': new_responder_documents_from_payload[0]['description'],
                                        'url': f"{GlobalClassMetadata.metadata_document_url}/"
                                               f"{new_responder_documents_from_payload[0]['id']}",
                                        'datePublished': GlobalClassCreateDeclareNonConflict.feed_point_message[
                                            'data']['operationDate']
                                    }]
                                }]
                            }
                        }

                        if n != 1:
                            iterable_item_added_object.update(
                                GlobalClassCreateDeclareNonConflict.previous_value_of_iterable_item_object)

                        expected_result = {
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreatePn.pn_ocid}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreatePn.pn_ocid}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                            'operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['date']
                                }
                            },
                            'iterable_item_added': iterable_item_added_object
                        }

                        GlobalClassCreateDeclareNonConflict.previous_value_of_iterable_item_object = \
                            copy.deepcopy(expected_result['iterable_item_added'])

                        n += 1

                        with allure.step('Compare actual MS release and expected MS release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases
        try:
            """
            Rollback specific value into submission.rules
            """
            GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                value=min_bids_from_submission_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_two -> \n" \
                          f"Step: Rollback specific value into submission.rules.\n" \
                          f"Message: Impossible to rollback specific value into submission.rules.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into submission.rules.")
        try:
            """
             Rollback specific value into evaluation.rules
             """
            GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                value=min_bids_from_evaluation_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_two -> \n" \
                          f"Step: Rollback specific value into evaluation.rules.\n" \
                          f"Message: Impossible to rollback specific value into evaluation.rules\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into evaluation.rules")
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

                GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.declaration_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id)

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

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[1][
                        'X-OPERATION-ID'])

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassCreateDeclareNonConflict.feed_point_message[
                        'X-OPERATION-ID'])
            else:
                with allure.step('# Steps from Casandra DataBase'):
                    database = GlobalClassMetadata.database
                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                    allure.attach(steps, "Cassandra DataBase: steps of process")

        except ValueError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_two -> \n" \
                          f"Step:Clean up database.\n" \
                          f"Message: Impossible to cLean up the database.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise ValueError("Can not return BPE operation step.")

    @allure.title("Проверить подачу декларации c изменением данных существующей в БД персоны\n"
                  "------------------------------------------------\n"
                  "Ei: full data model with items array;\n"
                  "Fs: full data model, own money;\n"
                  "Pn: full data model, 1 lots, 1 items;\n"
                  "CnOnPn: full data model without auction, 1 lots, 1 items, criteria, conversions;\n"
                  "First Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "Second Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "QualificationDeclaration non conflict interest: full data model with old person but new businessFunctions and "
                  "new businessFunctions.documents.\n"
                  )
    def test_check_result_of_sending_the_request_three(self):
        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Ei'):
            """
            Send api request to BPE host for expenditure item creation.
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
                payload=GlobalClassCreateEi.payload,
                test_mode=True
            )
            GlobalClassCreateEi.feed_point_message = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()

            GlobalClassCreateEi.ei_ocid = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

            GlobalClassCreateEi.actual_ei_release = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Fs'):
            """
            Send api request to BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload = copy.deepcopy(FinancialSourcePayload(ei_payload=GlobalClassCreateEi.payload))
            GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
            Requests().createFs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Pn'):
            """
            Send api request to BPE host for planning notice creating.
            Save asynchronous result of sending the request.
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=1,
                    quantity_of_item_object=1)

            Requests().createPn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreatePn.access_token,
                x_operation_id=GlobalClassCreatePn.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                pmd=GlobalClassMetadata.pmd,
                payload=GlobalClassCreatePn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create CnOnPn'):
            """
            Send api request to BPE host for contract notice creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=1,
                    quantity_of_items_object=1,
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
                payload=GlobalClassCreateCnOnPn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create first Bid'):
            """
            Tender platform authorization for create first bid.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create first Bid'):
            """
            Send api request to BPE host for first bid creating.
            Save asynchronous result of sending the request.
            """
            try:
                """
                Set specific value into submission.rules for this testcase.
                """
                min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_submission_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_three -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into submission.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into submission.rules")
            try:
                """
                Set specific value into evaluation.rules for this testcase.
                """
                min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_evaluation_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_three -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into evaluation.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into evaluation.rules")

            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateFirstBid.payload = \
                bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)

            Requests().submit_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFirstBid.access_token,
                x_operation_id=GlobalClassCreateFirstBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateFirstBid.payload,
                test_mode=True
            )
        with allure.step(f'# {step_number}. Authorization platform one: create second Bid'):
            """
            Tender platform authorization for create second bid.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateSecondBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateSecondBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateSecondBid.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create second Bid'):
            """
            Send api request to BPE host for second bid creating.
            Save asynchronous result of sending the request.
            """
            try:
                """
                Set specific value into submission.rules for this testcase.
                """
                min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_submission_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_three -> \n" \
                              f"Step: # {step_number}. Send request for create second Bid.\n" \
                              f"Message: Impossible to set specific value into submission.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into submission.rules")
            try:
                """
                Set specific value into evaluation.rules for this testcase.
                """
                min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_evaluation_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_three -> \n" \
                              f"Step: # {step_number}. Send request for create second Bid.\n" \
                              f"Message: Impossible to set specific value into evaluation.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into evaluation.rules")

            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateSecondBid.payload = \
                bid_payload_class.create_second_bid_full_data_model_with_requirement_responses(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)

            Requests().submit_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateSecondBid.access_token,
                x_operation_id=GlobalClassCreateSecondBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateSecondBid.payload,
                test_mode=True
            )

            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])

            GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()
            while "awardPeriod" not in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']:
                GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()
            time_bot(
                expected_time=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0][
                    'tender']['awardPeriod']['startDate'])
            time.sleep(2)
            GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassTenderPeriodEndAuction.feed_point_message = \
                KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                             initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()

            GlobalClassCreateDeclareNonConflict.award_id = get_id_token_of_award_in_pending_awaiting_state(
                actual_awards_array=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'],
                feed_point_message=GlobalClassTenderPeriodEndAuction.feed_point_message[0])[0]

            GlobalClassCreateDeclareNonConflict.award_token = get_id_token_of_award_in_pending_awaiting_state(
                actual_awards_array=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'],
                feed_point_message=GlobalClassTenderPeriodEndAuction.feed_point_message[0])[1]

        step_number += 1
        requirements_list = list()
        for c in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']['criteria']:
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
        tenderers_list = list()
        for aw in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
            if aw['status'] == "pending":
                if aw['statusDetails'] == "awaiting":
                    for s in aw['suppliers']:
                        for s_1 in s:
                            if s_1 == "id":
                                tenderers_list.append(s['id'])
        n = 1
        for x in range(len(requirements_list)):
            for y in range(len(tenderers_list)):
                x_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                y_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                with allure.step(f'# {step_number}.Authorization platform one: create declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Tender platform authorization for create declaration non conflict interest.
                    As result get Tender platform's access token and process operation-id.
                    """
                    GlobalClassCreateDeclareNonConflict.access_token = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

                    GlobalClassCreateDeclareNonConflict.operation_id = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                        GlobalClassCreateDeclareNonConflict.access_token)
                    step_number += 1
                with allure.step(f'# {step_number}. Send request: create declaration non conflict interest'
                                 f'with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Send api request to BPE host for declaration non conflict interest creating.
                    Save asynchronous result of sending the request.
                    """
                    time.sleep(1)
                    declare_payload_class = copy.deepcopy(DeclarePreparePayload())
                    GlobalClassCreateDeclareNonConflict.payload = \
                        declare_payload_class.create_declare_old_person_but_new_bf_new_doc_full_data_model(
                            requirement_id=requirements_list[x],
                            tenderer_id=tenderers_list[y],
                            number_of_iteration=step_number,
                            actual_ms_release=GlobalClassTenderPeriodEndAuction.actual_ms_release)

                    Requests().create_declare_non_conflict_interest(
                        host_of_request=GlobalClassMetadata.host_for_bpe,
                        access_token=GlobalClassCreateDeclareNonConflict.access_token,
                        x_operation_id=GlobalClassCreateDeclareNonConflict.operation_id,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        tender_id=GlobalClassCreateCnOnPn.ev_id,
                        payload=GlobalClassCreateDeclareNonConflict.payload,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        award_token=GlobalClassCreateDeclareNonConflict.award_token,
                        test_mode=True
                    )
                    GlobalClassCreateDeclareNonConflict.feed_point_message = \
                        KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                    step_number += 1

                with allure.step(f'# {step_number}. See result: create declaration declaration with '
                                 f'{y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Check the results of test case running.
                    """
                    with allure.step(f'# {step_number}.1. Check message in feed point'):
                        """
                        Check the asynchronous_result_of_sending_the_request.
                        """
                        time.sleep(1)
                        GlobalClassCreateDeclareNonConflict.feed_point_message = \
                            KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                        allure.attach(str(GlobalClassCreateDeclareNonConflict.feed_point_message),
                                      'Message in feed point')

                        asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                            GlobalClassCreateDeclareNonConflict.operation_id).declare_non_confl_message_is_successful(
                            environment=GlobalClassMetadata.environment,
                            kafka_message=GlobalClassCreateDeclareNonConflict.feed_point_message,
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
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_three -> \n" \
                                          f"Step: # {step_number}.1. Check message in feed point.\n" \
                                          f"Message: Could not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Could not return BPE operation step")
                        with allure.step('Compare actual message from feed point and expected pattern'):
                            allure.attach(str(json.dumps(asynchronous_result_of_sending_the_request_was_checked)),
                                          "Actual result of comparing the message from feed point.")
                            allure.attach(str(True), "Expected result of comparing the message from feed point.")
                            assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)
                        step_number += 1

                    with allure.step(f'# {step_number}.1. Check EV release'):
                        """
                        Compare actual evaluation value release with expected evaluation value release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
                                      "Actual EV release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ev_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreateCnOnPn.ev_id}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ev_release)),
                                      "Actual EV release after declaration creation.")

                        compare_releases = DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ev_release,
                            GlobalClassCreateDeclareNonConflict.actual_ev_release)

                        dictionary_item_added_was_cleaned = \
                            str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                        compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                        compare_releases = dict(compare_releases)

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        expected_result = {
                            "dictionary_item_added": "['releases'][0]['awards'][0]['requirementResponses']",
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                            'operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['date']
                                }
                            }
                        }

                        actual_awards_array = GlobalClassCreateDeclareNonConflict.actual_ev_release['releases'][0][
                            'awards']
                        try:
                            """
                            Prepare actual awards.requirementResponses array.
                            """
                            actual_awards_requirement_responses_array = list()
                            for a in actual_awards_array:
                                if a['status'] == "pending":
                                    if a['statusDetails'] == "awaiting":
                                        for a_1 in a:
                                            if a_1 == "requirementResponses":
                                                for a_2 in a['requirementResponses']:
                                                    if a_2['requirement']['id'] == \
                                                            GlobalClassCreateDeclareNonConflict.payload[
                                                                'requirementResponse']['requirement']['id']:
                                                        if a_2['relatedTenderer']['id'] == \
                                                                GlobalClassCreateDeclareNonConflict.payload[
                                                                    'requirementResponse'][
                                                                    'relatedTenderer']['id']:
                                                            actual_awards_requirement_responses_array.append(a_2)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_three -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare actual awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare actual awards.requirementResponses.")

                        try:
                            """
                            Prepare expected awards.requirementResponses array.
                            """
                            expected_requirement_response_array = list()
                            expected_requirement_response_object = DeclareExpectedRelease(
                                environment=GlobalClassMetadata.environment,
                                language=GlobalClassMetadata.language
                            ).awards_requirement_responses_array(
                                actual_awards_array=actual_awards_array,
                                declare_payload=GlobalClassCreateDeclareNonConflict.payload)
                            expected_requirement_response_array.append(expected_requirement_response_object)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_three -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare expected awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare expected awards.requirementResponses.")

                        try:
                            """
                                If compare_releases !=expected_result, then return process steps by operation-id.
                                """
                            if compare_releases == expected_result and \
                                    expected_requirement_response_array == actual_awards_requirement_responses_array:
                                pass
                            else:
                                with allure.step('# Steps from Casandra DataBase'):
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TTestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_three -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Can not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Can not return BPE operation step.")

                        with allure.step('Compare actual EV release and expected EV release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases

                        with allure.step('Compare actual requirementResponse and '
                                         'expected requirementResponse into awards array'):
                            allure.attach(str(json.dumps(actual_awards_requirement_responses_array)),
                                          "Actual requirementResponse")
                            allure.attach(str(json.dumps(expected_requirement_response_array)),
                                          "Expected requirementResponse")
                            assert actual_awards_requirement_responses_array == \
                                   expected_requirement_response_array

                    with allure.step(f'# {step_number}.3. Check MS release'):
                        """
                        Compare multistage release with expected multistage release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
                                      "Actual MS release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ms_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreatePn.pn_ocid}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ms_release)),
                                      "Actual MS release after declaration creation.")

                        compare_releases = dict(DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ms_release,
                            GlobalClassCreateDeclareNonConflict.actual_ms_release))

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ms_release[
                                                       'releases'][0]['id'][29:42]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ms_release[
                                                       'releases'][0]['id'][29:42]

                        new_responder_documents_from_payload = GlobalClassCreateDeclareNonConflict.payload[
                            'requirementResponse']['responder']['businessFunctions'][0]['documents']

                        iterable_item_added_object = {
                            f"root['releases'][0]['parties'][3]['persones'][0]['businessFunctions'][{n}]": {
                                'id': GlobalClassCreateDeclareNonConflict.payload[
                                    'requirementResponse']['responder']['businessFunctions'][0]['id'],
                                'type': GlobalClassCreateDeclareNonConflict.payload[
                                    'requirementResponse']['responder']['businessFunctions'][0]['type'],
                                'jobTitle': GlobalClassCreateDeclareNonConflict.payload[
                                    'requirementResponse']['responder']['businessFunctions'][0]['jobTitle'],
                                'period': {
                                    'startDate': GlobalClassCreateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['businessFunctions'][0][
                                        'period']['startDate']
                                },
                                'documents': [{
                                    'id': new_responder_documents_from_payload[0]['id'],
                                    'documentType': new_responder_documents_from_payload[0]['documentType'],
                                    'title': new_responder_documents_from_payload[0]['title'],
                                    'description': new_responder_documents_from_payload[0]['description'],
                                    'url': f"{GlobalClassMetadata.metadata_document_url}/"
                                           f"{new_responder_documents_from_payload[0]['id']}",
                                    'datePublished': GlobalClassCreateDeclareNonConflict.feed_point_message[
                                        'data']['operationDate']
                                }]
                            }
                        }

                        if n != 1:
                            iterable_item_added_object.update(
                                GlobalClassCreateDeclareNonConflict.previous_value_of_iterable_item_object)

                        expected_result = {
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreatePn.pn_ocid}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreatePn.pn_ocid}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                            'operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['date']
                                }
                            },
                            'iterable_item_added': iterable_item_added_object
                        }

                        GlobalClassCreateDeclareNonConflict.previous_value_of_iterable_item_object = \
                            copy.deepcopy(expected_result['iterable_item_added'])

                        n += 1

                        with allure.step('Compare actual MS release and expected MS release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                        allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                        assert expected_result == compare_releases
        try:
            """
            Rollback specific value into submission.rules
            """
            GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                value=min_bids_from_submission_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_three -> \n" \
                          f"Step: Rollback specific value into submission.rules.\n" \
                          f"Message: Impossible to rollback specific value into submission.rules.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into submission.rules.")
        try:
            """
            Rollback specific value into evaluation.rules
            """
            GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                value=min_bids_from_evaluation_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_three -> \n" \
                          f"Step: Rollback specific value into evaluation.rules.\n" \
                          f"Message: Impossible to rollback specific value into evaluation.rules\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into evaluation.rules")

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

                GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.declaration_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id)

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

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[0][
                        'X-OPERATION-ID'])

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassCreateDeclareNonConflict.feed_point_message[
                        'X-OPERATION-ID'])
            else:
                with allure.step('# Steps from Casandra DataBase'):
                    database = GlobalClassMetadata.database
                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                    allure.attach(steps, "Cassandra DataBase: steps of process")

        except ValueError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_three -> \n" \
                          f"Step:Clean up database.\n" \
                          f"Message: Impossible to cLean up the database.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise ValueError("Can not return BPE operation step.")

    @allure.title("Баг https://ustudio.atlassian.net/browse/ES-6461\n"
                  "================================================\n"
                  "Изменить решение по декларации\n"
                  "------------------------------------------------\n"
                  "Ei: full data model with items array;\n"
                  "Fs: full data model, own money;\n"
                  "Pn: full data model, 1 lots, 1 items;\n"
                  "CnOnPn: full data model without auction, 1 lots, 1 items, criteria, conversions;\n"
                  "First Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "Second Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "QualificationDeclaration non conflict interest: full data model with old person.\n"
                  )
    def test_check_result_of_sending_the_request_four(self):
        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Ei'):
            """
            Send api request to BPE host for expenditure item creation.
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
                payload=GlobalClassCreateEi.payload,
                test_mode=True
            )
            GlobalClassCreateEi.feed_point_message = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()

            GlobalClassCreateEi.ei_ocid = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

            GlobalClassCreateEi.actual_ei_release = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Fs'):
            """
            Send api request to BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload = copy.deepcopy(FinancialSourcePayload(ei_payload=GlobalClassCreateEi.payload))
            GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
            Requests().createFs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Pn'):
            """
            Send api request to BPE host for planning notice creating.
            Save asynchronous result of sending the request.
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=1,
                    quantity_of_item_object=1)

            Requests().createPn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreatePn.access_token,
                x_operation_id=GlobalClassCreatePn.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                pmd=GlobalClassMetadata.pmd,
                payload=GlobalClassCreatePn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create CnOnPn'):
            """
            Send api request to BPE host for contract notice creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=1,
                    quantity_of_items_object=1,
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
                payload=GlobalClassCreateCnOnPn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create first Bid'):
            """
            Tender platform authorization for create first bid.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create first Bid'):
            """
            Send api request to BPE host for first bid creating.
            Save asynchronous result of sending the request.
            """
            try:
                """
                Set specific value into submission.rules for this testcase.
                """
                min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_submission_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_four -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into submission.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into submission.rules")
            try:
                """
                Set specific value into evaluation.rules for this testcase.
                """
                min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_evaluation_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_four -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into evaluation.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into evaluation.rules")

            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateFirstBid.payload = \
                bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)

            Requests().submit_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFirstBid.access_token,
                x_operation_id=GlobalClassCreateFirstBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateFirstBid.payload,
                test_mode=True
            )
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])

            GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()
            while "awardPeriod" not in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']:
                GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()
            time_bot(
                expected_time=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0][
                    'tender']['awardPeriod']['startDate'])

            GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassTenderPeriodEndAuction.feed_point_message = \
                KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                             initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()

            GlobalClassCreateDeclareNonConflict.award_id = \
                GlobalClassTenderPeriodEndAuction.feed_point_message[0]['data']['outcomes']['awards'][0]['id']
            GlobalClassCreateDeclareNonConflict.award_token = \
                GlobalClassTenderPeriodEndAuction.feed_point_message[0]['data']['outcomes']['awards'][0][
                    'X-TOKEN']
        step_number += 1
        requirements_list = list()
        for c in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']['criteria']:
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
        tenderers_list = list()
        for aw in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
            if aw['status'] == "pending":
                if aw['statusDetails'] == "awaiting":
                    for s in aw['suppliers']:
                        for s_1 in s:
                            if s_1 == "id":
                                tenderers_list.append(s['id'])

        for x in range(len(requirements_list)):
            for y in range(len(tenderers_list)):
                x_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                y_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                with allure.step(f'# {step_number}.Authorization platform one: create declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Tender platform authorization for create declare non conflict interest.
                    As result get Tender platform's access token and process operation-id.
                    """
                    GlobalClassCreateDeclareNonConflict.access_token = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

                    GlobalClassCreateDeclareNonConflict.operation_id = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                        GlobalClassCreateDeclareNonConflict.access_token)
                    step_number += 1
                with allure.step(f'# {step_number}. Send request: create declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Send api request to BPE host for declare non conflict interest creating.
                    Save asynchronous result of sending the request.
                    """
                    time.sleep(1)
                    declare_payload_class = copy.deepcopy(DeclarePreparePayload())
                    GlobalClassCreateDeclareNonConflict.payload = \
                        declare_payload_class.create_declare_old_person_full_data_model(
                            requirement_id=requirements_list[x],
                            tenderer_id=tenderers_list[y],
                            actual_ms_release=GlobalClassTenderPeriodEndAuction.actual_ms_release)

                    Requests().create_declare_non_conflict_interest(
                        host_of_request=GlobalClassMetadata.host_for_bpe,
                        access_token=GlobalClassCreateDeclareNonConflict.access_token,
                        x_operation_id=GlobalClassCreateDeclareNonConflict.operation_id,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        tender_id=GlobalClassCreateCnOnPn.ev_id,
                        payload=GlobalClassCreateDeclareNonConflict.payload,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        award_token=GlobalClassCreateDeclareNonConflict.award_token,
                        test_mode=True
                    )
                    GlobalClassCreateDeclareNonConflict.feed_point_message = \
                        KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                    step_number += 1

                with allure.step(f'# {step_number}. See result: create declaration declaration with '
                                 f'{y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Check the results of test case running.
                    """
                    with allure.step(f'# {step_number}.1. Check message in feed point'):
                        """
                        Check the asynchronous_result_of_sending_the_request.
                        """
                        time.sleep(1)
                        GlobalClassCreateDeclareNonConflict.feed_point_message = \
                            KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                        allure.attach(str(GlobalClassCreateDeclareNonConflict.feed_point_message),
                                      'Message in feed point')

                        asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                            GlobalClassCreateDeclareNonConflict.operation_id).declare_non_confl_message_is_successful(
                            environment=GlobalClassMetadata.environment,
                            kafka_message=GlobalClassCreateDeclareNonConflict.feed_point_message,
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
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_four -> \n" \
                                          f"Step: # {step_number}.1. Check message in feed point.\n" \
                                          f"Message: Could not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Could not return BPE operation step")
                        with allure.step('Compare actual message from feed point and expected pattern'):
                            allure.attach(str(json.dumps(asynchronous_result_of_sending_the_request_was_checked)),
                                          "Actual result of comparing the message from feed point.")
                            allure.attach(str(True), "Expected result of comparing the message from feed point.")
                            assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)
                        step_number += 1

                    with allure.step(f'# {step_number}.2. Check EV release'):
                        """
                        Compare actual evaluation value release with expected evaluation value release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
                                      "Actual EV release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ev_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreateCnOnPn.ev_id}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ev_release)),
                                      "Actual EV release after declaration creation.")

                        compare_releases = dict(DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ev_release,
                            GlobalClassCreateDeclareNonConflict.actual_ev_release))
                        dictionary_item_added_was_cleaned = \
                            str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                        compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                        compare_releases = dict(compare_releases)

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        expected_result = {
                            "dictionary_item_added": "['releases'][0]['awards'][0]['requirementResponses']",
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                            'operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['date']
                                }
                            }
                        }

                        actual_awards_array = GlobalClassCreateDeclareNonConflict.actual_ev_release['releases'][0][
                            'awards']
                        try:
                            """
                            Prepare actual awards.requirementResponses array.
                            """
                            actual_awards_requirement_responses_array = list()
                            for a in actual_awards_array:
                                if a['status'] == "pending":
                                    if a['statusDetails'] == "awaiting":
                                        for a_1 in a:
                                            if a_1 == "requirementResponses":
                                                for a_2 in a['requirementResponses']:
                                                    if a_2['requirement']['id'] == \
                                                            GlobalClassCreateDeclareNonConflict.payload[
                                                                'requirementResponse']['requirement']['id']:
                                                        if a_2['relatedTenderer']['id'] == \
                                                                GlobalClassCreateDeclareNonConflict.payload[
                                                                    'requirementResponse'][
                                                                    'relatedTenderer']['id']:
                                                            actual_awards_requirement_responses_array.append(a_2)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_four -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare actual awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare actual awards.requirementResponses.")

                        try:
                            """
                            Prepare expected awards.requirementResponses array.
                            """
                            expected_requirement_response_array = list()
                            expected_requirement_response_object = DeclareExpectedRelease(
                                environment=GlobalClassMetadata.environment,
                                language=GlobalClassMetadata.language
                            ).awards_requirement_responses_array(
                                actual_awards_array=actual_awards_array,
                                declare_payload=GlobalClassCreateDeclareNonConflict.payload)
                            expected_requirement_response_array.append(expected_requirement_response_object)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_four -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare expected awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare expected awards.requirementResponses.")

                        try:
                            """
                                If compare_releases !=expected_result, then return process steps by operation-id.
                                """
                            if compare_releases == expected_result and \
                                    expected_requirement_response_array == actual_awards_requirement_responses_array:
                                pass
                            else:
                                with allure.step('# Steps from Casandra DataBase'):
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TTestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_four -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Can not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Can not return BPE operation step.")

                        with allure.step('Compare actual EV release and expected EV release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases

                        with allure.step('Compare actual requirementResponse and '
                                         'expected requirementResponse into awards array'):
                            allure.attach(str(json.dumps(actual_awards_requirement_responses_array)),
                                          "Actual requirementResponse")
                            allure.attach(str(json.dumps(expected_requirement_response_array)),
                                          "Expected requirementResponse")
                            assert actual_awards_requirement_responses_array == \
                                   expected_requirement_response_array

                    with allure.step(f'# {step_number}.3. Check MS release'):
                        """
                        Compare multistage release with expected multistage release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
                                      "Actual MS release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ms_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreatePn.pn_ocid}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ms_release)),
                                      "Actual MS release after declaration creation.")

                        compare_releases = DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ms_release,
                            GlobalClassCreateDeclareNonConflict.actual_ms_release)

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ms_release[
                                                       'releases'][0]['id'][29:42]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ms_release[
                                                       'releases'][0]['id'][29:42]

                        expected_result = {
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreatePn.pn_ocid}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreatePn.pn_ocid}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassCreateDeclareNonConflict.feed_point_message['data']['operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['date']
                                }
                            }
                        }

                        with allure.step('Compare actual MS release and expected MS release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases

                with allure.step(f'# {step_number}.Authorization platform one: update declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Tender platform authorization for update declare non conflict interest.
                    As result get Tender platform's access token and process operation-id.
                    """
                    GlobalClassUpdateDeclareNonConflict.access_token = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

                    GlobalClassUpdateDeclareNonConflict.operation_id = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                        GlobalClassUpdateDeclareNonConflict.access_token)
                    step_number += 1
                with allure.step(f'# {step_number}. Send request: update declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Send api request to BPE host for declare non conflict interest updating.
                    Save asynchronous result of sending the request.
                    """
                    time.sleep(1)
                    declare_payload_class = copy.deepcopy(DeclarePreparePayload())
                    GlobalClassUpdateDeclareNonConflict.payload = \
                        declare_payload_class.create_declare_old_person_full_data_model(
                            requirement_id=requirements_list[x],
                            tenderer_id=tenderers_list[y],
                            req_resp_id=actual_awards_requirement_responses_array[0]['id'],
                            value=False,
                            actual_ms_release=GlobalClassCreateDeclareNonConflict.actual_ms_release)

                    Requests().create_declare_non_conflict_interest(
                        host_of_request=GlobalClassMetadata.host_for_bpe,
                        access_token=GlobalClassUpdateDeclareNonConflict.access_token,
                        x_operation_id=GlobalClassUpdateDeclareNonConflict.operation_id,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        tender_id=GlobalClassCreateCnOnPn.ev_id,
                        payload=GlobalClassUpdateDeclareNonConflict.payload,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        award_token=GlobalClassCreateDeclareNonConflict.award_token,
                        test_mode=True
                    )
                    GlobalClassUpdateDeclareNonConflict.feed_point_message = \
                        KafkaMessage(GlobalClassUpdateDeclareNonConflict.operation_id).get_message_from_kafka()
                    step_number += 1

                with allure.step(f'# {step_number}. See result: update declaration declaration with '
                                 f'{y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Check the results of test case running.
                    """
                    with allure.step(f'# {step_number}.1. Check message in feed point'):
                        """
                        Check the asynchronous_result_of_sending_the_request.
                        """
                        time.sleep(1)
                        GlobalClassUpdateDeclareNonConflict.feed_point_message = \
                            KafkaMessage(GlobalClassUpdateDeclareNonConflict.operation_id).get_message_from_kafka()
                        allure.attach(str(GlobalClassUpdateDeclareNonConflict.feed_point_message),
                                      'Message in feed point')

                        asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                            GlobalClassUpdateDeclareNonConflict.operation_id).declare_non_confl_message_is_successful(
                            environment=GlobalClassMetadata.environment,
                            kafka_message=GlobalClassUpdateDeclareNonConflict.feed_point_message,
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
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassUpdateDeclareNonConflict.feed_point_message)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_four -> \n" \
                                          f"Step: # {step_number}.1. Check message in feed point.\n" \
                                          f"Message: Could not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Could not return BPE operation step")
                        with allure.step('Compare actual message from feed point and expected pattern'):
                            allure.attach(str(json.dumps(asynchronous_result_of_sending_the_request_was_checked)),
                                          "Actual result of comparing the message from feed point.")
                            allure.attach(str(True), "Expected result of comparing the message from feed point.")
                            assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)
                        step_number += 1
        try:
            """
            Rollback specific value into submission.rules
            """
            GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                value=min_bids_from_submission_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_four -> \n" \
                          f"Step: Rollback specific value into submission.rules.\n" \
                          f"Message: Impossible to rollback specific value into submission.rules.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into submission.rules.")
        try:
            """
            Rollback specific value into evaluation.rules
            """
            GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                value=min_bids_from_evaluation_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_four -> \n" \
                          f"Step: Rollback specific value into evaluation.rules.\n" \
                          f"Message: Impossible to rollback specific value into evaluation.rules\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into evaluation.rules")

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

                GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.declaration_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id)

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

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[0][
                        'X-OPERATION-ID'])

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassCreateDeclareNonConflict.feed_point_message[
                        'X-OPERATION-ID'])

            else:
                with allure.step('# Steps from Casandra DataBase'):
                    database = GlobalClassMetadata.database
                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                    allure.attach(steps, "Cassandra DataBase: steps of process")

        except ValueError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_four -> \n" \
                          f"Step:Clean up database.\n" \
                          f"Message: Impossible to cLean up the database.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise ValueError("Can not return BPE operation step.")

    @allure.title("Добавить ответы более, чем одной персоной, относительно одного аварда\n"
                  "------------------------------------------------\n"
                  "Ei: full data model with items array;\n"
                  "Fs: full data model, own money;\n"
                  "Pn: full data model, 1 lots, 1 items;\n"
                  "CnOnPn: full data model without auction, 1 lots, 1 items, criteria, conversions;\n"
                  "First Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "Second Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "QualificationDeclaration non conflict interest: full data model with old person.\n"
                  )
    def test_check_result_of_sending_the_request_five(self):
        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Ei'):
            """
            Send api request to BPE host for expenditure item creation.
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
                payload=GlobalClassCreateEi.payload,
                test_mode=True
            )
            GlobalClassCreateEi.feed_point_message = \
                KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()

            GlobalClassCreateEi.ei_ocid = \
                GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

            GlobalClassCreateEi.actual_ei_release = requests.get(
                url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateEi.ei_ocid}").json()
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Fs'):
            """
            Send api request to BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload = copy.deepcopy(FinancialSourcePayload(ei_payload=GlobalClassCreateEi.payload))
            GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
            Requests().createFs(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFs.access_token,
                x_operation_id=GlobalClassCreateFs.operation_id,
                ei_ocid=GlobalClassCreateEi.ei_ocid,
                payload=GlobalClassCreateFs.payload,
                test_mode=True)

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
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create Pn'):
            """
            Send api request to BPE host for planning notice creating.
            Save asynchronous result of sending the request.
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=1,
                    quantity_of_item_object=1)

            Requests().createPn(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreatePn.access_token,
                x_operation_id=GlobalClassCreatePn.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                pmd=GlobalClassMetadata.pmd,
                payload=GlobalClassCreatePn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create CnOnPn'):
            """
            Send api request to BPE host for contract notice creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)
            cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
            GlobalClassCreateCnOnPn.payload = \
                cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv(
                    enquiry_interval=121,
                    tender_interval=300,
                    quantity_of_lots_object=1,
                    quantity_of_items_object=1,
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
                payload=GlobalClassCreateCnOnPn.payload,
                test_mode=True
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
            step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create first Bid'):
            """
            Tender platform authorization for create first bid.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: create first Bid'):
            """
            Send api request to BPE host for first bid creating.
            Save asynchronous result of sending the request.
            """
            try:
                """
                Set specific value into submission.rules for this testcase.
                """
                min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_submission_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_five -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into submission.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into submission.rules")
            try:
                """
                Set specific value into evaluation.rules for this testcase.
                """
                min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_evaluation_rules != "1":
                    GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                        value='1',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = declare_non_conflict_interest_test.py -> \n" \
                              f"Class = TestDeclareNonConflictInterest -> \n" \
                              f"Method = test_check_result_of_sending_the_request_five -> \n" \
                              f"Step: # {step_number}. Send request for create first Bid.\n" \
                              f"Message: Impossible to set specific value into evaluation.rules.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                raise Exception("Impossible to set specific value into evaluation.rules")

            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateFirstBid.payload = \
                bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)

            Requests().submit_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFirstBid.access_token,
                x_operation_id=GlobalClassCreateFirstBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateFirstBid.payload,
                test_mode=True
            )
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])

            GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()
            while "awardPeriod" not in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']:
                GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()
            time_bot(
                expected_time=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0][
                    'tender']['awardPeriod']['startDate'])

            GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassTenderPeriodEndAuction.feed_point_message = \
                KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                             initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()

            GlobalClassCreateDeclareNonConflict.award_id = \
                GlobalClassTenderPeriodEndAuction.feed_point_message[0]['data']['outcomes']['awards'][0]['id']
            GlobalClassCreateDeclareNonConflict.award_token = \
                GlobalClassTenderPeriodEndAuction.feed_point_message[0]['data']['outcomes']['awards'][0][
                    'X-TOKEN']
        step_number += 1
        requirements_list = list()
        for c in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']['criteria']:
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
        tenderers_list = list()
        for aw in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
            if aw['status'] == "pending":
                if aw['statusDetails'] == "awaiting":
                    for s in aw['suppliers']:
                        for s_1 in s:
                            if s_1 == "id":
                                tenderers_list.append(s['id'])
        n = 0
        for x in range(len(requirements_list)):
            for y in range(len(tenderers_list)):
                x_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                y_mapper = {
                    0: "first",
                    1: "second",
                    2: "third",
                    3: "fourth",
                    4: "fifth",
                    5: "sixth",
                    6: "seventh",
                    7: "eighth",
                    8: "ninth",
                    9: "tenth"
                }
                with allure.step(f'# {step_number}.Authorization platform one: create declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Tender platform authorization for create declare non conflict interest.
                    As result get Tender platform's access token and process operation-id.
                    """
                    GlobalClassCreateDeclareNonConflict.access_token = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

                    GlobalClassCreateDeclareNonConflict.operation_id = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                        GlobalClassCreateDeclareNonConflict.access_token)
                    step_number += 1
                with allure.step(f'# {step_number}. Send request: create declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Send api request to BPE host for declare non conflict interest creating.
                    Save asynchronous result of sending the request.
                    """
                    time.sleep(1)
                    declare_payload_class = copy.deepcopy(DeclarePreparePayload())
                    GlobalClassCreateDeclareNonConflict.payload = \
                        declare_payload_class.create_declare_old_person_full_data_model(
                            requirement_id=requirements_list[x],
                            tenderer_id=tenderers_list[y],
                            actual_ms_release=GlobalClassTenderPeriodEndAuction.actual_ms_release)

                    Requests().create_declare_non_conflict_interest(
                        host_of_request=GlobalClassMetadata.host_for_bpe,
                        access_token=GlobalClassCreateDeclareNonConflict.access_token,
                        x_operation_id=GlobalClassCreateDeclareNonConflict.operation_id,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        tender_id=GlobalClassCreateCnOnPn.ev_id,
                        payload=GlobalClassCreateDeclareNonConflict.payload,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        award_token=GlobalClassCreateDeclareNonConflict.award_token,
                        test_mode=True
                    )
                    GlobalClassCreateDeclareNonConflict.feed_point_message = \
                        KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                    step_number += 1

                with allure.step(f'# {step_number}. See result: create declaration declaration with '
                                 f'{y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Check the results of test case running.
                    """
                    with allure.step(f'# {step_number}.1. Check message in feed point.'):
                        """
                        Check the asynchronous_result_of_sending_the_request.
                        """
                        time.sleep(1)
                        GlobalClassCreateDeclareNonConflict.feed_point_message = \
                            KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                        allure.attach(str(GlobalClassCreateDeclareNonConflict.feed_point_message),
                                      'Message in feed point')

                        asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                            GlobalClassCreateDeclareNonConflict.operation_id).declare_non_confl_message_is_successful(
                            environment=GlobalClassMetadata.environment,
                            kafka_message=GlobalClassCreateDeclareNonConflict.feed_point_message,
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
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                                          f"Step: # {step_number}.1. Check message in feed point.\n" \
                                          f"Message: Could not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Could not return BPE operation step")
                        with allure.step('Compare actual message from feed point and expected pattern'):
                            allure.attach(str(json.dumps(asynchronous_result_of_sending_the_request_was_checked)),
                                          "Actual result of comparing the message from feed point.")
                            allure.attach(str(True), "Expected result of comparing the message from feed point.")
                            assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)
                        step_number += 1

                    with allure.step(f'# {step_number}.2. Check EV release.'):
                        """
                        Compare actual evaluation value release with expected evaluation value release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
                                      "Actual EV release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ev_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreateCnOnPn.ev_id}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ev_release)),
                                      "Actual EV release after declaration creation.")

                        compare_releases = dict(DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ev_release,
                            GlobalClassCreateDeclareNonConflict.actual_ev_release))
                        dictionary_item_added_was_cleaned = \
                            str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                        compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                        compare_releases = dict(compare_releases)

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ev_release[
                                                       'releases'][0]['id'][46:59]

                        expected_result = {
                            "dictionary_item_added": "['releases'][0]['awards'][0]['requirementResponses']",
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                            'operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['date']
                                }
                            }
                        }

                        actual_awards_array = GlobalClassCreateDeclareNonConflict.actual_ev_release['releases'][0][
                            'awards']
                        try:
                            """
                            Prepare actual awards.requirementResponses array.
                            """
                            actual_awards_requirement_responses_array = list()
                            for a in actual_awards_array:
                                if a['status'] == "pending":
                                    if a['statusDetails'] == "awaiting":
                                        for a_1 in a:
                                            if a_1 == "requirementResponses":
                                                for a_2 in a['requirementResponses']:
                                                    if a_2['requirement']['id'] == \
                                                            GlobalClassCreateDeclareNonConflict.payload[
                                                                'requirementResponse']['requirement']['id']:
                                                        if a_2['relatedTenderer']['id'] == \
                                                                GlobalClassCreateDeclareNonConflict.payload[
                                                                    'requirementResponse'][
                                                                    'relatedTenderer']['id']:
                                                            actual_awards_requirement_responses_array.append(a_2)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare actual awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare actual awards.requirementResponses.")

                        try:
                            """
                            Prepare expected awards.requirementResponses array.
                            """
                            expected_requirement_response_array = list()
                            expected_requirement_response_object = DeclareExpectedRelease(
                                environment=GlobalClassMetadata.environment,
                                language=GlobalClassMetadata.language
                            ).awards_requirement_responses_array(
                                actual_awards_array=actual_awards_array,
                                declare_payload=GlobalClassCreateDeclareNonConflict.payload)
                            expected_requirement_response_array.append(expected_requirement_response_object)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare expected awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare expected awards.requirementResponses.")

                        try:
                            """
                                If compare_releases !=expected_result, then return process steps by operation-id.
                                """
                            if compare_releases == expected_result and \
                                    expected_requirement_response_array == actual_awards_requirement_responses_array:
                                pass
                            else:
                                with allure.step('# Steps from Casandra DataBase'):
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TTestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Can not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Can not return BPE operation step.")

                        with allure.step('Compare actual EV release and expected EV release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases

                        with allure.step('Compare actual requirementResponse and '
                                         'expected requirementResponse into awards array'):
                            allure.attach(str(json.dumps(actual_awards_requirement_responses_array)),
                                          "Actual requirementResponse")
                            allure.attach(str(json.dumps(expected_requirement_response_array)),
                                          "Expected requirementResponse")
                            assert actual_awards_requirement_responses_array == \
                                   expected_requirement_response_array

                    with allure.step(f'# {step_number}.3. Check MS release.'):
                        """
                        Compare multistage release with expected multistage release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
                                      "Actual MS release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ms_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreatePn.pn_ocid}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ms_release)),
                                      "Actual MS release after declaration creation.")

                        compare_releases = dict(DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ms_release,
                            GlobalClassCreateDeclareNonConflict.actual_ms_release))

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ms_release[
                                                       'releases'][0]['id'][29:42]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ms_release[
                                                       'releases'][0]['id'][29:42]

                        if n == 0:
                            expected_result = {
                                "values_changed": {
                                    "root['releases'][0]['id']": {
                                        "new_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{new_value_for_release_id}",
                                        "old_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{old_value_for_release_id}"
                                    },
                                    "root['releases'][0]['date']": {
                                        "new_value":
                                            GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                                'operationDate'],
                                        "old_value":
                                            GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['date']
                                    }
                                }
                            }
                        elif n == 1:
                            new_responder_identifier_from_payload = GlobalClassUpdateDeclareNonConflict.payload[
                                'requirementResponse']['responder']['identifier']
                            new_responder_documents_from_payload = GlobalClassUpdateDeclareNonConflict.payload[
                                'requirementResponse']['responder']['businessFunctions'][0]['documents']
                            iterable_item_added_object = {
                                f"root['releases'][0]['parties'][3]['persones'][{n}]": {
                                    'id': f"{new_responder_identifier_from_payload['scheme']}-"
                                          f"{new_responder_identifier_from_payload['id']}",
                                    'title': GlobalClassCreateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['title'],
                                    'name': GlobalClassUpdateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['name'],
                                    'identifier': {
                                        'scheme': new_responder_identifier_from_payload['scheme'],
                                        'id': new_responder_identifier_from_payload['id'],
                                        'uri': new_responder_identifier_from_payload['uri']
                                    },
                                    'businessFunctions': [{
                                        'id': GlobalClassUpdateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['id'],
                                        'type': GlobalClassUpdateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['type'],
                                        'jobTitle': GlobalClassCreateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['jobTitle'],
                                        'period': {
                                            'startDate': GlobalClassUpdateDeclareNonConflict.payload[
                                                'requirementResponse']['responder']['businessFunctions'][0][
                                                'period']['startDate']
                                        },
                                        'documents': [{
                                            'id': new_responder_documents_from_payload[0]['id'],
                                            'documentType': new_responder_documents_from_payload[0]['documentType'],
                                            'title': new_responder_documents_from_payload[0]['title'],
                                            'description': new_responder_documents_from_payload[0]['description'],
                                            'url': f"{GlobalClassMetadata.metadata_document_url}/"
                                                   f"{new_responder_documents_from_payload[0]['id']}",
                                            'datePublished': GlobalClassCreateCnOnPn.feed_point_message[
                                                'data']['operationDate']
                                        }]
                                    }]
                                }
                            }

                            expected_result = {
                                "values_changed": {
                                    "root['releases'][0]['id']": {
                                        "new_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{new_value_for_release_id}",
                                        "old_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{old_value_for_release_id}"
                                    },
                                    "root['releases'][0]['date']": {
                                        "new_value":
                                            GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                                'operationDate'],
                                        "old_value":
                                            GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['date']
                                    }
                                },
                                "iterable_item_added": iterable_item_added_object
                            }

                            GlobalClassUpdateDeclareNonConflict.previous_value_of_iterable_item_object = \
                                copy.deepcopy(expected_result['iterable_item_added'])

                        else:
                            new_responder_identifier_from_payload = GlobalClassUpdateDeclareNonConflict.payload[
                                'requirementResponse']['responder']['identifier']
                            new_responder_documents_from_payload = GlobalClassUpdateDeclareNonConflict.payload[
                                'requirementResponse']['responder']['businessFunctions'][0]['documents']
                            iterable_item_added_object = {
                                f"root['releases'][0]['parties'][3]['persones'][{n}]": {
                                    'id': f"{new_responder_identifier_from_payload['scheme']}-"
                                          f"{new_responder_identifier_from_payload['id']}",
                                    'title': GlobalClassCreateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['title'],
                                    'name': GlobalClassUpdateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['name'],
                                    'identifier': {
                                        'scheme': new_responder_identifier_from_payload['scheme'],
                                        'id': new_responder_identifier_from_payload['id'],
                                        'uri': new_responder_identifier_from_payload['uri']
                                    },
                                    'businessFunctions': [{
                                        'id': GlobalClassUpdateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['id'],
                                        'type': GlobalClassUpdateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['type'],
                                        'jobTitle': GlobalClassCreateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['jobTitle'],
                                        'period': {
                                            'startDate': GlobalClassUpdateDeclareNonConflict.payload[
                                                'requirementResponse']['responder']['businessFunctions'][0][
                                                'period']['startDate']
                                        },
                                        'documents': [{
                                            'id': new_responder_documents_from_payload[0]['id'],
                                            'documentType': new_responder_documents_from_payload[0]['documentType'],
                                            'title': new_responder_documents_from_payload[0]['title'],
                                            'description': new_responder_documents_from_payload[0]['description'],
                                            'url': f"{GlobalClassMetadata.metadata_document_url}/"
                                                   f"{new_responder_documents_from_payload[0]['id']}",
                                            'datePublished': GlobalClassCreateCnOnPn.feed_point_message[
                                                'data']['operationDate']
                                        }]
                                    }]
                                }
                            }

                            iterable_item_added_object.update(
                                GlobalClassUpdateDeclareNonConflict.previous_value_of_iterable_item_object)

                            expected_result = {
                                "values_changed": {
                                    "root['releases'][0]['id']": {
                                        "new_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{new_value_for_release_id}",
                                        "old_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{old_value_for_release_id}"
                                    },
                                    "root['releases'][0]['date']": {
                                        "new_value":
                                            GlobalClassCreateDeclareNonConflict.feed_point_message['data'][
                                                'operationDate'],
                                        "old_value":
                                            GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['date']
                                    }
                                },
                                "iterable_item_added": iterable_item_added_object
                            }

                            GlobalClassUpdateDeclareNonConflict.previous_value_of_iterable_item_object = \
                                copy.deepcopy(expected_result['iterable_item_added'])

                        with allure.step('Compare actual MS release and expected MS release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases

                with allure.step(f'# {step_number}. Authorization platform one: update declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} '
                                 f'requirement.t'):
                    """
                    Tender platform authorization for update declare non conflict interest.
                    As result get Tender platform's access token and process operation-id.
                    """
                    GlobalClassUpdateDeclareNonConflict.access_token = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

                    GlobalClassUpdateDeclareNonConflict.operation_id = PlatformAuthorization(
                        GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                        GlobalClassUpdateDeclareNonConflict.access_token)
                    step_number += 1
                with allure.step(f'# {step_number}. Send request: update declaration '
                                 f'non conflict interest with {y_mapper[y]} tenderer and {x_mapper[x]} '
                                 f'requirement.'):
                    """
                    Send api request to BPE host for declare non conflict interest updating.
                    Save asynchronous result of sending the request.
                    """
                    time.sleep(1)
                    declare_payload_class = copy.deepcopy(DeclarePreparePayload())
                    GlobalClassUpdateDeclareNonConflict.payload = \
                        declare_payload_class.create_declare_new_responder_identifier_but_old_other_value_full(
                            requirement_id=requirements_list[x],
                            tenderer_id=tenderers_list[y],
                            number_of_iteration=step_number,
                            actual_ms_release=GlobalClassCreateDeclareNonConflict.actual_ms_release)

                    Requests().create_declare_non_conflict_interest(
                        host_of_request=GlobalClassMetadata.host_for_bpe,
                        access_token=GlobalClassUpdateDeclareNonConflict.access_token,
                        x_operation_id=GlobalClassUpdateDeclareNonConflict.operation_id,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        tender_id=GlobalClassCreateCnOnPn.ev_id,
                        payload=GlobalClassUpdateDeclareNonConflict.payload,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        award_token=GlobalClassCreateDeclareNonConflict.award_token,
                        test_mode=True
                    )
                    GlobalClassUpdateDeclareNonConflict.feed_point_message = \
                        KafkaMessage(GlobalClassUpdateDeclareNonConflict.operation_id).get_message_from_kafka()
                    step_number += 1
                with allure.step(f'# {step_number}. See result: update declaration with '
                                 f'{y_mapper[y]} tenderer and {x_mapper[x]} requirement.'):
                    """
                    Check the results of test case running.
                    """
                    with allure.step(f'# {step_number}.1. Check message in feed point.'):
                        """
                        Check the asynchronous_result_of_sending_the_request.
                        """
                        time.sleep(1)
                        GlobalClassCreateDeclareNonConflict.feed_point_message = \
                            KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                        allure.attach(str(GlobalClassCreateDeclareNonConflict.feed_point_message),
                                      'Message in feed point')

                        asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                            GlobalClassCreateDeclareNonConflict.operation_id).declare_non_confl_message_is_successful(
                            environment=GlobalClassMetadata.environment,
                            kafka_message=GlobalClassUpdateDeclareNonConflict.feed_point_message,
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
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                                          f"Step: # {step_number}.1. Check message in feed point.\n" \
                                          f"Message: Could not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Could not return BPE operation step")
                        with allure.step('Compare actual message from feed point and expected pattern'):
                            allure.attach(str(json.dumps(asynchronous_result_of_sending_the_request_was_checked)),
                                          "Actual result of comparing the message from feed point.")
                            allure.attach(str(True), "Expected result of comparing the message from feed point.")
                            assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)
                        step_number += 1

                    with allure.step(f'# {step_number}.2. Check EV release.'):
                        """
                        Compare actual evaluation value release with expected evaluation value release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
                                      "Actual EV release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ev_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreateCnOnPn.ev_id}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ev_release)),
                                      "Actual EV release after declaration creation.")

                        compare_releases = dict(DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ev_release,
                            GlobalClassCreateDeclareNonConflict.actual_ev_release))
                        dictionary_item_added_was_cleaned = \
                            str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                        compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                        compare_releases = dict(compare_releases)

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ev_release[
                                                       'releases'][0]['id'][46:59]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ev_release[
                                                       'releases'][0]['id'][46:59]

                        expected_result = {
                            "dictionary_item_added": "['releases'][0]['awards'][0]['requirementResponses']",
                            "values_changed": {
                                "root['releases'][0]['id']": {
                                    "new_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{new_value_for_release_id}",
                                    "old_value":
                                        f"{GlobalClassCreateCnOnPn.ev_id}-{old_value_for_release_id}"
                                },
                                "root['releases'][0]['date']": {
                                    "new_value":
                                        GlobalClassUpdateDeclareNonConflict.feed_point_message['data'][
                                            'operationDate'],
                                    "old_value":
                                        GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['date']
                                }
                            }
                        }

                        actual_awards_array = GlobalClassCreateDeclareNonConflict.actual_ev_release['releases'][0][
                            'awards']
                        try:
                            """
                            Prepare actual awards.requirementResponses array.
                            """
                            actual_awards_requirement_responses_array = list()
                            for a in actual_awards_array:
                                if a['status'] == "pending":
                                    if a['statusDetails'] == "awaiting":
                                        for a_1 in a:
                                            if a_1 == "requirementResponses":
                                                for a_2 in a['requirementResponses']:
                                                    if a_2['requirement']['id'] == \
                                                            GlobalClassCreateDeclareNonConflict.payload[
                                                                'requirementResponse']['requirement']['id']:
                                                        if a_2['relatedTenderer']['id'] == \
                                                                GlobalClassCreateDeclareNonConflict.payload[
                                                                    'requirementResponse'][
                                                                    'relatedTenderer']['id']:
                                                            actual_awards_requirement_responses_array.append(a_2)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare actual awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare actual awards.requirementResponses.")

                        try:
                            """
                            Prepare expected awards.requirementResponses array.
                            """
                            expected_requirement_response_array = list()
                            expected_requirement_response_object = DeclareExpectedRelease(
                                environment=GlobalClassMetadata.environment,
                                language=GlobalClassMetadata.language
                            ).awards_requirement_responses_array(
                                actual_awards_array=actual_awards_array,
                                declare_payload=GlobalClassCreateDeclareNonConflict.payload)
                            expected_requirement_response_array.append(expected_requirement_response_object)

                            expected_requirement_response_object = DeclareExpectedRelease(
                                environment=GlobalClassMetadata.environment,
                                language=GlobalClassMetadata.language
                            ).awards_requirement_responses_array(
                                actual_awards_array=actual_awards_array,
                                declare_payload=GlobalClassUpdateDeclareNonConflict.payload)
                            expected_requirement_response_array.append(expected_requirement_response_object)
                        except Exception:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Impossible to prepare expected awards.requirementResponses.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise Exception("Impossible to prepare expected awards.requirementResponses.")

                        try:
                            """
                                If compare_releases !=expected_result, then return process steps by operation-id.
                                """
                            if compare_releases == expected_result and \
                                    expected_requirement_response_array == actual_awards_requirement_responses_array:
                                pass
                            else:
                                with allure.step('# Steps from Casandra DataBase'):
                                    database = GlobalClassMetadata.database
                                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                                    allure.attach(steps, "Cassandra DataBase: steps of process")
                        except ValueError:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = declare_non_conflict_interest_test.py -> \n" \
                                          f"Class = TTestDeclareNonConflictInterest -> \n" \
                                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                                          f"Step: # {step_number}.2. Check EV release.\n" \
                                          f"Message: Can not return BPE operation step.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            raise ValueError("Can not return BPE operation step.")

                        with allure.step('Compare actual EV release and expected EV release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases

                        with allure.step('Compare actual requirementResponse and '
                                         'expected requirementResponse into awards array'):
                            allure.attach(str(json.dumps(actual_awards_requirement_responses_array)),
                                          "Actual requirementResponse")
                            allure.attach(str(json.dumps(expected_requirement_response_array)),
                                          "Expected requirementResponse")
                            assert actual_awards_requirement_responses_array == \
                                   expected_requirement_response_array

                    with allure.step(f'# {step_number}.3. Check MS release.'):
                        """
                        Compare multistage release with expected multistage release model.
                        """
                        time.sleep(2)
                        allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
                                      "Actual MS release before declaration creation.")

                        GlobalClassCreateDeclareNonConflict.actual_ms_release = requests.get(
                            url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                                f"{GlobalClassCreatePn.pn_ocid}").json()

                        allure.attach(str(json.dumps(GlobalClassCreateDeclareNonConflict.actual_ms_release)),
                                      "Actual MS release after declaration creation.")

                        compare_releases = dict(DeepDiff(
                            GlobalClassTenderPeriodEndAuction.actual_ms_release,
                            GlobalClassCreateDeclareNonConflict.actual_ms_release))

                        new_value_for_release_id = GlobalClassCreateDeclareNonConflict.actual_ms_release[
                                                       'releases'][0]['id'][29:42]
                        old_value_for_release_id = GlobalClassTenderPeriodEndAuction.actual_ms_release[
                                                       'releases'][0]['id'][29:42]

                        if n == 0:
                            new_responder_identifier_from_payload = GlobalClassUpdateDeclareNonConflict.payload[
                                'requirementResponse']['responder']['identifier']
                            new_responder_documents_from_payload = GlobalClassUpdateDeclareNonConflict.payload[
                                'requirementResponse']['responder']['businessFunctions'][0]['documents']
                            iterable_item_added_object = {
                                f"root['releases'][0]['parties'][3]['persones'][{n + 1}]": {
                                    'id': f"{new_responder_identifier_from_payload['scheme']}-"
                                          f"{new_responder_identifier_from_payload['id']}",
                                    'title': GlobalClassCreateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['title'],
                                    'name': GlobalClassUpdateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['name'],
                                    'identifier': {
                                        'scheme': new_responder_identifier_from_payload['scheme'],
                                        'id': new_responder_identifier_from_payload['id'],
                                        'uri': new_responder_identifier_from_payload['uri']
                                    },
                                    'businessFunctions': [{
                                        'id': GlobalClassUpdateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['id'],
                                        'type': GlobalClassUpdateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['type'],
                                        'jobTitle': GlobalClassCreateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['jobTitle'],
                                        'period': {
                                            'startDate': GlobalClassUpdateDeclareNonConflict.payload[
                                                'requirementResponse']['responder']['businessFunctions'][0][
                                                'period']['startDate']
                                        },
                                        'documents': [{
                                            'id': new_responder_documents_from_payload[0]['id'],
                                            'documentType': new_responder_documents_from_payload[0]['documentType'],
                                            'title': new_responder_documents_from_payload[0]['title'],
                                            'description': new_responder_documents_from_payload[0]['description'],
                                            'url': f"{GlobalClassMetadata.metadata_document_url}/"
                                                   f"{new_responder_documents_from_payload[0]['id']}",
                                            'datePublished': GlobalClassCreateCnOnPn.feed_point_message[
                                                'data']['operationDate']
                                        }]
                                    }]
                                }
                            }

                            expected_result = {
                                "values_changed": {
                                    "root['releases'][0]['id']": {
                                        "new_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{new_value_for_release_id}",
                                        "old_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{old_value_for_release_id}"
                                    },
                                    "root['releases'][0]['date']": {
                                        "new_value":
                                            GlobalClassUpdateDeclareNonConflict.feed_point_message['data'][
                                                'operationDate'],
                                        "old_value":
                                            GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['date']
                                    }
                                },
                                "iterable_item_added": iterable_item_added_object
                            }

                            GlobalClassUpdateDeclareNonConflict.previous_value_of_iterable_item_object = \
                                copy.deepcopy(expected_result['iterable_item_added'])

                        else:
                            new_responder_identifier_from_payload = GlobalClassUpdateDeclareNonConflict.payload[
                                'requirementResponse']['responder']['identifier']
                            new_responder_documents_from_payload = GlobalClassUpdateDeclareNonConflict.payload[
                                'requirementResponse']['responder']['businessFunctions'][0]['documents']
                            iterable_item_added_object = {
                                f"root['releases'][0]['parties'][3]['persones'][{n + 1}]": {
                                    'id': f"{new_responder_identifier_from_payload['scheme']}-"
                                          f"{new_responder_identifier_from_payload['id']}",
                                    'title': GlobalClassCreateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['title'],
                                    'name': GlobalClassUpdateDeclareNonConflict.payload[
                                        'requirementResponse']['responder']['name'],
                                    'identifier': {
                                        'scheme': new_responder_identifier_from_payload['scheme'],
                                        'id': new_responder_identifier_from_payload['id'],
                                        'uri': new_responder_identifier_from_payload['uri']
                                    },
                                    'businessFunctions': [{
                                        'id': GlobalClassUpdateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['id'],
                                        'type': GlobalClassUpdateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['type'],
                                        'jobTitle': GlobalClassCreateDeclareNonConflict.payload[
                                            'requirementResponse']['responder']['businessFunctions'][0]['jobTitle'],
                                        'period': {
                                            'startDate': GlobalClassUpdateDeclareNonConflict.payload[
                                                'requirementResponse']['responder']['businessFunctions'][0][
                                                'period']['startDate']
                                        },
                                        'documents': [{
                                            'id': new_responder_documents_from_payload[0]['id'],
                                            'documentType': new_responder_documents_from_payload[0]['documentType'],
                                            'title': new_responder_documents_from_payload[0]['title'],
                                            'description': new_responder_documents_from_payload[0]['description'],
                                            'url': f"{GlobalClassMetadata.metadata_document_url}/"
                                                   f"{new_responder_documents_from_payload[0]['id']}",
                                            'datePublished': GlobalClassCreateCnOnPn.feed_point_message[
                                                'data']['operationDate']
                                        }]
                                    }]
                                }
                            }

                            iterable_item_added_object.update(
                                GlobalClassUpdateDeclareNonConflict.previous_value_of_iterable_item_object)

                            expected_result = {
                                "values_changed": {
                                    "root['releases'][0]['id']": {
                                        "new_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{new_value_for_release_id}",
                                        "old_value":
                                            f"{GlobalClassCreatePn.pn_ocid}-{old_value_for_release_id}"
                                    },
                                    "root['releases'][0]['date']": {
                                        "new_value":
                                            GlobalClassUpdateDeclareNonConflict.feed_point_message['data'][
                                                'operationDate'],
                                        "old_value":
                                            GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['date']
                                    }
                                },
                                "iterable_item_added": iterable_item_added_object
                            }

                            GlobalClassUpdateDeclareNonConflict.previous_value_of_iterable_item_object = \
                                copy.deepcopy(expected_result['iterable_item_added'])

                        with allure.step('Compare actual MS release and expected MS release'):
                            allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                            allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                            assert expected_result == compare_releases
                        n += 1
        try:
            """
            Rollback specific value into submission.rules
            """
            GlobalClassMetadata.database.set_min_bids_from_submission_rules(
                value=min_bids_from_submission_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                          f"Step: Rollback specific value into submission.rules.\n" \
                          f"Message: Impossible to rollback specific value into submission.rules.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into submission.rules.")
        try:
            """
            Rollback specific value into evaluation.rules
            """
            GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                value=min_bids_from_evaluation_rules,
                country=GlobalClassMetadata.country,
                pmd=GlobalClassMetadata.pmd,
                operation_type='all',
                parameter='minBids'
            )
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                          f"Step: Rollback specific value into evaluation.rules.\n" \
                          f"Message: Impossible to rollback specific value into evaluation.rules\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to rollback specific value into evaluation.rules")

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

                GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid)

                GlobalClassMetadata.database.declaration_cleanup_table_of_services(
                    pn_ocid=GlobalClassCreatePn.pn_ocid,
                    ev_id=GlobalClassCreateCnOnPn.ev_id)

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

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[0][
                        'X-OPERATION-ID'])

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassCreateDeclareNonConflict.feed_point_message[
                        'X-OPERATION-ID'])

                GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                    operation_id=GlobalClassUpdateDeclareNonConflict.feed_point_message[
                        'X-OPERATION-ID'])
            else:
                with allure.step('# Steps from Casandra DataBase'):
                    database = GlobalClassMetadata.database
                    steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                        operation_id=GlobalClassCreateDeclareNonConflict.operation_id)
                    allure.attach(steps, "Cassandra DataBase: steps of process")

        except ValueError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_test.py -> \n" \
                          f"Class = TestDeclareNonConflictInterest -> \n" \
                          f"Method = test_check_result_of_sending_the_request_five -> \n" \
                          f"Step:Clean up database.\n" \
                          f"Message: Impossible to cLean up the database.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise ValueError("Can not return BPE operation step.")
