import copy
import json
import random

import allure
import requests

from tests.utils.MessageModels.Pn.planning_notice_message import PlanningNoticeMessage
from tests.utils.PayloadModels.Budget.Fs.financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModels.FrameworkAgreement.Pn.planing_notice_payload import PlanningNoticePayload
from tests.utils.ReleaseModels.FrameworkAgreement.Pn.planning_notice_release import PlanningNoticeRelease
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
                  "CreateEi process: required data model, without items array, buyer_id = 0;\n"
                  "СreateFs process: full data model, the own money, procuringEntity_id = 1, buyer_id = 1;\n"
                  "СreateFs process: required data model, the treasury money, procuringEntity_id = 0;\n"
                  "СreatePn process: required data model, without lots and items.\n")
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
                ei_payload = copy.deepcopy(ExpenditureItemPayload(buyer_id=0))

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

        ei_message = get_message_for_platform(operation_id)
        ei_id = ei_message["data"]["outcomes"]["ei"][0]['id']
        ei_id_list = list()
        ei_id_list.append(ei_id)
        allure.attach(str(ei_message), 'Message for platform.')

        fs_id_list = list()
        fs_payloads_list = list()
        fs_message_list = list()
        currency = f"{random.choice(currency_tuple)}"
        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: first CreateFs process,'
                         f'based on full data model into payload, the own money.'):
            """
            Tender platform authorization for CreateFs process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            operation_id = platform_one.get_x_operation_id(access_token)

            step_number += 1
            with allure.step(f'# {step_number}. Send a request to create first CreateFS process,'
                             f'based on full data model into payload, the own money.'):
                """
                Send api request to BPE host to create a CreateFs process.
                And save in variable cpid.
                """
                try:
                    """
                    Build payload for CreateFs process.
                    """
                    fs_payload = copy.deepcopy(FinancialSourcePayload(
                        ei_payload=ei_payload,
                        amount=89999.89,
                        currency=currency,
                        procuringentity_id=1,
                        buyer_id=0)
                    )

                    fs_payload = fs_payload.build_financial_source_payload()
                    fs_payloads_list.append(fs_payload)
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

                fs_message = get_message_for_platform(operation_id)
                fs_message_list.append(fs_message)
                fs_id = fs_message["data"]["outcomes"]["fs"][0]['id']
                fs_id_list.append(fs_id)
                allure.attach(str(fs_message), 'Message for platform.')

        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: second CreateFs process,'
                         f'based on required value into payload, the treasury money.'):
            """
            Tender platform authorization for CreateFs process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            operation_id = platform_one.get_x_operation_id(access_token)

            step_number += 1
            with allure.step(f'# {step_number}. Send a request to create second CreateFS process, '
                             f'based on required value into payload, the treasury money'):
                """
                Send api request to BPE host to create a CreateFs process.
                And save in variable cpid.
                """
                try:
                    """
                    Build payload for CreateFs process.
                    """
                    fs_payload = copy.deepcopy(FinancialSourcePayload(
                        ei_payload=ei_payload,
                        amount=89999.89,
                        currency=currency,
                        procuringentity_id=1)
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
                        "buyer"
                    )

                    fs_payload = fs_payload.build_financial_source_payload()
                    fs_payloads_list.append(fs_payload)
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

                fs_message = get_message_for_platform(operation_id)
                fs_message_list.append(fs_message)
                fs_id = fs_message["data"]["outcomes"]["fs"][0]['id']
                fs_id_list.append(fs_id)
                allure.attach(str(fs_message), 'Message for platform.')

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
                    amount=909.99,
                    currency=currency,
                    tender_classification_id=tender_classification_id,
                    host_to_service=get_hosts[2])
                )

                pn_payload.customize_planning_budget_budgetbreakdown(fs_id_list)

                # pn_payload.delete_optional_fields(
                #     "planning.rationale",
                #     "planning.budget.description",
                #     "tender.procurementMethodRationale",
                #     "tender.procurementMethodAdditionalInfo",
                #     "tender.lots",
                #     "tender.items",
                #     "tender.documents"
                # )
                pn_payload = pn_payload.build_plan_payload()
                print("PAYLOAD")
                print(json.dumps(pn_payload))
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

            with allure.step(f'# {step_number}.2. Check the fs_message for platform.'):
                """
                Check the fs_message for platform.
                """
                actual_message = get_message_for_platform(operation_id)

                try:
                    """
                    Build expected fs_message for CreatePn process.
                    """
                    expected_message = copy.deepcopy(PlanningNoticeMessage(
                        environment=parse_environment,
                        actual_message=actual_message,
                        expected_quantity_of_outcomes_pn=1,
                        test_mode=True)
                    )

                    expected_message = expected_message.build_expected_message_for_pn_process()
                except ValueError:
                    raise ValueError("Impossible to build expected fs_message for CreatePn process.")

                with allure.step('Compare actual and expected fs_message for platform.'):
                    allure.attach(json.dumps(actual_message), "Actual fs_message.")
                    allure.attach(json.dumps(expected_message), "Expected fs_message.")

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

                ms_url = f"{actual_message['data']['url']}/{actual_message['data']['ocid']}"
                actual_ms_release = requests.get(url=ms_url).json()

                allure.attach(str(json.dumps(actual_pn_release)), "Actual PN release.")

                try:
                    """
                    Build expected PN release.
                    """
                    expected_release = copy.deepcopy(PlanningNoticeRelease(
                        environment=parse_environment,
                        host_to_service=get_hosts[2],
                        language=parse_language,
                        pmd=parse_pmd,
                        pn_payload=pn_payload,
                        pn_message=actual_message,
                        actual_pn_release=actual_pn_release,
                        actual_ms_release=actual_ms_release
                    ))

                    expected_pn_release = expected_release.build_expected_pn_release()
                except ValueError:
                    raise ValueError("Impossible to build expected PN release.")

                with allure.step('Compare actual and expected PN release.'):
                    allure.attach(json.dumps(actual_pn_release), "Actual PN release.")
                    allure.attach(json.dumps(expected_pn_release), "Expected PN release.")

                    assert actual_pn_release == expected_pn_release, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{operation_id}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process")

            with allure.step(f'# {step_number}.4. Check MS release.'):
                """
                Compare actual MS release and expected MS release.
                """

                allure.attach(str(json.dumps(actual_ms_release)), "Actual MS release.")
                print("actual ms release")
                print(json.dumps(actual_ms_release))
                try:
                    """
                    Build expected MS release.
                    """
                    expected_ms_release = expected_release.build_expected_ms_release(
                        ei_payload,
                        ei_message,
                        fs_payloads_list,
                        fs_message_list,
                        tender_classification_id)

                    print("expected ms release")
                    print(json.dumps(expected_ms_release))
                except ValueError:
                    raise ValueError("Impossible to build expected MS release.")
                #
                # with allure.step('Compare actual and expected MS release.'):
                #     allure.attach(json.dumps(actual_ms_release), "Actual MS release.")
                #     allure.attach(json.dumps(expected_ms_release), "Expected MS release.")
                #
                #     assert actual_pn_release == expected_release, \
                #         allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                #                       f"operation_id = '{operation_id}' ALLOW FILTERING;",
                #                       "Cassandra DataBase: steps of process")
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
