""" Test of Create Aggregated Plan process for Framework Agreement procedure. """
import copy
import json
import allure
import requests

from tests.utils.MessageModels.FrameworkAgreement.aggregatedPlan_message import AggregatedPlanMessage
from tests.utils.PayloadModels.FrameworkAgreement.AggregatedPlan.aggregatedPlan_payload import AggregatedPlan
from tests.utils.ReleaseModels.FrameworkAgreement.AP_release.createAggregatedPlan_process import \
    CreateAggregatedPlanRelease
from tests.utils.cassandra_session import CassandraSession
from tests.utils.functions_collection.get_message_for_platform import get_message_for_platform
from tests.utils.platform_query_library import PlatformQueryRequest
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Framework Agreement')
@allure.suite('AP_release')
@allure.sub_suite('BPE: Create AP_release')
@allure.severity('Critical')
@allure.testcase(url=None)
class TestCreatePn:
    @allure.title("\nCheck AP_release and MS releases after CreateAp process, without optional fields. \n"
                  "\n===================================================================================\n"
                  "\nСreateAp process: required data mode.\n"
                  "\n===================================================================================\n")
    def test_case_1(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment, connect_to_ocds,
                    connect_to_access):

        step_number = 1
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

                ap_payload = copy.deepcopy(AggregatedPlan(
                    centralPurchasingBody_id=55,
                    host_to_service=get_hosts[2],
                    maxDurationOfFA=maxDurationOfFA)
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

            synchronous_result = PlatformQueryRequest().create_ap_process(
                host_to_bpe=get_hosts[1],
                access_token=accessToken,
                x_operation_id=ap_operationId,
                payload=ap_payload,
                testMode=True,
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
                    allure.attach(str(synchronous_result.status_code), "Actual status code.")
                    allure.attach(str(202), "Expected status code.")
                    assert synchronous_result.status_code == 202

            with allure.step(f'# {step_number}.2. Check the message of AP_release for platform.'):
                """
                Check the message for platform.
                """
                actual_message = get_message_for_platform(ap_operationId)

                try:
                    """
                    Build expected message of AP_release process.
                    """
                    expected_message = copy.deepcopy(AggregatedPlanMessage(
                        environment=parse_environment,
                        actual_message=actual_message,
                        testMode=True)
                    )

                    expected_message = expected_message.build_expected_message_for_pn_process()
                except ValueError:
                    raise ValueError("Impossible to build expected message of AP_release process.")

                with allure.step('Compare actual and expected message for platform.'):
                    allure.attach(json.dumps(actual_message), "Actual message.")
                    allure.attach(json.dumps(expected_message), "Expected message.")

                    processId = database.get_processId_by_operationId(connect_to_ocds, ap_operationId)

                    assert actual_message == expected_message, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{processId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.3. Check AP_release release.'):
                """
                Compare actual AP_release release and expected AP_release release.
                """
                ap_url = f"{actual_message['data']['url']}/{actual_message['data']['outcomes']['ap'][0]['id']}"
                actual_ap_release = requests.get(url=ap_url).json()

                ms_url = f"{actual_message['data']['url']}/{actual_message['data']['ocid']}"
                actual_ms_release = requests.get(url=ms_url).json()

                try:
                    """
                    Build expected AP_release release.
                    """
                    expected_release = copy.deepcopy(CreateAggregatedPlanRelease(
                        environment=parse_environment,
                        host_to_service=get_hosts[2],
                        language=parse_language,
                        pmd=parse_pmd,
                        ap_payload=ap_payload,
                        ap_message=actual_message,
                        actual_ap_release=actual_ap_release,
                        actual_ms_release=actual_ms_release
                    ))

                    expected_ap_release = expected_release.build_expected_ap_release()
                except ValueError:
                    raise ValueError("Impossible to build expected AP_release release.")

                with allure.step('Compare actual and expected AP_release release.'):
                    allure.attach(json.dumps(actual_ap_release), "Actual AP_release release.")
                    allure.attach(json.dumps(expected_ap_release), "Expected AP_release release.")

                    assert actual_ap_release == expected_ap_release, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{processId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.4. Check MS release.'):
                """
                Compare actual MS release and expected MS release.
                """
                try:
                    """
                    Build expected MS release.
                    """
                    expected_ms_release = expected_release.build_expected_ms_release()

                except ValueError:
                    raise ValueError("Impossible to build expected MS release.")

                with allure.step('Compare actual and expected MS release.'):
                    allure.attach(json.dumps(actual_ms_release), "Actual MS release.")
                    allure.attach(json.dumps(expected_ms_release), "Expected MS release.")

                    assert actual_ms_release == expected_ms_release, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{processId}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

                try:
                    """
                    CLean up the database.
                    """
                    # Clean after aggregatedPlan process:
                    database.cleanup_ocds_orchestratorOperationStep_by_operationId(
                        connect_to_ocds,
                        ap_operationId
                    )

                    database.cleanup_table_of_services_for_aggregatedPlan(
                        connect_to_ocds,
                        connect_to_access,
                        ap_cpid=actual_message['data']['ocid']
                    )
                except ValueError:
                    raise ValueError("Impossible to cLean up the database.")
