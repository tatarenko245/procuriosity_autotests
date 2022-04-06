import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.PayloadModels.Budget.ExpenditureItem.expenditure_item_payload__ import EiPreparePayload
from tests.utils.PayloadModels.Budget.FinancialSource.deldete_financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModels.LimitedProcedure.Award.award_payloads import AwardPayloads
from tests.utils.PayloadModels.LimitedProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModels.LimitedProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.ReleaseModels.LimitedProcedure.Award.award_releases import AwardReleases

from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestCreateAward:
    @allure.title("Check Ev and MS releases data after CreateAward process without optional fields. \n"
                  "------------------------------------------------\n"
                  "CreateEi process: obligatory data model without items array;\n"
                  "СreateFs process: obligatory data model, treasury money;\n"
                  "СreatePn process: obligatory data model, without lots and items;\n"
                  "СreateCnOnPn process: obligatory data model, with lots and items;\n"
                  "СreateAward process: obligatory data model.\n")
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

        with allure.step(f'# {step_number}. Authorization platform one: CreateEi process.'):
            """
            Tender platform authorization for CreateEi process.
            As result get Tender platform's access token and process operation-id.
            """
            createEi_accessToken = authorization.get_access_token_for_platform_one()
            createEi_operationId = authorization.get_x_operation_id(createEi_accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a CreateEi process.'):
            """
            Send api request to BPE host to create a CreateEi process.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            createEi_payload = ei_payload_class.create_ei_obligatory_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=createEi_accessToken,
                x_operation_id=createEi_operationId,
                country=parse_country,
                language=parse_language,
                payload=createEi_payload,
                test_mode=True)

            createEi_feedPoint_message = KafkaMessage(createEi_operationId).get_message_from_kafka()
            ei_ocid = createEi_feedPoint_message["data"]["outcomes"]["ei"][0]['id']

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: CreateFs process.'):
            """
            Tender platform authorization for CreateFs process.
            As result get Tender platform's access token and process operation-id.
            """
            createFs_accessToken = authorization.get_access_token_for_platform_one()
            createFs_operationId = authorization.get_x_operation_id(createFs_accessToken)
            step_number += 1

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a CreateFs process.'):
            """
            Send api request to BPE host to create a CreateFs process.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=createEi_payload))
            createFs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=createEi_payload)

            Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=createFs_accessToken,
                x_operation_id=createFs_operationId,
                ei_ocid=ei_ocid,
                payload=createFs_payload,
                test_mode=True)

            createFs_feedPoint_message = KafkaMessage(createFs_operationId).get_message_from_kafka()

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: CreatePn process.'):
            """
            Tender platform authorization for CreatePn process.
            As result get Tender platform's access token and process operation-id.
            """
            createPn_accessToken = authorization.get_access_token_for_platform_one()
            createPn_operationId = authorization.get_x_operation_id(createPn_accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a CreatePn process.'):
            """
            Send api request to BPE host to create a CreatePn process.
            Save synchronous result of sending the request.
            And save in variable pn_ocid, pn_id, pn_token.
            """
            time.sleep(1)
            pn_payload_class = copy.deepcopy(PnPreparePayload(
                fs_payload=createFs_payload,
                fs_feed_point_message=createFs_feedPoint_message))
            createPn_payload = \
                pn_payload_class.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            Requests().createPn(
                host_of_request=get_hosts[1],
                access_token=createPn_accessToken,
                x_operation_id=createPn_operationId,
                country=parse_country,
                language=parse_language,
                pmd=parse_pmd,
                payload=createPn_payload,
                test_mode=True)

            createPn_feedPoint_message = KafkaMessage(createPn_operationId).get_message_from_kafka()
            pn_ocid = createPn_feedPoint_message['data']['ocid']
            pn_id = createPn_feedPoint_message['data']['outcomes']['pn'][0]['id']
            pn_token = createPn_feedPoint_message['data']['outcomes']['pn'][0]['X-TOKEN']
            pn_url = createPn_feedPoint_message['data']['url']
            actual_ei_release_before_createCnOnPn = requests.get(
                url=f"{createEi_feedPoint_message['data']['url']}/{ei_ocid}").json()

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: CreateCnOnPn process.'):
            """
            Tender platform authorization for CreateCnOnPn process.
            As result get Tender platform's access token and process operation-id.
            """
            createCn_accessToken = authorization.get_access_token_for_platform_one()
            createCn_operationId = authorization.get_x_operation_id(createCn_accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a CreateCnOnPn process.'):
            """
            Send api request to BPE host to create a CreateCnOnPn process.
            Save synchronous result of sending the request.
            """
            time.sleep(1)

            cn_payload_class = copy.deepcopy(CnOnPnPreparePayload(host_for_services=get_hosts[2]))
            createCn_payload = \
                cn_payload_class.create_cnonpn_obligatory_data_model(
                    actual_ei_release=actual_ei_release_before_createCnOnPn,
                    pn_payload=createPn_payload)

            Requests().createCnOnPn(
                host_of_request=get_hosts[1],
                access_token=createCn_accessToken,
                x_operation_id=createCn_operationId,
                pn_ocid=pn_ocid,
                pn_id=pn_id,
                pn_token=pn_token,
                payload=createCn_payload,
                test_mode=True)

            createCn_feedPoint_message = KafkaMessage(createCn_operationId).get_message_from_kafka()
            np_id = createCn_feedPoint_message['data']['outcomes']['np'][0]['id']
            actual_np_release_before_createAward = requests.get(url=f"{pn_url}/{np_id}").json()
            actual_ms_release_before_createAward = requests.get(url=f"{pn_url}/{pn_ocid}").json()
            lot_id = actual_np_release_before_createAward['releases'][0]['tender']['lots'][0]['id']

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: CreateAward process.'):
            """
            Tender platform authorization for CreateAward process.
            As result get Tender platform's access token and process operation-id.
            """
            createAward_accessToken = authorization.get_access_token_for_platform_one()
            createAward_operationId = authorization.get_x_operation_id(createAward_accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a CreateAward process.'):
            """
            Send api request to BPE host to create a CreateAward process.
            Save synchronous result of sending the request.
            """
            time.sleep(1)

            award_payload_class = copy.deepcopy(AwardPayloads(
                host_for_services=get_hosts[2],
                currency=createCn_payload['tender']['lots'][0]['value']['currency'])
            )
            createAward_payload = award_payload_class.create_award_obligatory_data_model(
                quantity_of_suppliers_objects=1
            )

            synchronous_result_of_sending_the_request = Requests().createAward_for_limitedProcedure(
                host_of_request=get_hosts[1],
                access_token=createAward_accessToken,
                x_operation_id=createAward_operationId,
                pn_ocid=pn_ocid,
                pn_token=pn_token,
                tender_id=np_id,
                lot_id=lot_id,
                payload=createAward_payload,
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
                createAward_feedPointMessage = KafkaMessage(createAward_operationId).get_message_from_kafka()
                allure.attach(str(createAward_feedPointMessage), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    createAward_operationId).award_for_limited_procedure_message_is_successful(
                    environment=parse_environment,
                    kafka_message=createAward_feedPointMessage,
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
                        f"operation_id = '{createAward_operationId}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

            with allure.step(f'# {step_number}.3. Check NP release'):
                """
                Compare actual NP release before CreateAward process and NP release after CreateAward process.
                """
                allure.attach(str(json.dumps(actual_np_release_before_createAward)),
                              "Actual NP release before CreateAward process.")

                actual_np_release_after_createAward = requests.get(url=f"{pn_url}/{np_id}").json()
                allure.attach(str(json.dumps(actual_np_release_after_createAward)),
                              "Actual NP release after CreateAward process.")

                compare_releases = dict(DeepDiff(
                    actual_np_release_before_createAward,
                    actual_np_release_after_createAward)
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
                                f"{actual_np_release_after_createAward['releases'][0]['id'][46:59]}",
                            "old_value":
                                f"{np_id}-"
                                f"{actual_np_release_before_createAward['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": createAward_feedPointMessage['data']['operationDate'],
                            "old_value": actual_np_release_before_createAward['releases'][0]['date']
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
                        environment=parse_environment,
                        language=parse_language,
                        award_payload=createAward_payload,
                        awardFeedPointMessage=createAward_feedPointMessage
                    )

                    final_expected_parties_array = expected_award_release_class.create_parties_array(
                        actual_parties_array=actual_np_release_after_createAward['releases'][0]['parties']
                    )

                except Exception:
                    raise Exception("Impossible to prepare expected parties array")

                try:
                    """
                    Prepare expected awards array.
                    """
                    final_expected_awards_array = expected_award_release_class.create_awards_array(
                        lot_id=lot_id,
                        actual_awards_array=actual_np_release_after_createAward['releases'][0]['awards']
                    )
                except Exception:
                    raise Exception("Impossible to prepare expected awards array")

                try:
                    """
                    Prepare expected tender.awardPeriod object.
                    """
                    final_expected_tender_awardPeriod_object = {
                        "startDate": createAward_feedPointMessage['data']['operationDate']
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
                        f"operation_id = '{createAward_operationId}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

                with allure.step('Check a difference of comparing actual parties array and expected parties array.'):
                    allure.attach(str(actual_np_release_after_createAward['releases'][0]['parties']),
                                  "Actual parties array.")
                    allure.attach(str(final_expected_parties_array),
                                  "Expected parties array")

                    assert str(actual_np_release_after_createAward['releases'][0]['parties']) == \
                           str(final_expected_parties_array), allure.attach(
                        f"SELECT * FROM orchestrator.steps WHERE "
                        f"operation_id = '{createAward_operationId}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

                with allure.step('Check a difference of comparing actual awards array and expected awards array.'):
                    allure.attach(str(actual_np_release_after_createAward['releases'][0]['awards']),
                                  "Actual awards array.")
                    allure.attach(str(final_expected_awards_array),
                                  "Expected awards array")
                    assert str(actual_np_release_after_createAward['releases'][0]['awards']) == \
                           str(final_expected_awards_array), allure.attach(
                        f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                        f"process_id = '{createAward_operationId}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

                with allure.step('Check a difference of comparing actual tender.awardPeriod object and '
                                 'expected tender.awardPeriod object.'):
                    allure.attach(str(actual_np_release_after_createAward['releases'][0]['tender']['awardPeriod']),
                                  "Actual tender.awardPeriod object.")
                    allure.attach(str(final_expected_tender_awardPeriod_object),
                                  "Expected tender.awardPeriod object.")
                    assert str(actual_np_release_after_createAward['releases'][0]['tender']['awardPeriod']) == \
                           str(final_expected_tender_awardPeriod_object), allure.attach(
                        f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                        f"process_id = '{createAward_operationId}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare actual multistage release before CreateAward process and 
                actual multistage release after CreateAward process.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_createAward)),
                              "Actual Ms release before AwardCreate process.")

                actual_ms_release_after_createAward = requests.get(url=f"{pn_url}/{pn_ocid}").json()
                allure.attach(str(json.dumps(actual_ms_release_after_createAward)),
                              "Actual Ms release after AwardCreate process")

                compare_releases = dict(DeepDiff(actual_ms_release_before_createAward,
                                                 actual_ms_release_after_createAward)
                                        )
                expected_result = {}

                with allure.step('Check a difference of comparing Ms release before CreateAward process and '
                                 'Ms release after CreateAward process.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing MS releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms releases.")
                    assert str(compare_releases) == str(expected_result), allure.attach(
                        f"SELECT * FROM orchestrator.steps WHERE "
                        f"operation_id = '{createAward_operationId}' ALLOW FILTERING;",
                        "Cassandra DataBase: steps of process")

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

                            connect_to_database.createAward_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                            connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=createEi_operationId)

                            connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=createFs_operationId)

                            connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=createPn_operationId)

                            connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=createCn_operationId)

                            connect_to_database.cleanup_orchestrator_steps_by_cpid(
                                cpid=pn_ocid)

                    except ValueError:
                        raise ValueError("Can not return BPE operation step")
