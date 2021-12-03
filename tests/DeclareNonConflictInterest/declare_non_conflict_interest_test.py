import copy
import datetime
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn, GlobalClassCreateFirstBid, GlobalClassTenderPeriodEndAuction, \
    GlobalClassCreateDeclareNonConflict
from tests.utils.PayloadModel.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.DeclareNonConflictInterest.declare_non_conflict_interest_prepared_payload import \
    DeclarePreparePayload
from tests.utils.PayloadModel.EI.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.FS.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.PN.pn_prepared_payload import PnPreparePayload
from tests.utils.PayloadModel.SubmitBid.bid_prepared_payload import BidPreparePayload
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions import get_project_root, time_bot
from tests.utils.kafka_message import KafkaMessage
from tests.utils.my_requests import Requests
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Awarding')
@allure.suite('Declare non conflict interest')
@allure.sub_suite('BPE: ')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1Q9MdmSbP88PQ18Jx28qXT_'
                     'akIPQ1uoUgnBg3fg8Ry8A/edit#gid=1095206362',
                 name='Google sheets: Declare non conflict interest.')
class TestDeclareNonConflictInterest:
    def test_setup(self, environment, country, language, pmd, cassandra_username, cassandra_password):
        """
        Get 'country', 'language', 'cassandra_username', 'cassandra_password', 'environment' parameters
        from test run command.
        Then choose BPE host.
        Then choose host for Database connection.
        """
        GlobalClassMetadata.country = country
        GlobalClassMetadata.language = language
        GlobalClassMetadata.pmd = pmd
        GlobalClassMetadata.cassandra_username = cassandra_username
        GlobalClassMetadata.cassandra_password = cassandra_password
        GlobalClassMetadata.environment = environment
        GlobalClassMetadata.hosts = Environment().choose_environment(GlobalClassMetadata.environment)
        GlobalClassMetadata.host_for_bpe = GlobalClassMetadata.hosts[1]
        GlobalClassMetadata.host_for_services = GlobalClassMetadata.hosts[2]
        GlobalClassMetadata.cassandra_cluster = GlobalClassMetadata.hosts[0]
        GlobalClassMetadata.database = CassandraSession(
            cassandra_username=GlobalClassMetadata.cassandra_username,
            cassandra_password=GlobalClassMetadata.cassandra_password,
            cassandra_cluster=GlobalClassMetadata.cassandra_cluster)

        if environment == "dev":
            self.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"

        elif environment == "sandbox":
            self.metadata_document_url = "http://storage.eprocurement.systems/get"

    @allure.title("Проверить подачу декларации персоной PE, которая существует в БД без изменений (полная модель)\n"
                  "------------------------------------------------\n"
                  "EI: full data model with items array;\n"
                  "FS: full data model, own money;\n"
                  "PN: full data model, 1 lots, 1 items;\n"
                  "CnOnPn: full data model with auction, 1 lots, 1 items, criteria, conversions;\n"
                  "First Bid: full data model with 2 tenderers, in relation to the first lot.\n"
                  )
    def test_check_result_of_sending_the_request_one(self):
        with allure.step('# 1. Authorization platform one: create EI'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
        with allure.step('# 2. Send request for create EI'):
            """
            Send api request to BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model(quantity_of_tender_item_object=2)
            Requests().create_ei(
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
        with allure.step('# 3. Authorization platform one: create FS'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFs.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFs.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
        with allure.step('# 4. Send request for create FS'):
            """
            Send api request to BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload = copy.deepcopy(FsPreparePayload())
            GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
            Requests().create_fs(
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
        with allure.step('# 5. Authorization platform one: create PN'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreatePn.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreatePn.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)

        with allure.step('# 6. Send request for create PN'):
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

            Requests().create_pn(
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
        with allure.step('# 8. Send request for create CnOnPn'):
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

            Requests().create_cnonpn(
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

            GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
                url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreateCnOnPn.ev_id}").json()

            GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
                url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                    f"{GlobalClassCreatePn.pn_ocid}").json()

        with allure.step('# 9. Authorization platform one: create first Bid'):
            """
            Tender platform authorization for create first bid.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)

        with allure.step('# 10. Send request for create first Bid'):
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
                              f"File = tender_period_end_auction_test.py -> \n" \
                              f"Class = TenderPeriodENdAuction -> \n" \
                              f"Method = test_check_result_of_sending_the_request_three -> \n" \
                              f"Step: Send request for create first Bid.\n" \
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
                              f"File = tender_period_end_auction_test.py -> \n" \
                              f"Class = TenderPeriodENdAuction -> \n" \
                              f"Method = test_check_result_of_sending_the_request_three -> \n" \
                              f"Step: Send request for create first Bid.\n" \
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

            Requests().create_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateFirstBid.access_token,
                x_operation_id=GlobalClassCreateFirstBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateFirstBid.payload
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
        step_number = 0
        for x in range(len(requirements_list)):
            for y in range(len(tenderers_list)):
                with allure.step(f'# 1{step_number}-{y}.Authorization platform one: create declare '
                                 f'non conflict interest'):
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
                with allure.step(f'# 1{step_number}-{y}. Send request for create declare non conflict interest'):
                    """
                    Send api request to BPE host for declare non conflict interest creating.
                    Save asynchronous result of sending the request.
                    """
                    time.sleep(1)
                    declare_payload_class = copy.deepcopy(DeclarePreparePayload())
                    GlobalClassCreateDeclareNonConflict.payload = \
                        declare_payload_class.create_declare_old_person_full_data_model(
                            requirement_id=requirements_list[x],
                            tenderer_id=tenderers_list[y])

                    Requests().create_declare_non_conflict_interest(
                        host_of_request=GlobalClassMetadata.host_for_bpe,
                        access_token=GlobalClassCreateDeclareNonConflict.access_token,
                        x_operation_id=GlobalClassCreateDeclareNonConflict.operation_id,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        ev_id=GlobalClassCreateCnOnPn.ev_id,
                        payload=GlobalClassCreateDeclareNonConflict.payload,
                        award_id=GlobalClassCreateDeclareNonConflict.award_id,
                        award_token=GlobalClassCreateDeclareNonConflict.award_token
                    )
                    GlobalClassCreateDeclareNonConflict.feed_point_message = \
                        KafkaMessage(GlobalClassCreateDeclareNonConflict.operation_id).get_message_from_kafka()
                    step_number += 1

        # with allure.step('# 11. See result'):
        #     """
        #     Check the results of test case running.
        #     """
        #     with allure.step('# 11.1. Check message in feed point'):
        #         """
        #         Check the asynchronous_result_of_sending_the_request.
        #         """
        #         time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])
        #         time.sleep(1)
        #         GlobalClassTenderPeriodEndAuction.feed_point_message = \
        #             KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
        #                          initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()
        #         allure.attach(str(GlobalClassTenderPeriodEndAuction.feed_point_message[0]), 'Message in feed point')
        #
        #         asynchronous_result_of_expired_tender_period_end = \
        #             KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
        #                          initiation="bpe").tender_period_end_auction_message_is_successful(
        #                 environment=GlobalClassMetadata.environment,
        #                 kafka_message=GlobalClassTenderPeriodEndAuction.feed_point_message[0],
        #                 pn_ocid=GlobalClassCreatePn.pn_ocid,
        #                 ev_id=GlobalClassCreateCnOnPn.ev_id
        #             )
        #         try:
        #             """
        #             If asynchronous_result_of_sending_the_request was False, then return process steps by
        #             operation-id.
        #             """
        #             if asynchronous_result_of_expired_tender_period_end is False:
        #                 with allure.step('# Steps from Casandra DataBase'):
        #                     steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
        #                         operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[0]['X-OPERATION-ID'])
        #                     allure.attach(steps, "Cassandra DataBase: steps of process")
        #         except ValueError:
        #             log_msg_one = f"\n{datetime.datetime.now()}\n" \
        #                           f"File = tender_period_end_auction_test.py -> \n" \
        #                           f"Class = TenderPeriodENdAuction -> \n" \
        #                           f"Method = test_check_result_of_sending_the_request_three -> \n" \
        #                           f"Step: Check message in feed point.\n" \
        #                           f"Message: Could not return BPE operation step.\n"
        #             with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
        #                 logfile.write(log_msg_one)
        #             raise ValueError("Could not return BPE operation step")
        #     with allure.step('# 11.2. Check EV release'):
        #         """
        #         Compare actual evaluation value release with expected evaluation value release model.
        #         """
        #         time.sleep(2)
        #         allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
        #                       "Actual EV release before tender period end expired")
        #
        #         GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
        #             url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
        #                 f"{GlobalClassCreateCnOnPn.ev_id}").json()
        #
        #         allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
        #                       "Actual EV release after tender period end expired")
        #
        #         compare_releases = DeepDiff(
        #             GlobalClassCreateCnOnPn.actual_ev_release,
        #             GlobalClassTenderPeriodEndAuction.actual_ev_release)
        #         dictionary_item_added_was_cleaned = \
        #             str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
        #         compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
        #         compare_releases = dict(compare_releases)
