import copy
import datetime
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn, GlobalClassCreateFirstBid, GlobalClassTenderPeriodEndNoAuction, \
    GlobalClassCreateDeclareNonConflict, GlobalClassAwardConsideration, GlobalClassCreateEvaluateAward, \
    GlobalClassProtocol
from tests.utils.PayloadModel.OpenProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.OpenProcedure.DeclareNonConflictInterest.declare_non_conflict_interest_prepared_payload import \
    DeclarePreparePayload
from tests.utils.PayloadModel.Budget.Ei.expenditure_item_payload import EiPreparePayload
from tests.utils.PayloadModel.OpenProcedure.EvaluateAward.evaluate_award_prepared_payload import EvaluateAwardPreparePayload
from tests.utils.PayloadModel.Budget.Fs.financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModel.OpenProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.PayloadModel.OpenProcedure.SubmitBid.bid_prepared_payload import BidPreparePayload
from tests.utils.ReleaseModel.OpenProcedure.Protocol.protocol_release import ProtocolRelease

from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions_collection import get_project_root, time_bot
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Awarding')
@allure.suite('EV')
@allure.sub_suite('BPE: Protocol')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1Q9MdmSbP88PQ18Jx28qXT_'
                     'akIPQ1uoUgnBg3fg8Ry8A/edit#gid=1095206362',
                 name='Google sheets: Protocol.')
