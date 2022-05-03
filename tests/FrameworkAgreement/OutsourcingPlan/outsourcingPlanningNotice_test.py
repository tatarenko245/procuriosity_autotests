""" Test of Outsourcing Planning Notice process for Framework Agreement procedure. """
import copy
import json
import random

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.MessageModels.FrameworkAgreement.outsourcingPlanningNotice_message import OutsourcingPnMessage
from tests.utils.PayloadModels.Budget.ExpenditureItem.expenditureItem_payload import ExpenditureItemPayload
from tests.utils.PayloadModels.Budget.FinancialSource.financialSource_payload import FinancialSourcePayload
from tests.utils.PayloadModels.FrameworkAgreement.AggregatedPlan.aggregatedPlan_payload import AggregatedPlan
from tests.utils.PayloadModels.FrameworkAgreement.PlanningNotice.planingNotice_payload import PlanningNoticePayload
from tests.utils.cassandra_session import CassandraSession
from tests.utils.data_of_enum import currency_tuple
from tests.utils.functions_collection.functions import is_it_uuid
from tests.utils.functions_collection.get_message_for_platform import get_message_for_platform
from tests.utils.platform_query_library import PlatformQueryRequest
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Framework Agreement')
@allure.suite('OutsourcingPlanningNotice')
@allure.sub_suite('BPE: Outsourcing PN_release')
@allure.severity('Critical')
@allure.testcase(url=None)
class TestOutsourcingPlanningNotice:
    @allure.title("\nCheck PN, MS, AP_release and MS of CPB releases after OutsourcingPlanningNotice process, "
                  "without optional fields. \n"
                  "\n==================================================================================="
                  "\nCreateEi process: required data model, without items array, buyer_id = 0;"
                  "\n==================================================================================="
                  "\nСreateFs process: full data model, the own money, procuringEntity_id = 1, buyer_id = 1;"
                  "\n==================================================================================="
                  "\nСreateFs process: required data model, the treasury money, procuringEntity_id = 0;"
                  "\n==================================================================================="
                  "\nСreatePn process: required data model, without lots and items."
                  "\n==================================================================================="
                  "\nСreateAp process: required data mode;"
                  "\n==================================================================================="
                  "OutsourcingPlanningNotice process: payload is not needed."
                  "\n===================================================================================")
    def test_case_1(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                    prepare_tender_classification_id, connect_to_ocds, connect_to_access, connect_to_orchestrator):

        metadata_tender_url = None
        try:
            if parse_environment == "dev":
                metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
            elif parse_environment == "sandbox":
                metadata_tender_url = "http://public.eprocurement.systems/tenders"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: CreateEi process.'):
            """
            Tender platform authorization for CreateEi process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            ei_operationId = platform_one.get_x_operation_id(accessToken)

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
                ei_payload = copy.deepcopy(ExpenditureItemPayload(
                    buyer_id=0,
                    tenderClassificationId=prepare_tender_classification_id)
                )

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

                ei_payload = ei_payload.build_expenditure_item_payload()
            except ValueError:
                raise ValueError("Impossible to build payload for CreateEi process.")

            PlatformQueryRequest().create_ei_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=ei_operationId,
                country=parse_country,
                language=parse_language,
                payload=ei_payload,
                testMode=True
            )

            ei_message = get_message_for_platform(ei_operationId)
            ei_cpid = ei_message['data']['ocid']
            allure.attach(str(ei_message), "Message for platform.")

        fs_ocid_list = list()
        fs_payloads_list = list()
        fs_message_list = list()
        currency = f"{random.choice(currency_tuple)}"
        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: first CreateFs process,'
                         f'based on full data model into payload, the own money.'):
            """
            Tender platform authorization for CreateFs process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            fs_1_operationId = platform_one.get_x_operation_id(accessToken)

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
                    payer_id=1,
                    funder_id=1)
                )

                fs_payload = fs_payload.build_financial_source_payload()
                fs_payloads_list.append(fs_payload)
            except ValueError:
                raise ValueError("Impossible to build payload for CreateFs process.")

            PlatformQueryRequest().create_fs_process(
                host_to_bpe=get_hosts[1],
                ei_cpid=ei_cpid,
                access_token=accessToken,
                x_operation_id=fs_1_operationId,
                payload=fs_payload,
                testMode=True
            )

            fs_message = get_message_for_platform(fs_1_operationId)
            fs_message_list.append(fs_message)
            fs_ocid = fs_message['data']['outcomes']['fs'][0]['id']
            fs_ocid_list.append(fs_ocid)
            allure.attach(str(fs_message), "Message for platform.")

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: second CreateFs process,'
                         f'based on required value into payload, the treasury money.'):
            """
            Tender platform authorization for CreateFs process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            fs_2_operationId = platform_one.get_x_operation_id(accessToken)

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
                    payer_id=0)
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

            PlatformQueryRequest().create_fs_process(
                host_to_bpe=get_hosts[1],
                ei_cpid=ei_cpid,
                access_token=accessToken,
                x_operation_id=fs_2_operationId,
                payload=fs_payload,
                testMode=True
            )

            fs_message = get_message_for_platform(fs_2_operationId)
            fs_message_list.append(fs_message)
            fs_ocid = fs_message['data']['outcomes']['fs'][0]['id']
            fs_ocid_list.append(fs_ocid)
            allure.attach(str(fs_message), "Message for platform.")

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: CreatePn process.'):
            """
            Tender platform authorization for CreatePn process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            pn_operationId = platform_one.get_x_operation_id(accessToken)

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
                    fs_id=fs_ocid,
                    amount=909.99,
                    currency=currency,
                    tenderClassificationId=prepare_tender_classification_id,
                    host_to_service=get_hosts[2])
                )

                pn_payload.customize_planning_budget_budgetBreakdown(fs_ocid_list)

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

            PlatformQueryRequest().create_pn_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=pn_operationId,
                payload=pn_payload,
                testMode=True,
                country=parse_country,
                language=parse_language,
                pmd="TEST_DCO"
            )

            pn_message = get_message_for_platform(pn_operationId)
            pn_cpid = pn_message['data']['ocid']
            pn_ocid = pn_message['data']['outcomes']['pn'][0]['id']
            pn_token = pn_message['data']['outcomes']['pn'][0]['X-TOKEN']
            allure.attach(str(pn_message), "Message for platform.")

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: CreateAp process.'):
            """
            Tender platform authorization for CreateAp process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            ap_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a CreateAp process.'):
            """
            Send api request to BPE host to create a CreateAp process.
            And save in variable ocid and token..
            """
            try:
                """
                Build payload for CreateAp process.
                """
                database = CassandraSession()
                maxDurationOfFA = database.get_max_duration_of_fa_from_access_rules(
                    connect_to_access,
                    parse_country,
                    parse_pmd
                )

                ap_payload = copy.deepcopy(AggregatedPlan(
                    centralPurchasingBody_id=55,
                    host_to_service=get_hosts[2],
                    maxDurationOfFA=maxDurationOfFA,
                    tenderClassificationId=prepare_tender_classification_id,
                    currency=currency)
                )

                ap_payload.delete_optional_fields(
                    "tender.procurementMethodRationale",
                    "tender.procuringEntity.additionalIdentifiers",
                    "tender.procuringEntity.address.postalCode",
                    "tender.procuringEntity.contactPoint.faxNumber",
                    "tender.procuringEntity.contactPoint.url"
                )

                ap_payload = ap_payload.build_aggregatedPlan_payload()
            except ValueError:
                raise ValueError("Impossible to build payload for CreateAp process.")

            PlatformQueryRequest().create_ap_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=ap_operationId,
                payload=ap_payload,
                testMode=True,
                country=parse_country,
                language=parse_language,
                pmd=parse_pmd
            )

            ap_message = get_message_for_platform(ap_operationId)
            ap_cpid = ap_message['data']['ocid']
            ap_ocid = ap_message['data']['outcomes']['ap'][0]['id']
            allure.attach(str(ap_message), "Message for platform.")

        pn_url = f"{pn_message['data']['url']}/{pn_ocid}"
        actual_pn_release_before_outsourcingPlanningNotice = requests.get(url=pn_url).json()

        ms_url = f"{pn_message['data']['url']}/{pn_cpid}"
        actual_ms_release_before_outsourcingPlannningNotice = requests.get(url=ms_url).json()

        ap_url = f"{ap_message['data']['url']}/{ap_ocid}"
        actual_ap_release_before_outsourcingPlanningNotice = requests.get(url=ap_url).json()

        cpb_ms_url = f"{ap_message['data']['url']}/{ap_cpid}"
        cpb_actual_ms_release_before_outsourcingPlanningNotice = requests.get(url=cpb_ms_url).json()

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: OutsourcingPlanningNotice process.'):
            """
            Tender platform authorization for OutsourcingPlanningNotice process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            outsourcingPn_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a OutsourcingPlanningNotice process.'):
            """
            Send api request to BPE host to create a OutsourcingPlanningNotice process.
            """
            synchronous_result = PlatformQueryRequest().do_outsourcing_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=outsourcingPn_operationId,
                pn_cpid=pn_cpid,
                pn_ocid=pn_ocid,
                pn_token=pn_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                testMode=True,

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
                    allure.attach(str(synchronous_result.status_code), "Actual status code.")
                    allure.attach(str(202), "Expected status code.")
                    assert synchronous_result.status_code == 202

            with allure.step(f'# {step_number}.2. Check the message for the platform, '
                             f'the OutsourcingPlanningNotice process.'):
                """
                Check the message for platform.
                """
                actual_message = get_message_for_platform(outsourcingPn_operationId)

                try:
                    """
                    Build expected message of OutsourcingPlanningNotice process.
                    """
                    expected_message = copy.deepcopy(OutsourcingPnMessage(
                        environment=parse_environment,
                        actual_message=actual_message,
                        pn_cpid=pn_cpid,
                        pn_ocid=pn_ocid,
                        testMode=True)
                    )

                    expected_message = expected_message.build_expected_message()
                except ValueError:
                    raise ValueError("Impossible to build expected message of OutsourcingPlanningNotice process.")

                with allure.step('Compare actual and expected message for platform.'):
                    allure.attach(json.dumps(actual_message), "Actual message.")
                    allure.attach(json.dumps(expected_message), "Expected message.")

                    assert actual_message == expected_message, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"cpid = '{pn_cpid}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.3. Check PN release.'):
                """
                Compare actual PN release before and after OutsourcingPlanningNotice process.
                """
                actual_pn_release_after_outsourcingPlanningNotice = requests.get(url=pn_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_pn_release_before_outsourcingPlanningNotice,
                    actual_pn_release_after_outsourcingPlanningNotice)
                )
                try:
                    """
                    Prepare relatedProcess object, with relationship = framework.
                    """
                    is_permanent_relatedProcess_id_correct = is_it_uuid(
                        actual_pn_release_after_outsourcingPlanningNotice['releases'][0]['relatedProcesses'][1]['id']
                    )

                    if is_permanent_relatedProcess_id_correct is True:
                        pass
                    else:
                        raise ValueError(f"The releases[0].relatedProcess[1].id must be uuid.")

                    relatedProcess_object_framework = {
                        "root['releases'][0]['relatedProcesses'][1]": {
                            "id": actual_pn_release_after_outsourcingPlanningNotice[
                                'releases'][0]['relatedProcesses'][1]['id'],

                            "relationship": [
                                "framework"
                            ],
                            "scheme": "ocid",
                            "identifier": ap_cpid,
                            "uri": f"{metadata_tender_url}/{ap_cpid}/{ap_cpid}"
                        }
                    }
                except ValueError:
                    raise ValueError("Impossible to prepare relatedProcess object, with relationship = framework")

                expected_result_of_comparing_releases = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{pn_ocid}-"
                                f"{actual_pn_release_after_outsourcingPlanningNotice['releases'][0]['id'][46:59]}",

                            "old_value":
                                f"{pn_ocid}-"
                                f"{actual_pn_release_before_outsourcingPlanningNotice['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": actual_message['data']['operationDate'],
                            "old_value": pn_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "aggregationPending",
                            "old_value": "planning"
                        }
                    },
                    "iterable_item_added": relatedProcess_object_framework
                }

                with allure.step('Check differences into actual PN release before and after '
                                 'OutsourcingPlanningNotice process.'):

                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"cpid = '{pn_cpid}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.4. Check MS release.'):
                """
                Compare actual MS release before and after OutsourcingPlanningNotice process.
                """
                actual_ms_release_after_outsourcingPlanningNotice = requests.get(url=ms_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_ms_release_before_outsourcingPlannningNotice,
                    actual_ms_release_after_outsourcingPlanningNotice)
                )

                expected_result_of_comparing_releases = {}

                with allure.step('Check differences into actual MS release before and after '
                                 'OutsourcingPlanningNotice process.'):
                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"cpid = '{pn_cpid}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.5. Check AP release.'):
                """
                Compare actual AP_release release before and after OutsourcingPlanningNotice process.
                """
                actual_ap_release_after_outsourcingPlanningNotice = requests.get(url=ap_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_ap_release_before_outsourcingPlanningNotice,
                    actual_ap_release_after_outsourcingPlanningNotice)
                )

                expected_result_of_comparing_releases = {}

                with allure.step('Check differences into actual AP_release release before and after '
                                 'OutsourcingPlanningNotice process.'):
                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"cpid = '{pn_cpid}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.6. Check MS release of CPB.'):
                """
                Compare actual MS release of CPB before and after OutsourcingPlanningNotice process.
                """
                actual_ms_release_after_outsourcingPlanningNotice = requests.get(url=cpb_ms_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    cpb_actual_ms_release_before_outsourcingPlanningNotice,
                    actual_ms_release_after_outsourcingPlanningNotice)
                )

                try:
                    """
                    Prepare relatedProcess object, with relationship = x-demand.
                    """
                    is_permanent_relatedProcess_id_correct = is_it_uuid(
                        actual_ms_release_after_outsourcingPlanningNotice['releases'][0]['relatedProcesses'][1]['id']
                    )

                    if is_permanent_relatedProcess_id_correct is True:
                        pass
                    else:
                        raise ValueError(f"The releases[0].relatedProcess[1].id must be uuid.")

                    relatedProcess_object_xDemand = {
                        "root['releases'][0]['relatedProcesses'][1]": {
                            "id": actual_ms_release_after_outsourcingPlanningNotice[
                                'releases'][0]['relatedProcesses'][1]['id'],

                            "relationship": [
                                "x_demand"
                            ],
                            "scheme": "ocid",
                            "identifier": pn_cpid,
                            "uri": f"{metadata_tender_url}/{pn_cpid}/{pn_cpid}"
                        }
                    }
                except ValueError:
                    raise ValueError("Impossible to prepare relatedProcess object, with relationship = framework")

                expected_result_of_comparing_releases = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{ap_cpid}-"
                                f"{actual_ms_release_after_outsourcingPlanningNotice['releases'][0]['id'][29:42]}",

                            "old_value":
                                f"{ap_cpid}-"
                                f"{cpb_actual_ms_release_before_outsourcingPlanningNotice['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": actual_message['data']['operationDate'],
                            "old_value": ap_message['data']['operationDate']
                        }
                    },
                    "iterable_item_added": relatedProcess_object_xDemand
                }

                with allure.step('Check differences into actual MS release of CPB before and after '
                                 'OutsourcingPlanningNotice process.'):

                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"cpid = '{pn_cpid}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")
                try:
                    """
                    CLean up the database.
                    """
                    # Clean after crateEi process:
                    database.cleanup_ocds_orchestrator_operation_step_by_operation_id(
                        connect_to_ocds,
                        ei_operationId
                    )

                    database.cleanup_table_of_services_for_expenditure_item(
                        connect_to_ocds,
                        ei_cpid
                    )

                    # Clean after crateFs process:
                    database.cleanup_ocds_orchestrator_operation_step_by_operation_id(
                        connect_to_ocds,
                        fs_1_operationId
                    )

                    database.cleanup_ocds_orchestrator_operation_step_by_operation_id(
                        connect_to_ocds,
                        fs_2_operationId
                    )

                    database.cleanup_table_of_services_for_financial_source(
                        connect_to_ocds,
                        ei_cpid
                    )

                    # Clean after cratePn process:
                    database.cleanup_ocds_orchestrator_operation_step_by_operation_id(
                        connect_to_ocds,
                        pn_operationId
                    )

                    database.cleanup_table_of_services_for_planning_notice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_cpid
                    )

                    # Clean after aggregatedPlan process:
                    database.cleanup_ocds_orchestrator_operation_step_by_operation_id(
                        connect_to_ocds,
                        ap_operationId
                    )

                    database.cleanup_table_of_services_for_aggregated_plan(
                        connect_to_ocds,
                        connect_to_access,
                        ap_cpid
                    )

                    # Clean after OutsourcingPlanningNotice process:
                    database.cleanup_orchestrator_steps_by_cpid(
                        connect_to_orchestrator,
                        pn_cpid
                    )

                    database.cleanup_table_of_services_for_outsourcing_planning_notice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_cpid
                    )
                except ValueError:
                    raise ValueError("Impossible to cLean up the database.")
