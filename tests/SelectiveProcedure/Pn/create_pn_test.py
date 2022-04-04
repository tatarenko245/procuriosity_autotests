import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.PayloadModels.Budget.Ei.expenditure_item_payload__ import EiPreparePayload
from tests.utils.PayloadModels.Budget.Fs.deldete_financial_source_payload import FinancialSourcePayload
from tests.utils.PayloadModels.SelectiveProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.ReleaseModels.SelectiveProcedure.Pn.pn_prepared_release import PnExpectedRelease
from tests.utils.functions_collection import check_uuid_version

from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestCreatePn:
    @allure.title("Check Pn and MS releases data after Pn creating without optional fields \n"
                  "------------------------------------------------\n"
                  "create Ei: obligatory data model without items array;\n"
                  "create Fs: obligatory data model, treasury money;\n"
                  "create Pn: obligatory data model, without lots and items;\n")
    def test_check_pn_ms_releases_one(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                      connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        metadata_tender_url = None
        try:
            if parse_environment == "dev":
                metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
            elif parse_environment == "sandbox":
                metadata_tender_url = "http://public.eprocurement.systems/tenders"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            ei_access_token = authorization.get_access_token_for_platform_one()
            ei_operation_id = authorization.get_x_operation_id(ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_obligatory_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=ei_access_token,
                x_operation_id=ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

            ei_feed_point_message = KafkaMessage(ei_operation_id).get_message_from_kafka()
            ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            actual_ei_release_before_fs_creation = requests.get(
                url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            fs_access_token = authorization.get_access_token_for_platform_one()
            fs_operation_id = authorization.get_x_operation_id(fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=create_ei_payload)

            Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=fs_access_token,
                x_operation_id=fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
                test_mode=True)

            fs_feed_point_message = KafkaMessage(fs_operation_id).get_message_from_kafka()
            fs_id = fs_feed_point_message['data']['outcomes']['fs'][0]['id']
            actual_fs_release_before_pn_creation = requests.get(
                url=f"{fs_feed_point_message['data']['url']}/{fs_id}").json()
            actual_ei_release_after_fs_creation = requests.get(
                url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Pn'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            pn_access_token = authorization.get_access_token_for_platform_one()
            pn_operation_id = authorization.get_x_operation_id(pn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Pn'):
            """
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            And save in variable pn_ocid, pn_id.
            """
            time.sleep(1)
            pn_payload_class = copy.deepcopy(PnPreparePayload(
                fs_payload=create_fs_payload,
                fs_feed_point_message=fs_feed_point_message))
            create_pn_payload = \
                pn_payload_class.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            synchronous_result_of_sending_the_request = Requests().createPn(
                host_of_request=get_hosts[1],
                access_token=pn_access_token,
                x_operation_id=pn_operation_id,
                country=parse_country,
                language=parse_language,
                pmd=parse_pmd,
                payload=create_pn_payload,
                test_mode=True)

            pn_feed_point_message = KafkaMessage(pn_operation_id).get_message_from_kafka()
            pn_ocid = pn_feed_point_message['data']['ocid']
            pn_id = pn_feed_point_message['data']['outcomes']['pn'][0]['id']
            actual_pn_release = requests.get(url=f"{pn_feed_point_message['data']['url']}/{pn_id}").json()
            actual_ms_release = requests.get(url=f"{pn_feed_point_message['data']['url']}/{pn_ocid}").json()
            actual_fs_release_after_pn_creation = requests.get(
                url=f"{fs_feed_point_message['data']['url']}/{fs_id}").json()
            actual_ei_release_after_pn_creation = requests.get(
                url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()
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
                allure.attach(str(pn_feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    pn_operation_id).create_pn_message_is_successful(
                    environment=parse_environment,
                    kafka_message=pn_feed_point_message,
                    test_mode=True)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=pn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual asynchronous result of sending the request and '
                                 'expected asynchronous result of sending request.'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)

            with allure.step(f'# {step_number}.3. Check Pn release'):
                """
                Compare actual planning notice release with expected planning notice release model.
                """
                allure.attach(str(json.dumps(actual_pn_release)), "Actual Pn release")

                expected_release_class = copy.deepcopy(PnExpectedRelease(
                    environment=parse_environment,
                    language=parse_language,
                    pn_feed_point_message=pn_feed_point_message,
                    pn_payload=create_pn_payload,
                    pmd=parse_pmd))

                expected_pn_release_model = \
                    expected_release_class.pn_release_obligatory_data_model_without_lots_and_items_based_on_one_fs(
                        actual_pn_release=actual_pn_release
                    )
                allure.attach(str(json.dumps(expected_pn_release_model)), "Expected Pn release")

                compare_releases = dict(DeepDiff(actual_pn_release, expected_pn_release_model))
                expected_result = {}

                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=pn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Pn release and expected Pn release and '
                                 'expected result of comparing Pn release and expected Pn release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Pn release and expected Pn release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Pn release and expected Pn release.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare multistage release with expected multistage release model.
                """
                allure.attach(str(json.dumps(actual_ms_release)), "Actual Ms release")

                expected_ms_release_model = \
                    expected_release_class.ms_release_obligatory_data_model_without_lots_and_items_based_on_one_fs(
                        actual_ms_release=actual_ms_release,
                        actual_fs_release=actual_fs_release_before_pn_creation,
                        actual_ei_release=actual_ei_release_before_fs_creation,
                        ei_ocid=ei_ocid,
                        fs_id=fs_id)
                allure.attach(str(json.dumps(expected_ms_release_model)), "Expected Ms release")

                compare_releases = dict(DeepDiff(actual_ms_release, expected_ms_release_model))
                expected_result = {}

                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=pn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ms release and expected Pn release and '
                                 'expected result of comparing Ms release and expected Pn release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ms release and expected Pn release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms release and expected Pn release.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step(f'# {step_number}.5. Check Ei release'):
                """
                Compare expenditure item release before pn creating and expenditure item after pn creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_fs_creation)),
                              "Actual Ei release before pn creating")

                allure.attach(str(json.dumps(actual_ei_release_after_pn_creation)),
                              "Actual Ei release after pn creating")

                compare_releases = dict(
                    DeepDiff(actual_ei_release_after_fs_creation, actual_ei_release_after_pn_creation))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{ei_ocid}-"
                                f"{actual_ei_release_after_pn_creation['releases'][0]['id'][29:42]}",
                            'old_value':
                                f"{ei_ocid}-"
                                f"{actual_ei_release_after_fs_creation['releases'][0]['id'][29:42]}",
                        },
                        "root['releases'][0]['date']": {
                            'new_value': pn_feed_point_message['data']['operationDate'],
                            'old_value': fs_feed_point_message['data']['operationDate']
                        }
                    },
                    'iterable_item_added': {
                        "root['releases'][0]['relatedProcesses'][1]": {
                            'id': actual_ei_release_after_pn_creation['releases'][0]['relatedProcesses'][1]['id'],
                            'relationship': ['x_execution'],
                            'scheme': 'ocid',
                            'identifier': pn_ocid,
                            'uri': f"{metadata_tender_url}/{pn_ocid}/{pn_ocid}"
                        }
                    }
                }

                try:
                    check_uuid_version(
                        uuid_to_test=actual_ei_release_after_pn_creation['releases'][0][
                            'relatedProcesses'][1]['id'],
                        version=4
                    )
                except ValueError:
                    raise ValueError(
                        "Check your ['releases'][0]['relatedProcesses'][1]['id'] in Ei release: "
                        "id must be uuid version 4")

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=pn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare result of comparing expenditure item release before pn creating and '
                                 'expenditure item after pn creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release and expected Ei release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release and expected Ei release.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step(f'# {step_number}.6. Check Fs release'):
                """
                Compare financial source before pn creating release and financial source after pn creating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_pn_creation)),
                              "Actual Fs release before pn creating")

                allure.attach(str(json.dumps(actual_fs_release_after_pn_creation)),
                              "Actual Fs release after pn creating")

                compare_releases = dict(
                    DeepDiff(actual_fs_release_before_pn_creation, actual_fs_release_after_pn_creation))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value":
                                f"{fs_id}-"
                                f"{actual_fs_release_after_pn_creation['releases'][0]['id'][46:59]}",
                            "old_value":
                                f"{fs_id}-"
                                f"{actual_fs_release_before_pn_creation['releases'][0]['id'][46:59]}",
                        },
                        "root['releases'][0]['date']": {
                            "new_value": pn_feed_point_message['data']['operationDate'],
                            "old_value": fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tag'][0]": {
                            "new_value": "planningUpdate",
                            "old_value": "planning"
                        }
                    },
                    "iterable_item_added": {
                        "root['releases'][0]['relatedProcesses'][1]": {
                            "id": actual_fs_release_after_pn_creation['releases'][0]['relatedProcesses'][1]['id'],
                            "relationship": ["x_execution"],
                            "scheme": "ocid",
                            "identifier": pn_ocid,
                            "uri": f"{metadata_tender_url}/{pn_ocid}/{pn_ocid}"
                        }
                    }
                }

                try:
                    check_uuid_version(
                        uuid_to_test=actual_fs_release_after_pn_creation['releases'][0][
                            'relatedProcesses'][1]['id'],
                        version=4
                    )
                except ValueError:
                    raise ValueError(
                        "Check your ['releases'][0]['relatedProcesses'][1]['id'] in Fs release: "
                        "id must be uuid version 4")

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=pn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditureItem(cp_id=ei_ocid)

                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)

                        connect_to_database.pn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=ei_operation_id)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=fs_operation_id)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=pn_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=pn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare result of comparing financial source release before pn creating and '
                                 'financial source after pn creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release and expected Fs release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release and expected Fs release.")
                    assert str(compare_releases) == str(expected_result)
