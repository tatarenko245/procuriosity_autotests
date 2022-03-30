import copy
import json
import random

import allure
import requests

from tests.utils.MessageModels.Pn.planning_notice_message import PlanningNoticeMessage
from tests.utils.PayloadModels.Budget.Fs.financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModels.FrameworkAgreement.Pn.planing_notice_payload import PlanningNoticePayload
from tests.utils.data_of_enum import currency_tuple
from tests.utils.functions_collection.get_message_for_platform import get_message_for_platform
from tests.utils.PayloadModels.Budget.Ei.expenditure_item_payload import ExpenditureItemPayload

from tests.utils.platform_query_library import PlatformQueryRequest
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Framework Agreement')
@allure.suite('PN')
@allure.sub_suite('BPE: Create Pn')
@allure.severity('Critical')
@allure.testcase(url=None,
                 name=None)
class TestCreatePn:
    @allure.title("Check PN and MS releases after CreatePn process, without optional fields. \n"
                  "------------------------------------------------\n"
                  "CreateEi process: obligatory data model, without items array;\n"
                  "СreateFs process: obligatory data model, treasury money;\n"
                  "СreatePn process: obligatory data model, without lots and items.\n")
    def test_case_1(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment):
        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: CreateEi process.'):
            """
            Tender platform authorization for CreateEi process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            operation_id = platform_one.get_x_operation_id(access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a CreateEi process.'):
            """
            Send api request to BPE host to create a CreateEi process.
            And save in variable ei_ocid.
            """
            try:
                """
                Build payload for CreateEi process.
                """
                ei_payload = copy.deepcopy(ExpenditureItemPayload())

                ei_payload.delete_optional_fields(
                    "tender.description",
                    "tender.items",
                    "planning.rationale",
                    "buyer.identifier.uri",
                    "buyer.address.postalCode",
                    "buyer.additionalIdentifiers",
                    "buyer.contactPoint.faxNumber",
                    "buyer.contactPoint.url",
                    "buyer.details"
                )
                tender_classification_id = ei_payload.get_tender_classification_id()
                ei_payload = ei_payload.build_expenditure_item_payload()
            except ValueError:
                raise ValueError("Impossible to build payload for CreateEi process.")

            PlatformQueryRequest().create_ei_process(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=operation_id,
                country=parse_country,
                language=parse_language,
                payload=ei_payload,
                test_mode=True
            )

        message = get_message_for_platform(operation_id)
        ei_id = message["data"]["outcomes"]["ei"][0]['id']
        allure.attach(str(message), 'Message for platform.')

        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: CreateFs process.'):
            """
            Tender platform authorization for CreateFs process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            operation_id = platform_one.get_x_operation_id(access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a CreateFS process.'):
            """
            Send api request to BPE host to create a CreateFs process.
            And save in variable cpid.
            """
            try:
                """
                Build payload for CreateFs process.
                """
                currency = f"{random.choice(currency_tuple)}"
                fs_payload = copy.deepcopy(FinancialSourcePayload(
                    ei_payload=ei_payload,
                    amount=89999.89,
                    currency=currency)
                )

                fs_payload.delete_optional_fields(
                    "tender.procuringEntity.identifier.uri",
                    "tender.procuringEntity.address.postalCode",
                    "tender.procuringEntity.additionalIdentifiers",
                    "tender.procuringEntity.contactPoint.faxNumber",
                    "tender.procuringEntity.contactPoint.url",
                    "planning.budget.id",
                    "planning.budget.description",
                    "planning.budget.europeanUnionFunding",
                    "planning.budget.project",
                    "planning.budget.projectID",
                    "planning.budget.uri",
                    "planning.rationale",
                    "buyer.identifier.uri",
                    "buyer.address.postalCode",
                    "buyer.additionalIdentifiers",
                    "buyer.contactPoint.faxNumber",
                    "buyer.contactPoint.url"
                )

                fs_payload = fs_payload.build_financial_source_payload()
            except ValueError:
                raise ValueError("Impossible to build payload for CreateFs process.")

            PlatformQueryRequest().create_fs_proces(
                host_to_bpe=get_hosts[1],
                ocid=ei_id,
                access_token=access_token,
                x_operation_id=operation_id,
                payload=fs_payload,
                test_mode=True
            )

            message = get_message_for_platform(operation_id)
            fs_id = message["data"]["outcomes"]["fs"][0]['id']
            allure.attach(str(message), 'Message for platform.')

        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: CreatePn process.'):
            """
            Tender platform authorization for CreatePn process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            operation_id = platform_one.get_x_operation_id(access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a CreatePn process.'):
            """
            Send api request to BPE host to create a CreatePn process.
            And save in variable ocid and token..
            """
            try:
                """
                Build payload for CreatePn process.
                """
                pn_payload = copy.deepcopy(PlanningNoticePayload(
                    fs_id=fs_id,
                    amount=89999.89,
                    currency=currency,
                    tender_classification_id=tender_classification_id,
                    host_to_service=get_hosts[2])
                )

                pn_payload.delete_optional_fields(
                    "planning.rationale",
                    "planning.budget.description",
                    "tender.procurementMethodRationale",
                    "tender.procurementMethodAdditionalInfo",
                    "tender.lots",
                    "tender.items",
                    "tender.documents"
                )

                pn_payload = pn_payload.build_plan_payload()
            except ValueError:
                raise ValueError("Impossible to build payload for CreatePn process.")

            synchronous_result = PlatformQueryRequest().create_pn_proces(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=operation_id,
                payload=pn_payload,
                test_mode=True,
                country=parse_country,
                language=parse_language,
                pmd=parse_pmd
            )

        step_number += 1
        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step(f'# {step_number}.1. Check status code'):
                """
                Check the status code of sending the request.
                """
                with allure.step('Compare actual status code and expected status code of sending request.'):
                    allure.attach(synchronous_result.status_code, "Actual status code.")
                    allure.attach(202, "Expected status code.")
                    assert synchronous_result.status_code == 202

            with allure.step(f'# {step_number}.2. Check the message for platform.'):
                """
                Check the message for platform.
                """
                actual_message = get_message_for_platform(operation_id)

                try:
                    """
                    Build expected message for CreatePn process.
                    """
                    expected_message = copy.deepcopy(PlanningNoticeMessage(
                        environment=parse_environment,
                        actual_message=actual_message,
                        expected_quantity_of_outcomes_pn=1,
                        test_mode=True)
                    )

                    expected_message = expected_message.build_expected_plan_message()
                except ValueError:
                    raise ValueError("Impossible to build expected message for CreatePn process.")

                with allure.step('Compare actual and expected message for platform.'):
                    allure.attach(json.dumps(actual_message), "Actual message.")
                    allure.attach(json.dumps(expected_message), "Expected message.")

                    assert actual_message == expected_message, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{operation_id}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process")

            with allure.step(f'# {step_number}.3. Check PN release.'):
                """
                Compare actual PN release and expected PN release.
                """
                pn_url = f"{actual_message['data']['url']}/{actual_message['data']['outcomes']['pn'][0]['id']}"
                actual_pn_release = requests.get(url=pn_url).json()
                allure.attach(str(json.dumps(actual_pn_release)), "Actual PN release.")

                try:
                    """
                    Build expected PN release.
                    """

                except ValueError:
                    raise ValueError("Impossible to build expected PN release.")
        #
        #         with allure.step('Check a difference of comparing actual NP release before Protocol process and '
        #                          'expected NP release after Protocol process.'):
        #             allure.attach(str(compare_releases),
        #                           "Actual result of comparing NP releases.")
        #             allure.attach(str(expected_result),
        #                           "Expected result of comparing NP releases.")
        #             assert str(compare_releases) == str(expected_result), allure.attach(
        #                 f"SELECT * FROM orchestrator.steps WHERE "
        #                 f"operation_id = '{protocol_operationId}' ALLOW FILTERING;",
        #                 "Cassandra DataBase: steps of process")
        #
        #     with allure.step(f'# {step_number}.4. Check MS release'):
        #         """
        #         Compare actual multistage release before Protocol process and
        #         actual multistage release after Protocol process.
        #         """
        #         allure.attach(str(json.dumps(actual_ms_release_before_protocol)),
        #                       "Actual Ms release before Protocol process.")
        #
        #         actual_ms_release_after_protocol = requests.get(url=f"{pn_url}/{pn_ocid}").json()
        #         allure.attach(str(json.dumps(actual_np_release_after_protocol)),
        #                       "Actual Ms release after Protocol process")
        #
        #         compare_releases = dict(DeepDiff(actual_ms_release_before_protocol,
        #                                          actual_ms_release_after_protocol
        #                                          )
        #                                 )
        #         expected_result = {}
        #
        #         with allure.step('Check a difference of comparing Ms release before Protocol and '
        #                          'Ms release after Protocol.'):
        #             allure.attach(str(compare_releases),
        #                           "Actual result of comparing MS releases.")
        #             allure.attach(str(expected_result),
        #                           "Expected result of comparing Ms releases.")
        #             assert str(compare_releases) == str(expected_result), allure.attach(
        #                 f"SELECT * FROM orchestrator.steps WHERE "
        #                 f"operation_id = '{protocol_operationId}' ALLOW FILTERING;",
        #                 "Cassandra DataBase: steps of process")
        #
        #             try:
        #                 """
        #                     If TestCase was passed, then cLean up the database.
        #                     If TestCase was failed, then return process steps by operation-id.
        #                     """
        #                 if compare_releases == expected_result:
        #                     connect_to_database.ei_process_cleanup_table_of_services(ei_id=ei_ocid)
        #
        #                     connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
        #
        #                     connect_to_database.pn_process_cleanup_table_of_services(pn_ocid=pn_ocid)
        #
        #                     connect_to_database.cnonpn_process_cleanup_table_of_services(pn_ocid=pn_ocid)
        #
        #                     connect_to_database.createAward_process_cleanup_table_of_services(pn_ocid=pn_ocid)
        #
        #                     connect_to_database.cleanup_steps_of_process(operation_id=createEi_operationId)
        #
        #                     connect_to_database.cleanup_steps_of_process(operation_id=createFs_operationId)
        #
        #                     connect_to_database.cleanup_steps_of_process(operation_id=createPn_operationId)
        #
        #                     connect_to_database.cleanup_steps_of_process(operation_id=createCn_operationId)
        #
        #                     connect_to_database.cleanup_steps_of_process_from_orchestrator(
        #                         pn_ocid=pn_ocid)
        #             except ValueError:
        #                 raise ValueError("Can not return BPE operation step")
