import copy
import json
import random

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.MessageModels.FrameworkAgreement.relationAggregatedPlan_message import RelationApMessage
from tests.utils.PayloadModels.Budget.ExpenditureItem.expenditureItem_payload import ExpenditureItemPayload
from tests.utils.PayloadModels.Budget.FinancialSource.financialSource_payload import FinancialSourcePayload
from tests.utils.PayloadModels.FrameworkAgreement.AggregatedPlan.aggregatedPlan_payload import AggregatedPayload
from tests.utils.PayloadModels.FrameworkAgreement.PlanningNotice.planingNotice_payload import PlanningNoticePayload
from tests.utils.cassandra_session import CassandraSession
from tests.utils.data_of_enum import currency_tuple
from tests.utils.functions_collection.functions import get_value_from_country_csv, get_value_from_region_csv, \
    get_value_from_locality_csv, is_it_uuid
from tests.utils.functions_collection.get_message_for_platform import get_message_for_platform
from tests.utils.platform_query_library import PlatformQueryRequest
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Framework Agreement')
@allure.suite('RelationAggregatedPlan')
@allure.sub_suite('BPE: Relation Aggregated Plan')
@allure.severity('Critical')
@allure.testcase(url=None,
                 name=None)
class TestCreatePn:
    @allure.title("Check PN, MS, AggregatedPlan and MS of CPB releases after RelationAggregatedPlan process, "
                  "without optional fields. \n"
                  "------------------------------------------------\n"
                  "CreateEi process: required data model, without items array, buyer_id = 0;\n"
                  "СreateFs process: full data model, the own money, procuringEntity_id = 1, buyer_id = 1;\n"
                  "СreateFs process: required data model, the treasury money, procuringEntity_id = 0;\n"

                  "СreatePn process: required data model, without lots and items, with pmd=TEST_DCO, "
                  "with amount = 910.00;\n"

                  "СreatePn process: required data model, without lots and items, with pmd=TEST_MC, "
                  "with amount = 50.00;\n"

                  "СreateAp process: required data mode;\n"
                  "OutsourcingPlan process: payload is not needed;\n"
                  "OutsourcingPlan process: payload is not needed;\n"
                  "RelationAggregatedPlan process: payload is not needed;\n"
                  "RelationAggregatedPlan process: payload is not needed.\n")
    def test_case_1(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                    prepare_tenderClassificationId, connect_to_ocds, connect_to_access, connect_to_orchestrator):

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
                    tenderClassificationId=prepare_tenderClassificationId)
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
            allure.attach(str(fs_message), 'Message for platform.')

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: first CreatePn process.'):
            """
            Tender platform authorization for CreatePn process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            pn_1_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a first CreatePn process.'):
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
                    amount=910.00,
                    currency=currency,
                    tenderClassificationId=prepare_tenderClassificationId,
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
                pn_1_payload = pn_payload.build_plan_payload()

            except ValueError:
                raise ValueError("Impossible to build payload for CreatePn process.")

            PlatformQueryRequest().create_pn_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=pn_1_operationId,
                payload=pn_1_payload,
                testMode=True,
                country=parse_country,
                language=parse_language,
                pmd="TEST_DCO"
            )

            pn_1_message = get_message_for_platform(pn_1_operationId)
            pn_1_cpid = pn_1_message['data']['ocid']
            pn_1_ocid = pn_1_message['data']['outcomes']['pn'][0]['id']
            pn_1_token = pn_1_message['data']['outcomes']['pn'][0]['X-TOKEN']
            allure.attach(str(pn_1_message), "Message for platform.")

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: second CreatePn process.'):
            """
            Tender platform authorization for CreatePn process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            pn_2_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a second CreatePn process.'):
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
                    amount=50.00,
                    currency=currency,
                    tenderClassificationId=prepare_tenderClassificationId,
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
                pn_2_payload = pn_payload.build_plan_payload()

            except ValueError:
                raise ValueError("Impossible to build payload for CreatePn process.")

            PlatformQueryRequest().create_pn_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=pn_2_operationId,
                payload=pn_2_payload,
                testMode=True,
                country=parse_country,
                language=parse_language,
                pmd="TEST_MC"
            )

            pn_2_message = get_message_for_platform(pn_2_operationId)
            pn_2_cpid = pn_2_message['data']['ocid']
            pn_2_ocid = pn_2_message['data']['outcomes']['pn'][0]['id']
            pn_2_token = pn_2_message['data']['outcomes']['pn'][0]['X-TOKEN']
            allure.attach(str(pn_2_message), "Message for platform.")

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
                maxDurationOfFA = database.get_maxDurationOfFA_from_access_rules(
                    connect_to_access,
                    parse_country,
                    parse_pmd
                )

                ap_payload = copy.deepcopy(AggregatedPayload(
                    centralPurchasingBody_id=55,
                    host_to_service=get_hosts[2],
                    maxDurationOfFA=maxDurationOfFA,
                    tenderClassificationId=prepare_tenderClassificationId,
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
            ap_token = ap_message['data']['outcomes']['ap'][0]['X-TOKEN']
            allure.attach(str(ap_message), "Message for platform.")

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: first OutsourcingPlan process.'):
            """
            Tender platform authorization for OutsourcingPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            outsourcingPn_1_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a first OutsourcingPlan process.'):
            """
            Send api request to BPE host to create a OutsourcingPlan process.
            """
            PlatformQueryRequest().do_outsourcing_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=outsourcingPn_1_operationId,
                pn_cpid=pn_1_cpid,
                pn_ocid=pn_1_ocid,
                pn_token=pn_1_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                testMode=True,
            )

            outsourcingPn_message_1 = get_message_for_platform(outsourcingPn_1_operationId)
            allure.attach(str(outsourcingPn_message_1), 'Message for platform.')

            pn_url_1 = f"{pn_1_message['data']['url']}/{pn_1_ocid}"
            actual_pn_release_1_before_relationAggregatedPlan = requests.get(url=pn_url_1).json()

            ms_url_1 = f"{pn_1_message['data']['url']}/{pn_1_cpid}"
            actual_ms_release_1_before_relationAggregatedPlan = requests.get(url=ms_url_1).json()

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: second OutsourcingPlan process.'):
            """
            Tender platform authorization for OutsourcingPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            outsourcingPn_2_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a second OutsourcingPlan process.'):
            """
            Send api request to BPE host to create a OutsourcingPlan process.
            """
            PlatformQueryRequest().do_outsourcing_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=outsourcingPn_2_operationId,
                pn_cpid=pn_2_cpid,
                pn_ocid=pn_2_ocid,
                pn_token=pn_2_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                testMode=True,
            )

            outsourcingPn_message_2 = get_message_for_platform(outsourcingPn_2_operationId)
            allure.attach(str(outsourcingPn_message_2), 'Message for platform.')

            pn_url_2 = f"{pn_2_message['data']['url']}/{pn_2_ocid}"
            actual_pn_release_2_before_relationAggregatedPlan = requests.get(url=pn_url_2).json()

            ms_url_2 = f"{pn_2_message['data']['url']}/{pn_2_cpid}"
            actual_ms_release_2_before_relationAggregatedPlan = requests.get(url=ms_url_2).json()

        ap_url = f"{ap_message['data']['url']}/{ap_ocid}"
        actual_ap_release_before_relationAggregatedPlan = requests.get(url=ap_url).json()

        cpb_ms_url = f"{ap_message['data']['url']}/{ap_cpid}"
        cpb_actual_ms_release_before_relationAggregatedPlan = requests.get(url=cpb_ms_url).json()

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: first RelationAggregatedPlan process.'):
            """
            Tender platform authorization for RelationAggregatedPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            relationAp_1_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a first RelationAggregatedPlan process.'):
            """
            Send api request to BPE host to create a RelationAggregatedPlan process.
            """
            synchronous_result = PlatformQueryRequest().do_relation_proces(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=relationAp_1_operationId,
                pn_cpid=pn_1_cpid,
                pn_ocid=pn_1_ocid,
                ap_token=ap_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                testMode=True,
            )

        step_number += 1
        with allure.step(f'# {step_number}. See result of first RelationAggregatedPlan process.'):
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

            with allure.step(f'# {step_number}.2. Check the message of RelationAggregatedPlan for platform.'):
                """
                Check the fs_message for platform.
                """
                actual_message = get_message_for_platform(relationAp_1_operationId)

                try:
                    """
                    Build expected message of RelationAggregatedPlan process.
                    """
                    expected_message = copy.deepcopy(RelationApMessage(

                        environment=parse_environment,
                        actual_message=actual_message,
                        ap_cpid=ap_cpid,
                        ap_ocid=ap_ocid,
                        testMode=True)
                    )

                    expected_message = expected_message.build_expected_message_for_relationAp_process()
                except ValueError:
                    raise ValueError("Impossible to build expected message of RelationAggregatedPlan process.")

                with allure.step('Compare actual and expected message for platform.'):
                    allure.attach(json.dumps(actual_message), "Actual message.")
                    allure.attach(json.dumps(expected_message), "Expected message.")

                    assert actual_message == expected_message, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_1_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.3. Check PN release.'):
                """
                Compare actual PN release before and after RelationAggregatedPlan process.
                """
                actual_pn_release_1_after_relationAggregatedPlan = requests.get(url=pn_url_1).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_pn_release_1_before_relationAggregatedPlan,
                    actual_pn_release_1_after_relationAggregatedPlan)
                )

                expected_result_of_comparing_releases = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{pn_1_ocid}-"
                                f"{actual_pn_release_1_after_relationAggregatedPlan['releases'][0]['id'][46:59]}",

                            "old_value":
                                f"{pn_1_ocid}-"
                                f"{actual_pn_release_1_before_relationAggregatedPlan['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": actual_message['data']['operationDate'],
                            "old_value": outsourcingPn_message_1['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "aggregated",
                            "old_value": "aggregationPending"
                        }
                    }
                }

                with allure.step('Compare actual PN release before and after RelationAggregatedPlan process.'):
                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_1_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.4. Check MS releases.'):
                """
                Compare actual MS releases before and after RelationAggregatedPlan process.
                """
                actual_ms_release_1_after_relationAggregatedPlan = requests.get(url=ms_url_1).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_ms_release_1_before_relationAggregatedPlan,
                    actual_ms_release_1_after_relationAggregatedPlan)
                )

                expected_result_of_comparing_releases = {}

                with allure.step('Compare actual MS release before and after RelationAggregatedPlan process.'):
                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual release.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected release.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_1_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.5. Check AP release.'):
                """
                Compare actual AggregatedPlan release before and after RelationAggregatedPlan process.
                """
                actual_ap_release_after_relationAggregatedPlan = requests.get(url=ap_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_ap_release_before_relationAggregatedPlan,
                    actual_ap_release_after_relationAggregatedPlan)
                )

                dictionary_item_added_was_cleaned = \
                    str(actual_result_of_comparing_releases['dictionary_item_added']).replace('root', '')[1:-1]

                actual_result_of_comparing_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                actual_result_of_comparing_releases = dict(actual_result_of_comparing_releases)

                try:
                    """
                    Prepare expected 'addressDetails' object for party with 'role'= ['client'].
                    """
                    country_data = get_value_from_country_csv(
                        country=ei_payload['buyer']['address']['addressDetails']['country']['id'],
                        language=parse_language
                    )

                    expected_country_object = {
                        "scheme": country_data[2],
                        "id": ei_payload['buyer']['address']['addressDetails']['country']['id'],
                        "description": country_data[1],
                        "uri": country_data[3]
                    }

                    region_data = get_value_from_region_csv(
                        region=ei_payload['buyer']['address']['addressDetails']['region']['id'],
                        country=ei_payload['buyer']['address']['addressDetails']['country']['id'],
                        language=parse_language
                    )
                    expected_region_object = {
                        "scheme": region_data[2],
                        "id": ei_payload['buyer']['address']['addressDetails']['region']['id'],
                        "description": region_data[1],
                        "uri": region_data[3]
                    }

                    if ei_payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                        locality_data = get_value_from_locality_csv(
                            locality=ei_payload['buyer']['address']['addressDetails']['locality']['id'],
                            region=ei_payload['buyer']['address']['addressDetails']['region']['id'],
                            country=ei_payload['buyer']['address']['addressDetails']['country']['id'],
                            language=parse_language
                        )

                        expected_locality_object = {
                            "scheme": locality_data[2],
                            "id": ei_payload['buyer']['address']['addressDetails']['locality']['id'],
                            "description": locality_data[1],
                            "uri": locality_data[3]
                        }

                    else:
                        expected_locality_object = {
                            "scheme": ei_payload['buyer']['address']['addressDetails']['locality']['scheme'],
                            "id": ei_payload['buyer']['address']['addressDetails']['locality']['id'],
                            "description": ei_payload['buyer']['address']['addressDetails']['locality']['description']
                        }
                except ValueError:
                    raise ValueError("Impossible to prepare expected 'addressDetails' object for party "
                                     "with 'role'= ['client'].")

                try:
                    """
                    Prepare expected 'relatedProcess' object with 'relationship' = ['x_scope'].
                    """
                    is_permanent_relatedProcess_id_correct = is_it_uuid(
                        actual_ap_release_after_relationAggregatedPlan['releases'][0]['relatedProcesses'][1]['id']
                    )

                    if is_permanent_relatedProcess_id_correct is True:
                        pass
                    else:
                        raise ValueError(f"The releases[0].relatedProcess[1].id must be uuid.")

                    expected_relatedProcess_object_xScope = {
                        "id": actual_ap_release_after_relationAggregatedPlan[
                            'releases'][0]['relatedProcesses'][1]['id'],

                        "relationship": ["x_scope"],
                        "scheme": "ocid",
                        "identifier": pn_1_ocid,
                        "uri": f"{metadata_tender_url}/{pn_1_cpid}/{pn_1_ocid}"
                    }
                except ValueError:
                    raise ValueError("Impossible to prepare expected 'relatedProcess' object "
                                     "with 'relationship' = ['x_scope'].")

                try:
                    """
                    Prepare expected 'tender.value' object.
                    """
                    amount_from_first_pn_payload = list()
                    for budget in range(len(pn_1_payload['planning']['budget']['budgetBreakdown'])):
                        amount_from_first_pn_payload.append(
                            pn_1_payload['planning']['budget']['budgetBreakdown'][budget]['amount']['amount'])

                    expected_tender_value_amount = sum(amount_from_first_pn_payload)

                    expected_tender_value_object = {
                        "amount": expected_tender_value_amount,
                        "currency": currency
                    }
                except ValueError:
                    raise ValueError("Impossible to prepare expected 'tender.value' object.")

                expected_result_of_comparing_releases = {
                    "dictionary_item_added": "['releases'][0]['tender']['value']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{ap_ocid}-"
                                f"{actual_ap_release_after_relationAggregatedPlan['releases'][0]['id'][46:59]}",

                            "old_value":
                                f"{ap_ocid}-"
                                f"{actual_ap_release_before_relationAggregatedPlan['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": actual_message['data']['operationDate'],
                            "old_value": ap_message['data']['operationDate']
                        }
                    },
                    "iterable_item_added": {
                        "root['releases'][0]['parties'][1]": {
                            "id": f"{ei_payload['buyer']['identifier']['scheme']}-"
                                  f"{ei_payload['buyer']['identifier']['id']}",
                            "name": ei_payload['buyer']['name'],
                            "identifier": {
                                "scheme": ei_payload['buyer']['identifier']['scheme'],
                                "id": ei_payload['buyer']['identifier']['id'],
                                "legalName": ei_payload['buyer']['identifier']['legalName']
                            },
                            "address": {
                                "streetAddress": ei_payload['buyer']['address']['streetAddress'],
                                "addressDetails": {
                                    "country": expected_country_object,
                                    "region": expected_region_object,
                                    "locality": expected_locality_object
                                }
                            },
                            "contactPoint": {
                                "name": ei_payload['buyer']['contactPoint']['name'],
                                "email": ei_payload['buyer']['contactPoint']['email'],
                                "telephone": ei_payload['buyer']['contactPoint']['telephone']
                            },
                            "roles": ["client"]
                        },
                        "root['releases'][0]['relatedProcesses'][1]": expected_relatedProcess_object_xScope
                    }
                }

                with allure.step('Check differences into actual AP release before and after '
                                 'RelationAggregatedPlan process.'):

                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_1_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

                with allure.step("Compare actual and expected 'tender.value' object into AP release,"
                                 " before and after RelationAggregatedPlan process."):

                    allure.attach(json.dumps(
                        actual_ap_release_after_relationAggregatedPlan['releases'][0]['tender']['value']),
                        "Actual object.")

                    allure.attach(json.dumps(expected_tender_value_object), "Expected object.")

                    assert \
                        actual_ap_release_after_relationAggregatedPlan['releases'][0]['tender']['value'] == \
                        expected_tender_value_object, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_1_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.6. Check MS release of CPB.'):
                """
                Compare actual MS release of CPB before and after RelationAggregatedPlan process.
                """
                cpb_actual_ms_release_after_relationAggregatedPlan = requests.get(url=cpb_ms_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    cpb_actual_ms_release_before_relationAggregatedPlan,
                    cpb_actual_ms_release_after_relationAggregatedPlan)
                )

                expected_result_of_comparing_releases = {}

                with allure.step('Check differences into actual MS release of CPB before and after '
                                 'RelationAggregatedPlan process.'):

                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_1_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

        actual_ap_release_before_relationAggregatedPlan = requests.get(url=ap_url).json()
        cpb_actual_ms_release_before_relationAggregatedPlan = requests.get(url=cpb_ms_url).json()

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: second RelationAggregatedPlan process.'):
            """
            Tender platform authorization for RelationAggregatedPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            relationAp_2_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a second RelationAggregatedPlan process.'):
            """
            Send api request to BPE host to create a RelationAggregatedPlan process.
            """
            synchronous_result = PlatformQueryRequest().do_relation_proces(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=relationAp_2_operationId,
                pn_cpid=pn_2_cpid,
                pn_ocid=pn_2_ocid,
                ap_token=ap_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                testMode=True,
            )

        step_number += 1
        with allure.step(f'# {step_number}. See result of second RelationAggregatedPlan process.'):
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

            with allure.step(f'# {step_number}.2. Check the message of RelationAggregatedPlan for platform.'):
                """
                Check the fs_message for platform.
                """
                actual_message = get_message_for_platform(relationAp_2_operationId)

                try:
                    """
                    Build expected message of RelationAggregatedPlan process.
                    """
                    expected_message = copy.deepcopy(RelationApMessage(

                        environment=parse_environment,
                        actual_message=actual_message,
                        ap_cpid=ap_cpid,
                        ap_ocid=ap_ocid,
                        testMode=True)
                    )

                    expected_message = expected_message.build_expected_message_for_relationAp_process()
                except ValueError:
                    raise ValueError("Impossible to build expected message of RelationAggregatedPlan process.")

                with allure.step('Compare actual and expected message for platform.'):
                    allure.attach(json.dumps(actual_message), "Actual message.")
                    allure.attach(json.dumps(expected_message), "Expected message.")

                    assert actual_message == expected_message, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_2_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.3. Check PN release.'):
                """
                Compare actual PN release before and after RelationAggregatedPlan process.
                """
                actual_pn_release_2_after_relationAggregatedPlan = requests.get(url=pn_url_2).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_pn_release_2_before_relationAggregatedPlan,
                    actual_pn_release_2_after_relationAggregatedPlan)
                )

                expected_result_of_comparing_releases = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{pn_2_ocid}-"
                                f"{actual_pn_release_2_after_relationAggregatedPlan['releases'][0]['id'][46:59]}",

                            "old_value":
                                f"{pn_2_ocid}-"
                                f"{actual_pn_release_2_before_relationAggregatedPlan['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": actual_message['data']['operationDate'],
                            "old_value": outsourcingPn_message_2['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "aggregated",
                            "old_value": "aggregationPending"
                        }
                    }
                }

                with allure.step('Check differences into actual PN release before and after '
                                 'RelationAggregatedPlan process.'):

                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_2_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.4. Check MS releases.'):
                """
                Compare actual MS releases before and after RelationAggregatedPlan process.
                """
                actual_ms_release_2_after_relationAggregatedPlan = requests.get(url=ms_url_2).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_ms_release_2_before_relationAggregatedPlan,
                    actual_ms_release_2_after_relationAggregatedPlan)
                )

                expected_result_of_comparing_releases = {}

                with allure.step('Check differences into actual MS release before and after '
                                 'RelationAggregatedPlan process.'):

                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_2_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.5. Check AP release.'):
                """
                Compare actual AggregatedPlan release before and after RelationAggregatedPlan process.
                """
                actual_ap_release_after_relationAggregatedPlan = requests.get(url=ap_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_ap_release_before_relationAggregatedPlan,
                    actual_ap_release_after_relationAggregatedPlan)
                )

                try:
                    """
                    Prepare expected 'relatedProcess' object with 'relationship' = ['x_scope'].
                    """
                    is_permanent_relatedProcess_id_correct = is_it_uuid(
                        actual_ap_release_after_relationAggregatedPlan['releases'][0]['relatedProcesses'][2]['id']
                    )

                    if is_permanent_relatedProcess_id_correct is True:
                        pass
                    else:
                        raise ValueError(f"The releases[0].relatedProcess[2].id must be uuid.")

                    expected_relatedProcess_object_xScope = {
                        "id": actual_ap_release_after_relationAggregatedPlan[
                            'releases'][0]['relatedProcesses'][2]['id'],

                        "relationship": ["x_scope"],
                        "scheme": "ocid",
                        "identifier": pn_2_ocid,
                        "uri": f"{metadata_tender_url}/{pn_2_cpid}/{pn_2_ocid}"
                    }
                except ValueError:
                    raise ValueError("Impossible to prepare expected 'relatedProcess' object "
                                     "with 'relationship' = ['x_scope'].")

                try:
                    """
                    Prepare expected 'tender.value.amount' attribute.
                    """
                    amount_from_first_pn_payload = list()
                    for budget in range(len(pn_1_payload['planning']['budget']['budgetBreakdown'])):
                        amount_from_first_pn_payload.append(
                            pn_1_payload['planning']['budget']['budgetBreakdown'][budget]['amount']['amount'])

                    amount_from_second_pn_payload = list()
                    for budget in range(len(pn_2_payload['planning']['budget']['budgetBreakdown'])):
                        amount_from_second_pn_payload.append(
                            pn_2_payload['planning']['budget']['budgetBreakdown'][budget]['amount']['amount'])

                    expected_tender_value_amount = sum(
                        amount_from_first_pn_payload + amount_from_second_pn_payload
                    )
                except ValueError:
                    raise ValueError("Impossible to prepare expected 'tender.value.amount' attribute.")

                expected_result_of_comparing_releases = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{ap_ocid}-"
                                f"{actual_ap_release_after_relationAggregatedPlan['releases'][0]['id'][46:59]}",

                            "old_value":
                                f"{ap_ocid}-"
                                f"{actual_ap_release_before_relationAggregatedPlan['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": actual_message['data']['operationDate'],
                            "old_value": actual_ap_release_before_relationAggregatedPlan['releases'][0]['date']
                        },
                        "root['releases'][0]['tender']['value']['amount']": {
                            "new_value": expected_tender_value_amount,

                            "old_value": actual_ap_release_before_relationAggregatedPlan[
                                'releases'][0]['tender']['value']['amount']
                        }
                    },
                    "iterable_item_added": {
                        "root['releases'][0]['relatedProcesses'][2]": expected_relatedProcess_object_xScope
                    }
                }

                with allure.step('Check differences into actual AP release before and after '
                                 'RelationAggregatedPlan process.'):

                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_2_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.6. Check MS release of CPB.'):
                """
                Compare actual MS release of CPB before and after RelationAggregatedPlan process.
                """
                cpb_actual_ms_release_after_relationAggregatedPlan = requests.get(url=cpb_ms_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    cpb_actual_ms_release_before_relationAggregatedPlan,
                    cpb_actual_ms_release_after_relationAggregatedPlan)
                )

                expected_result_of_comparing_releases = {}

                with allure.step('Check differences into actual MS release of CPB before and after '
                                 'RelationAggregatedPlan process.'):

                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM orchestrator.steps WHERE "
                                      f"operation_id = '{relationAp_2_operationId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

                try:
                    """
                    CLean up the database.
                    """
                    # Clean after crateEi process:
                    database.cleanup_ocds_orchestratorOperationStep_by_operationId(
                        connect_to_ocds,
                        ei_operationId
                    )

                    database.cleanup_table_of_services_for_expenditureItem(
                        connect_to_ocds,
                        ei_cpid
                    )

                    # Clean after crateFs process:
                    database.cleanup_ocds_orchestratorOperationStep_by_operationId(
                        connect_to_ocds,
                        fs_1_operationId
                    )

                    database.cleanup_ocds_orchestratorOperationStep_by_operationId(
                        connect_to_ocds,
                        fs_2_operationId
                    )

                    database.cleanup_table_of_services_for_financialSource(
                        connect_to_ocds,
                        ei_cpid
                    )

                    # Clean after cratePn process:
                    database.cleanup_ocds_orchestratorOperationStep_by_operationId(
                        connect_to_ocds,
                        pn_1_operationId
                    )

                    database.cleanup_ocds_orchestratorOperationStep_by_operationId(
                        connect_to_ocds,
                        pn_2_operationId
                    )

                    database.cleanup_table_of_services_for_planningNotice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_1_cpid
                    )

                    database.cleanup_table_of_services_for_planningNotice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_2_cpid
                    )

                    # Clean after aggregatedPlan process:
                    database.cleanup_ocds_orchestratorOperationStep_by_operationId(
                        connect_to_ocds,
                        ap_operationId
                    )

                    database.cleanup_table_of_services_for_aggregatedPlan(
                        connect_to_ocds,
                        connect_to_access,
                        ap_cpid
                    )

                    # Clean after outsourcingPlan process:
                    database.cleanup_orchestrator_steps_by_cpid(
                        connect_to_orchestrator,
                        pn_1_cpid
                    )

                    database.cleanup_orchestrator_steps_by_cpid(
                        connect_to_orchestrator,
                        pn_2_cpid
                    )

                    database.cleanup_table_of_services_for_outsourcingPlanningNotice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_1_cpid
                    )

                    database.cleanup_table_of_services_for_outsourcingPlanningNotice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_2_cpid
                    )

                    # Clean after relationAggregatedPlan process:
                    database.cleanup_orchestrator_steps_by_cpid(
                        connect_to_orchestrator,
                        ap_cpid
                    )

                    database.cleanup_table_of_services_for_relationAggregatedPlan(
                        connect_to_ocds,
                        connect_to_access,
                        ap_cpid
                    )
                except ValueError:
                    raise ValueError("Impossible to cLean up the database.")
