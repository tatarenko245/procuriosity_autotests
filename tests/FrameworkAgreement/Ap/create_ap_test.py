import copy
import json
import allure
import requests

from tests.utils.MessageModels.AP.aggregated_plan_message import AggregatedPlanMessage
from tests.utils.PayloadModels.FrameworkAgreement.Ap.aggregated_plan_payload import AggregatedPayload
from tests.utils.ReleaseModels.FrameworkAgreement.Ap.aggregated_plan_release import AggregatedPlanRelease
from tests.utils.cassandra_session import CassandraSession
from tests.utils.functions_collection.get_message_for_platform import get_message_for_platform
from tests.utils.platform_query_library import PlatformQueryRequest
from tests.utils.platform_authorization import PlatformAuthorization


@allure.parent_suite('Framework Agreement')
@allure.suite('Ap')
@allure.sub_suite('BPE: Create Ap')
@allure.severity('Critical')
@allure.testcase(url=None,
                 name=None)
class TestCreatePn:
    @allure.title("Check Ap and MS releases after CreateAp process, without optional fields. \n"
                  "------------------------------------------------\n"
                  "СreateAp process: required data mode.\n")
    def test_case_1(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment, connect_to_ocds,
                    connect_to_access):

        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: CreateAp process.'):
            """
            Tender platform authorization for CreateAp process.
            As result get Tender platform's access token and process operation-id.
            """
            platform_one = PlatformAuthorization(get_hosts[1])
            access_token = platform_one.get_access_token_for_platform_one()
            operation_id = platform_one.get_x_operation_id(access_token)

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
                    maxDurationOfFA=maxDurationOfFA)
                )

                ap_payload.delete_optional_fields(
                    "tender.procurementMethodRationale",
                    "tender.procuringEntity.additionalIdentifiers",
                    "tender.procuringEntity.address.postalCode",
                    "tender.procuringEntity.contactPoint.faxNumber",
                    "tender.procuringEntity.contactPoint.url"
                )

                ap_payload = ap_payload.build_aggregated_plan_payload()
            except ValueError:
                raise ValueError("Impossible to build payload for CreateAp process.")

            synchronous_result = PlatformQueryRequest().create_ap_proces(
                host_to_bpe=get_hosts[1],
                access_token=access_token,
                x_operation_id=operation_id,
                payload=ap_payload,
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

            with allure.step(f'# {step_number}.2. Check the ap_message for platform.'):
                """
                Check the fs_message for platform.
                """
                actual_message = get_message_for_platform(operation_id)

                try:
                    """
                    Build expected ap_message for CreatePn process.
                    """
                    expected_message = copy.deepcopy(AggregatedPlanMessage(
                        environment=parse_environment,
                        actual_message=actual_message,
                        expected_quantity_of_outcomes_ap=1,
                        test_mode=True)
                    )

                    expected_message = expected_message.build_expected_message_for_pn_process()
                except ValueError:
                    raise ValueError("Impossible to build expected fs_message for CreatePn process.")

                with allure.step('Compare actual and expected fs_message for platform.'):
                    allure.attach(json.dumps(actual_message), "Actual ap_message.")
                    allure.attach(json.dumps(expected_message), "Expected ap_message.")

                    process_id = database.get_processId_by_operationId(connect_to_ocds, operation_id)

                    assert actual_message == expected_message, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{process_id}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.3. Check AP release.'):
                """
                Compare actual AP release and expected AP release.
                """
                ap_url = f"{actual_message['data']['url']}/{actual_message['data']['outcomes']['ap'][0]['id']}"
                actual_ap_release = requests.get(url=ap_url).json()

                ms_url = f"{actual_message['data']['url']}/{actual_message['data']['ocid']}"
                actual_ms_release = requests.get(url=ms_url).json()

                allure.attach(str(json.dumps(actual_ap_release)), "Actual AP release.")

                try:
                    """
                    Build expected AP release.
                    """
                    expected_release = copy.deepcopy(AggregatedPlanRelease(
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
                    raise ValueError("Impossible to build expected AP release.")

                with allure.step('Compare actual and expected AP release.'):
                    allure.attach(json.dumps(actual_ap_release), "Actual AP release.")
                    allure.attach(json.dumps(expected_ap_release), "Expected AP release.")

                    assert actual_ap_release == expected_ap_release, \
                        allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                      f"process_id = '{process_id}' ALLOW FILTERING;",
                                      "Cassandra DataBase: steps of process.")

            with allure.step(f'# {step_number}.4. Check MS release.'):
                """
                Compare actual MS release and expected MS release.
                """

                allure.attach(str(json.dumps(actual_ms_release)), "Actual MS release.")

                try:
                    """
                    Build expected MS release.
                    """
                    expected_ms_release = expected_release.build_expected_ms_release()

                except ValueError:
                    raise ValueError("Impossible to build expected MS release.")
            print("actual_ms_release")
            print(json.dumps(actual_ms_release))
            print("expected_ms_release")
            print(json.dumps(expected_ms_release))
            with allure.step('Compare actual and expected MS release.'):
                allure.attach(json.dumps(actual_ms_release), "Actual MS release.")
                allure.attach(json.dumps(expected_ms_release), "Expected MS release.")

                assert actual_ms_release == expected_ms_release, \
                    allure.attach(f"SELECT * FROM ocds.orchestrator_operation_step WHERE "
                                  f"process_id = '{process_id}' ALLOW FILTERING;",
                                  "Cassandra DataBase: steps of process.")

                try:
                    """
                    CLean up the database.
                    """

                    database.cleanup_table_of_services_for_aggregatedPlan(
                        connect_to_ocds,
                        connect_to_access,
                        ap_ocid=actual_message['data']['ocid']
                    )

                    database.cleanup_ocds_orchestratorOperationStep_by_operationId(
                        connect_to_ocds,
                        operation_id
                    )
                except ValueError:
                    raise ValueError("Impposible to cLean up the database.")
