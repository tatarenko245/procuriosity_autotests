import copy
import datetime
import json
import time
import allure
import requests
from deepdiff import DeepDiff
from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn, GlobalClassTenderPeriodEndAuction, GlobalClassCreateFirstBid, GlobalClassCreateSecondBid
from tests.utils.PayloadModel.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.EI.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.FS.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.PN.pn_prepared_payload import PnPreparePayload
from tests.utils.PayloadModel.SubmitBid.bid_prepared_payload import BidPreparePayload
from tests.utils.ReleaseModel.tenderPeriodEndAuction.tender_period_end_auction_release import \
    TenderPeriodExpectedChanges
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions import time_bot, is_it_uuid, compare_actual_result_and_expected_result, get_project_root
from tests.utils.kafka_message import KafkaMessage
from tests.utils.my_requests import Requests
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Awarding')
@allure.suite('Tender period end auction')
@allure.sub_suite('BPE: ')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=270281171',
                 name='Google sheets: Tender period end auction')
class TestTenderPeriodEndAuction:
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

    @allure.title("Check message from Kafka topic, EV, MS releases, on the flow:\n"
                  "´Is tenderPeriodExpired -> True ->\n "
                  "Are there bids for opening? -> False ->\n "
                  "Send message to platform\n´"
                  "------------------------------------------------------------------------------------\n"
                  "EI: full data model with items array;\n "
                  "FS: full data model, own money;\n"
                  "PN: full data model, 2 lots, 2 items;\n"
                  "CnOnPn: full data model with auction, 2 lots, 2 items, criteria, conversions.\n"
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
        with allure.step('# 2. Send request to create EI'):
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
        with allure.step('# 4. Send request to create FS'):
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

        with allure.step('# 6. Send request to create PN'):
            """
            Send api request to BPE host for planning notice creating.
            Save asynchronous result of sending the request.
            Save pn_ocid and pn_token.
            """
            time.sleep(1)
            pn_payload = copy.deepcopy(PnPreparePayload())
            GlobalClassCreatePn.payload = \
                pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
                    quantity_of_lot_object=2,
                    quantity_of_item_object=2)

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
        with allure.step('# 8. Send request to create CnOnPn'):
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
                    quantity_of_lots_object=2,
                    quantity_of_items_object=2,
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

        with allure.step('# 9. See result'):
            """
            Check the results of test case running.
            """
            with allure.step('# 9.1. Check message in feed point'):
                """
                Check the asynchronous_result.
                """
                time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])
                time.sleep(1)
                GlobalClassTenderPeriodEndAuction.feed_point_message = \
                    KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                                 initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()
                allure.attach(str(GlobalClassTenderPeriodEndAuction.feed_point_message), 'Message from feed point')

                check_the_asynchronous_result_of_expired_tender_period_end = \
                    KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                                 initiation="bpe").tender_period_end_auction_message_is_successful(
                        environment=GlobalClassMetadata.environment,
                        kafka_message=GlobalClassTenderPeriodEndAuction.feed_point_message,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        ev_id=GlobalClassCreateCnOnPn.ev_id
                    )
                try:
                    """
                    If check_the_asynchronous_result_of_expired_tender_period_end is False,
                     then return process steps by operation-id.
                    """
                    if check_the_asynchronous_result_of_expired_tender_period_end is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = tender_period_end_auction_test.py -> \n" \
                                  f"Class = TenderPeriodENdAuction -> \n" \
                                  f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                  f"Step: Check message in feed point.\n" \
                                  f"Message: Could not return BPE operation step.\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)
                    raise ValueError("Could not return BPE operation step")
            with allure.step('# 9.2. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
                              "Actual EV release before tender period end expired")

                GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()

                allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
                              "Actual EV release after tender period end expired")

                compare_releases = DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, GlobalClassTenderPeriodEndAuction.actual_ev_release)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_releases_id = \
                    f"{GlobalClassCreateCnOnPn.ev_id}-" \
                    f"{GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['id'][46:59]}"
                expected_result = {
                    "dictionary_item_added": "['releases'][0]['awards']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": expected_releases_id,
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassTenderPeriodEndAuction.feed_point_message['data'][
                                'operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            "new_value": "tenderCancellation",
                            "old_value": "tender"
                        },
                        "root['releases'][0]['tender']['status']": {
                            "new_value": "unsuccessful",
                            "old_value": "active"
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "empty",
                            "old_value": "clarification"
                        },
                        "root['releases'][0]['tender']['lots'][0]['status']": {
                            "new_value": "unsuccessful",
                            "old_value": "active"
                        },
                        "root['releases'][0]['tender']['lots'][1]['status']": {
                            "new_value": "unsuccessful",
                            "old_value": "active"
                        }
                    }
                }
                try:
                    """
                    Check id of awards into actual EV release.
                    """
                    for a in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
                        for a_1 in a:
                            if a_1 == "id":
                                check_awards_id_first = is_it_uuid(
                                    uuid_to_test=a['id'],
                                    version=4
                                )
                                if check_awards_id_first is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = tender_period_end_auction_test.py -> \n" \
                                                  f"Class = TenderPeriodENdAuction -> \n" \
                                                  f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                                  f"Step: Check EV release.\n" \
                                                  f"Message: {a['id']} must be uuid version 4.\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    raise Exception(
                                        f"{a['id']} must be uuid version 4.")
                except Exception:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = tender_period_end_auction_test.py -> \n" \
                                  f"Class = TenderPeriodENdAuction -> \n" \
                                  f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                  f"Step: Check EV release.\n" \
                                  f"Message: Could not return BPE operation step.\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)
                    raise Exception("Impossible to check id of awards.")
                try:
                    """
                    Prepare expected awards array.
                    """
                    expected_awards_array = TenderPeriodExpectedChanges(
                        environment=GlobalClassMetadata.environment,
                        language=GlobalClassMetadata.language).prepare_unsuccessful_awards_array()
                except Exception:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = tender_period_end_auction_test.py -> \n" \
                                  f"Class = TenderPeriodENdAuction -> \n" \
                                  f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                  f"Step: Check EV release.\n" \
                                  f"Message: Impossible to prepare expected awards array.\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)
                    raise Exception("Impossible to prepare expected awards array.")
                try:
                    """
                        If result of comparing releases is incorrect , then return process steps by operation-id.
                        """
                    if compare_releases == expected_result and expected_awards_array == \
                            GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = tender_period_end_auction_test.py -> \n" \
                                  f"Class = TenderPeriodENdAuction -> \n" \
                                  f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                  f"Step: Check EV release.\n" \
                                  f"Message: Could not return BPE operation step.\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)
                    raise ValueError("Could not return BPE operation step")

                if expected_result != compare_releases:
                    allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                    allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                    assert str(compare_actual_result_and_expected_result(
                        expected_result=expected_result,
                        actual_result=compare_releases
                    )) == str(True)
                elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'] != \
                        expected_awards_array:
                    allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
                                                     'releases'][0]['awards'])), "Actual awards array")
                    allure.attach(str(json.dumps(expected_awards_array)), "Expected awards array")
                    assert str(compare_actual_result_and_expected_result(
                        expected_result=expected_awards_array,
                        actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']
                    )) == str(True)

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_awards_array,
                    actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']
                )) == str(True)
            with allure.step('# 9.3. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
                              "Actual MS release before tender period end expired")

                GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
                    url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()

                allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
                              "Actual MS release after tender period end expired")

                compare_releases = dict(DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ms_release,
                    GlobalClassTenderPeriodEndAuction.actual_ms_release))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{GlobalClassCreatePn.pn_ocid}-"
                                f"{GlobalClassTenderPeriodEndAuction.actual_ms_release['releases'][0]['id'][29:42]}",
                            "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassTenderPeriodEndAuction.feed_point_message['data'][
                                'operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['status']": {
                            "new_value": "unsuccessful",
                            "old_value": "active"
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "empty",
                            "old_value": "evaluation"
                        }
                    }
                }
                try:
                    """
                    If test case was passed, then cLean up the database.
                    If test case was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

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

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateFs.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreatePn.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateCnOnPn.operation_id)

                        GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
                            operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = \
                                GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id_from_orchestrator(
                                    operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[
                                        'X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = tender_period_end_auction_test.py -> \n" \
                                  f"Class = TenderPeriodENdAuction -> \n" \
                                  f"Method = test_check_result_of_sending_the_request_one -> \n" \
                                  f"Step: Check EV release.\n" \
                                  f"Message: Could not return BPE operation step.\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)
                    raise ValueError("Could not return BPE operation step")

                if expected_result != compare_releases:
                    allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
                    allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
                    assert str(compare_actual_result_and_expected_result(
                        expected_result=expected_result,
                        actual_result=compare_releases
                    )) == str(True)

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    # @allure.title("Баг https://ustudio.atlassian.net/browse/ES-6888 "
    #               "------------------------------------------------"
    #               "Check message from Kafka topic, EV, MS releases, "
    #               "on the flow ´Is tenderPeriodExpired -> True -> Are there bids for opening? -> True -> "
    #               "Are there unsuccessful lots? -> True -> Is tender unsuccessful? -> False -> "
    #               "Is auction started? -> False -> Is there award criteria -> True -> Stage -> EV -> "
    #               "Is operationType=TenderPeriodEndAuction -> False -> Send message to platform´"
    #               "------------------------------------------------------------------------------------"
    #               "EI: full data model with items array;"
    #               "FS: full data model, own money;"
    #               "PN: full data model, 2 lots, 2 items;"
    #               "CnOnPn: full data model with auction, 2 lots, 2 items, criteria, conversions;"
    #               "First Bid: full data model with 2 tenderers, in relation to the first lot."
    #               )
    # def test_check_result_of_sending_the_request_two(self):
    #     with allure.step('# 1. Authorization platform one: create EI'):
    #         """
    #         Tender platform authorization for create expenditure item process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateEi.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateEi.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
    #     with allure.step('# 2. Send request to create EI'):
    #         """
    #         Send api request to BPE host for expenditure item creation.
    #         And save in variable ei_ocid.
    #         """
    #         ei_payload = copy.deepcopy(EiPreparePayload())
    #         GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model(quantity_of_tender_item_object=2)
    #         Requests().create_ei(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateEi.access_token,
    #             x_operation_id=GlobalClassCreateEi.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             payload=GlobalClassCreateEi.payload
    #         )
    #         GlobalClassCreateEi.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateEi.ei_ocid = \
    #             GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']
    #
    #         GlobalClassCreateEi.actual_ei_release = requests.get(
    #             url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateEi.ei_ocid}").json()
    #     with allure.step('# 3. Authorization platform one: create FS'):
    #         """
    #         Tender platform authorization for create financial source process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFs.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFs.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
    #     with allure.step('# 4. Send request to create FS'):
    #         """
    #         Send api request to BPE host for financial source creating.
    #         And save in variable fs_id and fs_token.
    #         """
    #         time.sleep(1)
    #         fs_payload = copy.deepcopy(FsPreparePayload())
    #         GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
    #         Requests().create_fs(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFs.access_token,
    #             x_operation_id=GlobalClassCreateFs.operation_id,
    #             ei_ocid=GlobalClassCreateEi.ei_ocid,
    #             payload=GlobalClassCreateFs.payload
    #         )
    #         GlobalClassCreateFs.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFs.fs_id = \
    #             GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']
    #
    #         GlobalClassCreateFs.actual_fs_release = requests.get(
    #             url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateFs.fs_id}").json()
    #     with allure.step('# 5. Authorization platform one: create PN'):
    #         """
    #         Tender platform authorization for create planning notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreatePn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreatePn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)
    #
    #     with allure.step('# 6. Send request to create PN'):
    #         """
    #         Send api request to BPE host for planning notice creating.
    #         Save asynchronous result of sending the request.
    #         Save pn_ocid and pn_token.
    #         """
    #         time.sleep(1)
    #         pn_payload = copy.deepcopy(PnPreparePayload())
    #         GlobalClassCreatePn.payload = \
    #             pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
    #                 quantity_of_lot_object=2,
    #                 quantity_of_item_object=2)
    #
    #         Requests().create_pn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreatePn.access_token,
    #             x_operation_id=GlobalClassCreatePn.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             pmd=GlobalClassMetadata.pmd,
    #             payload=GlobalClassCreatePn.payload
    #         )
    #         GlobalClassCreatePn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreatePn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreatePn.pn_ocid = \
    #             GlobalClassCreatePn.feed_point_message['data']['ocid']
    #
    #         GlobalClassCreatePn.pn_id = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['id']
    #
    #         GlobalClassCreatePn.pn_token = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
    #
    #         GlobalClassCreatePn.actual_pn_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_id}").json()
    #
    #         GlobalClassCreatePn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #     with allure.step('# 7. Authorization platform one: create CnOnPn'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
    #     with allure.step('# 8. Send request to create CnOnPn'):
    #         """
    #         Send api request to BPE host for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         time.sleep(1)
    #         cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
    #         GlobalClassCreateCnOnPn.payload = \
    #             cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
    #                 enquiry_interval=121,
    #                 tender_interval=300,
    #                 quantity_of_lots_object=2,
    #                 quantity_of_items_object=2,
    #                 need_to_set_permanent_id_for_lots_array=True,
    #                 need_to_set_permanent_id_for_items_array=True,
    #                 need_to_set_permanent_id_for_documents_array=True,
    #                 based_stage_release=GlobalClassCreatePn.actual_pn_release
    #             )
    #
    #         Requests().create_cnonpn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateCnOnPn.access_token,
    #             x_operation_id=GlobalClassCreateCnOnPn.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             pn_id=GlobalClassCreatePn.pn_id,
    #             pn_token=GlobalClassCreatePn.pn_token,
    #             payload=GlobalClassCreateCnOnPn.payload
    #         )
    #
    #         GlobalClassCreateCnOnPn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateCnOnPn.ev_id = \
    #             GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']
    #
    #         GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
    #             url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #         GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #     with allure.step('# 9. Authorization platform one: create first Bid'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
    #
    #     with allure.step('# 10. Send request to create first Bid'):
    #         """
    #         Send api request on BPE hoto for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         try:
    #             """
    #             Set specific value into submission.rules for this testcase
    #             """
    #             min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_submission_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into submission.rules")
    #         try:
    #             """
    #             Set specific value into evaluation.rules for this testcase
    #             """
    #             min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_evaluation_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into evaluation.rules")
    #
    #         time.sleep(1)
    #         time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
    #         bid_payload_class = copy.deepcopy(BidPreparePayload())
    #         GlobalClassCreateFirstBid.payload = \
    #             bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
    #                 based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)
    #
    #         Requests().create_bid(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFirstBid.access_token,
    #             x_operation_id=GlobalClassCreateFirstBid.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             ev_id=GlobalClassCreateCnOnPn.ev_id,
    #             payload=GlobalClassCreateFirstBid.payload
    #         )
    #         GlobalClassCreateFirstBid.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFirstBid.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFirstBid.bid_id = GlobalClassCreateFirstBid.feed_point_message['data']['outcomes'][
    #             'bids'][0]['id']
    #
    #     with allure.step('# 11. See result'):
    #         """
    #         Check the results of test case running.
    #         """
    #         with allure.step('# 11.1. Check message in feed point'):
    #             """
    #             Check the asynchronous_result_of_sending_the_request.
    #             """
    #             time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])
    #             time.sleep(1)
    #             GlobalClassTenderPeriodEndAuction.feed_point_message = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()
    #             allure.attach(str(GlobalClassTenderPeriodEndAuction.feed_point_message), 'Message in feed point')
    #
    #             asynchronous_result_of_expired_tender_period_end = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").tender_period_end_auction_message_is_successful(
    #                     environment=GlobalClassMetadata.environment,
    #                     kafka_message=GlobalClassTenderPeriodEndAuction.feed_point_message,
    #                     pn_ocid=GlobalClassCreatePn.pn_ocid,
    #                     ev_id=GlobalClassCreateCnOnPn.ev_id
    #                 )
    #
    #             try:
    #                 """
    #                 If asynchronous_result_of_sending_the_request was False, then return process steps by
    #                 operation-id.
    #                 """
    #                 if asynchronous_result_of_expired_tender_period_end is False:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #         with allure.step('# 11.2. Check EV release'):
    #             """
    #             Compare actual evaluation value release with expected evaluation value release model.
    #             """
    #             time.sleep(2)
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
    #                           "Actual EV release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
    #                 url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
    #                           "Actual EV release after tender period end expired")
    #             compare_releases = DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ev_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ev_release)
    #             dictionary_item_added_was_cleaned = \
    #                 str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
    #             compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
    #             compare_releases = dict(compare_releases)
    #
    #             expected_result = {
    #                 "dictionary_item_added": "['releases'][0]['parties'], "
    #                                          "['releases'][0]['awards'], "
    #                                          "['releases'][0]['bids'], "
    #                                          "['releases'][0]['tender']['criteria'], "
    #                                          "['releases'][0]['tender']['awardPeriod']",
    #                 "values_changed": {
    #                     "root['releases'][0]['id']": {
    #                         "new_value":
    #                             f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                             f"{GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['id'][46:59]}",
    #                         "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                                      f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
    #                     },
    #                     "root['releases'][0]['date']": {
    #                         "new_value": GlobalClassTenderPeriodEndAuction.feed_point_message['data'][
    #                             'operationDate'],
    #                         "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
    #                     },
    #                     "root['releases'][0]['tag'][0]": {
    #                         'new_value': 'award',
    #                         'old_value': 'tender'
    #                     },
    #                     "root['releases'][0]['tender']['statusDetails']": {
    #                         'new_value': 'awarding',
    #                         'old_value': 'clarification'
    #                     }
    #                 }
    #             }
    #
    #             try:
    #                 """
    #                 Prepare expected awardPeriod object.
    #                 """
    #                 final_expected_award_period_object = {
    #                     "startDate": GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                         'tenderPeriod']['endDate']
    #                 }
    #             except Exception:
    #                 raise Exception("Prepare expected awardPeriod object.")
    #
    #             try:
    #                 """
    #                 Prepare expected parties array
    #                 """
    #                 final_expected_parties_array = list()
    #                 list_of_parties_id_from_release = list()
    #                 for i in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['parties']:
    #                     for i_1 in i:
    #                         if i_1 == "id":
    #                             list_of_parties_id_from_release.append(i['id'])
    #
    #                 expected_parties_array_first = TenderPeriodExpectedChanges(
    #                     environment=GlobalClassMetadata.environment,
    #                     language=GlobalClassMetadata.language
    #                 ).prepare_array_of_parties_mapper_for_successful_tender(
    #                     bid_payload=GlobalClassCreateFirstBid.payload)
    #
    #                 expected_parties_array = expected_parties_array_first
    #                 quantity_of_object_into_expected_parties_array = len(expected_parties_array)
    #                 quantity_of_object_into_list_of_parties_id_from_release = len(list_of_parties_id_from_release)
    #                 if quantity_of_object_into_expected_parties_array == \
    #                         quantity_of_object_into_list_of_parties_id_from_release:
    #                     for q in range(quantity_of_object_into_list_of_parties_id_from_release):
    #                         for q_1 in range(quantity_of_object_into_expected_parties_array):
    #                             if expected_parties_array[q_1]['id'] == list_of_parties_id_from_release[q]:
    #                                 final_expected_parties_array.append(expected_parties_array[q_1]['value'])
    #                 else:
    #                     raise Exception("Error: quantity_of_object_into_expected_parties_array != "
    #                                     "quantity_of_object_into_list_of_parties_id_from_release")
    #                 for pa in range(quantity_of_object_into_expected_parties_array):
    #                     try:
    #                         """
    #                         Check how many quantity of object into final_expected_parties_array['persones'].
    #                         """
    #                         list_of_final_party_persones_id = list()
    #                         for i in final_expected_parties_array[pa]['persones']:
    #                             for i_1 in i:
    #                                 if i_1 == "identifier":
    #                                     for i_2 in i['identifier']:
    #                                         if i_2 == "id":
    #                                             list_of_final_party_persones_id.append(i_2)
    #                         quantity_of_persones_into_final_expected_parties_array = \
    #                             len(list_of_final_party_persones_id)
    #                     except Exception:
    #                         raise Exception("Impossible to check how many quantity of object into "
    #                                         "final_expected_parties_array['persones'].")
    #                     for p in range(quantity_of_persones_into_final_expected_parties_array):
    #                         try:
    #                             """
    #                             Check how many quantity of object into
    #                             final_expected_parties_array['persones']['businessFunctions'].
    #                             """
    #                             list_of_final_party_persones_business_functions_id = list()
    #                             for i in \
    #                                     final_expected_parties_array[pa]['persones'][p]['businessFunctions']:
    #                                 for i_1 in i:
    #                                     if i_1 == "id":
    #                                         list_of_final_party_persones_business_functions_id.append(i_1)
    #                             quantity_of_business_functions_into_final = \
    #                                 len(list_of_final_party_persones_business_functions_id)
    #                         except Exception:
    #                             raise Exception("Impossible to check how many quantity of object into "
    #                                             "final_expected_parties_array['persones']['businessFunctions'].")
    #                         for bf in range(quantity_of_business_functions_into_final):
    #                             try:
    #                                 check = is_it_uuid(
    #                                     uuid_to_test=GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                         'releases'][0]['parties'][pa]['persones'][p]['businessFunctions'][bf][
    #                                         'id'],
    #                                     version=4
    #                                 )
    #                                 if check is True:
    #                                     final_expected_parties_array[pa]['persones'][p]['businessFunctions'][bf][
    #                                         'id'] = GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                         'releases'][0]['parties'][pa]['persones'][p]['businessFunctions'][bf][
    #                                         'id']
    #                                 else:
    #                                     raise ValueError("businessFunctions.id in release must be uuid version 4")
    #                             except Exception:
    #                                 raise Exception("Check your businessFunctions array in release")
    #             except Exception:
    #                 raise Exception("Impossible to prepare expected parties array")
    #
    #             try:
    #                 """
    #                 Prepare expected award array
    #                 """
    #                 final_expected_awards_array = list()
    #
    #                 list_of_awards_id_from_release = list()
    #                 for i in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
    #                     for i_1 in i:
    #                         if i_1 == "id":
    #                             list_of_awards_id_from_release.append(i['id'])
    #                 quantity_of_object_into_list_of_awards_id_from_release = \
    #                     len(list_of_awards_id_from_release)
    #
    #                 list_of_awards_suppliers_from_release = list()
    #                 for i in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
    #                     for i_1 in i:
    #                         if i_1 == "suppliers":
    #                             list_of_awards_suppliers_from_release.append(i['suppliers'])
    #
    #                 expected_awards_array_first = TenderPeriodExpectedChanges(
    #                     environment=GlobalClassMetadata.environment,
    #                     language=GlobalClassMetadata.language
    #                 ).prepare_array_of_awards_mapper(bid_payload=GlobalClassCreateFirstBid.payload)
    #
    #                 expected_awards_array = expected_awards_array_first
    #
    #                 list_of_awards_suppliers_from_expected_awards_array = list()
    #                 for i in expected_awards_array:
    #                     for i_1 in i:
    #                         if i_1 == "suppliers":
    #                             list_of_awards_suppliers_from_expected_awards_array.append(i['suppliers'])
    #                 quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array = \
    #                     len(list_of_awards_suppliers_from_expected_awards_array)
    #
    #                 if quantity_of_object_into_list_of_awards_id_from_release == \
    #                         quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array:
    #                     for q in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                         for q_1 in range(
    #                                 quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array):
    #                             if expected_awards_array[q_1]['suppliers'] == \
    #                                     list_of_awards_suppliers_from_release[q]:
    #                                 final_expected_awards_array.append(expected_awards_array[q_1]['value'])
    #                 else:
    #                     raise Exception("Error: quantity_of_object_into_list_of_awards_id_from_release !="
    #                                     "quantity_of_object_into_list_of_awards_suppliers_from_expected_"
    #                                     "awards_array")
    #                 try:
    #                     """
    #                     Check id into award array and set permanent id for 'final_expected_awards_array'.
    #                     """
    #                     for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                         try:
    #                             """
    #                             Check that actual_ev_release['releases'][0]['awards'][0]['id'] is uuid version 4
    #                             """
    #                             check_award_id = is_it_uuid(
    #                                 uuid_to_test=GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                     'releases'][0]['awards'][award]['id'],
    #                                 version=4
    #                             )
    #                             if check_award_id is True:
    #                                 final_expected_awards_array[award]['id'] = \
    #                                     GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                         'releases'][0]['awards'][award]['id']
    #                             else:
    #                                 raise Exception("actual_ev_release['releases'][0]['awards'][0]['id'] "
    #                                                 "must be uuid version 4")
    #                         except Exception:
    #                             raise Exception("Impossible to check that actual_ev_release['releases'][0]"
    #                                             "['awards'][0]['id'] is uuid version 4")
    #                 except Exception:
    #                     raise Exception("Impossible to check id into award array and set permanent id "
    #                                     "for 'final_expected_awards_array'.")
    #                 try:
    #                     """
    #                     Set 'statusDetails' for award, according with rule FReq-1.4.1.8.
    #                     """
    #                     if GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                         'awardCriteria'] == "ratedCriteria" or \
    #                             GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                                 'awardCriteria'] == "qualityOnly" or \
    #                             GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                                 'awardCriteria'] == "costOnly":
    #                         weight_values_list = list()
    #
    #                         for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                             weight_values_list.append(final_expected_awards_array[award]['weightedValue'][
    #                                                           'amount'])
    #                         min_weight_value = min(weight_values_list)
    #                         if final_expected_awards_array[award]['weightedValue']['amount'] == min_weight_value:
    #                             final_expected_awards_array[award]['statusDetails'] = "awaiting"
    #                         else:
    #                             final_expected_awards_array[award]['statusDetails'] = "empty"
    #                         awards_status_details_list = list()
    #                         try:
    #                             """
    #                             Check how many awards have statusDetails 'awaiting'.
    #                             """
    #                             for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                                 if final_expected_awards_array[award]['statusDetails'] == "awaiting":
    #                                     awards_status_details_list.append(
    #                                         final_expected_awards_array[award]['relatedBid'])
    #                         except Exception:
    #                             raise Exception(
    #                                 "Impossible to check how many awards have statusDetails 'awaiting'.")
    #                         try:
    #                             """
    #                             Check 'statusDetails' into final_expected_awards_array.
    #                             """
    #                             if len(awards_status_details_list) > 1:
    #                                 for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                                     if final_expected_awards_array[award]['relatedBid'] == \
    #                                             GlobalClassCreateFirstBid.bid_id:
    #                                         final_expected_awards_array[award]['statusDetails'] = "awaiting"
    #                                     else:
    #                                         final_expected_awards_array[award]['statusDetails'] = "empty"
    #                         except Exception:
    #                             raise Exception("Impossible to check 'statusDetails' into "
    #                                             "final_expected_awards_array.")
    #                     else:
    #                         values_list = list()
    #
    #                         for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                             values_list.append(final_expected_awards_array[award]['value']['amount'])
    #                         min_value = min(values_list)
    #                         if final_expected_awards_array[award]['value']['amount'] == min_value:
    #                             final_expected_awards_array[award]['statusDetails'] = "awaiting"
    #                         else:
    #                             final_expected_awards_array[award]['statusDetails'] = "empty"
    #                         awards_status_details_list = list()
    #                         try:
    #                             """
    #                             Check how many awards have statusDetails 'awaiting'.
    #                             """
    #                             for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                                 if final_expected_awards_array[award]['statusDetails'] == "awaiting":
    #                                     awards_status_details_list.append(
    #                                         final_expected_awards_array[award]['relatedBid'])
    #                         except Exception:
    #                             raise Exception(
    #                                 "Impossible to check how many awards have statusDetails 'awaiting'.")
    #                         try:
    #                             """
    #                             Check 'statusDetails' into final_expected_awards_array.
    #                             """
    #                             if len(awards_status_details_list) > 1:
    #                                 for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                                     if final_expected_awards_array[award]['relatedBid'] == \
    #                                             GlobalClassCreateFirstBid.bid_id:
    #                                         final_expected_awards_array[award]['statusDetails'] = "awaiting"
    #                                     else:
    #                                         final_expected_awards_array[award]['statusDetails'] = "empty"
    #                         except Exception:
    #                             raise Exception("Impossible to check 'statusDetails' into "
    #                                             "final_expected_awards_array.")
    #                 except Exception:
    #                     raise Exception("Impossible to set 'statusDetails' for award, "
    #                                     "according with rule FReq-1.4.1.8.")
    #             except Exception:
    #                 raise Exception("Impossible to prepare expected awards array")
    #
    #             try:
    #                 """
    #                 Prepare expected bid object
    #                 """
    #                 final_expected_bids_object = {"details": []}
    #                 expected_bids_array = list()
    #
    #                 expected_bids_object_first = TenderPeriodExpectedChanges(
    #                     environment=GlobalClassMetadata.environment,
    #                     language=GlobalClassMetadata.language
    #                 ).prepare_bid_details_mapper(
    #                     bid_payload=GlobalClassCreateFirstBid.payload,
    #                     bid_feed_point_message=GlobalClassCreateFirstBid.feed_point_message)
    #                 expected_bids_array.append(expected_bids_object_first)
    #
    #                 try:
    #                     """
    #                     Check how many quantity of object into expected_bids_array.
    #                     """
    #                     list_of_expected_bids_array_tenderers = list()
    #                     for i in expected_bids_array:
    #                         for i_1 in i:
    #                             if i_1 == "tenderers":
    #                                 list_of_expected_bids_array_tenderers.append(i_1)
    #                     quantity_of_list_of_expected_bids_array_tenderers = len(
    #                         list_of_expected_bids_array_tenderers)
    #                 except Exception:
    #                     raise Exception("Impossible to check how many quantity of object into expected_bids_array.")
    #                 try:
    #                     """
    #                     Check how many quantity of object into
    #                     GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]'bids']['details'].
    #                     """
    #                     list_of_releases_bids_details_tenderers = list()
    #                     for i in \
    #                             GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids'][
    #                                 'details']:
    #                         for i_1 in i:
    #                             if i_1 == "tenderers":
    #                                 list_of_releases_bids_details_tenderers.append(i['tenderers'])
    #                     quantity_of_list_of_releases_bids_details_tenderers = \
    #                         len(list_of_releases_bids_details_tenderers)
    #                 except Exception:
    #                     raise Exception("Impossible to calculate how many quantity of object into "
    #                                     "expected_bids_array['details']['tenderers']")
    #                 if quantity_of_list_of_expected_bids_array_tenderers == \
    #                         quantity_of_list_of_releases_bids_details_tenderers:
    #                     for q in range(quantity_of_list_of_releases_bids_details_tenderers):
    #                         for q_1 in range(quantity_of_list_of_expected_bids_array_tenderers):
    #                             if expected_bids_array[q_1]['tenderers'] == \
    #                                     list_of_releases_bids_details_tenderers[q]:
    #                                 final_expected_bids_object['details'].append(
    #                                     expected_bids_array[q_1]['value'])
    #                 else:
    #                     raise Exception("Error: quantity_of_details_id_into_expected_bids !="
    #                                     "quantity_of_details_id_into_releases_bids")
    #                 try:
    #                     """
    #                     Set permanent id for 'details' into expected_bids_array['details'].
    #                     """
    #                     for d in range(quantity_of_list_of_expected_bids_array_tenderers):
    #                         final_expected_bids_object['details'][d]['id'] = \
    #                             GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids'][
    #                                 'details'][d]['id']
    #                 except Exception:
    #                     raise Exception("Impossible to set permanent id for 'details', "
    #                                     "'evidences', 'requirementResponses' into expected_bids_array['details'].")
    #             except Exception:
    #                 raise Exception("Impossible to prepare expected bids object")
    #
    #             try:
    #                 """
    #                 Prepare expected criteria array
    #                 """
    #                 final_expected_criteria_array = TenderPeriodExpectedChanges(
    #                     environment=GlobalClassMetadata.environment,
    #                     language=GlobalClassMetadata.language).prepare_criteria_array_source_procuring_entity()
    #             except Exception:
    #                 raise Exception("Impossible to prepare expected criteria array")
    #
    #             try:
    #                 """
    #                     If compare_releases !=expected_result, then return process steps by operation-id.
    #                     """
    #                 if compare_releases == expected_result and \
    #                         expected_parties_array == \
    #                         GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['parties'] and \
    #                         expected_awards_array == \
    #                         GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'] and \
    #                         expected_bids_array == \
    #                         GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids']:
    #                     pass
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[
    #                                 'X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #             elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['parties'] != \
    #                     final_expected_parties_array:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['parties'])), "Actual parties array")
    #                 allure.attach(str(json.dumps(final_expected_parties_array)), "Expected parties array")
    #                 raise Exception("Error into comparing parties")
    #             elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'] != \
    #                     final_expected_awards_array:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['awards'])), "Actual awards array")
    #                 allure.attach(str(json.dumps(final_expected_awards_array)), "Expected awards array")
    #                 raise Exception("Error into comparing awards")
    #             elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids'] != \
    #                     final_expected_bids_object:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['bids'])), "Actual bids array")
    #                 allure.attach(str(json.dumps(final_expected_bids_object)), "Expected bids array")
    #                 raise Exception("Error into comparing bids")
    #             elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender']['criteria'] != \
    #                     final_expected_bids_object:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['tender']['criteria'])),
    #                               "Actual criteria array")
    #                 allure.attach(str(json.dumps(final_expected_criteria_array)), "Expected criteria array")
    #                 raise Exception("Error into comparing bids")
    #             elif \
    #                     GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                         'awardPeriod'] != final_expected_award_period_object:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['tender']['awardPeriod']['startDate'])),
    #                               "Actual awardPeriod object")
    #                 allure.attach(str(json.dumps(final_expected_award_period_object)),
    #                               "Expected awardPeriod object")
    #                 raise Exception("Error into comparing awardPeriod")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=final_expected_parties_array,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['parties']
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=final_expected_awards_array,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=final_expected_bids_object,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids']
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=final_expected_criteria_array,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                     'criteria']
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=final_expected_award_period_object,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                     'awardPeriod']
    #             )) == str(True)
    #
    #         with allure.step('# 11.3. Check MS release'):
    #             """
    #             Compare multistage release with expected multistage release model.
    #             """
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
    #                           "Actual MS release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
    #                           "Actual MS release after tender period end expired")
    #
    #             compare_releases = dict(DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ms_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ms_release))
    #
    #             expected_result = {}
    #             try:
    #                 """
    #                 If TestCase was passed, then cLean up the database.
    #                 If TestCase was failed, then return process steps by operation-id.
    #                 """
    #                 if compare_releases == expected_result:
    #                     GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateEi.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateFs.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreatePn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateCnOnPn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassCreateFirstBid.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         database = GlobalClassMetadata.database
    #                         steps = \
    #                             database.get_bpe_operation_step_by_operation_id_from_orchestrator(
    #                                 operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[
    #                                     'X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #
    #                 try:
    #                     """
    #                     Rollback specific value into submission.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                         value=min_bids_from_submission_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into submission.rules")
    #                 try:
    #                     """
    #                     Rollback specific value into evaluation.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                         value=min_bids_from_evaluation_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into evaluation.rules")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #
    # @allure.title("Check message from Kafka topic, EV, MS releases, "
    #               "on the flow ´Is tenderPeriodExpired -> True -> Are there bids for opening? -> True -> "
    #               "Are there unsuccessful lots? -> False -> Is tender unsuccessful? -> False -> "
    #               "Is auction started? -> False -> Is there award criteria -> True -> Stage -> EV -> "
    #               "Is operationType=TenderPeriodEndAuction -> False -> Send message to platform´"
    #               "------------------------------------------------------------------------------------"
    #               "EI: full data model with items array;"
    #               "FS: full data model, own money;"
    #               "PN: full data model, 1 lots, 1 items;"
    #               "CnOnPn: full data model with auction, 1 lots, 1 items, criteria, conversions;"
    #               "First Bid: full data model with 2 tenderers, in relation to the first lot."
    #               )
    # def test_check_result_of_sending_the_request_three(self):
    #     with allure.step('# 1. Authorization platform one: create EI'):
    #         """
    #         Tender platform authorization for create expenditure item process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateEi.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateEi.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
    #     with allure.step('# 2. Send request to create EI'):
    #         """
    #         Send api request to BPE host for expenditure item creation.
    #         And save in variable ei_ocid.
    #         """
    #         ei_payload = copy.deepcopy(EiPreparePayload())
    #         GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model(quantity_of_tender_item_object=2)
    #         Requests().create_ei(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateEi.access_token,
    #             x_operation_id=GlobalClassCreateEi.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             payload=GlobalClassCreateEi.payload
    #         )
    #         GlobalClassCreateEi.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateEi.ei_ocid = \
    #             GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']
    #
    #         GlobalClassCreateEi.actual_ei_release = requests.get(
    #             url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateEi.ei_ocid}").json()
    #     with allure.step('# 3. Authorization platform one: create FS'):
    #         """
    #         Tender platform authorization for create financial source process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFs.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFs.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
    #     with allure.step('# 4. Send request to create FS'):
    #         """
    #         Send api request to for financial source creating.
    #         And save in variable fs_id and fs_token.
    #         """
    #         time.sleep(1)
    #         fs_payload = copy.deepcopy(FsPreparePayload())
    #         GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
    #         Requests().create_fs(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFs.access_token,
    #             x_operation_id=GlobalClassCreateFs.operation_id,
    #             ei_ocid=GlobalClassCreateEi.ei_ocid,
    #             payload=GlobalClassCreateFs.payload
    #         )
    #         GlobalClassCreateFs.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFs.fs_id = \
    #             GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']
    #
    #         GlobalClassCreateFs.actual_fs_release = requests.get(
    #             url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateFs.fs_id}").json()
    #     with allure.step('# 5. Authorization platform one: create PN'):
    #         """
    #         Tender platform authorization for create planning notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreatePn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreatePn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)
    #
    #     with allure.step('# 6. Send request to create PN'):
    #         """
    #         Send api request to for planning notice creating.
    #         Save asynchronous result of sending the request.
    #         Save pn_ocid and pn_token.
    #         """
    #         time.sleep(1)
    #         pn_payload = copy.deepcopy(PnPreparePayload())
    #         GlobalClassCreatePn.payload = \
    #             pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
    #                 quantity_of_lot_object=1,
    #                 quantity_of_item_object=1)
    #
    #         Requests().create_pn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreatePn.access_token,
    #             x_operation_id=GlobalClassCreatePn.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             pmd=GlobalClassMetadata.pmd,
    #             payload=GlobalClassCreatePn.payload
    #         )
    #         GlobalClassCreatePn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreatePn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreatePn.pn_ocid = \
    #             GlobalClassCreatePn.feed_point_message['data']['ocid']
    #
    #         GlobalClassCreatePn.pn_id = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['id']
    #
    #         GlobalClassCreatePn.pn_token = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
    #
    #         GlobalClassCreatePn.actual_pn_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_id}").json()
    #
    #         GlobalClassCreatePn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #     with allure.step('# 7. Authorization platform one: create CnOnPn'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
    #     with allure.step('# 8. Send request to create CnOnPn'):
    #         """
    #         Send api request to for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         time.sleep(1)
    #         cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
    #         GlobalClassCreateCnOnPn.payload = \
    #             cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
    #                 enquiry_interval=121,
    #                 tender_interval=300,
    #                 quantity_of_lots_object=1,
    #                 quantity_of_items_object=1,
    #                 need_to_set_permanent_id_for_lots_array=True,
    #                 need_to_set_permanent_id_for_items_array=True,
    #                 need_to_set_permanent_id_for_documents_array=True,
    #                 based_stage_release=GlobalClassCreatePn.actual_pn_release
    #             )
    #
    #         Requests().create_cnonpn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateCnOnPn.access_token,
    #             x_operation_id=GlobalClassCreateCnOnPn.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             pn_id=GlobalClassCreatePn.pn_id,
    #             pn_token=GlobalClassCreatePn.pn_token,
    #             payload=GlobalClassCreateCnOnPn.payload
    #         )
    #
    #         GlobalClassCreateCnOnPn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateCnOnPn.ev_id = \
    #             GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']
    #
    #         GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
    #             url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #         GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #     with allure.step('# 9. Authorization platform one: create first Bid'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
    #
    #     with allure.step('# 10. Send request to create first Bid'):
    #         """
    #         Send api request to for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         try:
    #             """
    #             Set specific value into submission.rules for this testcase
    #             """
    #             min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_submission_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into submission.rules")
    #         try:
    #             """
    #             Set specific value into evaluation.rules for this testcase
    #             """
    #             min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_evaluation_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into evaluation.rules")
    #
    #         time.sleep(1)
    #         time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
    #         bid_payload_class = copy.deepcopy(BidPreparePayload())
    #         GlobalClassCreateFirstBid.payload = \
    #             bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
    #                 based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)
    #
    #         Requests().create_bid(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFirstBid.access_token,
    #             x_operation_id=GlobalClassCreateFirstBid.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             ev_id=GlobalClassCreateCnOnPn.ev_id,
    #             payload=GlobalClassCreateFirstBid.payload
    #         )
    #         GlobalClassCreateFirstBid.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFirstBid.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFirstBid.bid_id = GlobalClassCreateFirstBid.feed_point_message['data']['outcomes'][
    #             'bids'][0]['id']
    #
    #     with allure.step('# 11. See result'):
    #         """
    #         Check the results of test case running.
    #         """
    #         with allure.step('# 11.1. Check message in feed point'):
    #             """
    #             Check the asynchronous_result_of_sending_the_request.
    #             """
    #             time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])
    #             time.sleep(1)
    #             GlobalClassTenderPeriodEndAuction.feed_point_message = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()
    #             allure.attach(str(GlobalClassTenderPeriodEndAuction.feed_point_message), 'Message in feed point')
    #
    #             asynchronous_result_of_expired_tender_period_end = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").tender_period_end_auction_message_is_successful(
    #                     environment=GlobalClassMetadata.environment,
    #                     kafka_message=GlobalClassTenderPeriodEndAuction.feed_point_message,
    #                     pn_ocid=GlobalClassCreatePn.pn_ocid,
    #                     ev_id=GlobalClassCreateCnOnPn.ev_id
    #                 )
    #
    #             try:
    #                 """
    #                 If asynchronous_result_of_sending_the_request was False, then return process steps by
    #                 operation-id.
    #                 """
    #                 if asynchronous_result_of_expired_tender_period_end is False:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #         with allure.step('# 11.2. Check EV release'):
    #             """
    #             Compare actual evaluation value release with expected evaluation value release model.
    #             """
    #             time.sleep(2)
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
    #                           "Actual EV release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
    #                 url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
    #                           "Actual EV release after tender period end expired")
    #             compare_releases = DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ev_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ev_release)
    #             dictionary_item_added_was_cleaned = \
    #                 str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
    #             compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
    #             compare_releases = dict(compare_releases)
    #             expected_criteria_array_source_p_entity = TenderPeriodExpectedChanges(
    #                 environment=GlobalClassMetadata.environment,
    #                 language=GlobalClassMetadata.language
    #             ).prepare_criteria_array_source_procuring_entity()
    #
    #             expected_result = {
    #                 "dictionary_item_added": "['releases'][0]['parties'], "
    #                                          "['releases'][0]['awards'], "
    #                                          "['releases'][0]['bids'], "
    #                                          "['releases'][0]['tender']['awardPeriod']",
    #                 "values_changed": {
    #                     "root['releases'][0]['id']": {
    #                         "new_value":
    #                             f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                             f"{GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['id'][46:59]}",
    #                         "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                                      f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
    #                     },
    #                     "root['releases'][0]['date']": {
    #                         "new_value": GlobalClassTenderPeriodEndAuction.feed_point_message['data'][
    #                             'operationDate'],
    #                         "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
    #                     },
    #                     "root['releases'][0]['tag'][0]": {
    #                         'new_value': 'award',
    #                         'old_value': 'tender'
    #                     },
    #                     "root['releases'][0]['tender']['statusDetails']": {
    #                         'new_value': 'awarding',
    #                         'old_value': 'clarification'
    #                     }
    #                 },
    #                 "iterable_item_added": {
    #                     f"root['releases'][0]['tender']['criteria'][{expected_criteria_array_source_p_entity[1]}]":
    #                         expected_criteria_array_source_p_entity[0]
    #                 }
    #             }
    #
    #             try:
    #                 """
    #                 Prepare expected awardPeriod object.
    #                 """
    #                 final_expected_award_period_object = {
    #                     "startDate": GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                         'tenderPeriod']['endDate']
    #                 }
    #             except Exception:
    #                 raise Exception("Prepare expected awardPeriod object.")
    #
    #             try:
    #                 """
    #                 Prepare expected parties array
    #                 """
    #                 final_expected_parties_array = list()
    #                 list_of_parties_id_from_release = list()
    #                 for i in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['parties']:
    #                     for i_1 in i:
    #                         if i_1 == "id":
    #                             list_of_parties_id_from_release.append(i['id'])
    #
    #                 expected_parties_array_first = TenderPeriodExpectedChanges(
    #                     environment=GlobalClassMetadata.environment,
    #                     language=GlobalClassMetadata.language
    #                 ).prepare_array_of_parties_mapper_for_successful_tender(
    #                     bid_payload=GlobalClassCreateFirstBid.payload)
    #
    #                 expected_parties_array = expected_parties_array_first
    #                 quantity_of_object_into_expected_parties_array = len(expected_parties_array)
    #                 quantity_of_object_into_list_of_parties_id_from_release = len(list_of_parties_id_from_release)
    #                 if quantity_of_object_into_expected_parties_array == \
    #                         quantity_of_object_into_list_of_parties_id_from_release:
    #                     for q in range(quantity_of_object_into_list_of_parties_id_from_release):
    #                         for q_1 in range(quantity_of_object_into_expected_parties_array):
    #                             if expected_parties_array[q_1]['id'] == list_of_parties_id_from_release[q]:
    #                                 final_expected_parties_array.append(expected_parties_array[q_1]['value'])
    #                 else:
    #                     raise Exception("Error: quantity_of_object_into_expected_parties_array != "
    #                                     "quantity_of_object_into_list_of_parties_id_from_release")
    #                 for pa in range(quantity_of_object_into_expected_parties_array):
    #                     try:
    #                         """
    #                         Check how many quantity of object into final_expected_parties_array['persones'].
    #                         """
    #                         list_of_final_party_persones_id = list()
    #                         for i in final_expected_parties_array[pa]['persones']:
    #                             for i_1 in i:
    #                                 if i_1 == "identifier":
    #                                     for i_2 in i['identifier']:
    #                                         if i_2 == "id":
    #                                             list_of_final_party_persones_id.append(i_2)
    #                         quantity_of_persones_into_final_expected_parties_array = \
    #                             len(list_of_final_party_persones_id)
    #                     except Exception:
    #                         raise Exception("Impossible to check how many quantity of object into "
    #                                         "final_expected_parties_array['persones'].")
    #                     for p in range(quantity_of_persones_into_final_expected_parties_array):
    #                         try:
    #                             """
    #                             Check how many quantity of object into
    #                             final_expected_parties_array['persones']['businessFunctions'].
    #                             """
    #                             list_of_final_party_persones_business_functions_id = list()
    #                             for i in \
    #                                     final_expected_parties_array[pa]['persones'][p]['businessFunctions']:
    #                                 for i_1 in i:
    #                                     if i_1 == "id":
    #                                         list_of_final_party_persones_business_functions_id.append(i_1)
    #                             quantity_of_business_functions_into_final = \
    #                                 len(list_of_final_party_persones_business_functions_id)
    #                         except Exception:
    #                             raise Exception("Impossible to check how many quantity of object into "
    #                                             "final_expected_parties_array['persones']['businessFunctions'].")
    #                         for bf in range(quantity_of_business_functions_into_final):
    #                             try:
    #                                 check = is_it_uuid(
    #                                     uuid_to_test=GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                         'releases'][0]['parties'][pa]['persones'][p]['businessFunctions'][bf][
    #                                         'id'],
    #                                     version=4
    #                                 )
    #                                 if check is True:
    #                                     final_expected_parties_array[pa]['persones'][p]['businessFunctions'][bf][
    #                                         'id'] = GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                         'releases'][0]['parties'][pa]['persones'][p]['businessFunctions'][bf][
    #                                         'id']
    #                                 else:
    #                                     raise ValueError("businessFunctions.id in release must be uuid version 4")
    #                             except Exception:
    #                                 raise Exception("Check your businessFunctions array in release")
    #             except Exception:
    #                 raise Exception("Impossible to prepare expected parties array")
    #
    #             try:
    #                 """
    #                 Prepare expected award array
    #                 """
    #                 final_expected_awards_array = list()
    #
    #                 list_of_awards_id_from_release = list()
    #                 for i in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
    #                     for i_1 in i:
    #                         if i_1 == "id":
    #                             list_of_awards_id_from_release.append(i['id'])
    #                 quantity_of_object_into_list_of_awards_id_from_release = \
    #                     len(list_of_awards_id_from_release)
    #
    #                 list_of_awards_suppliers_from_release = list()
    #                 for i in GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
    #                     for i_1 in i:
    #                         if i_1 == "suppliers":
    #                             list_of_awards_suppliers_from_release.append(i['suppliers'])
    #
    #                 expected_awards_array_first = TenderPeriodExpectedChanges(
    #                     environment=GlobalClassMetadata.environment,
    #                     language=GlobalClassMetadata.language
    #                 ).prepare_array_of_awards_mapper(bid_payload=GlobalClassCreateFirstBid.payload)
    #
    #                 expected_awards_array = expected_awards_array_first
    #
    #                 list_of_awards_suppliers_from_expected_awards_array = list()
    #                 for i in expected_awards_array:
    #                     for i_1 in i:
    #                         if i_1 == "suppliers":
    #                             list_of_awards_suppliers_from_expected_awards_array.append(i['suppliers'])
    #                 quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array = \
    #                     len(list_of_awards_suppliers_from_expected_awards_array)
    #
    #                 if quantity_of_object_into_list_of_awards_id_from_release == \
    #                         quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array:
    #                     for q in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                         for q_1 in range(
    #                                 quantity_of_object_into_list_of_awards_suppliers_from_expected_awards_array):
    #                             if expected_awards_array[q_1]['suppliers'] == \
    #                                     list_of_awards_suppliers_from_release[q]:
    #                                 final_expected_awards_array.append(expected_awards_array[q_1]['value'])
    #                 else:
    #                     raise Exception("Error: quantity_of_object_into_list_of_awards_id_from_release !="
    #                                     "quantity_of_object_into_list_of_awards_suppliers_from_expected_"
    #                                     "awards_array")
    #                 try:
    #                     """
    #                     Check id into award array and set permanent id for 'final_expected_awards_array'.
    #                     """
    #                     for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                         try:
    #                             """
    #                             Check that actual_ev_release['releases'][0]['awards'][0]['id'] is uuid version 4
    #                             """
    #                             check_award_id = is_it_uuid(
    #                                 uuid_to_test=GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                     'releases'][0]['awards'][award]['id'],
    #                                 version=4
    #                             )
    #                             if check_award_id is True:
    #                                 final_expected_awards_array[award]['id'] = \
    #                                     GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                         'releases'][0]['awards'][award]['id']
    #                             else:
    #                                 raise Exception("actual_ev_release['releases'][0]['awards'][0]['id'] "
    #                                                 "must be uuid version 4")
    #                         except Exception:
    #                             raise Exception("Impossible to check that actual_ev_release['releases'][0]"
    #                                             "['awards'][0]['id'] is uuid version 4")
    #                 except Exception:
    #                     raise Exception("Impossible to check id into award array and set permanent id "
    #                                     "for 'final_expected_awards_array'.")
    #                 try:
    #                     """
    #                     Set 'statusDetails' for award, according with rule FReq-1.4.1.8.
    #                     """
    #                     if GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                         'awardCriteria'] == "ratedCriteria" or \
    #                             GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                                 'awardCriteria'] == "qualityOnly" or \
    #                             GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                                 'awardCriteria'] == "costOnly":
    #                         weight_values_list = list()
    #
    #                         for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                             weight_values_list.append(final_expected_awards_array[award]['weightedValue'][
    #                                                           'amount'])
    #                         min_weight_value = min(weight_values_list)
    #                         if final_expected_awards_array[award]['weightedValue']['amount'] == min_weight_value:
    #                             final_expected_awards_array[award]['statusDetails'] = "awaiting"
    #                         else:
    #                             final_expected_awards_array[award]['statusDetails'] = "empty"
    #                         awards_status_details_list = list()
    #                         try:
    #                             """
    #                             Check how many awards have statusDetails 'awaiting'.
    #                             """
    #                             for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                                 if final_expected_awards_array[award]['statusDetails'] == "awaiting":
    #                                     awards_status_details_list.append(
    #                                         final_expected_awards_array[award]['relatedBid'])
    #                         except Exception:
    #                             raise Exception(
    #                                 "Impossible to check how many awards have statusDetails 'awaiting'.")
    #                         try:
    #                             """
    #                             Check 'statusDetails' into final_expected_awards_array.
    #                             """
    #                             if len(awards_status_details_list) > 1:
    #                                 for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                                     if final_expected_awards_array[award]['relatedBid'] == \
    #                                             GlobalClassCreateFirstBid.bid_id:
    #                                         final_expected_awards_array[award]['statusDetails'] = "awaiting"
    #                                     else:
    #                                         final_expected_awards_array[award]['statusDetails'] = "empty"
    #                         except Exception:
    #                             raise Exception("Impossible to check 'statusDetails' into "
    #                                             "final_expected_awards_array.")
    #                     else:
    #                         values_list = list()
    #
    #                         for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                             values_list.append(final_expected_awards_array[award]['value']['amount'])
    #                         min_value = min(values_list)
    #                         if final_expected_awards_array[award]['value']['amount'] == min_value:
    #                             final_expected_awards_array[award]['statusDetails'] = "awaiting"
    #                         else:
    #                             final_expected_awards_array[award]['statusDetails'] = "empty"
    #                         awards_status_details_list = list()
    #                         try:
    #                             """
    #                             Check how many awards have statusDetails 'awaiting'.
    #                             """
    #                             for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                                 if final_expected_awards_array[award]['statusDetails'] == "awaiting":
    #                                     awards_status_details_list.append(
    #                                         final_expected_awards_array[award]['relatedBid'])
    #                         except Exception:
    #                             raise Exception(
    #                                 "Impossible to check how many awards have statusDetails 'awaiting'.")
    #                         try:
    #                             """
    #                             Check 'statusDetails' into final_expected_awards_array.
    #                             """
    #                             if len(awards_status_details_list) > 1:
    #                                 for award in range(quantity_of_object_into_list_of_awards_id_from_release):
    #                                     if final_expected_awards_array[award]['relatedBid'] == \
    #                                             GlobalClassCreateFirstBid.bid_id:
    #                                         final_expected_awards_array[award]['statusDetails'] = "awaiting"
    #                                     else:
    #                                         final_expected_awards_array[award]['statusDetails'] = "empty"
    #                         except Exception:
    #                             raise Exception("Impossible to check 'statusDetails' into "
    #                                             "final_expected_awards_array.")
    #                 except Exception:
    #                     raise Exception("Impossible to set 'statusDetails' for award, "
    #                                     "according with rule FReq-1.4.1.8.")
    #             except Exception:
    #                 raise Exception("Impossible to prepare expected awards array")
    #
    #             try:
    #                 """
    #                 Prepare expected bid object
    #                 """
    #                 final_expected_bids_object = {"details": []}
    #                 expected_bids_array = list()
    #
    #                 expected_bids_object_first = TenderPeriodExpectedChanges(
    #                     environment=GlobalClassMetadata.environment,
    #                     language=GlobalClassMetadata.language
    #                 ).prepare_bid_details_mapper(
    #                     bid_payload=GlobalClassCreateFirstBid.payload,
    #                     bid_feed_point_message=GlobalClassCreateFirstBid.feed_point_message)
    #                 expected_bids_array.append(expected_bids_object_first)
    #
    #                 try:
    #                     """
    #                     Check how many quantity of object into expected_bids_array.
    #                     """
    #                     list_of_expected_bids_array_tenderers = list()
    #                     for i in expected_bids_array:
    #                         for i_1 in i:
    #                             if i_1 == "tenderers":
    #                                 list_of_expected_bids_array_tenderers.append(i_1)
    #                     quantity_of_list_of_expected_bids_array_tenderers = len(
    #                         list_of_expected_bids_array_tenderers)
    #                 except Exception:
    #                     raise Exception("Impossible to check how many quantity of object into expected_bids_array.")
    #                 try:
    #                     """
    #                     Check how many quantity of object into
    #                     GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]'bids']['details'].
    #                     """
    #                     list_of_releases_bids_details_tenderers = list()
    #                     for i in \
    #                             GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids'][
    #                                 'details']:
    #                         for i_1 in i:
    #                             if i_1 == "tenderers":
    #                                 list_of_releases_bids_details_tenderers.append(i['tenderers'])
    #                     quantity_of_list_of_releases_bids_details_tenderers = \
    #                         len(list_of_releases_bids_details_tenderers)
    #                 except Exception:
    #                     raise Exception("Impossible to calculate how many quantity of object into "
    #                                     "expected_bids_array['details']['tenderers']")
    #                 if quantity_of_list_of_expected_bids_array_tenderers == \
    #                         quantity_of_list_of_releases_bids_details_tenderers:
    #                     for q in range(quantity_of_list_of_releases_bids_details_tenderers):
    #                         for q_1 in range(quantity_of_list_of_expected_bids_array_tenderers):
    #                             if expected_bids_array[q_1]['tenderers'] == \
    #                                     list_of_releases_bids_details_tenderers[q]:
    #                                 final_expected_bids_object['details'].append(
    #                                     expected_bids_array[q_1]['value'])
    #                 else:
    #                     raise Exception("Error: quantity_of_details_id_into_expected_bids !="
    #                                     "quantity_of_details_id_into_releases_bids")
    #                 try:
    #                     """
    #                     Set permanent id for 'details' into expected_bids_array['details'].
    #                     """
    #                     for d in range(quantity_of_list_of_expected_bids_array_tenderers):
    #                         final_expected_bids_object['details'][d]['id'] = \
    #                             GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids'][
    #                                 'details'][d]['id']
    #                 except Exception:
    #                     raise Exception("Impossible to set permanent id for 'details', "
    #                                     "'evidences', 'requirementResponses' into expected_bids_array['details'].")
    #             except Exception:
    #                 raise Exception("Impossible to prepare expected bids object")
    #
    #             try:
    #                 """
    #                     If compare_releases !=expected_result, then return process steps by operation-id.
    #                     """
    #                 if compare_releases == expected_result and \
    #                         expected_parties_array == \
    #                         GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['parties'] and \
    #                         expected_awards_array == \
    #                         GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'] and \
    #                         expected_bids_array == \
    #                         GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids']:
    #                     pass
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[
    #                                 'X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #             elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['parties'] != \
    #                     final_expected_parties_array:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['parties'])), "Actual parties array")
    #                 allure.attach(str(json.dumps(final_expected_parties_array)), "Expected parties array")
    #                 raise Exception("Error into comparing parties")
    #             elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'] != \
    #                     final_expected_awards_array:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['awards'])), "Actual awards array")
    #                 allure.attach(str(json.dumps(final_expected_awards_array)), "Expected awards array")
    #                 raise Exception("Error into comparing awards")
    #             elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids'] != \
    #                     final_expected_bids_object:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['bids'])), "Actual bids array")
    #                 allure.attach(str(json.dumps(final_expected_bids_object)), "Expected bids array")
    #                 raise Exception("Error into comparing bids")
    #             elif \
    #                     GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                         'awardPeriod'] != final_expected_award_period_object:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['tender']['awardPeriod']['startDate'])),
    #                               "Actual awardPeriod object")
    #                 allure.attach(str(json.dumps(final_expected_award_period_object)),
    #                               "Expected awardPeriod object")
    #                 raise Exception("Error into comparing awardPeriod")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=final_expected_parties_array,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['parties']
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=final_expected_awards_array,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=final_expected_bids_object,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['bids']
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=final_expected_award_period_object,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['tender'][
    #                     'awardPeriod']
    #             )) == str(True)
    #
    #         with allure.step('# 11.3. Check MS release'):
    #             """
    #             Compare multistage release with expected multistage release model.
    #             """
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
    #                           "Actual MS release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
    #                           "Actual MS release after tender period end expired")
    #
    #             compare_releases = dict(DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ms_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ms_release))
    #
    #             expected_result = {}
    #             try:
    #                 """
    #                 If TestCase was passed, then cLean up the database.
    #                 If TestCase was failed, then return process steps by operation-id.
    #                 """
    #                 if compare_releases == expected_result:
    #                     GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateEi.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateFs.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreatePn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateCnOnPn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassCreateFirstBid.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         database = GlobalClassMetadata.database
    #                         steps = \
    #                             database.get_bpe_operation_step_by_operation_id_from_orchestrator(
    #                                 operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[
    #                                     'X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #
    #                 try:
    #                     """
    #                     Rollback specific value into submission.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                         value=min_bids_from_submission_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into submission.rules")
    #                 try:
    #                     """
    #                     Rollback specific value into evaluation.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                         value=min_bids_from_evaluation_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into evaluation.rules")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #
    # @allure.title("Check message from Kafka topic, EV, MS releases, "
    #               "on the flow ´Is tenderPeriodExpired -> True -> Are there bids for opening? -> True -> "
    #               "Are there unsuccessful lots? -> False -> Is tender unsuccessful? -> False -> "
    #               "Is auction started? -> True -> "
    #               "Is operationType=TenderPeriodEndAuction -> ?? -> Send auction message to platform´"
    #               "------------------------------------------------------------------------------------"
    #               "EI: full data model with items array;"
    #               "FS: full data model, own money;"
    #               "PN: full data model, 1 lots, 1 items;"
    #               "CnOnPn: full data model with auction, 1 lots, 1 items, criteria, conversions;"
    #               "First Bid: full data model with 2 tenderers, in relation to the first lot;"
    #               "Second Bid: full data model with 2 tenderers, in relation to the first lot."
    #               )
    # def test_check_result_of_sending_the_request_four(self):
    #     with allure.step('# 1. Authorization platform one: create EI'):
    #         """
    #         Tender platform authorization for create expenditure item process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateEi.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateEi.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
    #     with allure.step('# 2. Send request to create EI'):
    #         """
    #         Send api request to BPE host for expenditure item creation.
    #         And save in variable ei_ocid.
    #         """
    #         ei_payload = copy.deepcopy(EiPreparePayload())
    #         GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model(quantity_of_tender_item_object=2)
    #         Requests().create_ei(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateEi.access_token,
    #             x_operation_id=GlobalClassCreateEi.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             payload=GlobalClassCreateEi.payload
    #         )
    #         GlobalClassCreateEi.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateEi.ei_ocid = \
    #             GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']
    #
    #         GlobalClassCreateEi.actual_ei_release = requests.get(
    #             url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateEi.ei_ocid}").json()
    #     with allure.step('# 3. Authorization platform one: create FS'):
    #         """
    #         Tender platform authorization for create financial source process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFs.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFs.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
    #     with allure.step('# 4. Send request to create FS'):
    #         """
    #         Send api request to for financial source creating.
    #         And save in variable fs_id and fs_token.
    #         """
    #         time.sleep(1)
    #         fs_payload = copy.deepcopy(FsPreparePayload())
    #         GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
    #         Requests().create_fs(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFs.access_token,
    #             x_operation_id=GlobalClassCreateFs.operation_id,
    #             ei_ocid=GlobalClassCreateEi.ei_ocid,
    #             payload=GlobalClassCreateFs.payload
    #         )
    #         GlobalClassCreateFs.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFs.fs_id = \
    #             GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']
    #
    #         GlobalClassCreateFs.actual_fs_release = requests.get(
    #             url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateFs.fs_id}").json()
    #     with allure.step('# 5. Authorization platform one: create PN'):
    #         """
    #         Tender platform authorization for create planning notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreatePn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreatePn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)
    #
    #     with allure.step('# 6. Send request to create PN'):
    #         """
    #         Send api request to BPE host for planning notice creating.
    #         Save asynchronous result of sending the request.
    #         Save pn_ocid and pn_token.
    #         """
    #         time.sleep(1)
    #         pn_payload = copy.deepcopy(PnPreparePayload())
    #         GlobalClassCreatePn.payload = \
    #             pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
    #                 quantity_of_lot_object=1,
    #                 quantity_of_item_object=1)
    #
    #         Requests().create_pn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreatePn.access_token,
    #             x_operation_id=GlobalClassCreatePn.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             pmd=GlobalClassMetadata.pmd,
    #             payload=GlobalClassCreatePn.payload
    #         )
    #         GlobalClassCreatePn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreatePn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreatePn.pn_ocid = \
    #             GlobalClassCreatePn.feed_point_message['data']['ocid']
    #
    #         GlobalClassCreatePn.pn_id = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['id']
    #
    #         GlobalClassCreatePn.pn_token = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
    #
    #         GlobalClassCreatePn.actual_pn_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_id}").json()
    #
    #         GlobalClassCreatePn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #     with allure.step('# 7. Authorization platform one: create CnOnPn'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
    #     with allure.step('# 8. Send request to create CnOnPn'):
    #         """
    #         Send api request to for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         time.sleep(1)
    #         cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
    #         GlobalClassCreateCnOnPn.payload = \
    #             cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
    #                 enquiry_interval=121,
    #                 tender_interval=300,
    #                 quantity_of_lots_object=1,
    #                 quantity_of_items_object=1,
    #                 need_to_set_permanent_id_for_lots_array=True,
    #                 need_to_set_permanent_id_for_items_array=True,
    #                 need_to_set_permanent_id_for_documents_array=True,
    #                 based_stage_release=GlobalClassCreatePn.actual_pn_release
    #             )
    #
    #         Requests().create_cnonpn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateCnOnPn.access_token,
    #             x_operation_id=GlobalClassCreateCnOnPn.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             pn_id=GlobalClassCreatePn.pn_id,
    #             pn_token=GlobalClassCreatePn.pn_token,
    #             payload=GlobalClassCreateCnOnPn.payload
    #         )
    #
    #         GlobalClassCreateCnOnPn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateCnOnPn.ev_id = \
    #             GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']
    #
    #         GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
    #             url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #         GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #     with allure.step('# 9. Authorization platform one: create first Bid'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
    #
    #     with allure.step('# 10. Send request to create first Bid'):
    #         """
    #         Send api request to for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         try:
    #             """
    #             Set specific value into submission.rules for this testcase
    #             """
    #             min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_submission_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into submission.rules")
    #         try:
    #             """
    #             Set specific value into evaluation.rules for this testcase
    #             """
    #             min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_evaluation_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into evaluation.rules")
    #
    #         time.sleep(1)
    #         time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
    #         bid_payload_class = copy.deepcopy(BidPreparePayload())
    #         GlobalClassCreateFirstBid.payload = \
    #             bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
    #                 based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)
    #
    #         Requests().create_bid(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFirstBid.access_token,
    #             x_operation_id=GlobalClassCreateFirstBid.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             ev_id=GlobalClassCreateCnOnPn.ev_id,
    #             payload=GlobalClassCreateFirstBid.payload
    #         )
    #         GlobalClassCreateFirstBid.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFirstBid.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFirstBid.bid_id = GlobalClassCreateFirstBid.feed_point_message['data']['outcomes'][
    #             'bids'][0]['id']
    #
    #     with allure.step('# 11. Authorization platform one: create second Bid'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateSecondBid.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateSecondBid.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateSecondBid.access_token)
    #
    #     with allure.step('# 12. Send request to create second Bid'):
    #         """
    #         Send api request to for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         try:
    #             """
    #             Set specific value into submission.rules for this testcase
    #             """
    #             min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_submission_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into submission.rules")
    #         try:
    #             """
    #             Set specific value into evaluation.rules for this testcase
    #             """
    #             min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_evaluation_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into evaluation.rules")
    #
    #         time.sleep(1)
    #         time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
    #         bid_payload_class = copy.deepcopy(BidPreparePayload())
    #         GlobalClassCreateSecondBid.payload = \
    #             bid_payload_class.create_second_bid_full_data_model_with_requirement_responses(
    #                 based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)
    #
    #         Requests().create_bid(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateSecondBid.access_token,
    #             x_operation_id=GlobalClassCreateSecondBid.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             ev_id=GlobalClassCreateCnOnPn.ev_id,
    #             payload=GlobalClassCreateSecondBid.payload
    #         )
    #         GlobalClassCreateSecondBid.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateSecondBid.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateSecondBid.bid_id = GlobalClassCreateSecondBid.feed_point_message['data']['outcomes'][
    #             'bids'][0]['id']
    #
    #     with allure.step('# 13. See result'):
    #         """
    #         Check the results of test case running.
    #         """
    #         with allure.step('# 13.1. Check message in feed point'):
    #             """
    #             Check the asynchronous_result_of_sending_the_request.
    #             """
    #             time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])
    #             time.sleep(1)
    #             GlobalClassTenderPeriodEndAuction.feed_point_message = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()
    #             allure.attach(str(GlobalClassTenderPeriodEndAuction.feed_point_message), 'Message in feed point')
    #
    #             asynchronous_result_of_expired_tender_period_end = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").tender_period_end_auction_message_is_successful(
    #                     environment=GlobalClassMetadata.environment,
    #                     kafka_message=GlobalClassTenderPeriodEndAuction.feed_point_message,
    #                     pn_ocid=GlobalClassCreatePn.pn_ocid,
    #                     ev_id=GlobalClassCreateCnOnPn.ev_id
    #                 )
    #
    #             try:
    #                 """
    #                 If asynchronous_result_of_sending_the_request was False, then return process steps by
    #                 operation-id.
    #                 """
    #                 if asynchronous_result_of_expired_tender_period_end is False:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #         with allure.step('# 13.2. Check EV release'):
    #             """
    #             Compare actual evaluation value release with expected evaluation value release model.
    #             """
    #             time.sleep(2)
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
    #                           "Actual EV release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
    #                 url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
    #                           "Actual EV release after tender period end expired")
    #             compare_releases = dict(DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ev_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ev_release))
    #
    #             expected_result = {
    #                 "values_changed": {
    #                     "root['releases'][0]['id']": {
    #                         "new_value":
    #                             f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                             f"{GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['id'][46:59]}",
    #                         "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                                      f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
    #                     },
    #                     "root['releases'][0]['date']": {
    #                         "new_value": GlobalClassTenderPeriodEndAuction.feed_point_message['data'][
    #                             'operationDate'],
    #                         "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
    #                     },
    #                     "root['releases'][0]['tag'][0]": {
    #                         'new_value': 'award',
    #                         'old_value': 'tender'
    #                     },
    #                     "root['releases'][0]['tender']['statusDetails']": {
    #                         'new_value': 'auction',
    #                         'old_value': 'clarification'
    #                     }
    #                 }
    #             }
    #
    #             try:
    #                 """
    #                     If compare_releases !=expected_result, then return process steps by operation-id.
    #                     """
    #                 if compare_releases == expected_result:
    #                     pass
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[
    #                                 'X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #
    #         with allure.step('# 13.3. Check MS release'):
    #             """
    #             Compare multistage release with expected multistage release model.
    #             """
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
    #                           "Actual MS release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
    #                           "Actual MS release after tender period end expired")
    #
    #             compare_releases = dict(DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ms_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ms_release))
    #
    #             expected_result = {}
    #             try:
    #                 """
    #                 If TestCase was passed, then cLean up the database.
    #                 If TestCase was failed, then return process steps by operation-id.
    #                 """
    #                 if compare_releases == expected_result:
    #                     GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateEi.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateFs.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreatePn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateCnOnPn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassCreateFirstBid.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         database = GlobalClassMetadata.database
    #                         steps = \
    #                             database.get_bpe_operation_step_by_operation_id_from_orchestrator(
    #                                 operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[
    #                                     'X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #
    #                 try:
    #                     """
    #                     Rollback specific value into submission.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                         value=min_bids_from_submission_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into submission.rules")
    #                 try:
    #                     """
    #                     Rollback specific value into evaluation.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                         value=min_bids_from_evaluation_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into evaluation.rules")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #
    # @allure.title("Check message from Kafka topic, EV, MS releases, "
    #               "on the flow ´Is tenderPeriodExpired -> True -> Are there bids for opening? -> True -> "
    #               "Are there unsuccessful lots? -> True -> Is tender unsuccessful? -> False -> "
    #               "Is auction started? -> True -> "
    #               "Is operationType=TenderPeriodEndAuction -> True -> Send auction message to platform."
    #               "------------------------------------------------------------------------------------"
    #               "EI: full data model with items array;"
    #               "FS: full data model, own money;"
    #               "PN: full data model, 2 lots, 2 items;"
    #               "CnOnPn: full data model with auction, 2 lots, 2 items, criteria, conversions;"
    #               "First Bid: full data model with 2 tenderers, in relation to the first lot;"
    #               "Second Bid: full data model with 2 tenderers, in relation to the first lot.")
    # def test_check_result_of_sending_the_request_five(self):
    #     with allure.step('# 1. Authorization platform one: create EI'):
    #         """
    #         Tender platform authorization for create expenditure item process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateEi.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateEi.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
    #     with allure.step('# 2. Send request to create EI'):
    #         """
    #         Send api request to BPE host for expenditure item creation.
    #         And save in variable ei_ocid.
    #         """
    #         ei_payload = copy.deepcopy(EiPreparePayload())
    #         GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model(quantity_of_tender_item_object=2)
    #         Requests().create_ei(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateEi.access_token,
    #             x_operation_id=GlobalClassCreateEi.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             payload=GlobalClassCreateEi.payload
    #         )
    #         GlobalClassCreateEi.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateEi.ei_ocid = \
    #             GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']
    #
    #         GlobalClassCreateEi.actual_ei_release = requests.get(
    #             url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateEi.ei_ocid}").json()
    #     with allure.step('# 3. Authorization platform one: create FS'):
    #         """
    #         Tender platform authorization for create financial source process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFs.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFs.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
    #     with allure.step('# 4. Send request to create FS'):
    #         """
    #         Send api request to BPE host for financial source creating.
    #         And save in variable fs_id and fs_token.
    #         """
    #         time.sleep(1)
    #         fs_payload = copy.deepcopy(FsPreparePayload())
    #         GlobalClassCreateFs.payload = fs_payload.create_fs_full_data_model_own_money()
    #         Requests().create_fs(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFs.access_token,
    #             x_operation_id=GlobalClassCreateFs.operation_id,
    #             ei_ocid=GlobalClassCreateEi.ei_ocid,
    #             payload=GlobalClassCreateFs.payload
    #         )
    #         GlobalClassCreateFs.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFs.fs_id = \
    #             GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']
    #
    #         GlobalClassCreateFs.actual_fs_release = requests.get(
    #             url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateFs.fs_id}").json()
    #     with allure.step('# 5. Authorization platform one: create PN'):
    #         """
    #         Tender platform authorization for create planning notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreatePn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreatePn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)
    #
    #     with allure.step('# 6. Send request to create PN'):
    #         """
    #         Send api request to BPE host for planning notice creating.
    #         Save asynchronous result of sending the request.
    #         Save pn_ocid and pn_token.
    #         """
    #         time.sleep(1)
    #         pn_payload = copy.deepcopy(PnPreparePayload())
    #         GlobalClassCreatePn.payload = \
    #             pn_payload.create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(
    #                 quantity_of_lot_object=2,
    #                 quantity_of_item_object=2)
    #
    #         Requests().create_pn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreatePn.access_token,
    #             x_operation_id=GlobalClassCreatePn.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             pmd=GlobalClassMetadata.pmd,
    #             payload=GlobalClassCreatePn.payload
    #         )
    #         GlobalClassCreatePn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreatePn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreatePn.pn_ocid = \
    #             GlobalClassCreatePn.feed_point_message['data']['ocid']
    #
    #         GlobalClassCreatePn.pn_id = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['id']
    #
    #         GlobalClassCreatePn.pn_token = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
    #
    #         GlobalClassCreatePn.actual_pn_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_id}").json()
    #
    #         GlobalClassCreatePn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #     with allure.step('# 7. Authorization platform one: create CnOnPn'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
    #     with allure.step('# 8. Send request to create CnOnPn'):
    #         """
    #         Send api request to for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         time.sleep(1)
    #         cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
    #         GlobalClassCreateCnOnPn.payload = \
    #             cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
    #                 enquiry_interval=121,
    #                 tender_interval=300,
    #                 quantity_of_lots_object=2,
    #                 quantity_of_items_object=2,
    #                 need_to_set_permanent_id_for_lots_array=True,
    #                 need_to_set_permanent_id_for_items_array=True,
    #                 need_to_set_permanent_id_for_documents_array=True,
    #                 based_stage_release=GlobalClassCreatePn.actual_pn_release
    #             )
    #
    #         Requests().create_cnonpn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateCnOnPn.access_token,
    #             x_operation_id=GlobalClassCreateCnOnPn.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             pn_id=GlobalClassCreatePn.pn_id,
    #             pn_token=GlobalClassCreatePn.pn_token,
    #             payload=GlobalClassCreateCnOnPn.payload
    #         )
    #
    #         GlobalClassCreateCnOnPn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateCnOnPn.ev_id = \
    #             GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']
    #
    #         GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
    #             url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #         GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #     with allure.step('# 9. Authorization platform one: create first Bid'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
    #
    #     with allure.step('# 10. Send request to create first Bid'):
    #         """
    #         Send api request to BPE host for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         try:
    #             """
    #             Set specific value into submission.rules for this testcase
    #             """
    #             min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_submission_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into submission.rules")
    #         try:
    #             """
    #             Set specific value into evaluation.rules for this testcase
    #             """
    #             min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_evaluation_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into evaluation.rules")
    #
    #         time.sleep(1)
    #         time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
    #         bid_payload_class = copy.deepcopy(BidPreparePayload())
    #         GlobalClassCreateFirstBid.payload = \
    #             bid_payload_class.create_first_bid_full_data_model_with_requirement_responses(
    #                 based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)
    #
    #         Requests().create_bid(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFirstBid.access_token,
    #             x_operation_id=GlobalClassCreateFirstBid.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             ev_id=GlobalClassCreateCnOnPn.ev_id,
    #             payload=GlobalClassCreateFirstBid.payload
    #         )
    #         GlobalClassCreateFirstBid.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFirstBid.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFirstBid.bid_id = GlobalClassCreateFirstBid.feed_point_message['data']['outcomes'][
    #             'bids'][0]['id']
    #
    #     with allure.step('# 11. Authorization platform one: create second Bid'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateSecondBid.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateSecondBid.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateSecondBid.access_token)
    #
    #     with allure.step('# 12. Send request to create second Bid'):
    #         """
    #         Send api request to BPE host for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         try:
    #             """
    #             Set specific value into submission.rules for this testcase
    #             """
    #             min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_submission_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into submission.rules")
    #         try:
    #             """
    #             Set specific value into evaluation.rules for this testcase
    #             """
    #             min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_evaluation_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into evaluation.rules")
    #
    #         time.sleep(1)
    #         time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
    #         bid_payload_class = copy.deepcopy(BidPreparePayload())
    #         GlobalClassCreateSecondBid.payload = \
    #             bid_payload_class.create_second_bid_full_data_model_with_requirement_responses(
    #                 based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release)
    #
    #         Requests().create_bid(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateSecondBid.access_token,
    #             x_operation_id=GlobalClassCreateSecondBid.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             ev_id=GlobalClassCreateCnOnPn.ev_id,
    #             payload=GlobalClassCreateSecondBid.payload
    #         )
    #         GlobalClassCreateSecondBid.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateSecondBid.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateSecondBid.bid_id = GlobalClassCreateSecondBid.feed_point_message['data']['outcomes'][
    #             'bids'][0]['id']
    #
    #     with allure.step('# 13. See result'):
    #         """
    #         Check the results of test case running.
    #         """
    #         with allure.step('# 13.1. Check message in feed point'):
    #             """
    #             Check the asynchronous_result_of_sending_the_request.
    #             """
    #             time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])
    #             time.sleep(1)
    #             GlobalClassTenderPeriodEndAuction.feed_point_message = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()
    #             allure.attach(str(GlobalClassTenderPeriodEndAuction.feed_point_message), 'Message in feed point')
    #
    #             asynchronous_result_of_expired_tender_period_end = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").tender_period_end_auction_message_is_successful(
    #                     environment=GlobalClassMetadata.environment,
    #                     kafka_message=GlobalClassTenderPeriodEndAuction.feed_point_message,
    #                     pn_ocid=GlobalClassCreatePn.pn_ocid,
    #                     ev_id=GlobalClassCreateCnOnPn.ev_id
    #                 )
    #
    #             try:
    #                 """
    #                 If asynchronous_result_of_sending_the_request was False, then return process steps by
    #                 operation-id.
    #                 """
    #                 if asynchronous_result_of_expired_tender_period_end is False:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #         with allure.step('# 13.2. Check EV release'):
    #             """
    #             Compare actual evaluation value release with expected evaluation value release model.
    #             """
    #             time.sleep(2)
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
    #                           "Actual EV release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
    #                 url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
    #                           "Actual EV release after tender period end expired")
    #
    #             compare_releases = DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ev_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ev_release)
    #             dictionary_item_added_was_cleaned = \
    #                 str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
    #             compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
    #             compare_releases = dict(compare_releases)
    #
    #             period_end_actual_ev_release = GlobalClassTenderPeriodEndAuction.actual_ev_release
    #             expected_result = {
    #                 "dictionary_item_added": "['releases'][0]['awards']",
    #                 "values_changed": {
    #                     "root['releases'][0]['id']": {
    #                         "new_value":
    #                             f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                             f"{period_end_actual_ev_release['releases'][0]['id'][46:59]}",
    #                         "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                                      f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
    #                     },
    #                     "root['releases'][0]['date']": {
    #                         "new_value": GlobalClassTenderPeriodEndAuction.feed_point_message['data'][
    #                             'operationDate'],
    #                         "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
    #                     },
    #                     "root['releases'][0]['tag'][0]": {
    #                         'new_value': 'award',
    #                         'old_value': 'tender'
    #                     },
    #                     "root['releases'][0]['tender']['statusDetails']": {
    #                         'new_value': 'auction',
    #                         'old_value': 'clarification'
    #                     },
    #                     "root['releases'][0]['tender']['lots'][1]['status']": {
    #                         "new_value": "unsuccessful",
    #                         "old_value": "active"
    #                     }
    #                 }
    #             }
    #
    #             try:
    #                 """
    #                 Check that actual_ev_release['releases'][0]['awards'][0]['id'] is uuid version 4
    #                 """
    #                 check_awards_zero_id = is_it_uuid(
    #                     uuid_to_test=GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                         'releases'][0]['awards'][0]['id'],
    #                     version=4
    #                 )
    #                 if check_awards_zero_id is True:
    #                     pass
    #                 else:
    #                     log_msg_one = f"\n{datetime.datetime.now()}\n" \
    #                                   f"File = kafka_message.py -> \n" \
    #                                   f"Class = TestTenderPeriodENdAuction -> \n" \
    #                                   f"Method = test_check_result_of_sending_the_request_five -> \n" \
    #                                   f"Actual result: check_awards_zero_id = {check_awards_zero_id} " \
    #                                   f"is not correct.\n" \
    #                                   f"Expected result: actual result must be UUID v.4\n"
    #                     with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
    #                         logfile.write(log_msg_one)
    #                     raise Exception(
    #                         "actual_ev_release['releases'][0]['awards'][0]['id'] must be uuid version 4")
    #             except KeyError:
    #                 log_msg_one = f"\n{datetime.datetime.now()}\n" \
    #                               f"File = kafka_message.py -> \n" \
    #                               f"Class = TestTenderPeriodENdAuction -> \n" \
    #                               f"Method = test_check_result_of_sending_the_request_five -> \n" \
    #                               f"KeyError: actual_ev_release['releases'][0]['awards'][0]['id']\n"
    #                 with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
    #                     logfile.write(log_msg_one)
    #                 raise KeyError("Impossible to check that actual_ev_release['releases'][0]['awards'][0]['id'] "
    #                                "is uuid version 4")
    #
    #             try:
    #                 """
    #                 Prepare expected awards array
    #                 """
    #                 expected_awards_array = TenderPeriodExpectedChanges(
    #                     environment=GlobalClassMetadata.environment,
    #                     language=GlobalClassMetadata.language).prepare_unsuccessful_awards_array()
    #             except Exception:
    #                 log_msg_one = f"\n{datetime.datetime.now()}\n" \
    #                               f"File = kafka_message.py -> \n" \
    #                               f"Class = TestTenderPeriodENdAuction -> \n" \
    #                               f"Method = test_check_result_of_sending_the_request_five -> \n" \
    #                               f"Localization: expected_awards_array\n"
    #                 with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
    #                     logfile.write(log_msg_one)
    #                 raise Exception("Impossible to prepare expected awards array")
    #
    #             try:
    #                 """
    #                     If compare_releases !=expected_result, then return process steps by operation-id.
    #                     """
    #                 if compare_releases == expected_result and expected_awards_array == \
    #                         GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
    #                     pass
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #
    #             elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'] != \
    #                     expected_awards_array:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['awards'])), "Actual awards array")
    #                 allure.attach(str(json.dumps(expected_awards_array)), "Expected awards array")
    #                 raise Exception("Error into comparing awards")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_awards_array,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']
    #             )) == str(True)
    #
    #         with allure.step('# 13.3. Check MS release'):
    #             """
    #             Compare multistage release with expected multistage release model.
    #             """
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
    #                           "Actual MS release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
    #                           "Actual MS release after tender period end expired")
    #
    #             compare_releases = dict(DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ms_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ms_release))
    #
    #             expected_result = {}
    #
    #             try:
    #                 """
    #                 If TestCase was passed, then cLean up the database.
    #                 If TestCase was failed, then return process steps by operation-id.
    #                 """
    #                 if compare_releases == expected_result:
    #                     GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateEi.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateFs.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreatePn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateCnOnPn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassCreateFirstBid.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         database = GlobalClassMetadata.database
    #                         steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[
    #                                 'X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #
    #                 try:
    #                     """
    #                     Rollback specific value into submission.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                         value=min_bids_from_submission_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into submission.rules")
    #                 try:
    #                     """
    #                     Rollback specific value into evaluation.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                         value=min_bids_from_evaluation_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into evaluation.rules")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #
    # @allure.title("Check message from Kafka topic, EV, MS releases, "
    #               "on the flow ´Is tenderPeriodExpired -> True -> Are there bids for opening? -> True -> "
    #               "Are there unsuccessful lots? -> True -> Is tender unsuccessful? -> False -> "
    #               "Is auction started? -> True -> "
    #               "Is operationType=TenderPeriodEndAuction -> True -> Send auction message to platform."
    #               "------------------------------------------------------------------------------------"
    #               "EI: obligatory data model without items array;"
    #               "FS: obligatory data model, treasury money;"
    #               "PN: obligatory data model;"
    #               "CnOnPn: obligatory data model with auction, 2 lots, 2 items;"
    #               "First Bid: obligatory data model with 1 tenderers, in relation to the first lot;"
    #               "Second Bid: obligatory data model with 1 tenderers, in relation to the first lot.")
    # def test_check_result_of_sending_the_request_six(self):
    #     with allure.step('# 1. Authorization platform one: create EI'):
    #         """
    #         Tender platform authorization for create expenditure item process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateEi.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateEi.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)
    #     with allure.step('# 2. Send request to create EI'):
    #         """
    #         Send api request to BPE host for expenditure item creation.
    #         And save in variable ei_ocid.
    #         """
    #         ei_payload = copy.deepcopy(EiPreparePayload())
    #         GlobalClassCreateEi.payload = ei_payload.create_ei_obligatory_data_model()
    #         Requests().create_ei(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateEi.access_token,
    #             x_operation_id=GlobalClassCreateEi.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             payload=GlobalClassCreateEi.payload
    #         )
    #         GlobalClassCreateEi.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateEi.ei_ocid = \
    #             GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']
    #
    #         GlobalClassCreateEi.actual_ei_release = requests.get(
    #             url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateEi.ei_ocid}").json()
    #     with allure.step('# 3. Authorization platform one: create FS'):
    #         """
    #         Tender platform authorization for create financial source process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFs.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFs.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFs.access_token)
    #     with allure.step('# 4. Send request to create FS'):
    #         """
    #         Send api request to BPE host for financial source creating.
    #         And save in variable fs_id and fs_token.
    #         """
    #         time.sleep(1)
    #         fs_payload = copy.deepcopy(FsPreparePayload())
    #         GlobalClassCreateFs.payload = fs_payload.create_fs_obligatory_data_model_treasury_money()
    #         Requests().create_fs(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFs.access_token,
    #             x_operation_id=GlobalClassCreateFs.operation_id,
    #             ei_ocid=GlobalClassCreateEi.ei_ocid,
    #             payload=GlobalClassCreateFs.payload
    #         )
    #         GlobalClassCreateFs.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFs.fs_id = \
    #             GlobalClassCreateFs.feed_point_message['data']['outcomes']['fs'][0]['id']
    #
    #         GlobalClassCreateFs.actual_fs_release = requests.get(
    #             url=f"{GlobalClassCreateFs.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateFs.fs_id}").json()
    #     with allure.step('# 5. Authorization platform one: create PN'):
    #         """
    #         Tender platform authorization for create planning notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreatePn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreatePn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreatePn.access_token)
    #
    #     with allure.step('# 6. Send request to create PN'):
    #         """
    #         Send api request to for planning notice creating.
    #         Save asynchronous result of sending the request.
    #         Save pn_ocid and pn_token.
    #         """
    #         time.sleep(1)
    #         pn_payload = copy.deepcopy(PnPreparePayload())
    #         GlobalClassCreatePn.payload = \
    #             pn_payload.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()
    #
    #         Requests().create_pn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreatePn.access_token,
    #             x_operation_id=GlobalClassCreatePn.operation_id,
    #             country=GlobalClassMetadata.country,
    #             language=GlobalClassMetadata.language,
    #             pmd=GlobalClassMetadata.pmd,
    #             payload=GlobalClassCreatePn.payload
    #         )
    #         GlobalClassCreatePn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreatePn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreatePn.pn_ocid = \
    #             GlobalClassCreatePn.feed_point_message['data']['ocid']
    #
    #         GlobalClassCreatePn.pn_id = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['id']
    #
    #         GlobalClassCreatePn.pn_token = \
    #             GlobalClassCreatePn.feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
    #
    #         GlobalClassCreatePn.actual_pn_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_id}").json()
    #
    #         GlobalClassCreatePn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #     with allure.step('# 7. Authorization platform one: create CnOnPn'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateCnOnPn.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateCnOnPn.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateCnOnPn.access_token)
    #
    #     with allure.step('# 8. Send request to create CnOnPn'):
    #         """
    #         Send api request to BPE host for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         time.sleep(1)
    #         cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
    #         GlobalClassCreateCnOnPn.payload = \
    #             cnonpn_payload_class.create_cnonpn_obligatory_data_model_with_lots_items_documents_auction(
    #                 enquiry_interval=121,
    #                 tender_interval=300,
    #                 quantity_of_lots_object=2,
    #                 quantity_of_items_object=2,
    #                 need_to_set_permanent_id_for_lots_array=False,
    #                 need_to_set_permanent_id_for_items_array=False,
    #                 need_to_set_permanent_id_for_documents_array=False,
    #                 based_stage_release=GlobalClassCreatePn.actual_pn_release
    #             )
    #
    #         Requests().create_cnonpn(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateCnOnPn.access_token,
    #             x_operation_id=GlobalClassCreateCnOnPn.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             pn_id=GlobalClassCreatePn.pn_id,
    #             pn_token=GlobalClassCreatePn.pn_token,
    #             payload=GlobalClassCreateCnOnPn.payload
    #         )
    #
    #         GlobalClassCreateCnOnPn.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateCnOnPn.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateCnOnPn.ev_id = \
    #             GlobalClassCreateCnOnPn.feed_point_message['data']['outcomes']['ev'][0]['id']
    #
    #         GlobalClassCreateCnOnPn.actual_ev_release = requests.get(
    #             url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #         GlobalClassCreateCnOnPn.actual_ms_release = requests.get(
    #             url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                 f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #     with allure.step('# 9. Authorization platform one: create first Bid'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateFirstBid.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateFirstBid.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateFirstBid.access_token)
    #
    #     with allure.step('# 10. Send request to create first Bid'):
    #         """
    #         Send api request to BPE host for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         try:
    #             """
    #             Set specific value into submission.rules for this testcase
    #             """
    #             min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_submission_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into submission.rules")
    #         try:
    #             """
    #             Set specific value into evaluation.rules for this testcase
    #             """
    #             min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_evaluation_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into evaluation.rules")
    #
    #         time.sleep(1)
    #         time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
    #         bid_payload_class = copy.deepcopy(BidPreparePayload())
    #         GlobalClassCreateFirstBid.payload = \
    #             bid_payload_class.create_first_bid_obligatory_data_model(
    #                 based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release
    #             )
    #
    #         Requests().create_bid(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateFirstBid.access_token,
    #             x_operation_id=GlobalClassCreateFirstBid.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             ev_id=GlobalClassCreateCnOnPn.ev_id,
    #             payload=GlobalClassCreateFirstBid.payload
    #         )
    #         GlobalClassCreateFirstBid.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateFirstBid.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateFirstBid.bid_id = GlobalClassCreateFirstBid.feed_point_message['data']['outcomes'][
    #             'bids'][0]['id']
    #
    #     with allure.step('# 11. Authorization platform one: create second Bid'):
    #         """
    #         Tender platform authorization for create contract notice process.
    #         As result get Tender platform's access token and process operation-id.
    #         """
    #         GlobalClassCreateSecondBid.access_token = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()
    #
    #         GlobalClassCreateSecondBid.operation_id = PlatformAuthorization(
    #             GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateSecondBid.access_token)
    #
    #     with allure.step('# 12. Send request to create second Bid'):
    #         """
    #         Send api request to BPE host for contract notice creating.
    #         Save asynchronous result of sending the request.
    #         """
    #         try:
    #             """
    #             Set specific value into submission.rules for this testcase
    #             """
    #             min_bids_from_submission_rules = GlobalClassMetadata.database.get_min_bids_from_submission_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_submission_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into submission.rules")
    #         try:
    #             """
    #             Set specific value into evaluation.rules for this testcase
    #             """
    #             min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
    #                 country=GlobalClassMetadata.country,
    #                 pmd=GlobalClassMetadata.pmd,
    #                 operation_type='all',
    #                 parameter='minBids'
    #             )
    #             if min_bids_from_evaluation_rules != "1":
    #                 GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                     value='1',
    #                     country=GlobalClassMetadata.country,
    #                     pmd=GlobalClassMetadata.pmd,
    #                     operation_type='all',
    #                     parameter='minBids'
    #                 )
    #             else:
    #                 pass
    #         except Exception:
    #             raise Exception("Impossible to set specific value into evaluation.rules")
    #
    #         time.sleep(1)
    #         time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
    #         bid_payload_class = copy.deepcopy(BidPreparePayload())
    #         GlobalClassCreateSecondBid.payload = \
    #             bid_payload_class.create_second_bid_obligatory_data_model(
    #                 based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release
    #             )
    #
    #         Requests().create_bid(
    #             host_of_request=GlobalClassMetadata.host_for_bpe,
    #             access_token=GlobalClassCreateSecondBid.access_token,
    #             x_operation_id=GlobalClassCreateSecondBid.operation_id,
    #             pn_ocid=GlobalClassCreatePn.pn_ocid,
    #             ev_id=GlobalClassCreateCnOnPn.ev_id,
    #             payload=GlobalClassCreateSecondBid.payload
    #         )
    #         GlobalClassCreateSecondBid.feed_point_message = \
    #             KafkaMessage(GlobalClassCreateSecondBid.operation_id).get_message_from_kafka()
    #
    #         GlobalClassCreateSecondBid.bid_id = GlobalClassCreateSecondBid.feed_point_message['data']['outcomes'][
    #             'bids'][0]['id']
    #
    #     with allure.step('# 13. See result'):
    #         """
    #         Check the results of test case running.
    #         """
    #         with allure.step('# 13.1. Check message in feed point'):
    #             """
    #             Check the asynchronous_result_of_sending_the_request.
    #             """
    #             time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])
    #             time.sleep(1)
    #             GlobalClassTenderPeriodEndAuction.feed_point_message = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()
    #             allure.attach(str(GlobalClassTenderPeriodEndAuction.feed_point_message), 'Message in feed point')
    #
    #             asynchronous_result_of_expired_tender_period_end = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").tender_period_end_auction_message_is_successful(
    #                     environment=GlobalClassMetadata.environment,
    #                     kafka_message=GlobalClassTenderPeriodEndAuction.feed_point_message,
    #                     pn_ocid=GlobalClassCreatePn.pn_ocid,
    #                     ev_id=GlobalClassCreateCnOnPn.ev_id
    #                 )
    #
    #             try:
    #                 """
    #                 If asynchronous_result_of_sending_the_request was False, then return process steps by
    #                 operation-id.
    #                 """
    #                 if asynchronous_result_of_expired_tender_period_end is False:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #         with allure.step('# 13.2. Check EV release'):
    #             """
    #             Compare actual evaluation value release with expected evaluation value release model.
    #             """
    #             time.sleep(2)
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
    #                           "Actual EV release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ev_release = requests.get(
    #                 url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release)),
    #                           "Actual EV release after tender period end expired")
    #
    #             compare_releases = DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ev_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ev_release)
    #             dictionary_item_added_was_cleaned = \
    #                 str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
    #             compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
    #             compare_releases = dict(compare_releases)
    #
    #             period_end_actual_ev_release = GlobalClassTenderPeriodEndAuction.actual_ev_release
    #             expected_result = {
    #                 "dictionary_item_added": "['releases'][0]['awards']",
    #                 "values_changed": {
    #                     "root['releases'][0]['id']": {
    #                         "new_value":
    #                             f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                             f"{period_end_actual_ev_release['releases'][0]['id'][46:59]}",
    #                         "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                                      f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
    #                     },
    #                     "root['releases'][0]['date']": {
    #                         "new_value": GlobalClassTenderPeriodEndAuction.feed_point_message['data'][
    #                             'operationDate'],
    #                         "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
    #                     },
    #                     "root['releases'][0]['tag'][0]": {
    #                         'new_value': 'award',
    #                         'old_value': 'tender'
    #                     },
    #                     "root['releases'][0]['tender']['statusDetails']": {
    #                         'new_value': 'auction',
    #                         'old_value': 'clarification'
    #                     },
    #                     "root['releases'][0]['tender']['lots'][1]['status']": {
    #                         "new_value": "unsuccessful",
    #                         "old_value": "active"
    #                     }
    #                 }
    #             }
    #
    #             try:
    #                 """
    #                 Check that actual_ev_release['releases'][0]['awards'][0]['id'] is uuid version 4
    #                 """
    #                 check_awards_zero_id = is_it_uuid(
    #                     uuid_to_test=GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                         'releases'][0]['awards'][0]['id'],
    #                     version=4
    #                 )
    #                 if check_awards_zero_id is True:
    #                     pass
    #                 else:
    #                     log_msg_one = f"\n{datetime.datetime.now()}\n" \
    #                                   f"File = kafka_message.py -> \n" \
    #                                   f"Class = TestTenderPeriodENdAuction -> \n" \
    #                                   f"Method = test_check_result_of_sending_the_request_five -> \n" \
    #                                   f"Actual result: check_awards_zero_id = {check_awards_zero_id} " \
    #                                   f"is not correct.\n" \
    #                                   f"Expected result: actual result must be UUID v.4\n"
    #                     with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
    #                         logfile.write(log_msg_one)
    #                     raise Exception(
    #                         "actual_ev_release['releases'][0]['awards'][0]['id'] must be uuid version 4")
    #             except KeyError:
    #                 log_msg_one = f"\n{datetime.datetime.now()}\n" \
    #                               f"File = kafka_message.py -> \n" \
    #                               f"Class = TestTenderPeriodENdAuction -> \n" \
    #                               f"Method = test_check_result_of_sending_the_request_five -> \n" \
    #                               f"KeyError: actual_ev_release['releases'][0]['awards'][0]['id']\n"
    #                 with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
    #                     logfile.write(log_msg_one)
    #                 raise KeyError("Impossible to check that actual_ev_release['releases'][0]['awards'][0]['id'] "
    #                                "is uuid version 4")
    #
    #             try:
    #                 """
    #                 Prepare expected awards array
    #                 """
    #                 expected_awards_array = TenderPeriodExpectedChanges(
    #                     environment=GlobalClassMetadata.environment,
    #                     language=GlobalClassMetadata.language).prepare_unsuccessful_awards_array()
    #             except Exception:
    #                 log_msg_one = f"\n{datetime.datetime.now()}\n" \
    #                               f"File = kafka_message.py -> \n" \
    #                               f"Class = TestTenderPeriodENdAuction -> \n" \
    #                               f"Method = test_check_result_of_sending_the_request_five -> \n" \
    #                               f"Localization: expected_awards_array\n"
    #                 with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
    #                     logfile.write(log_msg_one)
    #                 raise Exception("Impossible to prepare expected awards array")
    #
    #             try:
    #                 """
    #                     If compare_releases !=expected_result, then return process steps by operation-id.
    #                     """
    #                 if compare_releases == expected_result and expected_awards_array == \
    #                         GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']:
    #                     pass
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #
    #             elif GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards'] != \
    #                     expected_awards_array:
    #                 allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ev_release[
    #                                                  'releases'][0]['awards'])), "Actual awards array")
    #                 allure.attach(str(json.dumps(expected_awards_array)), "Expected awards array")
    #                 raise Exception("Error into comparing awards")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_awards_array,
    #                 actual_result=GlobalClassTenderPeriodEndAuction.actual_ev_release['releases'][0]['awards']
    #             )) == str(True)
    #
    #         with allure.step('# 13.3. Check MS release'):
    #             """
    #             Compare multistage release with expected multistage release model.
    #             """
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
    #                           "Actual MS release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndAuction.actual_ms_release)),
    #                           "Actual MS release after tender period end expired")
    #
    #             compare_releases = dict(DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ms_release,
    #                 GlobalClassTenderPeriodEndAuction.actual_ms_release))
    #
    #             expected_result = {}
    #
    #             try:
    #                 """
    #                 If TestCase was passed, then cLean up the database.
    #                 If TestCase was failed, then return process steps by operation-id.
    #                 """
    #                 if compare_releases == expected_result:
    #                     GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
    #                         ei_id=GlobalClassCreateEi.ei_ocid)
    #
    #                     GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
    #                         pn_ocid=GlobalClassCreatePn.pn_ocid)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateEi.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateFs.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreatePn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process(
    #                         operation_id=GlobalClassCreateCnOnPn.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassCreateFirstBid.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message['X-OPERATION-ID'])
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         database = GlobalClassMetadata.database
    #                         steps = database.get_bpe_operation_step_by_operation_id_from_orchestrator(
    #                             operation_id=GlobalClassTenderPeriodEndAuction.feed_point_message[
    #                                 'X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #
    #                 try:
    #                     """
    #                     Rollback specific value into submission.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_submission_rules(
    #                         value=min_bids_from_submission_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into submission.rules")
    #                 try:
    #                     """
    #                     Rollback specific value into evaluation.rules
    #                     """
    #                     GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
    #                         value=min_bids_from_evaluation_rules,
    #                         country=GlobalClassMetadata.country,
    #                         pmd=GlobalClassMetadata.pmd,
    #                         operation_type='all',
    #                         parameter='minBids'
    #                     )
    #                 except Exception:
    #                     raise Exception("Impossible to rollback specific value into evaluation.rules")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             if expected_result != compare_releases:
    #                 allure.attach(str(json.dumps(compare_releases)), "Actual comparing releases")
    #                 allure.attach(str(json.dumps(expected_result)), "Expected comparing releases")
    #                 raise Exception("Error into comparing releases")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
