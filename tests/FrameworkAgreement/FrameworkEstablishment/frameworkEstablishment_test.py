""" Test of Framework Establishment process for Framework Agreement procedure. """
import copy
import json
import random
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.MessageModels.FrameworkAgreement.frameworkEstablishment_message import FrameworkEstablishmentMessage
from tests.utils.PayloadModels.Budget.ExpenditureItem.expenditureItem_payload import ExpenditureItemPayload
from tests.utils.PayloadModels.Budget.FinancialSource.financialSource_payload import FinancialSourcePayload
from tests.utils.PayloadModels.FrameworkAgreement.AggregatedPlan.aggregatedPlan_payload import AggregatedPlan
from tests.utils.PayloadModels.FrameworkAgreement.AggregatedPlan.updateAggregatedPlan_payload import \
    UpdateAggregatedPlan
from tests.utils.PayloadModels.FrameworkAgreement.FrameworkEstablishment.frameworkEstablishment_payload import \
    FrameworkEstablishmentPayload
from tests.utils.PayloadModels.FrameworkAgreement.PlanningNotice.planingNotice_payload import PlanningNoticePayload
from tests.utils.ReleaseModels.FrameworkAgreement.FE_release.frameworkEstablishment_process import \
    FrameworkEstablishmentRelease
from tests.utils.cassandra_session import CassandraSession
from tests.utils.data_of_enum import currency_tuple
from tests.utils.functions_collection.functions import is_it_uuid
from tests.utils.functions_collection.get_message_for_platform import get_message_for_platform
from tests.utils.platform_query_library import PlatformQueryRequest
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Framework Agreement')
@allure.suite('FrameworkEstablishment')
@allure.sub_suite('BPE: Framework Establishment')
@allure.severity('Critical')
@allure.testcase(url=None)
class TestFrameworkEstablishment:
    @allure.title("\nУВАГА! БАГ https://ustudio.atlassian.net/browse/ES-6922\n"
                  "\nУВАГА! БАГ https://ustudio.atlassian.net/browse/OCDS-225\n"
                  "\n===================================================================================\n"
                  "\nCheck PN, MS, AP_release and MS of CPB releases after RelationAggregatedPlan process, "
                  "without optional fields. \n"
                  "\n===================================================================================\n"
                  "\nCreateEi process: required data model, without items array, buyer_id = 0;\n"
                  "\n===================================================================================\n"
                  "\nСreateFs process: full data model, the own money, procuringEntity_id = 1, buyer_id = 1;\n"
                  "\n===================================================================================\n"
                  "\nСreateFs process: required data model, the treasury money, procuringEntity_id = 0;\n"
                  "\n===================================================================================\n"
                  "\nСreatePn process: required data model, without lots and items, with pmd=TEST_DCO, "
                  "with amount = 910.00;\n"
                  "\n===================================================================================\n"
                  "\nСreatePn process: required data model, without lots and items, with pmd=TEST_MC, "
                  "with amount = 50.00;\n"
                  "\n===================================================================================\n"
                  "\nСreateAp process: required data mode;\n"
                  "\n===================================================================================\n"
                  "\nOutsourcingPlan process: payload is not needed;\n"
                  "\n===================================================================================\n"
                  "\nOutsourcingPlan process: payload is not needed;\n"
                  "\n===================================================================================\n"
                  "\nRelationAggregatedPlan process: payload is not needed;\n"
                  "\n===================================================================================\n"
                  "\nRelationAggregatedPlan process: payload is not needed.\n"
                  "\n===================================================================================\n"
                  "\nUpdateAggregatedPlan process: required data model.\n"
                  "\n===================================================================================\n"
                  "\nFrameworkEstablishment process: required data model.\n"
                  "\n===================================================================================\n"
                  )
    def test_case_1(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                    prepare_tender_classification_id, connect_to_ocds, connect_to_access, connect_to_orchestrator,
                    connect_to_clarification, connect_to_dossier):

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
                    "tender.procuringEntity.contactPoint.url",
                    "tender.documents"
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
            PlatformQueryRequest().do_relation_proces(
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

            relationAp_message_1 = get_message_for_platform(relationAp_1_operationId)
            allure.attach(str(relationAp_message_1), 'Message for platform.')

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
            PlatformQueryRequest().do_relation_proces(
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

            relationAp_message_2 = get_message_for_platform(relationAp_2_operationId)
            allure.attach(str(relationAp_message_2), 'Message for platform.')

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: UpdateAggregatedPlan process.'):
            """
            Tender platform authorization for UpdateAggregatedPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            updateAp_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a UpdateAggregatedPlan process.'):
            """
            Send api request to BPE host to create a UpdateAggregatedPlan process.
            And save in variable ocid and token..
            """
            try:
                """
                Build payload for UpdateAggregatedPlan process.
                """
                update_ap_payload = copy.deepcopy(UpdateAggregatedPlan(
                    host_to_service=get_hosts[2],
                    currency=currency,
                    createAp_payload=ap_payload,
                    maxDurationOfFA=maxDurationOfFA,
                    tenderClassificationId=prepare_tender_classification_id)
                )

                # Read the rule VR.COM-1.26.14.
                update_ap_payload.delete_optional_fields(
                    "tender.procurementMethodRationale",
                    "tender.lots.internalId",
                    # "tender.lots.placeOfPerformance",
                    "tender.items.internalId",
                    "tender.items.additionalClassifications",
                    "tender.items.deliveryAddress",
                    "tender.documents",
                    "tender.value"
                )

                update_ap_payload = update_ap_payload.build_updateAggregatedPlan_payload()
            except ValueError:
                raise ValueError("Impossible to build payload for UpdateAggregatedPlan process.")

            PlatformQueryRequest().update_ap_process(
                host_to_bpe=get_hosts[1],
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                access_token=accessToken,
                x_operation_id=updateAp_operationId,
                ap_token=ap_token,
                payload=update_ap_payload,
                testMode=True
            )

            updateAp_message = get_message_for_platform(updateAp_operationId)
            allure.attach(str(updateAp_message), 'Message for platform.')

        time.sleep(15)
        ap_url = f"{ap_message['data']['url']}/{ap_ocid}"
        actual_ap_release_before_frameworkEstablishment = requests.get(url=ap_url).json()

        cpb_ms_url = f"{ap_message['data']['url']}/{ap_cpid}"
        cpb_actual_ms_release_before_frameworkEstablishment = requests.get(url=cpb_ms_url).json()

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: Framework Establishment process.'):
            """
            Tender platform authorization for CreateFrameworkEstablishment process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            accessToken = platform_one.get_access_token_for_platform_one()
            fe_operationId = platform_one.get_x_operation_id(accessToken)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a Framework Establishment process.'):
            """
            Send api request to BPE host to create a CreateFrameworkEstablishment process.
            """
            try:
                """
                Build payload for CreateFe process. Attention: check optional fields for criteria array. 
                """
                fe_payload = copy.deepcopy(FrameworkEstablishmentPayload(
                    ap_payload=ap_payload,
                    host_to_service=get_hosts[2],
                    country=parse_country,
                    language=parse_language,
                    environment=parse_environment)
                )
                fe_payload.customize_tender_procuringEntity_persones(
                    quantity_of_persones_objects=3,
                    quantity_of_businessFunctions_objects=3,
                    quantity_of_businessFunctions_documents_objects=3
                )

                # # Get all 'standard' criteria from eMDM service.
                # mdm_service = MdmService(
                #     host_to_service=get_hosts[2],
                #     environment=parse_environment)
                #
                # standard_criteria = mdm_service.get_standard_criteria(
                #     parse_country,
                #     parse_language
                # )
                #
                # # Prepare 'exclusion' criteria for payload.
                # some_criteria = CriteriaArray(
                #     host_to_service=get_hosts[2],
                #     country=parse_country,
                #     language=parse_language,
                #     environment=parse_environment,
                #     quantity_of_criteria_objects=len(standard_criteria[1]),
                #     quantity_of_requirementGroups_objects=1,
                #     quantity_of_requirements_objects=2,
                #     quantity_of_eligibleEvidences_objects=2,
                #     type_of_standardCriteria=1
                # )
                #
                # some_criteria.delete_optional_fields(
                #     "criteria.description",
                #     "criteria.requirementGroups.description",
                #     "criteria.requirementGroups.requirements.description",
                #     "criteria.requirementGroups.requirements.period",
                #     "criteria.requirementGroups.requirements.minValue",
                #     "criteria.requirementGroups.requirements.maxValue",
                #     "criteria.requirementGroups.requirements.eligibleEvidences"
                # )
                #
                # some_criteria.prepare_criteria_array(criteria_relatesTo="tenderer")
                # some_criteria.set_unique_temporary_id_for_eligibleEvidences()
                # some_criteria.set_unique_temporary_id_for_criteria()
                # exclusion_criteria_array = some_criteria.build_criteria_array()
                #
                # # Prepare 'selection' criteria for payload.
                # some_criteria = CriteriaArray(
                #     host_to_service=get_hosts[2],
                #     country=parse_country,
                #     language=parse_language,
                #     environment=parse_environment,
                #     quantity_of_criteria_objects=len(standard_criteria[2]),
                #     quantity_of_requirementGroups_objects=2,
                #     quantity_of_requirements_objects=2,
                #     quantity_of_eligibleEvidences_objects=2,
                #     type_of_standardCriteria=2
                # )
                #
                # some_criteria.delete_optional_fields(
                #     "criteria.description",
                #     "criteria.requirementGroups.description",
                #     "criteria.requirementGroups.requirements.description",
                #     "criteria.requirementGroups.requirements.period",
                #     "criteria.requirementGroups.requirements.expectedValue",
                #     "criteria.requirementGroups.requirements.eligibleEvidences"
                # )
                #
                # some_criteria.prepare_criteria_array(criteria_relatesTo="tenderer")
                # some_criteria.set_unique_temporary_id_for_eligibleEvidences()
                # some_criteria.set_unique_temporary_id_for_criteria()
                # selection_criteria_array = some_criteria.build_criteria_array()
                #
                # fe_payload.customize_tender_criteria(exclusion_criteria_array, selection_criteria_array)
                # fe_payload.customize_tender_documents(quantity_of_new_documents=0)

                fe_payload.delete_optional_fields(
                    "tender.secondStage",
                    "tender.procurementMethodModalities",
                    "tender.procurementMethodRationale",
                    "tender.procuringEntity",
                    "tender.criteria",
                    "tender.documents"
                )

                fe_payload = fe_payload.build_frameworkEstablishment_payload()
            except ValueError:
                raise ValueError("Impossible to build payload for CreateFe process.")

            synchronous_result = PlatformQueryRequest().create_fe_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=fe_operationId,
                ap_token=ap_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                payload=fe_payload,
                testMode=True,
            )

        step_number += 1
        with allure.step(f'# {step_number}. See result of FrameworkEstablishment process.'):
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
                             f'the FrameworkEstablishment process.'):
                """
                Check the message for platform.
                """
                actual_message = get_message_for_platform(fe_operationId)

                try:
                    """
                    Build expected message of Framework Establishment process.
                    """
                    expected_message = copy.deepcopy(FrameworkEstablishmentMessage(

                        environment=parse_environment,
                        actual_message=actual_message,
                        testMode=True)
                    )

                    expected_message = expected_message.build_expected_message()
                except ValueError:
                    raise ValueError("Impossible to build expected message of Framework Establishment process.")

                with allure.step('Compare actual and expected message for platform.'):
                    allure.attach(json.dumps(actual_message), "Actual message.")
                    allure.attach(json.dumps(expected_message), "Expected message.")

                    processId = CassandraSession().get_process_id_by_operation_id(connect_to_ocds, fe_operationId)
                    assert actual_message == expected_message, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{processId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.3. Check FE release.'):
                """
                Compare actual and expected FE release.
                """
                actual_fe_release = requests.get(url=f"{actual_message['data']['url']}/"
                                                     f"{actual_message['data']['outcomes']['fe'][0]['id']}").json()

                cpb_actual_ms_release_after_frameworkEstablishment = requests.get(url=cpb_ms_url).json()

                try:
                    """
                    Build expected FE release.
                    """
                    expected_release = copy.deepcopy(FrameworkEstablishmentRelease(
                        environment=parse_environment,
                        host_to_service=get_hosts[2],
                        country=parse_country,
                        language=parse_language,
                        pmd=parse_pmd,
                        fe_payload=fe_payload,
                        fe_message=actual_message,
                        actual_fe_release=actual_fe_release,
                        actual_ms_release=cpb_actual_ms_release_after_frameworkEstablishment,
                        actual_ap_release=actual_ap_release_before_frameworkEstablishment,
                        connect_to_clarification=connect_to_clarification,
                        operation_type="all",
                        parameter="period_shift",
                        ap_cpid=ap_cpid,
                        ap_ocid=ap_ocid
                    ))

                    expected_fe_release = expected_release.build_expected_fe_release()
                except ValueError:
                    raise ValueError("Impossible to build expected FE release.")

                with allure.step("'Compare actual and expected FE release."):

                    allure.attach(json.dumps(actual_fe_release), "Actual result.")
                    allure.attach(json.dumps(expected_fe_release), "Expected result.")

                    assert actual_fe_release == expected_fe_release, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{processId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.4. Check AP release.'):
                """
                Compare actual AP release before and after Framework Establishment process.
                """
                actual_ap_release_after_frameworkEstablishment = requests.get(url=ap_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    actual_ap_release_before_frameworkEstablishment,
                    actual_ap_release_after_frameworkEstablishment)
                )

                # FR-5.0.1 - FR-5.0.3, FR.COM-3.2.11 - FR.COM-3.2.14
                expected_result_of_comparing_releases = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{ap_ocid}-"
                                f"{actual_ap_release_after_frameworkEstablishment['releases'][0]['id'][46:59]}",
                            "old_value":
                                f"{ap_ocid}-"
                                f"{actual_ap_release_before_frameworkEstablishment['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": actual_message['data']['operationDate'],
                            "old_value": actual_ap_release_before_frameworkEstablishment['releases'][0]['date']
                        },
                        "root['releases'][0]['tender']['status']": {
                            "new_value": "planned",
                            "old_value": actual_ap_release_before_frameworkEstablishment[
                                'releases'][0]['tender']['status']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "aggregated",
                            "old_value": actual_ap_release_before_frameworkEstablishment[
                                'releases'][0]['tender']['statusDetails']
                        }
                    }
                }

                with allure.step('Check differences into actual AP release before and after '
                                 'Framework Establishment process.'):
                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{processId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.4. Check MS release of CPB.'):
                """
                 Compare actual MS release of CPB before and after Framework Establishment process.
                """
                cpb_actual_ms_release_after_frameworkEstablishment = requests.get(url=cpb_ms_url).json()

                actual_result_of_comparing_releases = dict(DeepDiff(
                    cpb_actual_ms_release_before_frameworkEstablishment,
                    cpb_actual_ms_release_after_frameworkEstablishment)
                )

                dictionary_item_added_was_cleaned = \
                    str(actual_result_of_comparing_releases['dictionary_item_added']).replace('root', '')[1:-1]

                actual_result_of_comparing_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                actual_result_of_comparing_releases = dict(actual_result_of_comparing_releases)

                # FR.COM-3.2.15 - FR.COM-3.2.19, FR-5.0.8 - FR-5.0.2, FR-5.0.4, BR-1.0.1.4.2, FR.COM-1.28.1
                try:
                    """
                    Prepare expected 'relatedProcess' object with 'relationship' = ['x_establishment'].
                    """
                    is_permanent_relatedProcess_id_correct = is_it_uuid(
                        cpb_actual_ms_release_after_frameworkEstablishment['releases'][0]['relatedProcesses'][3]['id']
                    )

                    if is_permanent_relatedProcess_id_correct is True:
                        pass
                    else:
                        raise ValueError(f"The releases[0].relatedProcess[3].id must be uuid.")

                    expected_relatedProcess_object_xEstablishment = {
                        "id": cpb_actual_ms_release_after_frameworkEstablishment[
                            'releases'][0]['relatedProcesses'][3]['id'],

                        "relationship": ["x_establishment"],
                        "scheme": "ocid",
                        "identifier": actual_message['data']['outcomes']['fe'][0]['id'],
                        "uri": f"{metadata_tender_url}/{ap_cpid}/{actual_message['data']['outcomes']['fe'][0]['id']}"
                    }
                except ValueError:
                    raise ValueError("Impossible to prepare expected 'relatedProcess' object "
                                     "with 'relationship' = ['x_establishment'].")

                try:
                    """
                    Prepare expected 'procuringEntity' object.
                    """
                    for q_0 in range(len(expected_fe_release['releases'][0]['parties'])):
                        if expected_fe_release['releases'][0]['parties'][q_0]['roles'] == ["procuringEntity"]:

                            expected_procuringEntity_object = {
                                "id": expected_fe_release['releases'][0]['parties'][q_0]['id'],
                                "name": expected_fe_release['releases'][0]['parties'][q_0]['name']
                            }
                except ValueError:
                    raise ValueError("Impossible to prepare expected 'procuringEntity' object.")

                expected_result_of_comparing_releases = {
                    "dictionary_item_added": "['releases'][0]['tender']['procuringEntity']",
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{ap_cpid}-"
                                f"{cpb_actual_ms_release_after_frameworkEstablishment['releases'][0]['id'][29:42]}",
                            "old_value":
                                f"{ap_cpid}-"
                                f"{cpb_actual_ms_release_before_frameworkEstablishment['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": actual_message['data']['operationDate'],
                            "old_value": cpb_actual_ms_release_before_frameworkEstablishment['releases'][0]['date']
                        },
                        "root['releases'][0]['tender']['status']": {
                            "new_value": "active",
                            "old_value": cpb_actual_ms_release_before_frameworkEstablishment[
                                'releases'][0]['tender']['status']
                        },
                        "root['releases'][0]['tender']['statusDetails']": {
                            "new_value": "establishment",
                            "old_value": cpb_actual_ms_release_before_frameworkEstablishment[
                                'releases'][0]['tender']['statusDetails']
                        }
                    },
                    "iterable_item_added": {
                        "root['releases'][0]['relatedProcesses'][3]": expected_relatedProcess_object_xEstablishment
                    }
                }

                with allure.step('Check differences into actual MS release before and after '
                                 'Framework Establishment process.'):
                    allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
                    allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")

                    assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{processId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

                with allure.step("Compare actual and expected 'releases[0].tender.procuringEntity' object."):
                    allure.attach(json.dumps(
                        cpb_actual_ms_release_after_frameworkEstablishment['releases'][0]['tender']['procuringEntity']),
                        "Actual result.")

                    allure.attach(json.dumps(expected_procuringEntity_object), "Expected result.")

                    assert cpb_actual_ms_release_after_frameworkEstablishment[
                               'releases'][0]['tender']['procuringEntity'] == expected_procuringEntity_object, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{processId}' ALLOW FILTERING;",
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
                        pn_1_operationId
                    )

                    database.cleanup_ocds_orchestrator_operation_step_by_operation_id(
                        connect_to_ocds,
                        pn_2_operationId
                    )

                    database.cleanup_table_of_services_for_planning_notice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_1_cpid
                    )

                    database.cleanup_table_of_services_for_planning_notice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_2_cpid
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

                    # Clean after outsourcingPlan process:
                    database.cleanup_orchestrator_steps_by_cpid(
                        connect_to_orchestrator,
                        pn_1_cpid
                    )

                    database.cleanup_orchestrator_steps_by_cpid(
                        connect_to_orchestrator,
                        pn_2_cpid
                    )

                    database.cleanup_table_of_services_for_outsourcing_planning_notice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_1_cpid
                    )

                    database.cleanup_table_of_services_for_outsourcing_planning_notice(
                        connect_to_ocds,
                        connect_to_access,
                        pn_2_cpid
                    )

                    # Clean after relationAggregatedPlan process:
                    database.cleanup_orchestrator_steps_by_cpid(
                        connect_to_orchestrator,
                        ap_cpid
                    )

                    database.cleanup_table_of_services_for_relation_aggregated_plan(
                        connect_to_ocds,
                        connect_to_access,
                        ap_cpid
                    )

                    # Clean after updateAggregatedPlan process:
                    database.cleanup_ocds_orchestrator_operation_step_by_operation_id(
                        connect_to_ocds,
                        updateAp_operationId
                    )

                    database.cleanup_table_of_services_for_update_aggregated_plan(
                        connect_to_ocds,
                        connect_to_access,
                        ap_cpid
                    )

                    # Clean after Framework Establishment process:
                    database.cleanup_ocds_orchestrator_operation_step_by_operation_id(
                        connect_to_ocds,
                        fe_operationId
                    )

                    database.cleanup_table_of_services_for_framework_establishment(
                        connect_to_ocds,
                        connect_to_access,
                        connect_to_clarification,
                        connect_to_dossier,
                        ap_cpid
                    )
                except ValueError:
                    raise ValueError("Impossible to cLean up the database.")
