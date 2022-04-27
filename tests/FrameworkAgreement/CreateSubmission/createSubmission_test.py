""" Test of Framework Establishment process for Framework Agreement procedure. """
import copy
import json
import random
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.MessageModels.FrameworkAgreement.amendFrameworkEstablishment_message import \
    AmendFrameworkEstablishmentMessage
from tests.utils.PayloadModels.Budget.ExpenditureItem.expenditureItem_payload import ExpenditureItemPayload
from tests.utils.PayloadModels.Budget.FinancialSource.financialSource_payload import FinancialSourcePayload
from tests.utils.PayloadModels.FrameworkAgreement.AggregatedPlan.aggregatedPlan_payload import AggregatedPlan
from tests.utils.PayloadModels.FrameworkAgreement.AggregatedPlan.updateAggregatedPlan_payload import \
    UpdateAggregatedPlan
from tests.utils.PayloadModels.FrameworkAgreement.FrameworkEstablishment.amendFrameworkEstablishment_payload import \
    AmendFrameworkEstablishmentPayload
from tests.utils.PayloadModels.FrameworkAgreement.FrameworkEstablishment.frameworkEstablishment_payload import \
    FrameworkEstablishmentPayload
from tests.utils.PayloadModels.FrameworkAgreement.PlanningNotice.planingNotice_payload import PlanningNoticePayload
from tests.utils.PayloadModels.FrameworkAgreement.Submission.createSubmission_payload import CreateSubmissionPayload
from tests.utils.cassandra_session import CassandraSession
from tests.utils.data_of_enum import currency_tuple
from tests.utils.date_class import Date
from tests.utils.functions_collection.generate_criteria_array import CriteriaArray
from tests.utils.functions_collection.get_message_for_platform import get_message_for_platform
from tests.utils.platform_query_library import PlatformQueryRequest
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.services.e_mdm_service import MdmService


