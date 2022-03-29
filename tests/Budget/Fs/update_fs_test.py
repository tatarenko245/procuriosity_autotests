# файл з самим тестом
import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassMetadata, GlobalClassUpdateFs
from tests.utils.PayloadModel.Budget.Ei.expenditure_item_payload__ import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.deldete_financial_source_payload import FinancialSourcePayload
from tests.utils.ReleaseModel.Budget.Fs.fs_prepared_release import FsExpectedRelease
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment

from tests.utils.functions_collection import compare_actual_result_and_expected_result
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.platform_query_library import Requests


@allure.parent_suite('Budget')
@allure.suite('Fs')
@allure.sub_suite('BPE: Update Fs')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=344712387',
                 name='Google sheets: Update Fs')
class TestUpdateFs:
    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check status code and message from Kafka topic after Fs updating')
    def test_check_result_of_sending_the_request(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                                 connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1
        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
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
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step('# 4. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_full_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step('# 6. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_full_data_model_own_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is True:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload without optional fields treasury money,'
                  'update fs: payload without optional fields treasury money ')
    def test_check_fs_release_one(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                  connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
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
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=create_ei_payload)

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_obligatory_data_model_treasury_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result

    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload full data model treasury money, '
                  'update fs: payload full data model treasury money ')
    def test_check_fs_release_two(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                  connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
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
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_full_data_model_treasury_money()

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_full_data_model_treasury_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['id']": {
                            "new_value": update_fs_payload['planning']['budget']['id'],
                            "old_value": create_fs_payload['planning']['budget']['id']
                        },
                        "root['releases'][0]['planning']['budget']['description']": {
                            "new_value": update_fs_payload['planning']['budget']['description'],
                            "old_value": create_fs_payload['planning']['budget']['description']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['projectIdentifier']": {
                            'new_value':
                                update_fs_payload['planning']['budget']['europeanUnionFunding']['projectIdentifier'],
                            'old_value':
                                create_fs_payload['planning']['budget']['europeanUnionFunding']['projectIdentifier']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['projectName']": {
                            'new_value':
                                update_fs_payload['planning']['budget']['europeanUnionFunding']['projectName'],
                            'old_value':
                                create_fs_payload['planning']['budget']['europeanUnionFunding']['projectName']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['uri']": {
                            'new_value':
                                update_fs_payload['planning']['budget']['europeanUnionFunding']['uri'],
                            'old_value':
                                create_fs_payload['planning']['budget']['europeanUnionFunding']['uri']
                        },
                        "root['releases'][0]['planning']['budget']['project']": {
                            'new_value': update_fs_payload['planning']['budget']['project'],
                            'old_value': create_fs_payload['planning']['budget']['project']
                        },
                        "root['releases'][0]['planning']['budget']['projectID']": {
                            'new_value': update_fs_payload['planning']['budget']['projectID'],
                            'old_value': create_fs_payload['planning']['budget']['projectID']
                        },
                        "root['releases'][0]['planning']['budget']['uri']": {
                            'new_value': update_fs_payload['planning']['budget']['uri'],
                            'old_value': create_fs_payload['planning']['budget']['uri']
                        },
                        "root['releases'][0]['planning']['rationale']": {
                            'new_value': update_fs_payload['planning']['rationale'],
                            'old_value': create_fs_payload['planning']['rationale']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result

    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload without optional fields treasury money, '
                  'update fs: payload full data model treasury money ')
    def test_check_fs_release_three(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                    connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
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
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=create_ei_payload)

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_full_data_model_treasury_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_added": "['releases'][0]['planning']['rationale'], "
                                             "['releases'][0]['planning']['budget']['id'], "
                                             "['releases'][0]['planning']['budget']['description'], "
                                             "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                             "['releases'][0]['planning']['budget']['project'], "
                                             "['releases'][0]['planning']['budget']['projectID'], "
                                             "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': update_fs_payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': create_fs_payload['planning']['budget']['isEuropeanUnionFunded']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Fs release[releases][planning][rationale].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['rationale']),
                                  "Actual result of publication Fs release[releases][planning][rationale].")
                    allure.attach(str(update_fs_payload['planning']['rationale']),
                                  "Expected result of publication Fs release[releases][planning][rationale].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['rationale'] == \
                           update_fs_payload['planning']['rationale']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][id].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['id']),
                                  "Actual result of publication Fs release[releases][planning][budget][id].")
                    allure.attach(str(update_fs_payload['planning']['budget']['id']),
                                  "Expected result of publication Fs release[releases][planning][budget][id].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['id'] == \
                           update_fs_payload['planning']['budget']['id']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget]['
                                 'description].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'description']),
                                  "Actual result of publication Fs release[releases][planning][budget][description].")
                    allure.attach(str(update_fs_payload['planning']['budget']['description']),
                                  "Expected result of publication Fs release[releases][planning][budget][description].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['description'] == \
                           update_fs_payload['planning']['budget']['description']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget]['
                                 'europeanUnionFunding].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'europeanUnionFunding']),
                                  "Actual result of publication Fs release[releases][planning][budget]["
                                  "europeanUnionFunding].")
                    allure.attach(str(update_fs_payload['planning']['budget']['europeanUnionFunding']),
                                  "Expected result of publication Fs release[releases][planning][budget]["
                                  "europeanUnionFunding].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                               'europeanUnionFunding'] == \
                           update_fs_payload['planning']['budget']['europeanUnionFunding']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][''project].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'project']),
                                  "Actual result of publication Fs release[releases][planning][budget][project].")
                    allure.attach(str(update_fs_payload['planning']['budget']['project']),
                                  "Expected result of publication Fs release[releases][planning][budget][project].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['project'] == \
                           update_fs_payload['planning']['budget']['project']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][projectID].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'projectID']),
                                  "Actual result of publication Fs release[releases][planning][budget][projectID].")
                    allure.attach(str(update_fs_payload['planning']['budget']['projectID']),
                                  "Expected result of publication Fs release[releases][planning][budget][projectID].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['projectID'] == \
                           update_fs_payload['planning']['budget']['projectID']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][uri].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['uri']),
                                  "Actual result of publication Fs release[releases][planning][budget][uri].")
                    allure.attach(str(update_fs_payload['planning']['budget']['uri']),
                                  "Expected result of publication Fs release[releases][planning][budget][uri].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['uri'] == \
                           update_fs_payload['planning']['budget']['uri']

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result

    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload full data model treasury money, '
                  'update fs: payload without optional fields treasury money')
    def test_check_fs_release_four(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                   connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_full_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_full_data_model_treasury_money()

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_obligatory_data_model_treasury_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    "dictionary_item_removed": "['releases'][0]['planning']['rationale'], "
                                             "['releases'][0]['planning']['budget']['id'], "
                                             "['releases'][0]['planning']['budget']['description'], "
                                             "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                             "['releases'][0]['planning']['budget']['project'], "
                                             "['releases'][0]['planning']['budget']['projectID'], "
                                             "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': update_fs_payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': create_fs_payload['planning']['budget']['isEuropeanUnionFunded']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result


    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload without optional fields own money,'
                  'update fs: payload without optional fields own money ')
    def test_check_fs_release_five(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                   connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
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
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_own_money()

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_obligatory_data_model_own_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result


    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload full data model own money, '
                  'update fs: payload full data model own money ')
    def test_check_fs_release_six(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                  connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
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
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_full_data_model_own_money()

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_full_data_model_own_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['description']": {
                            "new_value": update_fs_payload['planning']['budget']['description'],
                            "old_value": create_fs_payload['planning']['budget']['description']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['projectIdentifier']": {
                            "new_value":
                                update_fs_payload['planning']['budget']['europeanUnionFunding']['projectIdentifier'],
                            "old_value":
                                create_fs_payload['planning']['budget']['europeanUnionFunding']['projectIdentifier']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['projectName']": {
                            "new_value":
                                update_fs_payload['planning']['budget']['europeanUnionFunding']['projectName'],
                            "old_value":
                                create_fs_payload['planning']['budget']['europeanUnionFunding']['projectName']
                        },
                        "root['releases'][0]['planning']['budget']['europeanUnionFunding']['uri']": {
                            "new_value": update_fs_payload['planning']['budget']['europeanUnionFunding']['uri'],
                            "old_value": create_fs_payload['planning']['budget']['europeanUnionFunding']['uri']
                        },
                        "root['releases'][0]['planning']['budget']['project']": {
                            "new_value": update_fs_payload['planning']['budget']['project'],
                            "old_value": create_fs_payload['planning']['budget']['project']
                        },
                        "root['releases'][0]['planning']['budget']['projectID']": {
                            "new_value": update_fs_payload['planning']['budget']['projectID'],
                            "old_value": create_fs_payload['planning']['budget']['projectID']
                        },
                        "root['releases'][0]['planning']['budget']['uri']": {
                            "new_value": update_fs_payload['planning']['budget']['uri'],
                            "old_value": create_fs_payload['planning']['budget']['uri']
                        },
                        "root['releases'][0]['planning']['rationale']": {
                            "new_value": update_fs_payload['planning']['rationale'],
                            "old_value": create_fs_payload['planning']['rationale']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result


    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload without optional fields own money, '
                  'update fs: payload full data model own money ')
    def test_check_fs_release_seven(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                    connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_full_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_own_money()

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_full_data_model_own_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['planning']['rationale'], "
                                             "['releases'][0]['planning']['budget']['description'], "
                                             "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                             "['releases'][0]['planning']['budget']['project'], "
                                             "['releases'][0]['planning']['budget']['projectID'], "
                                             "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': update_fs_payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': create_fs_payload['planning']['budget']['isEuropeanUnionFunded']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Fs release[releases][planning][rationale].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['rationale']),
                                  "Actual result of publication Fs release[releases][planning][rationale].")
                    allure.attach(str(update_fs_payload['planning']['rationale']),
                                  "Expected result of publication Fs release[releases][planning][rationale].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['rationale'] == \
                           update_fs_payload['planning']['rationale']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget]['
                                 'description].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'description']),
                                  "Actual result of publication Fs release[releases][planning][budget][description].")
                    allure.attach(str(update_fs_payload['planning']['budget']['description']),
                                  "Expected result of publication Fs release[releases][planning][budget][description].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['description'] == \
                           update_fs_payload['planning']['budget']['description']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget]['
                                 'europeanUnionFunding].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'europeanUnionFunding']),
                                  "Actual result of publication Fs release[releases][planning][budget]["
                                  "europeanUnionFunding].")
                    allure.attach(str(update_fs_payload['planning']['budget']['europeanUnionFunding']),
                                  "Expected result of publication Fs release[releases][planning][budget]["
                                  "europeanUnionFunding].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                               'europeanUnionFunding'] == \
                           update_fs_payload['planning']['budget']['europeanUnionFunding']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][''project].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'project']),
                                  "Actual result of publication Fs release[releases][planning][budget][project].")
                    allure.attach(str(update_fs_payload['planning']['budget']['project']),
                                  "Expected result of publication Fs release[releases][planning][budget][project].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['project'] == \
                           update_fs_payload['planning']['budget']['project']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][projectID].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'projectID']),
                                  "Actual result of publication Fs release[releases][planning][budget][projectID].")
                    allure.attach(str(update_fs_payload['planning']['budget']['projectID']),
                                  "Expected result of publication Fs release[releases][planning][budget][projectID].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['projectID'] == \
                           update_fs_payload['planning']['budget']['projectID']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][uri].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['uri']),
                                  "Actual result of publication Fs release[releases][planning][budget][uri].")
                    allure.attach(str(update_fs_payload['planning']['budget']['uri']),
                                  "Expected result of publication Fs release[releases][planning][budget][uri].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['uri'] == \
                           update_fs_payload['planning']['budget']['uri']

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result


    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload full data model own money, '
                  'update fs: payload without optional fields own money')
    def test_check_fs_release_eight(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                    connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_full_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_full_data_model_own_money()

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_obligatory_data_model_own_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_removed': "['releases'][0]['planning']['rationale'], "
                                             "['releases'][0]['planning']['budget']['description'], "
                                             "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                             "['releases'][0]['planning']['budget']['project'], "
                                             "['releases'][0]['planning']['budget']['projectID'], "
                                             "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': update_fs_payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': create_fs_payload['planning']['budget']['isEuropeanUnionFunded']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result


    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload without optional fields treasury money, '
                  'update fs: payload full data model own money ')
    def test_check_fs_release_nine(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                   connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_full_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=create_ei_payload)

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_full_data_model_own_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['planning']['rationale'], "
                                             "['releases'][0]['planning']['budget']['id'], "
                                             "['releases'][0]['planning']['budget']['description'], "
                                             "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                             "['releases'][0]['planning']['budget']['project'], "
                                             "['releases'][0]['planning']['budget']['projectID'], "
                                             "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': update_fs_payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': create_fs_payload['planning']['budget']['isEuropeanUnionFunded']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Fs release[releases][planning][rationale].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['rationale']),
                                  "Actual result of publication Fs release[releases][planning][rationale].")
                    allure.attach(str(update_fs_payload['planning']['rationale']),
                                  "Expected result of publication Fs release[releases][planning][rationale].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['rationale'] == \
                           update_fs_payload['planning']['rationale']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][''id].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['id']),
                                  "Actual result of publication Fs release[releases][planning][budget][id].")
                    allure.attach(str(update_fs_payload['planning']['budget']['id']),
                                  "Expected result of publication Fs release[releases][planning][budget][id].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['id'] == \
                           update_fs_payload['planning']['budget']['id']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget]['
                                 'description].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'description']),
                                  "Actual result of publication Fs release[releases][planning][budget][description].")
                    allure.attach(str(update_fs_payload['planning']['budget']['description']),
                                  "Expected result of publication Fs release[releases][planning][budget][description].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['description'] == \
                           update_fs_payload['planning']['budget']['description']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget]['
                                 'europeanUnionFunding].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'europeanUnionFunding']),
                                  "Actual result of publication Fs release[releases][planning][budget]["
                                  "europeanUnionFunding].")
                    allure.attach(str(update_fs_payload['planning']['budget']['europeanUnionFunding']),
                                  "Expected result of publication Fs release[releases][planning][budget]["
                                  "europeanUnionFunding].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                               'europeanUnionFunding'] == \
                           update_fs_payload['planning']['budget']['europeanUnionFunding']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][''project].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'project']),
                                  "Actual result of publication Fs release[releases][planning][budget][project].")
                    allure.attach(str(update_fs_payload['planning']['budget']['project']),
                                  "Expected result of publication Fs release[releases][planning][budget][project].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['project'] == \
                           update_fs_payload['planning']['budget']['project']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][projectID].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'projectID']),
                                  "Actual result of publication Fs release[releases][planning][budget][projectID].")
                    allure.attach(str(update_fs_payload['planning']['budget']['projectID']),
                                  "Expected result of publication Fs release[releases][planning][budget][projectID].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['projectID'] == \
                           update_fs_payload['planning']['budget']['projectID']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][uri].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['uri']),
                                  "Actual result of publication Fs release[releases][planning][budget][uri].")
                    allure.attach(str(update_fs_payload['planning']['budget']['uri']),
                                  "Expected result of publication Fs release[releases][planning][budget][uri].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['uri'] == \
                           update_fs_payload['planning']['budget']['uri']

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result


    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  'create fs: payload without optional fields own money, '
                  'update fs: payload full data modeltreasury money ')
    def test_check_fs_release_ten(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                  connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_full_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_own_money()

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_full_data_model_treasury_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['planning']['rationale'], "
                                             "['releases'][0]['planning']['budget']['description'], "
                                             "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                             "['releases'][0]['planning']['budget']['project'], "
                                             "['releases'][0]['planning']['budget']['projectID'], "
                                             "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': update_fs_payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': create_fs_payload['planning']['budget']['isEuropeanUnionFunded']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Fs release[releases][planning][rationale].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['rationale']),
                                  "Actual result of publication Fs release[releases][planning][rationale].")
                    allure.attach(str(update_fs_payload['planning']['rationale']),
                                  "Expected result of publication Fs release[releases][planning][rationale].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['rationale'] == \
                           update_fs_payload['planning']['rationale']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget]['
                                 'description].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'description']),
                                  "Actual result of publication Fs release[releases][planning][budget][description].")
                    allure.attach(str(update_fs_payload['planning']['budget']['description']),
                                  "Expected result of publication Fs release[releases][planning][budget][description].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['description'] == \
                           update_fs_payload['planning']['budget']['description']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget]['
                                 'europeanUnionFunding].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'europeanUnionFunding']),
                                  "Actual result of publication Fs release[releases][planning][budget]["
                                  "europeanUnionFunding].")
                    allure.attach(str(update_fs_payload['planning']['budget']['europeanUnionFunding']),
                                  "Expected result of publication Fs release[releases][planning][budget]["
                                  "europeanUnionFunding].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                               'europeanUnionFunding'] == \
                           update_fs_payload['planning']['budget']['europeanUnionFunding']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][''project].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'project']),
                                  "Actual result of publication Fs release[releases][planning][budget][project].")
                    allure.attach(str(update_fs_payload['planning']['budget']['project']),
                                  "Expected result of publication Fs release[releases][planning][budget][project].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['project'] == \
                           update_fs_payload['planning']['budget']['project']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][projectID].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget'][
                                          'projectID']),
                                  "Actual result of publication Fs release[releases][planning][budget][projectID].")
                    allure.attach(str(update_fs_payload['planning']['budget']['projectID']),
                                  "Expected result of publication Fs release[releases][planning][budget][projectID].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['projectID'] == \
                           update_fs_payload['planning']['budget']['projectID']

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][uri].'):
                    allure.attach(str(actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['uri']),
                                  "Actual result of publication Fs release[releases][planning][budget][uri].")
                    allure.attach(str(update_fs_payload['planning']['budget']['uri']),
                                  "Expected result of publication Fs release[releases][planning][budget][uri].")
                    assert actual_fs_release_after_fs_updating['releases'][0]['planning']['budget']['uri'] == \
                           update_fs_payload['planning']['budget']['uri']

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result


    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs updating:'
                  ' create fs: payload full data model treasury money, '
                  'update fs: payload without optional fields own money')
    def test_check_fs_release_eleven(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
                                     connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_full_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id and fs_token.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FinancialSourcePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_full_data_model_treasury_money()

            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload)

            create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
            fs_token = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['X-TOKEN']
            actual_ei_release_before_fs_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            actual_fs_release_before_fs_updating = requests.get(
                url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Fs'):
            """
            Tender platform authorization for update financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            update_fs_access_token = authorization.get_access_token_for_platform_one()
            update_fs_operation_id = authorization.get_x_operation_id(update_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Fs'):
            """
            Send api request on BPE host for financial source updating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            update_fs_payload = fs_payload_class.update_fs_obligatory_data_model_own_money(
                create_fs_payload=create_fs_payload)

            synchronous_result_of_sending_the_request = Requests().update_fs(
                host_of_request=get_hosts[1],
                access_token=update_fs_access_token,
                x_operation_id=update_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=update_fs_payload,
                fs_id=fs_id,
                fs_token=fs_token,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step('Compare actual status code of sending the request and '
                             'expected status code of sending request.'):
                allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                              "Actual status code of sending the request.")
                allure.attach(str(202), "Expected status code of sending request.")
                assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_fs_feed_point_message = KafkaMessage(update_fs_operation_id).get_message_from_kafka()
                allure.attach(str(update_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_fs_operation_id).update_fs_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_fs_feed_point_message,
                    ei_ocid=ei_ocid,
                    fs_id=fs_id)

                try:
                    """
                        If asynchronous_result_of_sending_the_request was False, then return process steps by
                        operation-id.
                        """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.4. Check Fs release.'):
                """
                Compare actual financial source release after updating with financial source release before updating.
                """
                allure.attach(str(json.dumps(actual_fs_release_before_fs_updating)),
                              "Actual Fs release before updating")

                actual_fs_release_after_fs_updating = requests.get(
                    url=f"{update_fs_feed_point_message['data']['url']}").json()
                allure.attach(str(json.dumps(actual_fs_release_after_fs_updating)), "Actual Fs release after updating")

                compare_releases = dict(DeepDiff(actual_fs_release_before_fs_updating,
                                                 actual_fs_release_after_fs_updating))

                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_removed': "['releases'][0]['planning']['rationale'], "
                                               "['releases'][0]['planning']['budget']['id'], "
                                               "['releases'][0]['planning']['budget']['description'], "
                                               "['releases'][0]['planning']['budget']['europeanUnionFunding'], "
                                               "['releases'][0]['planning']['budget']['project'], "
                                               "['releases'][0]['planning']['budget']['projectID'], "
                                               "['releases'][0]['planning']['budget']['uri']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value':
                                f"{fs_id}-{actual_fs_release_after_fs_updating['releases'][0]['id'][46:59]}",
                            'old_value':
                                f"{fs_id}-{actual_fs_release_before_fs_updating['releases'][0]['id'][46:59]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_fs_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['startDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['startDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['startDate']
                        },
                        "root['releases'][0]['planning']['budget']['period']['endDate']": {
                            'new_value': update_fs_payload['planning']['budget']['period']['endDate'],
                            'old_value': create_fs_payload['planning']['budget']['period']['endDate']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': create_fs_payload['planning']['budget']['amount']['amount']
                        },
                        "root['releases'][0]['planning']['budget']['isEuropeanUnionFunded']": {
                            'new_value': update_fs_payload['planning']['budget']['isEuropeanUnionFunded'],
                            'old_value': create_fs_payload['planning']['budget']['isEuropeanUnionFunded']
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
                                operation_id=update_fs_feed_point_message)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release before updating and after updating.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.5. Check Ei release.'):
                """
                Compare expenditure item release before fs updating and 
                expenditure item release after fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_updating)),
                              "Actual Ei release before Fs updating")

                actual_ei_release_after_fs_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_fs_updating)),
                              "Actual Ei release after Fs updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_fs_updating,
                                                 actual_ei_release_after_fs_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_updating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_fs_feed_point_message['data']['operationDate'],
                            'old_value': actual_ei_release_before_fs_updating['releases'][0]['date']
                        },
                        "root['releases'][0]['planning']['budget']['amount']['amount']": {
                            'new_value': update_fs_payload['planning']['budget']['amount']['amount'],
                            'old_value': actual_ei_release_before_fs_updating[
                                'releases'][0]['planning']['budget']['amount']['amount']
                        }
                    }
                }

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_fs_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs updating and '
                                 'after Fs updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release before Fs updating and after Fs updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs updating and after Fs updating.")
                    assert compare_releases == expected_result