class TestProtocol:
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

    @allure.title("create protocol (award.statusDetails=active) to award\n"
                  "------------------------------------------------\n"
                  "Ei: full data model with items array;\n"
                  "Fs: full data model, own money;\n"
                  "Pn: full data model, 1 lots, 1 items;\n"
                  "CnOnPn: full data model without auction, 1 lots, 1 items, criteria, conversions, "
                  "awardCriteriaDetails = automated;\n"
                  "First Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "QualificationDeclaration non conflict interest: full data model with old person.\n"
                  "Evaluate award: full data model with full documents.\n"
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
                              f"File = protocol_test.py -> \n" \
                              f"Class = TestProtocol-> \n" \
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
                              f"File = protocol_test.py-> \n" \
                              f"Class = TestProtocol-> \n" \
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

            GlobalClassTenderPeriodEndNoAuction.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()
            while "awardPeriod" not in GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']:
                GlobalClassTenderPeriodEndNoAuction.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()
            time_bot(
                expected_time=GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0][
                    'tender']['awardPeriod']['startDate'])

            GlobalClassTenderPeriodEndNoAuction.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassTenderPeriodEndNoAuction.feed_point_message = \
                KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                             initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()

            GlobalClassCreateDeclareNonConflict.award_id = \
                GlobalClassTenderPeriodEndNoAuction.feed_point_message[0]['data']['outcomes']['awards'][0]['id']
            GlobalClassCreateDeclareNonConflict.award_token = \
                GlobalClassTenderPeriodEndNoAuction.feed_point_message[0]['data']['outcomes']['awards'][0][
                    'X-TOKEN']
        step_number += 1
        requirements_list = list()
        for c in GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']['criteria']:
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
        for aw in GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['awards']:
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
                            actual_ms_release=GlobalClassTenderPeriodEndNoAuction.actual_ms_release)

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

                    GlobalClassCreateDeclareNonConflict.actual_ev_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreateCnOnPn.ev_id}").json()

                    GlobalClassCreateDeclareNonConflict.actual_ms_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_ocid}").json()

                    step_number += 1

        with allure.step(f'# {step_number}.Authorization platform one: award consideration.'):
            """
            Tender platform authorization for create declare non conflict interest.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassAwardConsideration.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassAwardConsideration.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                GlobalClassAwardConsideration.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: award consideration.'):
            """
            Send api request to BPE host for declare non conflict interest creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)

            Requests().do_award_consideration(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassAwardConsideration.access_token,
                x_operation_id=GlobalClassAwardConsideration.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                award_id=GlobalClassCreateDeclareNonConflict.award_id,
                award_token=GlobalClassCreateDeclareNonConflict.award_token,
                test_mode=True
            )
            GlobalClassAwardConsideration.feed_point_message = \
                KafkaMessage(GlobalClassAwardConsideration.operation_id).get_message_from_kafka()
            step_number += 1

        with allure.step(f'# {step_number}.Authorization platform one: evaluate award.'):
            """
            Tender platform authorization for create evaluate award.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEvaluateAward.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEvaluateAward.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                GlobalClassCreateEvaluateAward.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: evaluate award.'):
            """
            Send api request to BPE host for evaluate award creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)
            evaluate_award_payload_class = copy.deepcopy(EvaluateAwardPreparePayload())

            GlobalClassAwardConsideration.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

            GlobalClassAwardConsideration.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassCreateEvaluateAward.payload = \
                evaluate_award_payload_class.create_evaluate_award_full_data_model(
                    award_status_details="active",
                    based_stage_release=GlobalClassAwardConsideration.actual_ev_release
                )

            Requests().do_award_evaluation(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEvaluateAward.access_token,
                x_operation_id=GlobalClassCreateEvaluateAward.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                award_id=GlobalClassCreateDeclareNonConflict.award_id,
                award_token=GlobalClassCreateDeclareNonConflict.award_token,
                payload=GlobalClassCreateEvaluateAward.payload,
                test_mode=True
            )
            GlobalClassCreateEvaluateAward.feed_point_message = \
                KafkaMessage(GlobalClassCreateEvaluateAward.operation_id).get_message_from_kafka()

            GlobalClassCreateEvaluateAward.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

            GlobalClassCreateEvaluateAward.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            step_number += 1
        with allure.step(f'# {step_number}.Authorization platform one: protocol.'):
            """
            Tender platform authorization for create protocol.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassProtocol.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassProtocol.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                GlobalClassProtocol.access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request: protocol.'):
            """
            Send api request to BPE host for protocol creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)

            Requests().do_protocol(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassProtocol.access_token,
                x_operation_id=GlobalClassProtocol.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_token=GlobalClassCreatePn.pn_token,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                lot_id=GlobalClassCreateEvaluateAward.actual_ev_release['releases'][0]['tender']['lots'][0]['id'],
                test_mode=True
            )

            step_number += 1

        with allure.step(f'# {step_number}. See result.'):
            """
            Check the results of test case running.
            """
            with allure.step(f'# {step_number}.1. Check message in feed point.'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                time.sleep(1)
                GlobalClassProtocol.feed_point_message = \
                    KafkaMessage(GlobalClassProtocol.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassProtocol.feed_point_message),
                              'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassProtocol.operation_id).protocol_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassProtocol.feed_point_message,
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
                                operation_id=GlobalClassProtocol.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = protocol_test.py -> \n" \
                                  f"Class = TestProtocol-> \n" \
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
                allure.attach(str(json.dumps(GlobalClassCreateEvaluateAward.actual_ev_release)),
                              "Actual EV release award evaluation.")

                GlobalClassProtocol.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()

                allure.attach(str(json.dumps(GlobalClassProtocol.actual_ev_release)),
                              "Actual EV release protocol.")

                new_value_for_release_id = GlobalClassProtocol.actual_ev_release[
                                               'releases'][0]['id'][46:59]
                old_value_for_release_id = GlobalClassCreateEvaluateAward.actual_ev_release[
                                               'releases'][0]['id'][46:59]

                compare_releases = dict(DeepDiff(
                    GlobalClassCreateEvaluateAward.actual_ev_release,
                    GlobalClassProtocol.actual_ev_release))
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['contracts'], "
                                             "['releases'][0]['bids']['details'][0]['statusDetails']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{GlobalClassCreateCnOnPn.ev_id}-{new_value_for_release_id}",
                            "old_value":
                                f"{GlobalClassCreateCnOnPn.ev_id}-{old_value_for_release_id}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value":
                                GlobalClassProtocol.feed_point_message['data'][
                                    'operationDate'],
                            "old_value":
                                GlobalClassCreateEvaluateAward.actual_ev_release['releases'][0][
                                    'date']
                        },
                        "root['releases'][0]['tender']['lots'][0]['statusDetails']": {
                            "new_value": "awarded",
                            "old_value": "empty"
                        }
                    }
                }

                expected_award_evaluation_release_class = ProtocolRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language)

                expected_contracts_array = \
                    expected_award_evaluation_release_class.iterable_item_added_contracts_array_as_contract_project(
                        actual_ev_release=GlobalClassProtocol.actual_ev_release,
                        protocol_feed_point_message=GlobalClassProtocol.feed_point_message,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        lot_id=GlobalClassCreateEvaluateAward.actual_ev_release['releases'][0]['tender']['lots'][0][
                            'id']
                    )

                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result and \
                            GlobalClassProtocol.actual_ev_release['releases'][0][
                                'contracts'] == expected_contracts_array and \
                            GlobalClassProtocol.actual_ev_release['releases'][0]['bids']['details'][0][
                                'statusDetails'] == "valid":
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            database = GlobalClassMetadata.database
                            steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                operation_id=GlobalClassProtocol.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = protocol_test.py -> \n" \
                                  f"Class = TestProtocol -> \n" \
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

                with allure.step('Compare actual contracts array and expected contracts array.'):
                    allure.attach(str(json.dumps(GlobalClassProtocol.actual_ev_release['releases'][0]['contracts'])),
                                  "Actual contracts array.")
                    allure.attach(str(json.dumps(expected_contracts_array)),
                                  "Expected contracts array.")
                    assert GlobalClassProtocol.actual_ev_release['releases'][0]['contracts'] == expected_contracts_array

                with allure.step('Compare actual statusDetails of bid  and expected statusDetails of bid.'):
                    allure.attach(str(json.dumps(GlobalClassProtocol.actual_ev_release['releases'][0]['bids'][
                                                     'details'][0]['statusDetails'])),
                                  "Actual statusDetails of bid.")
                    allure.attach("valid", "Expected statusDetails of bid.")
                    assert GlobalClassProtocol.actual_ev_release['releases'][0]['bids'][
                               'details'][0]['statusDetails'] == "valid"

            with allure.step(f'# {step_number}.3. Check MS release.'):
                """
                Compare multistage release with expected multistage release model.
                """
                time.sleep(2)
                allure.attach(str(json.dumps(GlobalClassCreateEvaluateAward.actual_ms_release)),
                              "Actual MS release award evaluation.")

                GlobalClassProtocol.actual_ms_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()

                allure.attach(str(json.dumps(GlobalClassProtocol.actual_ms_release)),
                              "Actual MS release protocol.")

                compare_releases = DeepDiff(
                    GlobalClassCreateEvaluateAward.actual_ms_release,
                    GlobalClassProtocol.actual_ms_release)

                expected_result = {}

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
                                  f"File = protocol_test.py -> \n" \
                                  f"Class = TestProtocol -> \n" \
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
                                  f"File = protocol_test.py-> \n" \
                                  f"Class = TestProtocol -> \n" \
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

                        GlobalClassMetadata.database.award_consideration_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid,
                            ev_id=GlobalClassCreateCnOnPn.ev_id)

                        GlobalClassMetadata.database.award_evaluation_cleanup_table_of_services(
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
                            operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message[0][
                                'X-OPERATION-ID'])

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateDeclareNonConflict.feed_point_message[
                                'X-OPERATION-ID'])
                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassAwardConsideration.feed_point_message[
                                'X-OPERATION-ID'])

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEvaluateAward.feed_point_message[
                                'X-OPERATION-ID'])

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassProtocol.feed_point_message[
                                'X-OPERATION-ID'])
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            database = GlobalClassMetadata.database
                            steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                operation_id=GlobalClassAwardConsideration.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = protocol_test.py -> \n" \
                                  f"Class = TestProtocol -> \n" \
                                  f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                  f"Step:Clean up database.\n" \
                                  f"Message: Impossible to cLean up the database.\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)
                    raise ValueError("Can not return BPE operation step.")

                with allure.step('Compare actual MS release and expected MS release'):
                    allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                    allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                    assert expected_result == compare_releases

    @allure.title("create protocol (award.statusDetails=unsuccessful) to award\n"
                  "------------------------------------------------\n"
                  "Ei: full data model with items array;\n"
                  "Fs: full data model, own money;\n"
                  "Pn: full data model, 1 lots, 1 items;\n"
                  "CnOnPn: full data model without auction, 1 lots, 1 items, criteria, conversions, "
                  "awardCriteriaDetails = automated;\n"
                  "First Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  "QualificationDeclaration non conflict interest: full data model with old person.\n"
                  "Evaluate award: full data model with full documents.\n"
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
                              f"File = protocol_test.py -> \n" \
                              f"Class = TestProtocol-> \n" \
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
                              f"File = protocol_test.py-> \n" \
                              f"Class = TestProtocol-> \n" \
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

            GlobalClassTenderPeriodEndNoAuction.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()
            while "awardPeriod" not in GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']:
                GlobalClassTenderPeriodEndNoAuction.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()
            time_bot(
                expected_time=GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0][
                    'tender']['awardPeriod']['startDate'])

            GlobalClassTenderPeriodEndNoAuction.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassTenderPeriodEndNoAuction.feed_point_message = \
                KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                             initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()

            GlobalClassCreateDeclareNonConflict.award_id = \
                GlobalClassTenderPeriodEndNoAuction.feed_point_message[0]['data']['outcomes']['awards'][0]['id']
            GlobalClassCreateDeclareNonConflict.award_token = \
                GlobalClassTenderPeriodEndNoAuction.feed_point_message[0]['data']['outcomes']['awards'][0][
                    'X-TOKEN']
        step_number += 1
        requirements_list = list()
        for c in GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']['criteria']:
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
        for aw in GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['awards']:
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
                            actual_ms_release=GlobalClassTenderPeriodEndNoAuction.actual_ms_release)

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

                    GlobalClassCreateDeclareNonConflict.actual_ev_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreateCnOnPn.ev_id}").json()

                    GlobalClassCreateDeclareNonConflict.actual_ms_release = requests.get(
                        url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                            f"{GlobalClassCreatePn.pn_ocid}").json()

                    step_number += 1

        with allure.step(f'# {step_number}.Authorization platform one: award consideration.'):
            """
            Tender platform authorization for create declare non conflict interest.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassAwardConsideration.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassAwardConsideration.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                GlobalClassAwardConsideration.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: award consideration.'):
            """
            Send api request to BPE host for declare non conflict interest creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)

            Requests().do_award_consideration(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassAwardConsideration.access_token,
                x_operation_id=GlobalClassAwardConsideration.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                award_id=GlobalClassCreateDeclareNonConflict.award_id,
                award_token=GlobalClassCreateDeclareNonConflict.award_token,
                test_mode=True
            )
            GlobalClassAwardConsideration.feed_point_message = \
                KafkaMessage(GlobalClassAwardConsideration.operation_id).get_message_from_kafka()
            step_number += 1

        with allure.step(f'# {step_number}.Authorization platform one: evaluate award.'):
            """
            Tender platform authorization for create evaluate award.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEvaluateAward.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEvaluateAward.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                GlobalClassCreateEvaluateAward.access_token)
            step_number += 1
        with allure.step(f'# {step_number}. Send request: evaluate award.'):
            """
            Send api request to BPE host for evaluate award creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)
            evaluate_award_payload_class = copy.deepcopy(EvaluateAwardPreparePayload())

            GlobalClassAwardConsideration.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

            GlobalClassAwardConsideration.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            GlobalClassCreateEvaluateAward.payload = \
                evaluate_award_payload_class.create_evaluate_award_full_data_model(
                    award_status_details="unsuccessful",
                    based_stage_release=GlobalClassAwardConsideration.actual_ev_release
                )

            Requests().do_award_evaluation(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEvaluateAward.access_token,
                x_operation_id=GlobalClassCreateEvaluateAward.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                award_id=GlobalClassCreateDeclareNonConflict.award_id,
                award_token=GlobalClassCreateDeclareNonConflict.award_token,
                payload=GlobalClassCreateEvaluateAward.payload,
                test_mode=True
            )
            GlobalClassCreateEvaluateAward.feed_point_message = \
                KafkaMessage(GlobalClassCreateEvaluateAward.operation_id).get_message_from_kafka()

            GlobalClassCreateEvaluateAward.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

            GlobalClassCreateEvaluateAward.actual_ms_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

            step_number += 1
        with allure.step(f'# {step_number}.Authorization platform one: protocol.'):
            """
            Tender platform authorization for create protocol.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassProtocol.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassProtocol.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(
                GlobalClassProtocol.access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request: protocol.'):
            """
            Send api request to BPE host for protocol creating.
            Save asynchronous result of sending the request.
            """
            time.sleep(1)

            Requests().do_protocol(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassProtocol.access_token,
                x_operation_id=GlobalClassProtocol.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                pn_token=GlobalClassCreatePn.pn_token,
                tender_id=GlobalClassCreateCnOnPn.ev_id,
                lot_id=GlobalClassCreateEvaluateAward.actual_ev_release['releases'][0]['tender']['lots'][0]['id'],
                test_mode=True
            )

            step_number += 1

        with allure.step(f'# {step_number}. See result.'):
            """
            Check the results of test case running.
            """
            with allure.step(f'# {step_number}.1. Check message in feed point.'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                time.sleep(1)
                GlobalClassProtocol.feed_point_message = \
                    KafkaMessage(GlobalClassProtocol.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassProtocol.feed_point_message),
                              'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassProtocol.operation_id).protocol_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassProtocol.feed_point_message,
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
                                operation_id=GlobalClassProtocol.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = protocol_test.py -> \n" \
                                  f"Class = TestProtocol-> \n" \
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

            with allure.step(f'# {step_number}.2. Check EV release.'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                time.sleep(2)
                allure.attach(str(json.dumps(GlobalClassCreateEvaluateAward.actual_ev_release)),
                              "Actual EV release award evaluation.")

                GlobalClassProtocol.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()

                allure.attach(str(json.dumps(GlobalClassProtocol.actual_ev_release)),
                              "Actual EV release protocol.")

                new_value_for_release_id = GlobalClassProtocol.actual_ev_release[
                                               'releases'][0]['id'][46:59]
                old_value_for_release_id = GlobalClassCreateEvaluateAward.actual_ev_release[
                                               'releases'][0]['id'][46:59]

                compare_releases = dict(DeepDiff(
                    GlobalClassCreateEvaluateAward.actual_ev_release,
                    GlobalClassProtocol.actual_ev_release))
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['contracts'], "
                                             "['releases'][0]['bids']['details'][0]['statusDetails']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{GlobalClassCreateCnOnPn.ev_id}-{new_value_for_release_id}",
                            "old_value":
                                f"{GlobalClassCreateCnOnPn.ev_id}-{old_value_for_release_id}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value":
                                GlobalClassProtocol.feed_point_message['data'][
                                    'operationDate'],
                            "old_value":
                                GlobalClassCreateEvaluateAward.actual_ev_release['releases'][0][
                                    'date']
                        },
                        "root['releases'][0]['tender']['lots'][0]['statusDetails']": {
                            "new_value": "awarded",
                            "old_value": "empty"
                        }
                    }
                }

                expected_award_evaluation_release_class = ProtocolRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language)

                expected_contracts_array = \
                    expected_award_evaluation_release_class.iterable_item_added_contracts_array_as_unsuccessful(
                        actual_ev_release=GlobalClassProtocol.actual_ev_release,
                        protocol_feed_point_message=GlobalClassProtocol.feed_point_message,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        lot_id=GlobalClassCreateEvaluateAward.actual_ev_release['releases'][0]['tender']['lots'][0][
                            'id']
                    )

                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result and \
                            GlobalClassProtocol.actual_ev_release['releases'][0][
                                'contracts'] == expected_contracts_array and \
                            GlobalClassProtocol.actual_ev_release['releases'][0]['bids']['details'][0][
                                'statusDetails'] == "disqualified":
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            database = GlobalClassMetadata.database
                            steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                operation_id=GlobalClassProtocol.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = protocol_test.py -> \n" \
                                  f"Class = TestProtocol -> \n" \
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

                with allure.step('Compare actual contracts array and expected contracts array.'):
                    allure.attach(str(json.dumps(GlobalClassProtocol.actual_ev_release['releases'][0]['contracts'])),
                                  "Actual contracts array.")
                    allure.attach(str(json.dumps(expected_contracts_array)),
                                  "Expected contracts array.")
                    assert GlobalClassProtocol.actual_ev_release['releases'][0]['contracts'] == expected_contracts_array

                with allure.step('Compare actual statusDetails of bid  and expected statusDetails of bid.'):
                    allure.attach(str(json.dumps(GlobalClassProtocol.actual_ev_release['releases'][0]['bids'][
                                                     'details'][0]['statusDetails'])),
                                  "Actual statusDetails of bid.")
                    allure.attach("valid", "Expected statusDetails of bid.")
                    assert GlobalClassProtocol.actual_ev_release['releases'][0]['bids'][
                               'details'][0]['statusDetails'] == "disqualified"

            with allure.step(f'# {step_number}.3. Check MS release.'):
                """
                Compare multistage release with expected multistage release model.
                """
                time.sleep(2)
                allure.attach(str(json.dumps(GlobalClassCreateEvaluateAward.actual_ms_release)),
                              "Actual MS release award evaluation.")

                GlobalClassProtocol.actual_ms_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()

                allure.attach(str(json.dumps(GlobalClassProtocol.actual_ms_release)),
                              "Actual MS release protocol.")

                compare_releases = DeepDiff(
                    GlobalClassCreateEvaluateAward.actual_ms_release,
                    GlobalClassProtocol.actual_ms_release)

                expected_result = {}

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
                                  f"File = protocol_test.py -> \n" \
                                  f"Class = TestProtocol -> \n" \
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
                                  f"File = protocol_test.py-> \n" \
                                  f"Class = TestProtocol -> \n" \
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

                        GlobalClassMetadata.database.award_consideration_cleanup_table_of_services(
                            pn_ocid=GlobalClassCreatePn.pn_ocid,
                            ev_id=GlobalClassCreateCnOnPn.ev_id)

                        GlobalClassMetadata.database.award_evaluation_cleanup_table_of_services(
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
                            operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message[0][
                                'X-OPERATION-ID'])

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateDeclareNonConflict.feed_point_message[
                                'X-OPERATION-ID'])
                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassAwardConsideration.feed_point_message[
                                'X-OPERATION-ID'])

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassCreateEvaluateAward.feed_point_message[
                                'X-OPERATION-ID'])

                        GlobalClassMetadata.database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=GlobalClassProtocol.feed_point_message[
                                'X-OPERATION-ID'])
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            database = GlobalClassMetadata.database
                            steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                operation_id=GlobalClassAwardConsideration.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = protocol_test.py -> \n" \
                                  f"Class = TestProtocol -> \n" \
                                  f"Method = test_check_result_of_sending_the_request_two -> \n" \
                                  f"Step:Clean up database.\n" \
                                  f"Message: Impossible to cLean up the database.\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)
                    raise ValueError("Can not return BPE operation step.")

                with allure.step('Compare actual MS release and expected MS release'):
                    allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                    allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                    assert expected_result == compare_releases