@allure.parent_suite('Framework Agreement')
@allure.suite('CreateSubmission')
@allure.sub_suite('BPE: Create Submission')
@allure.severity('Critical')
@allure.testcase(url=None)
class TestCreatePn:
    @allure.title("\nУВАГА! БАГ https://ustudio.atlassian.net/browse/ES-6922\n"
                  "\nУВАГА! БАГ https://ustudio.atlassian.net/browse/OCDS-225\n"
                  "\nУВАГА! БАГ https://ustudio.atlassian.net/browse/OCDS-266\n"
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
                  "\nAmendFrameworkEstablishment process: required data model (change 'preQualification').\n"
                  "\n===================================================================================\n"
                  "\nCreateSubmission process: required data model.\n"
                  "\n===================================================================================\n"
                  )
    def test_case_1(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                    prepare_tender_classification_id, connect_to_ocds, connect_to_access, connect_to_orchestrator,
                    connect_to_clarification, connect_to_dossier):

        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: CreateEi process.'):
            """
            Tender platform authorization for CreateEi process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            ei_operation_id = platform_one.get_x_operation_id(access_token)

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
                access_token=access_token,
                x_operation_id=ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=ei_payload,
                testMode=True
            )

            ei_message = get_message_for_platform(ei_operation_id)
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
            access_token = platform_one.get_access_token_for_platform_one()
            fs_1_operation_id = platform_one.get_x_operation_id(access_token)

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
                access_token=access_token,
                x_operation_id=fs_1_operation_id,
                payload=fs_payload,
                testMode=True
            )

            fs_message = get_message_for_platform(fs_1_operation_id)
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
            access_token = platform_one.get_access_token_for_platform_one()
            fs_2_operation_id = platform_one.get_x_operation_id(access_token)

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
                access_token=access_token,
                x_operation_id=fs_2_operation_id,
                payload=fs_payload,
                testMode=True
            )

            fs_message = get_message_for_platform(fs_2_operation_id)
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
            access_token = platform_one.get_access_token_for_platform_one()
            pn_1_operation_id = platform_one.get_x_operation_id(access_token)

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
                access_token=access_token,
                x_operation_id=pn_1_operation_id,
                payload=pn_1_payload,
                testMode=True,
                country=parse_country,
                language=parse_language,
                pmd="TEST_DCO"
            )

            pn_1_message = get_message_for_platform(pn_1_operation_id)
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
            access_token = platform_one.get_access_token_for_platform_one()
            pn_2_operation_id = platform_one.get_x_operation_id(access_token)

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
                access_token=access_token,
                x_operation_id=pn_2_operation_id,
                payload=pn_2_payload,
                testMode=True,
                country=parse_country,
                language=parse_language,
                pmd="TEST_MC"
            )

            pn_2_message = get_message_for_platform(pn_2_operation_id)
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
            access_token = platform_one.get_access_token_for_platform_one()
            ap_operation_id = platform_one.get_x_operation_id(access_token)

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
                max_duration_of_fa = database.get_maxDurationOfFA_from_access_rules(
                    connect_to_access,
                    parse_country,
                    parse_pmd
                )

                ap_payload = copy.deepcopy(AggregatedPlan(
                    centralPurchasingBody_id=55,
                    host_to_service=get_hosts[2],
                    maxDurationOfFA=max_duration_of_fa,
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
                access_token=access_token,
                x_operation_id=ap_operation_id,
                payload=ap_payload,
                testMode=True,
                country=parse_country,
                language=parse_language,
                pmd=parse_pmd
            )

            ap_message = get_message_for_platform(ap_operation_id)
            ap_cpid = ap_message['data']['ocid']
            ap_ocid = ap_message['data']['outcomes']['ap'][0]['id']
            ap_token = ap_message['data']['outcomes']['ap'][0]['X-TOKEN']
            ap_url = f"{ap_message['data']['url']}/{ap_ocid}"
            cpb_ms_url = f"{ap_message['data']['url']}/{ap_cpid}"
            allure.attach(str(ap_message), "Message for platform.")

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: first OutsourcingPlan process.'):
            """
            Tender platform authorization for OutsourcingPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            outsourcing_pn_1_operation_id = platform_one.get_x_operation_id(access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a first OutsourcingPlan process.'):
            """
            Send api request to BPE host to create a OutsourcingPlan process.
            """
            PlatformQueryRequest().do_outsourcing_process(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=outsourcing_pn_1_operation_id,
                pn_cpid=pn_1_cpid,
                pn_ocid=pn_1_ocid,
                pn_token=pn_1_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                testMode=True,
            )

            outsourcing_pn_message_1 = get_message_for_platform(outsourcing_pn_1_operation_id)
            allure.attach(str(outsourcing_pn_message_1), 'Message for platform.')

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: second OutsourcingPlan process.'):
            """
            Tender platform authorization for OutsourcingPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            outsourcing_pn_2_operation_id = platform_one.get_x_operation_id(access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a second OutsourcingPlan process.'):
            """
            Send api request to BPE host to create a OutsourcingPlan process.
            """
            PlatformQueryRequest().do_outsourcing_process(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=outsourcing_pn_2_operation_id,
                pn_cpid=pn_2_cpid,
                pn_ocid=pn_2_ocid,
                pn_token=pn_2_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                testMode=True,
            )

            outsourcing_pn_message_2 = get_message_for_platform(outsourcing_pn_2_operation_id)
            allure.attach(str(outsourcing_pn_message_2), 'Message for platform.')

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: first RelationAggregatedPlan process.'):
            """
            Tender platform authorization for RelationAggregatedPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            relation_ap_1_operation_id = platform_one.get_x_operation_id(access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a first RelationAggregatedPlan process.'):
            """
            Send api request to BPE host to create a RelationAggregatedPlan process.
            """
            PlatformQueryRequest().do_relation_proces(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=relation_ap_1_operation_id,
                pn_cpid=pn_1_cpid,
                pn_ocid=pn_1_ocid,
                ap_token=ap_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                testMode=True,
            )

            relation_ap_message_1 = get_message_for_platform(relation_ap_1_operation_id)
            allure.attach(str(relation_ap_message_1), 'Message for platform.')

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: second RelationAggregatedPlan process.'):
            """
            Tender platform authorization for RelationAggregatedPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            relation_ap_2_operation_id = platform_one.get_x_operation_id(access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create a second RelationAggregatedPlan process.'):
            """
            Send api request to BPE host to create a RelationAggregatedPlan process.
            """
            PlatformQueryRequest().do_relation_proces(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=relation_ap_2_operation_id,
                pn_cpid=pn_2_cpid,
                pn_ocid=pn_2_ocid,
                ap_token=ap_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                testMode=True,
            )

            relation_ap_message_2 = get_message_for_platform(relation_ap_2_operation_id)
            allure.attach(str(relation_ap_message_2), 'Message for platform.')

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: UpdateAggregatedPlan process.'):
            """
            Tender platform authorization for UpdateAggregatedPlan process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            update_ap_operation_id = platform_one.get_x_operation_id(access_token)

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
                    maxDurationOfFA=max_duration_of_fa,
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
                access_token=access_token,
                x_operation_id=update_ap_operation_id,
                ap_token=ap_token,
                payload=update_ap_payload,
                testMode=True
            )

            update_ap_message = get_message_for_platform(update_ap_operation_id)
            allure.attach(str(update_ap_message), 'Message for platform.')

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: Framework Establishment process.'):
            """
            Tender platform authorization for CreateFrameworkEstablishment process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            fe_operation_id = platform_one.get_x_operation_id(access_token)

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

                # Get all 'standard' criteria from eMDM service.
                mdm_service = MdmService(
                    host_to_service=get_hosts[2],
                    environment=parse_environment)

                standard_criteria = mdm_service.get_standard_criteria(
                    parse_country,
                    parse_language
                )

                # Prepare 'exclusion' criteria for payload.
                some_criteria = CriteriaArray(
                    host_to_service=get_hosts[2],
                    country=parse_country,
                    language=parse_language,
                    environment=parse_environment,
                    quantity_of_criteria_objects=len(standard_criteria[1]),
                    quantity_of_requirementGroups_objects=1,
                    quantity_of_requirements_objects=2,
                    quantity_of_eligibleEvidences_objects=2,
                    type_of_standardCriteria=1
                )

                some_criteria.delete_optional_fields(
                    # "criteria.description",
                    # "criteria.requirementGroups.description",
                    # "criteria.requirementGroups.requirements.description",
                    # "criteria.requirementGroups.requirements.period",
                    "criteria.requirementGroups.requirements.minValue",
                    "criteria.requirementGroups.requirements.maxValue",
                    # "criteria.requirementGroups.requirements.eligibleEvidences"
                )

                some_criteria.prepare_criteria_array(criteria_relatesTo="tenderer")
                some_criteria.set_unique_temporary_id_for_eligibleEvidences()
                some_criteria.set_unique_temporary_id_for_criteria()
                exclusion_criteria_array = some_criteria.build_criteria_array()

                # Prepare 'selection' criteria for payload.
                some_criteria = CriteriaArray(
                    host_to_service=get_hosts[2],
                    country=parse_country,
                    language=parse_language,
                    environment=parse_environment,
                    quantity_of_criteria_objects=len(standard_criteria[2]),
                    quantity_of_requirementGroups_objects=2,
                    quantity_of_requirements_objects=2,
                    quantity_of_eligibleEvidences_objects=2,
                    type_of_standardCriteria=2
                )

                some_criteria.delete_optional_fields(
                    # "criteria.description",
                    # "criteria.requirementGroups.description",
                    # "criteria.requirementGroups.requirements.description",
                    # "criteria.requirementGroups.requirements.period",
                    "criteria.requirementGroups.requirements.expectedValue",
                    # "criteria.requirementGroups.requirements.eligibleEvidences"
                )

                some_criteria.prepare_criteria_array(criteria_relatesTo="tenderer")
                some_criteria.set_unique_temporary_id_for_eligibleEvidences()
                some_criteria.set_unique_temporary_id_for_criteria()
                selection_criteria_array = some_criteria.build_criteria_array()

                fe_payload.customize_tender_criteria(exclusion_criteria_array, selection_criteria_array)
                fe_payload.customize_tender_documents(quantity_of_new_documents=0)

                # fe_payload.delete_optional_fields(
                #     "tender.secondStage",
                #     "tender.procurementMethodModalities",
                #     "tender.procurementMethodRationale",
                #     "tender.procuringEntity",
                #     "tender.criteria",
                #     "tender.documents"
                # )

                fe_payload = fe_payload.build_frameworkEstablishment_payload()
            except ValueError:
                raise ValueError("Impossible to build payload for CreateFe process.")

            PlatformQueryRequest().create_fe_process(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=fe_operation_id,
                ap_token=ap_token,
                ap_cpid=ap_cpid,
                ap_ocid=ap_ocid,
                payload=fe_payload,
                testMode=True,
            )

            fe_message = get_message_for_platform(fe_operation_id)
            fe_ocid = fe_message['data']['outcomes']['fe'][0]['id']
            fe_url = f"{fe_message['data']['url']}/{fe_ocid}"
            allure.attach(str(fe_message), 'Message for platform.')

        time.sleep(15)
        actual_fe_release_before_amend_framework_establishment = requests.get(url=fe_url).json()

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: Amend Framework Establishment process.'):
            """
            Tender platform authorization for AmendFrameworkEstablishment process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            amend_fe_operation_id = platform_one.get_x_operation_id(access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create an Amend Framework Establishment process.'):
            """
            Send api request to BPE host to create an AmendFrameworkEstablishment process.
            """
            try:
                """
                Build payload for Amend FE process.
                """
                amend_fe_payload = copy.deepcopy(AmendFrameworkEstablishmentPayload(
                    ap_payload=ap_payload,
                    fe_payload=fe_payload,
                    fe_release=actual_fe_release_before_amend_framework_establishment,
                    host_to_service=get_hosts[2],
                    country=parse_country,
                    language=parse_language,
                    environment=parse_environment)
                )

                amend_fe_payload.delete_optional_fields(
                    "tender.procuringEntity",
                    "tender.documents",
                    "tender.procurementMethodRationale"
                )
                amend_fe_payload = amend_fe_payload.build_amendFrameworkEstablishment_payload()

            except ValueError:
                raise ValueError("Impossible to build payload for Amend FE process.")

            PlatformQueryRequest().amend_fe_process(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=amend_fe_operation_id,
                ap_token=ap_token,
                ap_cpid=ap_cpid,
                ap_ocid=fe_ocid,
                payload=amend_fe_payload,
                testMode=True,
            )

            amend_fe_message = get_message_for_platform(amend_fe_operation_id)
            allure.attach(str(amend_fe_message), 'Message for platform.')

        time.sleep(15)
        actual_fe_release_before_create_submission = requests.get(url=fe_url).json()
        actual_ap_release_before_create_submission = requests.get(url=ap_url).json()
        cpb_actual_ms_release_before_create_submission = requests.get(url=cpb_ms_url).json()

        print("actual_fe_release_before_create_Submission")
        print(json.dumps(actual_fe_release_before_create_submission))

        step_number += 1
        with allure.step(f'# {step_number}. Authorization platform one: Create Submission process.'):
            """
            Tender platform authorization for CreateSubmission process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            create_submission_operation_id = platform_one.get_x_operation_id(access_token)

        step_number += 1
        with allure.step(f'# {step_number}. Send a request to create an Create Submission process.'):
            """
            Send api request to BPE host to create an CreateSubmission process.
            """
            try:
                """
                Build payload for Create Submission process.
                """
                create_submission_payload = CreateSubmissionPayload(
                    host_to_service=get_hosts[2],
                    actual_fe_release=actual_fe_release_before_create_submission
                )
                # create_submission_payload.delete_optional_fields(
                #     "submission.requirementResponses",
                #     "submission.candidates.identifier.uri",
                #     "submission.candidates.additionalIdentifiers",
                #     "submission.candidates.address.postalCode",
                #     "submission.candidates.contactPoint.faxNumber",
                #     "submission.candidates.contactPoint.url",
                #     "submission.candidates.persones",
                #     "submission.candidates.details.typeOfSupplier",
                #     "submission.candidates.details.mainEconomicActivities",
                #     "submission.candidates.details.bankAccounts",
                #     "submission.candidates.details.legalForm.uri",
                #     "submission.documents"
                # )
                create_submission_payload.prepare_submission_object(
                    quantity_of_candidates=3,
                    quantity_of_additional_identifiers=3,
                    quantity_of_persones=3,
                    quantity_of_evidences=3,
                    quantity_of_business_functions=3,
                    quantity_of_bf_documents=3,
                    quantity_of_main_economic_activities=3,
                    quantity_of_bank_accounts=3,
                    quantity_of_additional_account_identifiers=3,
                    quantity_of_documents=3
                )
                create_submission_payload = create_submission_payload.build_create_submission_payload()

                print("create_submission_payload")
                print(json.dumps(create_submission_payload))

            except ValueError:
                raise ValueError("Impossible to build payload for Create Submission process.")

            synchronous_result = PlatformQueryRequest().create_submission_process(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=create_submission_operation_id,
                ap_cpid=ap_cpid,
                ap_ocid=fe_ocid,
                payload=create_submission_payload,
                test_mode=True,
            )
            print(f"synchronous_result={synchronous_result.status_code}")
        # step_number += 1
        # with allure.step(f'# {step_number}. See result of Amend Framework Establishment process.'):
        #     """
        #     Check the results of TestCase.
        #     """
        #
        #     with allure.step(f'# {step_number}.1. Check status code'):
        #         """
        #         Check the status code of sending the request.
        #         """
        #         with allure.step('Compare actual status code and expected status code of sending request.'):
        #             allure.attach(str(synchronous_result.status_code), "Actual status code.")
        #             allure.attach(str(202), "Expected status code.")
        #             assert synchronous_result.status_code == 202
        #
        #     with allure.step(f'# {step_number}.2. Check the message for the platform, '
        #                      f'the Amend Framework Establishment process.'):
        #         """
        #         Check the message for platform.
        #         """
        #         actual_message = get_message_for_platform(amend_fe_operation_id)
        #
        #         try:
        #             """
        #             Build expected message of Amend Framework Establishment process.
        #             """
        #             expected_message = copy.deepcopy(AmendFrameworkEstablishmentMessage(
        #                 environment=parse_environment,
        #                 actual_message=actual_message,
        #                 ap_cpid=ap_cpid,
        #                 fe_ocid=fe_ocid,
        #                 testMode=True)
        #             )
        #
        #             expected_message = expected_message.build_expected_message()
        #         except ValueError:
        #             raise ValueError("Impossible to build expected message of Amend Framework Establishment process.")
        #
        #         with allure.step('Compare actual and expected message for platform.'):
        #             allure.attach(json.dumps(actual_message), "Actual message.")
        #             allure.attach(json.dumps(expected_message), "Expected message.")
        #
        #             processId = CassandraSession().get_processId_by_operationId(connect_to_ocds, amend_fe_operation_id)
        #             assert actual_message == expected_message, \
        #                 allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
        #                               f"process_id = '{processId}' ALLOW FILTERING;",
        #                               "Cassandra DataBase: steps of process.")
        #
        #     with allure.step(f'# {step_number}.3. Check FE release.'):
        #         """
        #         Compare actual FE release before and after Amend Framework Establishment process.
        #         """
        #         actual_fe_release_after_amendFrameworkEstablishment = requests.get(url=fe_url).json()
        #
        #         actual_result_of_comparing_releases = dict(DeepDiff(
        #             actual_fe_release_before_amend_framework_establishment,
        #             actual_fe_release_after_amendFrameworkEstablishment
        #         ))
        #
        #         try:
        #             """Prepare expected 'enquiryPeriod.endDate' attribute."""
        #             # FR.COM-8.1.1, FR.COM-8.1.2:
        #             database = CassandraSession()
        #
        #             period_shift = database.get_parameter_from_clarification_rules(
        #                 connect_to_clarification, parse_country, parse_pmd, "all", "period_shift")
        #
        #             date = Date()
        #             expected_enquiryPeriod_endDate = date.selectiveProcedure_enquiryPeriod_endDate(
        #                 preQualification_period_endDate=amend_fe_payload['preQualification']['period']['endDate'],
        #                 interval_seconds=int(period_shift)
        #             )
        #         except ValueError:
        #             raise ValueError("Impossible to prepare expected 'enquiryPeriod.endDate' attribute.")
        #
        #         # FR.COM-3.2.1, FR.COM-3.2.2, FR.COM-3.2.3, FR.COM-3.2.5, FR-5.0.1, FR-5.0.2, FR-5.0.3:
        #         expected_result_of_comparing_releases = {
        #             "values_changed": {
        #                 "root['releases'][0]['id']": {
        #                     "new_value":
        #                         f"{fe_ocid}-"
        #                         f"{actual_fe_release_after_amendFrameworkEstablishment['releases'][0]['id'][46:59]}",
        #                     "old_value":
        #                         f"{fe_ocid}-"
        #                         f"{actual_fe_release_before_amend_framework_establishment['releases'][0]['id'][46:59]}"
        #                 },
        #                 "root['releases'][0]['date']": {
        #                     "new_value": actual_message['data']['operationDate'],
        #                     "old_value": actual_fe_release_before_amend_framework_establishment['releases'][0]['date']
        #                 },
        #                 "root['releases'][0]['tag'][0]": {
        #                     "new_value": "tenderAmendment",
        #                     "old_value": actual_fe_release_before_amend_framework_establishment['releases'][0]['tag'][0]
        #                 },
        #                 "root['releases'][0]['tender']['enquiryPeriod']['endDate']": {
        #                     "new_value": expected_enquiryPeriod_endDate,
        #                     "old_value": actual_fe_release_before_amend_framework_establishment[
        #                         'releases'][0]['tender']['enquiryPeriod']['endDate']
        #                 },
        #                 "root['releases'][0]['preQualification']['period']['endDate']": {
        #                     "new_value": amend_fe_payload['preQualification']['period']['endDate'],
        #                     "old_value": actual_fe_release_before_amend_framework_establishment[
        #                         'releases'][0]['preQualification']['period']['endDate']
        #                 }
        #             }
        #         }
        #
        #         with allure.step('Check differences into actual FE release before and after '
        #                          'Amend Framework Establishment process.'):
        #             allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
        #             allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")
        #
        #             assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
        #                 allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
        #                               f"process_id = '{processId}' ALLOW FILTERING;",
        #                               "Cassandra DataBase: steps of process.")
        #
        #     with allure.step(f'# {step_number}.4. Check AP release.'):
        #         """
        #         Compare actual AP release before and after Amend Framework Establishment process.
        #         """
        #         actual_ap_release_after_amendFrameworkEstablishment = requests.get(url=ap_url).json()
        #
        #         actual_result_of_comparing_releases = dict(DeepDiff(
        #             actual_ap_release_before_amendFrameworkEstablishment,
        #             actual_ap_release_after_amendFrameworkEstablishment
        #         ))
        #
        #         expected_result_of_comparing_releases = {}
        #
        #         with allure.step('Check differences into actual AP release before and after '
        #                          'Amend Framework Establishment process.'):
        #             allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
        #             allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")
        #
        #             assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
        #                 allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
        #                               f"process_id = '{processId}' ALLOW FILTERING;",
        #                               "Cassandra DataBase: steps of process.")
        #
        #     with allure.step(f'# {step_number}.5. Check MS release of CPB.'):
        #         """
        #          Compare actual MS release of CPB before and after Amend Framework Establishment process.
        #         """
        #         cpb_actual_ms_release_after_amendFrameworkEstablishment = requests.get(url=cpb_ms_url).json()
        #
        #         actual_result_of_comparing_releases = dict(DeepDiff(
        #             cpb_actual_ms_release_before_amendFrameworkEstablishment,
        #             cpb_actual_ms_release_after_amendFrameworkEstablishment
        #         ))
        #
        #         # FR-5.0.8 - FR-5.0.2, FR-5.0.4, FR.COM-3.2.6 - FR.COM-3.2.11:
        #         expected_result_of_comparing_releases = {}
        #
        #         with allure.step('Check differences into actual MS release before and after '
        #                          'Amend Framework Establishment process.'):
        #             allure.attach(json.dumps(actual_result_of_comparing_releases), "Actual result.")
        #             allure.attach(json.dumps(expected_result_of_comparing_releases), "Expected result.")
        #
        #             assert actual_result_of_comparing_releases == expected_result_of_comparing_releases, \
        #                 allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
        #                               f"process_id = '{processId}' ALLOW FILTERING;",
        #                               "Cassandra DataBase: steps of process.")
        #
        #         try:
        #             """
        #             CLean up the database.
        #             """
        #             # Clean after crateEi process:
        #             database.cleanup_ocds_orchestratorOperationStep_by_operationId(
        #                 connect_to_ocds,
        #                 ei_operation_id
        #             )
        #
        #             database.cleanup_table_of_services_for_expenditureItem(
        #                 connect_to_ocds,
        #                 ei_cpid
        #             )
        #
        #             # Clean after crateFs process:
        #             database.cleanup_ocds_orchestratorOperationStep_by_operationId(
        #                 connect_to_ocds,
        #                 fs_1_operation_id
        #             )
        #
        #             database.cleanup_ocds_orchestratorOperationStep_by_operationId(
        #                 connect_to_ocds,
        #                 fs_2_operation_id
        #             )
        #
        #             database.cleanup_table_of_services_for_financialSource(
        #                 connect_to_ocds,
        #                 ei_cpid
        #             )
        #
        #             # Clean after cratePn process:
        #             database.cleanup_ocds_orchestratorOperationStep_by_operationId(
        #                 connect_to_ocds,
        #                 pn_1_operation_id
        #             )
        #
        #             database.cleanup_ocds_orchestratorOperationStep_by_operationId(
        #                 connect_to_ocds,
        #                 pn_2_operation_id
        #             )
        #
        #             database.cleanup_table_of_services_for_planningNotice(
        #                 connect_to_ocds,
        #                 connect_to_access,
        #                 pn_1_cpid
        #             )
        #
        #             database.cleanup_table_of_services_for_planningNotice(
        #                 connect_to_ocds,
        #                 connect_to_access,
        #                 pn_2_cpid
        #             )
        #
        #             # Clean after aggregatedPlan process:
        #             database.cleanup_ocds_orchestratorOperationStep_by_operationId(
        #                 connect_to_ocds,
        #                 ap_operation_id
        #             )
        #
        #             database.cleanup_table_of_services_for_aggregatedPlan(
        #                 connect_to_ocds,
        #                 connect_to_access,
        #                 ap_cpid
        #             )
        #
        #             # Clean after outsourcingPlan process:
        #             database.cleanup_orchestrator_steps_by_cpid(
        #                 connect_to_orchestrator,
        #                 pn_1_cpid
        #             )
        #
        #             database.cleanup_orchestrator_steps_by_cpid(
        #                 connect_to_orchestrator,
        #                 pn_2_cpid
        #             )
        #
        #             database.cleanup_table_of_services_for_outsourcingPlanningNotice(
        #                 connect_to_ocds,
        #                 connect_to_access,
        #                 pn_1_cpid
        #             )
        #
        #             database.cleanup_table_of_services_for_outsourcingPlanningNotice(
        #                 connect_to_ocds,
        #                 connect_to_access,
        #                 pn_2_cpid
        #             )
        #
        #             # Clean after relationAggregatedPlan process:
        #             database.cleanup_orchestrator_steps_by_cpid(
        #                 connect_to_orchestrator,
        #                 ap_cpid
        #             )
        #
        #             database.cleanup_table_of_services_for_relationAggregatedPlan(
        #                 connect_to_ocds,
        #                 connect_to_access,
        #                 ap_cpid
        #             )
        #
        #             # Clean after updateAggregatedPlan process:
        #             database.cleanup_ocds_orchestratorOperationStep_by_operationId(
        #                 connect_to_ocds,
        #                 update_ap_operation_id
        #             )
        #
        #             database.cleanup_table_of_services_for_updateAggregatedPlan(
        #                 connect_to_ocds,
        #                 connect_to_access,
        #                 ap_cpid
        #             )
        #
        #             # Clean after Framework Establishment process:
        #             database.cleanup_ocds_orchestratorOperationStep_by_operationId(
        #                 connect_to_ocds,
        #                 fe_operation_id
        #             )
        #
        #             database.cleanup_table_of_services_for_frameworkEstablishment(
        #                 connect_to_ocds,
        #                 connect_to_access,
        #                 connect_to_clarification,
        #                 connect_to_dossier,
        #                 ap_cpid
        #             )
        #
        #             # Clean after Amend Framework Establishment process:
        #             database.cleanup_ocds_orchestratorOperationStep_by_operationId(
        #                 connect_to_ocds,
        #                 amend_fe_operation_id
        #             )
        #         except ValueError:
        #             raise ValueError("Impossible to cLean up the database.")
