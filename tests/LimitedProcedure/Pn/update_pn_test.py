import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.utils.PayloadModel.Budget.Ei.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.LimitedProcedure.Pn.pn_prepared_payload import PnPreparePayload

from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_query_library import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestUpdatePn:
    @allure.title("Check Pn and MS releases data after Pn updating without optional fields. \n"
                  "------------------------------------------------\n"
                  "create Ei: obligatory data model without items array;\n"
                  "create Fs: obligatory data model, treasury money;\n"
                  "create Pn: obligatory data model, without lots and items;\n"
                  "update Pn: obligatory data model, without lots and items;\n")
    def test_check_pn_ms_releases_one(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                      connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
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
            fs_payload_class = copy.deepcopy(FsPreparePayload(ei_payload=create_ei_payload))
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
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Pn'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            pn_access_token = authorization.get_access_token_for_platform_one()
            create_pn_operation_id = authorization.get_x_operation_id(pn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Pn'):
            """
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            And save in variable pn_ocid, pn_id, pn_token.
            """
            time.sleep(1)
            pn_payload_class = copy.deepcopy(PnPreparePayload(
                fs_payload=create_fs_payload,
                fs_feed_point_message=fs_feed_point_message))
            create_pn_payload = \
                pn_payload_class.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            Requests().createPn(
                host_of_request=get_hosts[1],
                access_token=pn_access_token,
                x_operation_id=create_pn_operation_id,
                country=parse_country,
                language=parse_language,
                pmd=parse_pmd,
                payload=create_pn_payload,
                test_mode=True)

            create_pn_feed_point_message = KafkaMessage(create_pn_operation_id).get_message_from_kafka()
            pn_ocid = create_pn_feed_point_message['data']['ocid']
            pn_url = create_pn_feed_point_message['data']['url']
            pn_id = create_pn_feed_point_message['data']['outcomes']['pn'][0]['id']
            pn_token = create_pn_feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
            actual_pn_release_before_pn_updating = requests.get(
                url=f"{create_pn_feed_point_message['data']['url']}/{pn_id}").json()
            actual_ms_release_before_pn_updating = requests.get(
                url=f"{create_pn_feed_point_message['data']['url']}/{pn_ocid}").json()
            actual_fs_release_after_pn_creation = requests.get(
                url=f"{fs_feed_point_message['data']['url']}/{fs_id}").json()
            actual_ei_release_after_pn_creation = requests.get(
                url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Pn'):
            """
            Tender platform authorization for update planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            pn_access_token = authorization.get_access_token_for_platform_one()
            update_pn_operation_id = authorization.get_x_operation_id(pn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Pn'):
            """
            Send api request on BPE host for planning notice updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            pn_payload_class = copy.deepcopy(PnPreparePayload(
                fs_payload=create_fs_payload,
                fs_feed_point_message=fs_feed_point_message))
            update_pn_payload = \
                pn_payload_class.update_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            synchronous_result_of_sending_the_request = Requests().update_pn(
                host_of_request=get_hosts[1],
                access_token=pn_access_token,
                pn_ocid=pn_ocid,
                pn_id=pn_id,
                pn_token=pn_token,
                x_operation_id=update_pn_operation_id,
                payload=update_pn_payload,
                test_mode=True)

            update_pn_feed_point_message = KafkaMessage(update_pn_operation_id).get_message_from_kafka()
            actual_pn_release_after_pn_updating = requests.get(url=f"{pn_url}/{pn_id}").json()
            actual_ms_release_after_pn_updating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
            actual_fs_release_after_pn_updatting = requests.get(
                url=f"{fs_feed_point_message['data']['url']}/{fs_id}").json()
            actual_ei_release_after_pn_updateing = requests.get(
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
                allure.attach(str(update_pn_feed_point_message), 'Message in feed point')
                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_pn_operation_id).update_pn_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_pn_feed_point_message,
                    pn_ocid=pn_ocid,
                    pn_id=pn_id)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_pn_operation_id)
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
                Compare actual planning notice release before updating and actual planning release after updating.
                """
                allure.attach(str(json.dumps(actual_pn_release_before_pn_updating)),
                              "Actual Pn release before updating")

                allure.attach(str(json.dumps(actual_pn_release_after_pn_updating)), "Actual Pn release after updating")

                compare_releases = dict(DeepDiff(actual_pn_release_before_pn_updating,
                                                 actual_pn_release_after_pn_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{pn_id}-{actual_pn_release_after_pn_updating['releases'][0]['id'][46:59]}",
                            "old_value": f"{pn_id}-{actual_pn_release_before_pn_updating['releases'][0]['id'][46:59]}",
                        },
                        "root['releases'][0]['date']": {
                            "new_value": update_pn_feed_point_message['data']['operationDate'],
                            "old_value": actual_pn_release_before_pn_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['tag'][0]": {
                            'new_value': 'planningUpdate',
                            'old_value': 'planning'
                        },
                        "root['releases'][0]['tender']['tenderPeriod']['startDate']": {
                            "new_value": update_pn_payload['tender']['tenderPeriod']['startDate'],
                            "old_value": create_pn_payload['tender']['tenderPeriod']['startDate']
                        }
                    }
                }

                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_pn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Pn release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Pn release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Pn release before updating and after updating.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare actual multistage release before updating and actual multistage release after updating.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_pn_updating)),
                              "Actual Ms release before updating")

                allure.attach(str(json.dumps(actual_ms_release_after_pn_updating)),
                              "Actual Ms release after updating")

                compare_releases = dict(DeepDiff(actual_ms_release_before_pn_updating,
                                                 actual_ms_release_after_pn_updating))

                expected_result = {
                    "values_changed": {
                        "root['releases'][0]['id']": {
                            "new_value": f"{pn_ocid}-{actual_ms_release_after_pn_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{pn_ocid}-{actual_ms_release_before_pn_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            "new_value": update_pn_feed_point_message['data']['operationDate'],
                            "old_value": actual_ms_release_before_pn_updating['releases'][0]['date']
                        }
                    }
                }

                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_pn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing MS release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ms release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms release before updating and after updating.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step(f'# {step_number}.5. Check Ei release'):
                """
                Compare expenditure item release before pn updating and expenditure item after pn updating.
                """
                allure.attach(str(json.dumps(actual_ei_release_after_pn_creation)),
                              "Actual Ei release before pn updating")

                allure.attach(str(json.dumps(actual_ei_release_after_pn_updateing)),
                              "Actual Ei release after pn updating")

                compare_releases = dict(
                    DeepDiff(actual_ei_release_after_pn_creation,
                             actual_ei_release_after_pn_updateing))

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
                                operation_id=update_pn_operation_id)
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
                Compare financial source release before pn updating and financial source after pn updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_after_pn_creation)),
                              "Actual Fs release before pn updating")

                allure.attach(str(json.dumps(actual_fs_release_after_pn_updatting)),
                              "Actual Fs release after pn updating")

                compare_releases = dict(
                    DeepDiff(actual_fs_release_after_pn_creation,
                             actual_fs_release_after_pn_updatting))

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
                                operation_id=update_pn_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)

                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)

                        connect_to_database.pn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=ei_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=fs_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_pn_operation_id)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_pn_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_pn_operation_id)
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
