import copy
import json
import time
import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassMetadata, GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, \
    GlobalClassCreateCnOnPn, GlobalClassCreateBid, GlobalClassTenderPeriodEndNoAuction
from tests.utils.PayloadModel.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.EI.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.FS.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.PN.pn_prepared_payload import PnPreparePayload
from tests.utils.PayloadModel.SubmitBid.bid_prepared_payload import BidPreparePayload
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.functions import compare_actual_result_and_expected_result, time_bot, is_it_uuid
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.requests import Requests


@allure.parent_suite('Awarding')
@allure.suite('Tender period end no auction')
@allure.sub_suite('BPE: ')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=274880742',
                 name='Google sheets: Tender period end no auction')
class TestCreateBid:
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

    # @allure.title('Check message from Kafka topic, EV, MS releases if tender period expired without any bids')
    # def test_check_result_of_sending_the_request_one(self):
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
    #         Send api request on BPE host for expenditure item creation.
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
    #         Send api request on BPE host for financial source creating.
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
    #         Send api request on BPE host for planning notice creating.
    #         Save synchronous result of sending the request and asynchronous result of sending the request.
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
    #         Send api request on BPE host for contract notice creating.
    #         Save synchronous result of sending the request and asynchronous result of sending the request.
    #         """
    #         time.sleep(1)
    #         cnonpn_payload_class = copy.deepcopy(CnOnPnPreparePayload())
    #         GlobalClassCreateCnOnPn.payload = \
    #             cnonpn_payload_class.create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv(
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
    #     with allure.step('# 9. See result'):
    #         """
    #         Check the results of TestCase.
    #         """
    #         with allure.step('# 9.1. Check message in feed point'):
    #             """
    #             Check the asynchronous_result_of_sending_the_request.
    #             """
    #             time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])
    #             time.sleep(1)
    #             GlobalClassTenderPeriodEndNoAuction.feed_point_message = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()
    #             allure.attach(str(GlobalClassTenderPeriodEndNoAuction.feed_point_message), 'Message in feed point')
    #
    #             asynchronous_result_of_expired_tender_period_end = \
    #                 KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
    #                              initiation="bpe").tender_period_end_message_is_successful(
    #                     environment=GlobalClassMetadata.environment,
    #                     kafka_message=GlobalClassTenderPeriodEndNoAuction.feed_point_message,
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
    #                             operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message['X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #         with allure.step('# 9.2. Check EV release'):
    #             """
    #             Compare actual evaluation value release with expected evaluation value release model.
    #             """
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
    #                           "Actual EV release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndNoAuction.actual_ev_release = requests.get(
    #                 url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreateCnOnPn.ev_id}").json()
    #
    #             GlobalClassTenderPeriodEndNoAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndNoAuction.actual_ev_release)),
    #                           "Actual EV release after tender period end expired")
    #
    #             compare_releases = DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ev_release, GlobalClassTenderPeriodEndNoAuction.actual_ev_release)
    #             dictionary_item_added_was_cleaned = \
    #                 str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
    #             compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
    #             compare_releases = dict(compare_releases)
    #
    #             expected_result = {
    #                 "dictionary_item_added": "['releases'][0]['awards']",
    #                 "values_changed": {
    #                     "root['releases'][0]['id']": {
    #                         "new_value":
    #                             f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                             f"{GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['id'][46:59]}",
    #                         "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
    #                                      f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
    #                     },
    #                     "root['releases'][0]['date']": {
    #                         "new_value": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data'][
    #                             'operationDate'],
    #                         "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
    #                     },
    #                     "root['releases'][0]['tag'][0]": {
    #                         "new_value": "tenderCancellation",
    #                         "old_value": "tender"
    #                     },
    #                     "root['releases'][0]['tender']['status']": {
    #                         "new_value": "unsuccessful",
    #                         "old_value": "active"
    #                     },
    #                     "root['releases'][0]['tender']['statusDetails']": {
    #                         "new_value": "empty",
    #                         "old_value": "clarification"
    #                     },
    #                     "root['releases'][0]['tender']['lots'][0]['status']": {
    #                         "new_value": "unsuccessful",
    #                         "old_value": "active"
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
    #                     If compare_releases !=expected_result, then return process steps by operation-id.
    #                     """
    #                 if compare_releases == expected_result:
    #                     pass
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
    #                             operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message['X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)
    #
    #         with allure.step('# 9.3. Check MS release'):
    #             """
    #             Compare multistage release with expected multistage release model.
    #             """
    #             allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
    #                           "Actual MS release before tender period end expired")
    #
    #             GlobalClassTenderPeriodEndNoAuction.actual_ms_release = requests.get(
    #                 url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
    #                     f"{GlobalClassCreatePn.pn_ocid}").json()
    #
    #             allure.attach(str(json.dumps(GlobalClassTenderPeriodEndNoAuction.actual_ms_release)),
    #                           "Actual MS release after tender period end expired")
    #
    #             compare_releases = dict(DeepDiff(
    #                 GlobalClassCreateCnOnPn.actual_ms_release,
    #                 GlobalClassTenderPeriodEndNoAuction.actual_ms_release))
    #
    #             expected_result = {
    #                 "values_changed": {
    #                     "root['releases'][0]['id']": {
    #                         "new_value":
    #                             f"{GlobalClassCreatePn.pn_ocid}-"
    #                             f"{GlobalClassTenderPeriodEndNoAuction.actual_ms_release['releases'][0]['id'][29:42]}",
    #                         "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
    #                                      f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}"
    #                     },
    #                     "root['releases'][0]['date']": {
    #                         "new_value": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data'][
    #                             'operationDate'],
    #                         "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
    #                     },
    #                     "root['releases'][0]['tender']['status']": {
    #                         "new_value": "unsuccessful",
    #                         "old_value": "active"
    #                     },
    #                     "root['releases'][0]['tender']['statusDetails']": {
    #                         "new_value": "empty",
    #                         "old_value": "evaluation"
    #                     }
    #                 }
    #             }
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
    #                         operation_id=GlobalClassCreateBid.operation_id)
    #
    #                     GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
    #                         operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message['X-OPERATION-ID'])
    #                 else:
    #                     with allure.step('# Steps from Casandra DataBase'):
    #                         steps = \
    #                             GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id_from_orchestrator(
    #                                 operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message[
    #                                     'X-OPERATION-ID'])
    #                         allure.attach(steps, "Cassandra DataBase: steps of process")
    #             except ValueError:
    #                 raise ValueError("Can not return BPE operation step")
    #
    #             assert str(compare_actual_result_and_expected_result(
    #                 expected_result=expected_result,
    #                 actual_result=compare_releases
    #             )) == str(True)

    @allure.title('Check message from Kafka topic, EV, MS releases if '
                  'Are there bids for opening? -> True -> Are there unsuccessful lots? -> False -> '
                  'Is tender unsuccessful? -> True')
    def test_check_result_of_sending_the_request_two(self):
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
            Send api request on BPE host for expenditure item creation.
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
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
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
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
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
        with allure.step('# 8. Send request to create CnOnPn'):
            """
            Send api request on BPE host for contract notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
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

        with allure.step('# 9. Authorization platform one: create Bid'):
            """
            Tender platform authorization for create contract notice process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateBid.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateBid.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateBid.access_token)

        with allure.step('# 10. Send request to create Bid'):
            """
            Send api request on BPE host for contract notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            try:
                """
                Set specific value into evaluation.rules for this testcase
                """
                min_bids_from_evaluation_rules = GlobalClassMetadata.database.get_min_bids_from_evaluation_rules(
                    country=GlobalClassMetadata.country,
                    pmd=GlobalClassMetadata.pmd,
                    operation_type='all',
                    parameter='minBids'
                )
                if min_bids_from_evaluation_rules == "1":
                    GlobalClassMetadata.database.set_min_bids_from_evaluation_rules(
                        value='2',
                        country=GlobalClassMetadata.country,
                        pmd=GlobalClassMetadata.pmd,
                        operation_type='all',
                        parameter='minBids'
                    )
                else:
                    pass
            except Exception:
                raise Exception("Impossible to set specific value into evaluation.rules")

            time.sleep(1)
            time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate'])
            bid_payload_class = copy.deepcopy(BidPreparePayload())
            GlobalClassCreateBid.payload = \
                bid_payload_class.create_bid_full_data_model(
                    based_stage_release=GlobalClassCreateCnOnPn.actual_ev_release
                )

            Requests().create_bid(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateBid.access_token,
                x_operation_id=GlobalClassCreateBid.operation_id,
                pn_ocid=GlobalClassCreatePn.pn_ocid,
                ev_id=GlobalClassCreateCnOnPn.ev_id,
                payload=GlobalClassCreateBid.payload
            )

        with allure.step('# 11. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 11.1. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                time_bot(expected_time=GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate'])
                time.sleep(1)
                GlobalClassTenderPeriodEndNoAuction.feed_point_message = \
                    KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                                 initiation="bpe").get_message_from_kafka_by_ocid_and_initiator()

                allure.attach(str(GlobalClassTenderPeriodEndNoAuction.feed_point_message), 'Message in feed point')

                asynchronous_result_of_expired_tender_period_end = \
                    KafkaMessage(ocid=GlobalClassCreateCnOnPn.ev_id,
                                 initiation="bpe").tender_period_end_message_is_successful(
                        environment=GlobalClassMetadata.environment,
                        kafka_message=GlobalClassTenderPeriodEndNoAuction.feed_point_message,
                        pn_ocid=GlobalClassCreatePn.pn_ocid,
                        ev_id=GlobalClassCreateCnOnPn.ev_id
                    )

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_expired_tender_period_end is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message['X-OPERATION-ID'])
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

            with allure.step('# 11.2. Check EV release'):
                """
                Compare actual evaluation value release with expected evaluation value release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release)),
                              "Actual EV release before tender period end expired")

                GlobalClassTenderPeriodEndNoAuction.actual_ev_release = requests.get(
                    url=f"{GlobalClassCreateCnOnPn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateCnOnPn.ev_id}").json()

                GlobalClassTenderPeriodEndNoAuction.actual_ms_release = requests.get(
                    url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreatePn.pn_ocid}").json()

                allure.attach(str(json.dumps(GlobalClassTenderPeriodEndNoAuction.actual_ev_release)),
                              "Actual EV release after tender period end expired")

                # print("Actual EV release before tender period end expired")
                # print(json.dumps(GlobalClassCreateCnOnPn.actual_ev_release))
                # print("Actual EV release after tender period end expired")
                # print(json.dumps(GlobalClassTenderPeriodEndNoAuction.actual_ev_release))
                compare_releases = DeepDiff(
                    GlobalClassCreateCnOnPn.actual_ev_release, GlobalClassTenderPeriodEndNoAuction.actual_ev_release)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)
                # print("DEEPDIFF")
                # print(compare_releases)

                print("BID PAYLOAD")
                print(json.dumps(GlobalClassCreateBid.payload))
                expected_result = {
                    "dictionary_item_added": "['releases'][0]['parties'], "
                                             "['releases'][0]['awards'], "
                                             "['releases'][0]['bids']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{GlobalClassCreateCnOnPn.ev_id}-"
                                f"{GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['id'][46:59]}",
                            "old_value": f"{GlobalClassCreateCnOnPn.ev_id}-"
                                         f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data'][
                                'operationDate'],
                            "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            'new_value': 'tenderCancellation',
                            'old_value': 'tender'
                        },
                        "root['releases'][0]['tender']['status']": {
                            'new_value': 'unsuccessful',
                            'old_value': 'active'
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            'new_value': 'empty',
                            'old_value': 'clarification'
                        },
                        "root['releases'][0]['tender']['lots'][0]['status']": {
                            'new_value': 'unsuccessful',
                            'old_value': 'active'
                        }
                    }
                }

                try:
                    """
                    Prepare expected parties array
                    """
                    expected_parties_array = [
                        {
                            "id": f"{GlobalClassCreateBid.payload['bid']['tenderers'][0]['identifier']['scheme']}-"
                                  f"{GlobalClassCreateBid.payload['bid']['tenderers'][0]['identifier']['id']}",
                            "name": GlobalClassCreateBid.payload['bid']['tenderers'][0]['name'],
                            "identifier": {
                                "scheme": GlobalClassCreateBid.payload['bid']['tenderers'][0]['identifier']['scheme'],
                                "id": GlobalClassCreateBid.payload['bid']['tenderers'][0]['identifier']['id'],
                                "uri": GlobalClassCreateBid.payload['bid']['tenderers'][0]['identifier']['uri']
                            },
                            "address": {
                                "streetAddress": GlobalClassCreateBid.payload['bid']['tenderers'][0]['address'][
                                    'streetAddress'],
                                "postalCode": GlobalClassCreateBid.payload['bid']['tenderers'][0]['address'][
                                    'postalCode'],
                                "addressDetails": {
                                    "country": {
                                        "scheme": "ISO-ALPHA2",
                                        "id": "MD",
                                        "description": "Moldova, Republica",
                                        "uri": "http://reference.iatistandard.org"
                                    },
                                    "region": {
                                        "scheme": "CUATM",
                                        "id": "1700000",
                                        "description": "Cahul",
                                        "uri": "http://statistica.md"
                                    },
                                    "locality": {
                                        "scheme": "tenderers.address.addressDetails.locality.scheme: 0",
                                        "id": "1701000",
                                        "description": "tenderers.address.addressDetails.locality.description: 0"
                                    }
                                }
                            },
                            "additionalIdentifiers": [
                                {
                                    "scheme": "tenderers.additionalIdentifiers.scheme: 0.0",
                                    "id": "tenderers.additionalIdentifiers.id: 0.0",
                                    "uri": "tenderers.additionalIdentifiers.uri: 0.0"
                                },
                                {
                                    "scheme": "tenderers.additionalIdentifiers.scheme: 0.1",
                                    "id": "tenderers.additionalIdentifiers.id: 0.1",
                                    "uri": "tenderers.additionalIdentifiers.uri: 0.1"
                                }],
                            "contactPoint": {
                                "name": "tenderers.contactPoint.name: 0",
                                "email": "tenderers.contactPoint.email: 0",
                                "telephone": "tenderers.contactPoint.telephone: 0",
                                "faxNumber": "tenderers.contactPoint.faxNumber: 0",
                                "url": "tenderers.contactPoint.url: 0"
                            },
                            "details": {
                                "typeOfSupplier": "company",
                                "mainEconomicActivities": [
                                    {
                                        "scheme": "tenderers.details.mainEconomicActivities.scheme': 0.0",
                                        "id": "tenderers.details.mainEconomicActivities.id': 0.0",
                                        "description": "tenderers.details.mainEconomicActivities.description': 0.0",
                                        "uri": "tenderers.details.mainEconomicActivities.uri': 0.0"
                                    },
                                    {
                                        "scheme": "tenderers.details.mainEconomicActivities.scheme': 0.1",
                                        "id": "tenderers.details.mainEconomicActivities.id': 0.1",
                                        "description": "tenderers.details.mainEconomicActivities.description': 0.1",
                                        "uri": "tenderers.details.mainEconomicActivities.uri': 0.1"
                                    }],
                                "permits": [
                                    {
                                        "id": "tenderers.details.permits.id': 0.0",
                                        "scheme": "tenderers.details.permits.scheme': 0.0",
                                        "url": "tenderers.details.permits.url': 0.0",
                                        "permitDetails": {
                                            "issuedBy": {
                                                "id": "tenderers.details.permits.permitDetails.issueBy.id': 0.0",
                                                "name": "tenderers.details.permits.permitDetails.issueBy.id': 0.0"
                                            },
                                            "issuedThought": {
                                                "id": "tenderers.details.permits.permitDetails.issuedThought.id': 0.0",
                                                "name": "tenderers.details.permits.permitDetails.issuedThought.id': 0.0"
                                            },
                                            "validityPeriod": {
                                                "startDate": "2021-12-24T15:42:53Z",
                                                "endDate": "2022-01-13T15:42:53Z"
                                            }
                                        }
                                    },
                                    {
                                        "id": "tenderers.details.permits.id': 0.1",
                                        "scheme": "tenderers.details.permits.scheme': 0.1",
                                        "url": "tenderers.details.permits.url': 0.1",
                                        "permitDetails": {
                                            "issuedBy": {
                                                "id": "tenderers.details.permits.permitDetails.issueBy.id': 0.1",
                                                "name": "tenderers.details.permits.permitDetails.issueBy.id': 0.1"
                                            },
                                            "issuedThought": {
                                                "id": "tenderers.details.permits.permitDetails.issuedThought.id': 0.1",
                                                "name": "tenderers.details.permits.permitDetails.issuedThought.id': 0.1"
                                            },
                                            "validityPeriod": {
                                                "startDate": "2021-12-24T15:42:53Z",
                                                "endDate": "2022-01-13T15:42:53Z"
                                            }
                                        }
                                    }],
                                "bankAccounts": [
                                    {
                                        "description": "tenderers.details.bankAccounts.description.: 0.0",
                                        "bankName": "tenderers.details.bankAccounts.bankName.: 0.0",
                                        "address": {
                                            "streetAddress": "tenderers.details.bankAccounts.address.streetAddress.: 0.0",
                                            "postalCode": "tenderers.details.bankAccounts.address.postalCode.: 0.0",
                                            "addressDetails": {
                                                "country": {
                                                    "scheme": "ISO-ALPHA2",
                                                    "id": "MD",
                                                    "description": "Moldova, Republica",
                                                    "uri": "http://reference.iatistandard.org"
                                                },
                                                "region": {
                                                    "scheme": "CUATM",
                                                    "id": "1700000",
                                                    "description": "Cahul",
                                                    "uri": "http://statistica.md"
                                                },
                                                "locality": {
                                                    "scheme": "tenderers.details.bankAccounts.address.addressDetails.locality.scheme.: 0.0",
                                                    "id": "1701000",
                                                    "description": "tenderers.details.bankAccounts.address.addressDetails.locality.description.: 0.0"
                                                }
                                            }
                                        },
                                        "identifier": {
                                            "id": "tenderers.details.bankAccounts.address.identifier.id: 0.0",
                                            "scheme": "UA-MFO"
                                        },
                                        "accountIdentification": {
                                            "id": "tenderers.details.bankAccounts.address.accountIdentification.id: 0.0",
                                            "scheme": "IBAN"
                                        },
                                        "additionalAccountIdentifiers": [
                                            {
                                                "id": "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 0.0.0",
                                                "scheme": "fiscal"
                                            },
                                            {
                                                "id": "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 0.0.1",
                                                "scheme": "fiscal"
                                            }]
                                    },
                                    {
                                        "description": "tenderers.details.bankAccounts.description.: 0.1",
                                        "bankName": "tenderers.details.bankAccounts.bankName.: 0.1",
                                        "address": {
                                            "streetAddress": "tenderers.details.bankAccounts.address.streetAddress.: 0.1",
                                            "postalCode": "tenderers.details.bankAccounts.address.postalCode.: 0.1",
                                            "addressDetails": {
                                                "country": {
                                                    "scheme": "ISO-ALPHA2",
                                                    "id": "MD",
                                                    "description": "Moldova, Republica",
                                                    "uri": "http://reference.iatistandard.org"
                                                },
                                                "region": {
                                                    "scheme": "CUATM",
                                                    "id": "1700000",
                                                    "description": "Cahul",
                                                    "uri": "http://statistica.md"
                                                },
                                                "locality": {
                                                    "scheme": "tenderers.details.bankAccounts.address.addressDetails.locality.scheme.: 0.1",
                                                    "id": "1701000",
                                                    "description": "tenderers.details.bankAccounts.address.addressDetails.locality.description.: 0.1"
                                                }
                                            }
                                        },
                                        "identifier": {
                                            "id": "tenderers.details.bankAccounts.address.identifier.id: 0.1",
                                            "scheme": "UA-MFO"
                                        },
                                        "accountIdentification": {
                                            "id": "tenderers.details.bankAccounts.address.accountIdentification.id: 0.0",
                                            "scheme": "IBAN"
                                        },
                                        "additionalAccountIdentifiers": [
                                            {
                                                "id": "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 0.1.0",
                                                "scheme": "fiscal"
                                            },
                                            {
                                                "id": "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 0.1.1",
                                                "scheme": "fiscal"
                                            }]
                                    }],
                                "legalForm": {
                                    "id": "tenderers.details.details.legalForm.id: 0.",
                                    "scheme": "MD-CFOJ",
                                    "description": "tenderers.details.details.legalForm.scheme: 0.",
                                    "uri": "tenderers.details.details.legalForm.uri: 0."
                                },
                                "scale": "micro"
                            },
                            "persones": [
                                {
                                    "id": "MD-IDNO-tenderers.persones.identifier.id: 0.0",
                                    "title": "Mr.",
                                    "name": "tenderers.persones.name: 0.0",
                                    "identifier": {
                                        "scheme": "MD-IDNO",
                                        "id": "tenderers.persones.identifier.id: 0.0",
                                        "uri": "tenderers.persones.identifier.uri: 0.0"
                                    },
                                    "businessFunctions": [
                                        {
                                            "id": "b29aeebd-3750-4d8c-8a27-a2293a48c565",
                                            "type": "authority",
                                            "jobTitle": "tenderers.persones.businessFunctions.jobTitle.id: 0.0.0",
                                            "period": {
                                                "startDate": "2021-10-25T15:42:53Z"
                                            },
                                            "documents": [
                                                {
                                                    "id": "fcc1ff06-703a-4e05-aceb-9510827956d2-1635165768078",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.0.0.0",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.0.0.0",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/fcc1ff06-703a-4e05-aceb-9510827956d2-1635165768078",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                },
                                                {
                                                    "id": "e54ff675-4e00-43e4-bf46-3b2508f8dc9b-1635165769522",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.0.0.1",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.0.0.1",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/e54ff675-4e00-43e4-bf46-3b2508f8dc9b-1635165769522",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                }]
                                        },
                                        {
                                            "id": "f5da9f51-b4cc-4db2-8f8d-f1497555da96",
                                            "type": "contactPoint",
                                            "jobTitle": "tenderers.persones.businessFunctions.jobTitle.id: 0.0.1",
                                            "period": {
                                                "startDate": "2021-10-25T15:42:53Z"
                                            },
                                            "documents": [
                                                {
                                                    "id": "e7d19693-2bf3-4cf5-b2d3-4e3bda402fa3-1635165770009",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.0.1.0",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.0.1.0",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/e7d19693-2bf3-4cf5-b2d3-4e3bda402fa3-1635165770009",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                },
                                                {
                                                    "id": "68703c8c-b5bb-4644-8cdc-55776fda35ec-1635165770460",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.0.1.1",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.0.1.1",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/68703c8c-b5bb-4644-8cdc-55776fda35ec-1635165770460",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                }]
                                        }]
                                },
                                {
                                    "id": "MD-IDNO-tenderers.persones.identifier.id: 0.1",
                                    "title": "Ms.",
                                    "name": "tenderers.persones.name: 0.1",
                                    "identifier": {
                                        "scheme": "MD-IDNO",
                                        "id": "tenderers.persones.identifier.id: 0.1",
                                        "uri": "tenderers.persones.identifier.uri: 0.1"
                                    },
                                    "businessFunctions": [
                                        {
                                            "id": "ced4024e-93db-4711-80e3-787d34e94552",
                                            "type": "contactPoint",
                                            "jobTitle": "tenderers.persones.businessFunctions.jobTitle.id: 0.1.0",
                                            "period": {
                                                "startDate": "2021-10-25T15:42:53Z"
                                            },
                                            "documents": [
                                                {
                                                    "id": "8dc46f27-329f-4d97-98b4-aeacfc2dff1e-1635165770957",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.1.0.0",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.1.0.0",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/8dc46f27-329f-4d97-98b4-aeacfc2dff1e-1635165770957",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                },
                                                {
                                                    "id": "5429d41c-88a1-4f2e-8dff-6cc974b35641-1635165771349",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.1.0.1",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.1.0.1",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/5429d41c-88a1-4f2e-8dff-6cc974b35641-1635165771349",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                }]
                                        },
                                        {
                                            "id": "5f065397-1f02-478e-a837-6ba2a5ca2663",
                                            "type": "contactPoint",
                                            "jobTitle": "tenderers.persones.businessFunctions.jobTitle.id: 0.1.1",
                                            "period": {
                                                "startDate": "2021-10-25T15:42:53Z"
                                            },
                                            "documents": [
                                                {
                                                    "id": "eaee36ad-586a-43df-886f-aeaa4e5f6902-1635165771711",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.1.1.0",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.1.1.0",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/eaee36ad-586a-43df-886f-aeaa4e5f6902-1635165771711",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                },
                                                {
                                                    "id": "ab395557-0eda-43b1-b0c1-ea739b38ceeb-1635165772259",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.1.1.1",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.1.1.1",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/ab395557-0eda-43b1-b0c1-ea739b38ceeb-1635165772259",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                }]
                                        }]
                                }],
                            "roles": [
                                "tenderer"]
                        },
                        {
                            "id": "MD-IDNO-tenderers.identifier.id: 1",
                            "name": "tenderers.name: 1",
                            "identifier": {
                                "scheme": "MD-IDNO",
                                "id": "tenderers.identifier.id: 1",
                                "uri": "tenderers.identifier.uri: 1"
                            },
                            "address": {
                                "streetAddress": "tenderers.address.streetAddress: 1",
                                "postalCode": "tenderers.address.postalCode: 1",
                                "addressDetails": {
                                    "country": {
                                        "scheme": "ISO-ALPHA2",
                                        "id": "MD",
                                        "description": "Moldova, Republica",
                                        "uri": "http://reference.iatistandard.org"
                                    },
                                    "region": {
                                        "scheme": "CUATM",
                                        "id": "1700000",
                                        "description": "Cahul",
                                        "uri": "http://statistica.md"
                                    },
                                    "locality": {
                                        "scheme": "tenderers.address.addressDetails.locality.scheme: 1",
                                        "id": "1701000",
                                        "description": "tenderers.address.addressDetails.locality.description: 1"
                                    }
                                }
                            },
                            "additionalIdentifiers": [
                                {
                                    "scheme": "tenderers.additionalIdentifiers.scheme: 0.0",
                                    "id": "tenderers.additionalIdentifiers.id: 1.0",
                                    "uri": "tenderers.additionalIdentifiers.uri: 0.0"
                                },
                                {
                                    "scheme": "tenderers.additionalIdentifiers.scheme: 1.1",
                                    "id": "tenderers.additionalIdentifiers.id: 1.1",
                                    "uri": "tenderers.additionalIdentifiers.uri: 1.1"
                                }],
                            "contactPoint": {
                                "name": "tenderers.contactPoint.name: 1",
                                "email": "tenderers.contactPoint.email: 1",
                                "telephone": "tenderers.contactPoint.telephone: 1",
                                "faxNumber": "tenderers.contactPoint.faxNumber: 1",
                                "url": "tenderers.contactPoint.url: 1"
                            },
                            "details": {
                                "typeOfSupplier": "company",
                                "mainEconomicActivities": [
                                    {
                                        "scheme": "tenderers.details.mainEconomicActivities.scheme': 1.0",
                                        "id": "tenderers.details.mainEconomicActivities.id': 1.0",
                                        "description": "tenderers.details.mainEconomicActivities.description': 1.0",
                                        "uri": "tenderers.details.mainEconomicActivities.uri': 1.0"
                                    },
                                    {
                                        "scheme": "tenderers.details.mainEconomicActivities.scheme': 1.1",
                                        "id": "tenderers.details.mainEconomicActivities.id': 1.1",
                                        "description": "tenderers.details.mainEconomicActivities.description': 1.1",
                                        "uri": "tenderers.details.mainEconomicActivities.uri': 1.1"
                                    }],
                                "permits": [
                                    {
                                        "id": "tenderers.details.permits.id': 1.0",
                                        "scheme": "tenderers.details.permits.scheme': 1.0",
                                        "url": "tenderers.details.permits.url': 1.0",
                                        "permitDetails": {
                                            "issuedBy": {
                                                "id": "tenderers.details.permits.permitDetails.issueBy.id': 1.0",
                                                "name": "tenderers.details.permits.permitDetails.issueBy.id': 1.0"
                                            },
                                            "issuedThought": {
                                                "id": "tenderers.details.permits.permitDetails.issuedThought.id': 1.0",
                                                "name": "tenderers.details.permits.permitDetails.issuedThought.id': 1.0"
                                            },
                                            "validityPeriod": {
                                                "startDate": "2021-12-24T15:42:53Z",
                                                "endDate": "2022-01-13T15:42:53Z"
                                            }
                                        }
                                    },
                                    {
                                        "id": "tenderers.details.permits.id': 1.1",
                                        "scheme": "tenderers.details.permits.scheme': 1.1",
                                        "url": "tenderers.details.permits.url': 1.1",
                                        "permitDetails": {
                                            "issuedBy": {
                                                "id": "tenderers.details.permits.permitDetails.issueBy.id': 1.1",
                                                "name": "tenderers.details.permits.permitDetails.issueBy.id': 1.1"
                                            },
                                            "issuedThought": {
                                                "id": "tenderers.details.permits.permitDetails.issuedThought.id': 1.1",
                                                "name": "tenderers.details.permits.permitDetails.issuedThought.id': 1.1"
                                            },
                                            "validityPeriod": {
                                                "startDate": "2021-12-24T15:42:53Z",
                                                "endDate": "2022-01-13T15:42:53Z"
                                            }
                                        }
                                    }],
                                "bankAccounts": [
                                    {
                                        "description": "tenderers.details.bankAccounts.description.: 1.0",
                                        "bankName": "tenderers.details.bankAccounts.bankName.: 1.0",
                                        "address": {
                                            "streetAddress": "tenderers.details.bankAccounts.address.streetAddress.: 1.0",
                                            "postalCode": "tenderers.details.bankAccounts.address.postalCode.: 1.0",
                                            "addressDetails": {
                                                "country": {
                                                    "scheme": "ISO-ALPHA2",
                                                    "id": "MD",
                                                    "description": "Moldova, Republica",
                                                    "uri": "http://reference.iatistandard.org"
                                                },
                                                "region": {
                                                    "scheme": "CUATM",
                                                    "id": "1700000",
                                                    "description": "Cahul",
                                                    "uri": "http://statistica.md"
                                                },
                                                "locality": {
                                                    "scheme": "tenderers.details.bankAccounts.address.addressDetails.locality.scheme.: 1.0",
                                                    "id": "1701000",
                                                    "description": "tenderers.details.bankAccounts.address.addressDetails.locality.description.: 1.0"
                                                }
                                            }
                                        },
                                        "identifier": {
                                            "id": "tenderers.details.bankAccounts.address.identifier.id: 1.0",
                                            "scheme": "UA-MFO"
                                        },
                                        "accountIdentification": {
                                            "id": "tenderers.details.bankAccounts.address.accountIdentification.id: 1.0",
                                            "scheme": "IBAN"
                                        },
                                        "additionalAccountIdentifiers": [
                                            {
                                                "id": "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 1.0.0",
                                                "scheme": "fiscal"
                                            },
                                            {
                                                "id": "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 1.0.1",
                                                "scheme": "fiscal"
                                            }]
                                    },
                                    {
                                        "description": "tenderers.details.bankAccounts.description.: 1.1",
                                        "bankName": "tenderers.details.bankAccounts.bankName.: 1.1",
                                        "address": {
                                            "streetAddress": "tenderers.details.bankAccounts.address.streetAddress.: 1.1",
                                            "postalCode": "tenderers.details.bankAccounts.address.postalCode.: 1.1",
                                            "addressDetails": {
                                                "country": {
                                                    "scheme": "ISO-ALPHA2",
                                                    "id": "MD",
                                                    "description": "Moldova, Republica",
                                                    "uri": "http://reference.iatistandard.org"
                                                },
                                                "region": {
                                                    "scheme": "CUATM",
                                                    "id": "1700000",
                                                    "description": "Cahul",
                                                    "uri": "http://statistica.md"
                                                },
                                                "locality": {
                                                    "scheme": "tenderers.details.bankAccounts.address.addressDetails.locality.scheme.: 1.1",
                                                    "id": "1701000",
                                                    "description": "tenderers.details.bankAccounts.address.addressDetails.locality.description.: 1.1"
                                                }
                                            }
                                        },
                                        "identifier": {
                                            "id": "tenderers.details.bankAccounts.address.identifier.id: 1.1",
                                            "scheme": "UA-MFO"
                                        },
                                        "accountIdentification": {
                                            "id": "tenderers.details.bankAccounts.address.accountIdentification.id: 1.1",
                                            "scheme": "IBAN"
                                        },
                                        "additionalAccountIdentifiers": [
                                            {
                                                "id": "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 1.1.0",
                                                "scheme": "fiscal"
                                            },
                                            {
                                                "id": "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 1.1.1",
                                                "scheme": "fiscal"
                                            }]
                                    }],
                                "legalForm": {
                                    "id": "tenderers.details.details.legalForm.id: 1.",
                                    "scheme": "MD-CFOJ",
                                    "description": "tenderers.details.details.legalForm.scheme: 1.",
                                    "uri": "tenderers.details.details.legalForm.uri: 1."
                                },
                                "scale": "micro"
                            },
                            "persones": [
                                {
                                    "id": "MD-IDNO-tenderers.persones.identifier.id: 1.0",
                                    "title": "Mrs.",
                                    "name": "tenderers.persones.name: 1.0",
                                    "identifier": {
                                        "scheme": "MD-IDNO",
                                        "id": "tenderers.persones.identifier.id: 1.0",
                                        "uri": "tenderers.persones.identifier.uri: 1.0"
                                    },
                                    "businessFunctions": [
                                        {
                                            "id": "c9345d31-5692-45ac-b92b-127895bb8080",
                                            "type": "authority",
                                            "jobTitle": "tenderers.persones.businessFunctions.jobTitle.id: 1.0.0",
                                            "period": {
                                                "startDate": "2021-10-25T15:42:53Z"
                                            },
                                            "documents": [
                                                {
                                                    "id": "fcc1ff06-703a-4e05-aceb-9510827956d2-1635165768078",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.0.0.0",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.0.0.0",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/fcc1ff06-703a-4e05-aceb-9510827956d2-1635165768078",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                },
                                                {
                                                    "id": "e54ff675-4e00-43e4-bf46-3b2508f8dc9b-1635165769522",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.0.0.1",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.0.0.1",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/e54ff675-4e00-43e4-bf46-3b2508f8dc9b-1635165769522",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                }]
                                        },
                                        {
                                            "id": "e13e5f01-e6db-4218-8d51-1fcad4700fe8",
                                            "type": "contactPoint",
                                            "jobTitle": "tenderers.persones.businessFunctions.jobTitle.id: 1.0.1",
                                            "period": {
                                                "startDate": "2021-10-25T15:42:53Z"
                                            },
                                            "documents": [
                                                {
                                                    "id": "e7d19693-2bf3-4cf5-b2d3-4e3bda402fa3-1635165770009",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.0.1.0",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.0.1.0",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/e7d19693-2bf3-4cf5-b2d3-4e3bda402fa3-1635165770009",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                },
                                                {
                                                    "id": "68703c8c-b5bb-4644-8cdc-55776fda35ec-1635165770460",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.0.1.1",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.0.1.1",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/68703c8c-b5bb-4644-8cdc-55776fda35ec-1635165770460",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                }]
                                        }]
                                },
                                {
                                    "id": "MD-IDNO-tenderers.persones.identifier.id: 1.1",
                                    "title": "Ms.",
                                    "name": "tenderers.persones.name: 1.1",
                                    "identifier": {
                                        "scheme": "MD-IDNO",
                                        "id": "tenderers.persones.identifier.id: 1.1",
                                        "uri": "tenderers.persones.identifier.uri: 1.1"
                                    },
                                    "businessFunctions": [
                                        {
                                            "id": "272d5aa7-5a95-4d73-a597-05c9add83c55",
                                            "type": "contactPoint",
                                            "jobTitle": "tenderers.persones.businessFunctions.jobTitle.id: 1.1.0",
                                            "period": {
                                                "startDate": "2021-10-25T15:42:53Z"
                                            },
                                            "documents": [
                                                {
                                                    "id": "8dc46f27-329f-4d97-98b4-aeacfc2dff1e-1635165770957",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.1.0.0",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.1.0.0",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/8dc46f27-329f-4d97-98b4-aeacfc2dff1e-1635165770957",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                },
                                                {
                                                    "id": "5429d41c-88a1-4f2e-8dff-6cc974b35641-1635165771349",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.1.0.1",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.1.0.1",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/5429d41c-88a1-4f2e-8dff-6cc974b35641-1635165771349",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                }]
                                        },
                                        {
                                            "id": "663723e3-1bb8-44f5-9b7a-28ac07c955e7",
                                            "type": "contactPoint",
                                            "jobTitle": "tenderers.persones.businessFunctions.jobTitle.id: 1.1.1",
                                            "period": {
                                                "startDate": "2021-10-25T15:42:53Z"
                                            },
                                            "documents": [
                                                {
                                                    "id": "eaee36ad-586a-43df-886f-aeaa4e5f6902-1635165771711",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.1.1.0",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.1.1.0",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/eaee36ad-586a-43df-886f-aeaa4e5f6902-1635165771711",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                },
                                                {
                                                    "id": "ab395557-0eda-43b1-b0c1-ea739b38ceeb-1635165772259",
                                                    "documentType": "regulatoryDocument",
                                                    "title": "tenderers.persones.businessFunctions.documents.title: 1.1.1.1",
                                                    "description": "tenderers.persones.businessFunctions.documents.description: 1.1.1.1",
                                                    "url": "https://dev.bpe.eprocurement.systems/api/v1/storage/get/ab395557-0eda-43b1-b0c1-ea739b38ceeb-1635165772259",
                                                    "datePublished": "2021-10-25T12:45:44Z"
                                                }]
                                        }]
                                }],
                            "roles": [
                                "tenderer"]
                        }]

                except Exception:
                    raise Exception("Impossible to prepare expected awards array")

                print("Actual parties array")
                print(json.dumps(GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['parties']))
                print("Expected parties array")
                print(json.dumps(expected_parties_array))

                try:
                    """
                    Prepare expected awards array
                    """
                    expected_awards_array = [
                        {
                            "id":
                                GlobalClassTenderPeriodEndNoAuction.feed_point_message['data']['outcomes']['awards'][0][
                                    'id'],
                            "title": "The contract/lot is not awarded",
                            "description": "Other reasons (discontinuation of procedure)",
                            "status": "unsuccessful",
                            "statusDetails": "noOffersReceived",
                            "date": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data']['operationDate'],
                            "relatedLots": GlobalClassCreateBid.payload['bid']['relatedLots']
                        }]
                except Exception:
                    raise Exception("Impossible to prepare expected awards array")
                print("Prepare expected awards array")
                print(json.dumps(expected_awards_array))

                print("Prepare actual awards array")
                print(json.dumps(GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['awards']))
                try:
                    """
                    Prepare expected bid object
                    """
                    try:
                        for i in GlobalClassCreateBid.payload['bid']['requirementResponses']:
                            for i_1 in i:
                                if i_1 == "id":
                                    check_requirement_responses_id = is_it_uuid(i["id"], 4)
                                    if check_requirement_responses_id is True:
                                        pass
                                    else:
                                        raise Exception('check_requirement_responses_id is not UUID')
                                if i_1 == "evidences":
                                    for i_2 in i['evidences']:
                                        for i_3 in i_2:
                                            if i_3 == "id":
                                                check_evidences_id = is_it_uuid(i["id"], 4)
                                                if check_evidences_id is True:
                                                    pass
                                                else:
                                                    raise Exception('check_evidences_id is not UUID')
                    except KeyError:
                        raise KeyError('KeyError: id')

                    expected_bids_object = {
                        "details": [
                            {
                                "id": GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids'],
                                "date": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data']['operationDate'],
                                "status": "pending",
                                "tenderers": [
                                    {
                                        "id": f"{GlobalClassCreateBid.payload['bid']['tenderers'][0]['identifier']['scheme']}"
                                              f"-{GlobalClassCreateBid.payload['bid']['tenderers'][0]['identifier']['id']}",
                                        "name": GlobalClassCreateBid.payload['bid']['tenderers'][0]['name']
                                    },
                                    {
                                        "id": f"{GlobalClassCreateBid.payload['bid']['tenderers'][1]['identifier']['scheme']}"
                                              f"-{GlobalClassCreateBid.payload['bid']['tenderers'][1]['identifier']['id']}",
                                        "name": GlobalClassCreateBid.payload['bid']['tenderers'][1]['name']
                                    }
                                ],
                                "value": {
                                    "amount": GlobalClassCreateBid.payload['bid']['value']['amount'],
                                    "currency": GlobalClassCreateBid.payload['bid']['value']['currency']
                                },
                                "documents": [
                                    {
                                        "id": GlobalClassCreateBid.payload['bid']['documents'][0]['id'],
                                        "documentType": GlobalClassCreateBid.payload['bid']['documents'][0][
                                            'documentType'],
                                        "title": GlobalClassCreateBid.payload['bid']['documents'][0]['title'],
                                        "description": GlobalClassCreateBid.payload['bid']['documents'][0][
                                            'description'],
                                        "url": f"{self.metadata_document_url}/{GlobalClassCreateBid.payload['bid']['documents'][0]['id']}",
                                        "datePublished": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data'][
                                            'operationDate'],
                                        "relatedLots": GlobalClassCreateBid.payload['bid']['documents'][0][
                                            'relatedLots']
                                    },
                                    {
                                        "id": GlobalClassCreateBid.payload['bid']['documents'][1]['id'],
                                        "documentType": GlobalClassCreateBid.payload['bid']['documents'][1][
                                            'documentType'],
                                        "title": GlobalClassCreateBid.payload['bid']['documents'][1]['title'],
                                        "description": GlobalClassCreateBid.payload['bid']['documents'][1][
                                            'description'],
                                        "url": f"{self.metadata_document_url}/{GlobalClassCreateBid.payload['bid']['documents'][1]['id']}",
                                        "datePublished": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data'][
                                            'operationDate'],
                                        "relatedLots": GlobalClassCreateBid.payload['bid']['documents'][1][
                                            'relatedLots']
                                    }
                                ],
                                "relatedLots": GlobalClassCreateBid.payload['bid']['relatedLots'],
                                "requirementResponses": GlobalClassCreateBid.payload['bid']['requirementResponses']
                            }
                        ]
                    }
                except Exception:
                    raise Exception("Impossible to prepare expected bids object")
                print("expected_bids_object")
                print(json.dumps(expected_bids_object))

                print("Prepare actual bids object")
                print(json.dumps(GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids']))
                # try:
                #     """
                #         If compare_releases !=expected_result, then return process steps by operation-id.
                #         """
                #     if compare_releases == expected_result and \
                #             expected_awards_array == \
                #             GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['awards']:
                #         pass
                #     else:
                #         with allure.step('# Steps from Casandra DataBase'):
                #             steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                #                 operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message['X-OPERATION-ID'])
                #             allure.attach(steps, "Cassandra DataBase: steps of process")
                # except ValueError:
                #     raise ValueError("Can not return BPE operation step")
                #
                # assert str(compare_actual_result_and_expected_result(
                #     expected_result=expected_result,
                #     actual_result=compare_releases
                # )) == str(True)
            #
            # with allure.step('# 10.3. Check MS release'):
            #     """
            #     Compare multistage release with expected multistage release model.
            #     """
            #     allure.attach(str(json.dumps(GlobalClassCreateCnOnPn.actual_ms_release)),
            #                   "Actual MS release before tender period end expired")
            #
            #     GlobalClassTenderPeriodEndNoAuction.actual_ms_release = requests.get(
            #         url=f"{GlobalClassCreatePn.feed_point_message['data']['url']}/"
            #             f"{GlobalClassCreatePn.pn_ocid}").json()
            #
            #     allure.attach(str(json.dumps(GlobalClassTenderPeriodEndNoAuction.actual_ms_release)),
            #                   "Actual MS release after tender period end expired")
            #
            #     compare_releases = dict(DeepDiff(
            #         GlobalClassCreateCnOnPn.actual_ms_release,
            #         GlobalClassTenderPeriodEndNoAuction.actual_ms_release))
            #
            #     expected_result = {
            #         "values_changed": {
            #             "root['releases'][0]['id']": {
            #                 "new_value":
            #                     f"{GlobalClassCreatePn.pn_ocid}-"
            #                     f"{GlobalClassTenderPeriodEndNoAuction.actual_ms_release['releases'][0]['id'][29:42]}",
            #                 "old_value": f"{GlobalClassCreatePn.pn_ocid}-"
            #                              f"{GlobalClassCreateCnOnPn.actual_ms_release['releases'][0]['id'][29:42]}"
            #             },
            #             "root['releases'][0]['date']": {
            #                 "new_value": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data'][
            #                     'operationDate'],
            #                 "old_value": GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
            #             },
            #             "root['releases'][0]['tender']['status']": {
            #                 "new_value": "unsuccessful",
            #                 "old_value": "active"
            #             },
            #             "root['releases'][0]['tender']['statusDetails']": {
            #                 "new_value": "empty",
            #                 "old_value": "evaluation"
            #             }
            #         }
            #     }
            #     try:
            #         """
            #         If TestCase was passed, then cLean up the database.
            #         If TestCase was failed, then return process steps by operation-id.
            #         """
            #         if compare_releases == expected_result:
            #             GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
            #                 ei_id=GlobalClassCreateEi.ei_ocid)
            #
            #             GlobalClassMetadata.database.fs_process_cleanup_table_of_services(
            #                 ei_id=GlobalClassCreateEi.ei_ocid)
            #
            #             GlobalClassMetadata.database.pn_process_cleanup_table_of_services(
            #                 pn_ocid=GlobalClassCreatePn.pn_ocid)
            #
            #             GlobalClassMetadata.database.cnonpn_process_cleanup_table_of_services(
            #                 pn_ocid=GlobalClassCreatePn.pn_ocid)
            #
            #             GlobalClassMetadata.database.bid_process_cleanup_table_of_services(
            #                 pn_ocid=GlobalClassCreatePn.pn_ocid)
            #
            #             GlobalClassMetadata.database.tender_period_end_process_cleanup_table_of_services(
            #                 pn_ocid=GlobalClassCreatePn.pn_ocid)
            #
            #             GlobalClassMetadata.database.cleanup_steps_of_process(
            #                 operation_id=GlobalClassCreateEi.operation_id)
            #
            #             GlobalClassMetadata.database.cleanup_steps_of_process(
            #                 operation_id=GlobalClassCreateFs.operation_id)
            #
            #             GlobalClassMetadata.database.cleanup_steps_of_process(
            #                 operation_id=GlobalClassCreatePn.operation_id)
            #
            #             GlobalClassMetadata.database.cleanup_steps_of_process(
            #                 operation_id=GlobalClassCreateCnOnPn.operation_id)
            #
            #             GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
            #                 operation_id=GlobalClassCreateBid.operation_id)
            #
            #             GlobalClassMetadata.database.cleanup_steps_of_process_from_orchestrator(
            #                 operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message['X-OPERATION-ID'])
            #         else:
            #             with allure.step('# Steps from Casandra DataBase'):
            #                 steps = \
            #                     GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id_from_orchestrator(
            #                         operation_id=GlobalClassTenderPeriodEndNoAuction.feed_point_message[
            #                             'X-OPERATION-ID'])
            #                 allure.attach(steps, "Cassandra DataBase: steps of process")
            #     except ValueError:
            #         raise ValueError("Can not return BPE operation step")
            #
            #     assert str(compare_actual_result_and_expected_result(
            #         expected_result=expected_result,
            #         actual_result=compare_releases
            #     )) == str(True)
