import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.PayloadModel.Budget.Ei.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.LimitedProcedure.Award.award_payloads import AwardPayloads
from tests.utils.PayloadModel.LimitedProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.LimitedProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.ReleaseModel.LimitedProcedure.Award.award_releases import AwardReleases

from tests.utils.kafka_message import KafkaMessage
from tests.utils.my_requests import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestCreateAward:
    @allure.title("Check Ev and MS releases data after CnOnPn creating without optional fields. \n"
                  "------------------------------------------------\n"
                  "create Ei: obligatory data model without items array;\n"
                  "create Fs: obligatory data model, treasury money;\n"
                  "create Pn: obligatory data model, without lots and items;\n"
                  "create CnOnPn: obligatory data model, with lots and items;\n"
                  "create Award: obligatory data model\n")
    def test_check_pn_ms_releases_one(self, get_hosts, country, language, pmd, environment, connection_to_database):
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

            Requests().create_ei(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=country,
                language=language,
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

            Requests().create_fs(
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

            Requests().create_pn(
                host_of_request=get_hosts[1],
                access_token=create_pn_access_token,
                x_operation_id=create_pn_operation_id,
                country=country,
                language=language,
                pmd=pmd,
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

            cn_payload_class = copy.deepcopy(CnOnPnPreparePayload(host_for_services=get_hosts[2]))
            create_cn_payload = \
                cn_payload_class.create_cnonpn_obligatory_data_model(
                    actual_ei_release=actual_ei_release_before_cn_creation,
                    pn_payload=create_pn_payload)

            Requests().create_cnonpn(
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
            actual_np_release_before_award_creating = requests.get(url=f"{pn_url}/{np_id}").json()
            actual_ms_release_before_award_creating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
            lot_id = actual_np_release_before_award_creating['releases'][0]['tender']['lots'][0]['id']

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: create Award'):
            """
            Tender platform authorization for create award process.
            As result get Tender platform's access token and process operation-id.
            """
            create_award_access_token = authorization.get_access_token_for_platform_one()
            create_award_operation_id = authorization.get_x_operation_id(create_award_access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send request to create Award'):
            """
            Send api request on BPE host for create award process.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)

            award_payload_class = copy.deepcopy(AwardPayloads(
                host_for_services=get_hosts[2],
                currency=create_cn_payload['tender']['lots'][0]['value']['currency'])
            )
            create_award_payload = award_payload_class.create_obligatory_data_model(
                quantity_of_suppliers_objects=1
            )

            synchronous_result_of_sending_the_request = Requests().do_award_for_limited_procedure(
                host_of_request=get_hosts[1],
                access_token=create_award_access_token,
                x_operation_id=create_award_operation_id,
                pn_ocid=pn_ocid,
                pn_token=pn_token,
                tender_id=np_id,
                lot_id=lot_id,
                payload=create_award_payload,
                test_mode=True)

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
                create_award_feedPoint_message = KafkaMessage(create_award_operation_id).get_message_from_kafka()
                allure.attach(str(create_award_feedPoint_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_award_operation_id).award_for_limited_procedure_message_is_successful(
                    environment=environment,
                    kafka_message=create_award_feedPoint_message,
                    pn_ocid=pn_ocid,
                    tender_id=np_id
                )

                with allure.step('Compare actual asynchronous result of sending the request and '
                                 'expected asynchronous result of sending request.'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual asynchronous result of sending the request.")
                    allure.attach(str(True), "Expected asynchronous result of sending the request.")
                    assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True), allure.attach(
                        f"SELECT * FROM orchestrator.steps WHERE "
                        f"operation_id = '{create_award_operation_id}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

            with allure.step(f'# {step_number}.3. Check NP release'):
                """
                Compare actual NP release before CreateAward process and NP release after CreateAward process.
                """
                allure.attach(str(json.dumps(actual_np_release_before_award_creating)),
                              "Actual NP release before CreateAward process.")

                actual_np_release_after_award_creating = requests.get(url=f"{pn_url}/{np_id}").json()
                allure.attach(str(json.dumps(actual_np_release_after_award_creating)),
                              "Actual NP release after CreateAward process.")

                compare_releases = dict(DeepDiff(
                    actual_np_release_before_award_creating,
                    actual_np_release_after_award_creating)
                )

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned

                expected_result = {
                    "dictionary_item_added":
                        "['releases'][0]['parties'], "
                        "['releases'][0]['awards'], "
                        "['releases'][0]['tender']['awardPeriod']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{np_id}-"
                                f"{actual_np_release_after_award_creating['releases'][0]['id'][46:59]}",
                            "old_value":
                                f"{np_id}-"
                                f"{actual_np_release_before_award_creating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": create_award_feedPoint_message['data']['operationDate'],
                            "old_value": actual_np_release_before_award_creating['releases'][0]['date']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "awarding",
                            "old_value": "negotiation"
                        }
                    }
                }

                try:
                    """
                    Prepare expected parties array.
                    """
                    expected_award_release_class = AwardReleases(
                        environment=environment,
                        language=language,
                        award_payload=create_award_payload,
                        awardFeedPointMessage=create_award_feedPoint_message,
                        actual_award_release=actual_np_release_after_award_creating
                    )

                    final_expected_parties_array = expected_award_release_class.create_parties_array(
                        actual_parties_array=actual_np_release_after_award_creating['releases'][0]['parties']
                    )

                except Exception:
                    raise Exception("Impossible to prepare expected parties array")

                try:
                    """
                    Prepare expected awards array.
                    """
                    final_expected_awards_array = expected_award_release_class.create_awards_array(
                        lot_id=lot_id,
                        actual_awards_array=actual_np_release_after_award_creating['releases'][0]['awards']
                    )
                except Exception:
                    raise Exception("Impossible to prepare expected awards array")

                try:
                    """
                    Prepare expected tender.awardPeriod object.
                    """
                    final_expected_tender_awardPeriod_object = {
                        "startDate": create_award_feedPoint_message['data']['operationDate']
                    }
                except Exception:
                    raise Exception("Impossible to prepare expected tender.awardPeriod object")

                with allure.step('Check a difference of comparing actual NP release and expected NP release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing NP releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing NP releases.")
                    assert str(compare_releases) == str(expected_result), allure.attach(
                        f"SELECT * FROM orchestrator.steps WHERE "
                        f"operation_id = '{create_award_operation_id}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

                with allure.step('Check a difference of comparing actual parties array and expected parties array.'):
                    allure.attach(str(actual_np_release_after_award_creating['releases'][0]['parties']),
                                  "Actual parties array.")
                    allure.attach(str(final_expected_parties_array),
                                  "Expected parties array")

                    assert str(actual_np_release_after_award_creating['releases'][0]['parties']) == \
                           str(final_expected_parties_array), allure.attach(
                        f"SELECT * FROM orchestrator.steps WHERE "
                        f"operation_id = '{create_award_operation_id}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

                with allure.step('Check a difference of comparing actual awards array and expected awards array.'):
                    allure.attach(str(actual_np_release_after_award_creating['releases'][0]['awards']),
                                  "Actual awards array.")
                    allure.attach(str(final_expected_awards_array),
                                  "Expected awards array")
                    assert str(actual_np_release_after_award_creating['releases'][0]['awards']) == \
                           str(final_expected_awards_array), allure.attach(
                        f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                        f"process_id = '{create_award_operation_id}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

                with allure.step('Check a difference of comparing actual tender.awardPeriod object and '
                                 'expected tender.awardPeriod object.'):
                    allure.attach(str(actual_np_release_after_award_creating['releases'][0]['tender']['awardPeriod']),
                                  "Actual tender.awardPeriod object.")
                    allure.attach(str(final_expected_tender_awardPeriod_object),
                                  "Expected tender.awardPeriod object.")
                    assert str(actual_np_release_after_award_creating['releases'][0]['tender']['awardPeriod']) == \
                           str(final_expected_tender_awardPeriod_object), allure.attach(
                        f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                        f"process_id = '{create_award_operation_id}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare actual multistage release before CreateAward process and 
                actual multistage release after CreateAward process.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_award_creating)),
                              "Actual Ms release before AwardCreate process.")

                actual_ms_release_after_award_creating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
                allure.attach(str(json.dumps(actual_ms_release_after_award_creating)),
                              "Actual Ms release after AwardCreate process")

                compare_releases = dict(DeepDiff(actual_ms_release_before_award_creating,
                                                 actual_ms_release_after_award_creating)
                                        )
                expected_result = {}

                with allure.step('Check a difference of comparing Ms release before cn creating and '
                                 'Ms release after cn creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing MS releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms releases.")
                    assert str(compare_releases) == str(expected_result), allure.attach(
                        f"SELECT * FROM orchestrator.steps WHERE "
                        f"operation_id = '{create_award_operation_id}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

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

                            connection_to_database.createAward_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                            connection_to_database.cleanup_steps_of_process(operation_id=create_ei_operation_id)

                            connection_to_database.cleanup_steps_of_process(operation_id=create_fs_operation_id)

                            connection_to_database.cleanup_steps_of_process(operation_id=create_pn_operation_id)

                            connection_to_database.cleanup_steps_of_process(operation_id=create_cn_operation_id)

                            connection_to_database.cleanup_steps_of_process_from_orchestrator(
                                pn_ocid=pn_ocid)

                    except ValueError:
                        raise ValueError("Can not return BPE operation step")
