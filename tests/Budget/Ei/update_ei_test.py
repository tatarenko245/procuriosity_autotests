# файл з самим тестом
import copy
import json
import time
import allure
import requests
from deepdiff import DeepDiff
from tests.utils.PayloadModel.Budget.Ei.expenditure_item_payload import EiPreparePayload
from tests.utils.ReleaseModel.Budget.Ei.ei_prepared_release import EiExpectedRelease
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization

from tests.utils.platform_query_library import Requests


@allure.parent_suite('Budget')
@allure.suite('Ei')
@allure.sub_suite('BPE: Update Ei')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/edit#gid=0',
                 name='Google sheets: Update Ei')
class TestUpdateEi:
    @allure.title('Warning - payload of updating Ei contains THE CRUTCH '
                  '(the payload contains tender.classificaion.id and buyer): navigate to expenditure_item_payload.py ->'
                  'def update_ei_full_data_model -> look at comments\n'
                  'Check status code and message from Kafka topic after Ei updating')
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
            And save in variable ei_ocid and ei_token.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_obligatory_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            ei_token = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['X-TOKEN']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: update Ei'):
            """
            Tender platform authorization for update expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            update_ei_access_token = authorization.get_access_token_for_platform_one()
            update_ei_operation_id = authorization.get_x_operation_id(update_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Ei'):
            """
            Send api request on BPE host for expenditure item updating.
            """
            time.sleep(1)
            update_ei_payload = ei_payload_class.update_ei_full_data_model(create_ei_payload=create_ei_payload)

            synchronous_result_of_sending_the_request = Requests().update_ei(
                host_of_request=get_hosts[1],
                access_token=update_ei_access_token,
                x_operation_id=update_ei_operation_id,
                ei_ocid=ei_ocid,
                ei_token=ei_token,
                payload=update_ei_payload,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result: update Ei'):
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
                    assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_ei_feed_point_message = KafkaMessage(update_ei_operation_id).get_message_from_kafka()
                allure.attach(str(update_ei_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_ei_operation_id).update_ei_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_ei_feed_point_message,
                    ei_ocid=ei_ocid,
                    test_mode=True)

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is True:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)

                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(
                            operation_id=update_ei_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

    @allure.title('Warning - payload of updating Ei contains THE CRUTCH '
                  '(the payload contains tender.classificaion.id and buyer): navigate to expenditure_item_payload.py ->'
                  'def update_ei_obligatory_data_model -> look at comments\n'
                  'Check Ei release data after Ei updating with full data model')
    def test_check_ei_release_one(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
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
            And save in variable ei_ocid and ei_token.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_full_data_model(quantity_of_tender_item_object=3)

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            ei_token = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['X-TOKEN']
            actual_ei_release_before_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: Update Ei'):
            """
            Tender platform authorization for update expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            update_ei_access_token = authorization.get_access_token_for_platform_one()
            update_ei_operation_id = authorization.get_x_operation_id(update_ei_access_token)
            step_number += 1

        with allure.step('# 4. Send request to update Ei'):
            """
            Send api request on BPE host for expenditure item updating.
            """
            time.sleep(1)
            update_ei_payload = ei_payload_class.update_ei_obligatory_data_model(create_ei_payload=create_ei_payload)

            synchronous_result_of_sending_the_request = Requests().update_ei(
                host_of_request=get_hosts[1],
                access_token=update_ei_access_token,
                x_operation_id=update_ei_operation_id,
                ei_ocid=ei_ocid,
                ei_token=ei_token,
                payload=update_ei_payload,
                test_mode=True)

            step_number += 1

        with allure.step('# 5. See result: update Ei'):
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
                    assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_ei_feed_point_message = KafkaMessage(update_ei_operation_id).get_message_from_kafka()
                allure.attach(str(update_ei_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_ei_operation_id).update_ei_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_ei_feed_point_message,
                    ei_ocid=ei_ocid,
                    test_mode=True)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check Ei release'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)), "Actual Ei release before updating")

                actual_ei_release_after_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_updating)), "Actual Ei release after updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_updating, actual_ei_release_after_updating))

                dictionary_item_removed_was_cleaned = \
                    str(compare_releases['dictionary_item_removed']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_removed'] = dictionary_item_removed_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_removed': "['releases'][0]['tender']['description'], "
                                               "['releases'][0]['tender']['items'], "
                                               "['releases'][0]['planning']['rationale']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value': f"{ei_ocid}-{actual_ei_release_after_updating['releases'][0]['id'][29:42]}",
                            'old_value': f"{ei_ocid}-{actual_ei_release_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_ei_feed_point_message['data']['operationDate'],
                            'old_value': create_ei_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['title']": {
                            'new_value': update_ei_payload['tender']['title'],
                            'old_value': create_ei_payload['tender']['title']
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
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_ei_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before updating and after updating.")
                    assert compare_releases == expected_result

    @allure.title('Warning - payload of updating Ei contains THE CRUTCH '
                  '(the payload contains tender.classificaion.id and buyer): navigate to expenditure_item_payload.py ->'
                  'def update_ei_full_data_model -> look at comments\n'
                  'Check Ei release after Ei updating on model without optional fields')
    def test_check_ei_release_two(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
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
            And save in variable ei_ocid and ei_token.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_obligatory_data_model()

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            ei_token = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['X-TOKEN']
            actual_ei_release_before_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: Update Ei'):
            """
            Tender platform authorization for update expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            update_ei_access_token = authorization.get_access_token_for_platform_one()
            update_ei_operation_id = authorization.get_x_operation_id(update_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Ei'):
            """
            Send api request on BPE host for expenditure item updating.
            """
            time.sleep(1)
            update_ei_payload = ei_payload_class.update_ei_full_data_model(
                create_ei_payload=create_ei_payload,
                quantity_of_tender_item_object=1)

            synchronous_result_of_sending_the_request = Requests().update_ei(
                host_of_request=get_hosts[1],
                access_token=update_ei_access_token,
                x_operation_id=update_ei_operation_id,
                ei_ocid=ei_ocid,
                ei_token=ei_token,
                payload=update_ei_payload,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result: update Ei'):
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
                    assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_ei_feed_point_message = KafkaMessage(update_ei_operation_id).get_message_from_kafka()
                allure.attach(str(update_ei_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_ei_operation_id).update_ei_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_ei_feed_point_message,
                    ei_ocid=ei_ocid,
                    test_mode=True)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check Ei release'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)), "Actual Ei release before updating")

                actual_ei_release_after_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_updating)), "Actual Ei release after updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_updating, actual_ei_release_after_updating))

                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['tender']['description'], "
                                             "['releases'][0]['tender']['items'], "
                                             "['releases'][0]['planning']['rationale']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value': f"{ei_ocid}-{actual_ei_release_after_updating['releases'][0]['id'][29:42]}",
                            'old_value': f"{ei_ocid}-{actual_ei_release_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_ei_feed_point_message['data']['operationDate'],
                            'old_value': create_ei_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['title']": {
                            'new_value': update_ei_payload['tender']['title'],
                            'old_value': create_ei_payload['tender']['title']
                        }
                    }
                }
                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=parse_environment,
                    language=parse_language,
                    ei_payload=update_ei_payload,
                    ei_feed_point_message=create_ei_feed_point_message,
                    actual_ei_release=actual_ei_release_after_updating))

                expected_items_array_model = expected_release_class.prepare_expected_items_array()

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_ei_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before updating and after updating.")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Ei release[releases][tender][description].'):
                    allure.attach(str(actual_ei_release_after_updating['releases'][0]['tender']['description']),
                                  "Actual result of publication Ei release[releases][tender][description].")
                    allure.attach(str(update_ei_payload['tender']['description']),
                                  "Expected result of publication Ei release[releases][tender][description].")
                    assert actual_ei_release_after_updating['releases'][0]['tender']['description'] == \
                           update_ei_payload['tender']['description']

                with allure.step('Check correctness of publication Ei release[releases][tender][items].'):
                    allure.attach(str(actual_ei_release_after_updating['releases'][0]['tender']['items']),
                                  "Actual result of publication Ei release[releases][tender][items].")
                    allure.attach(str(expected_items_array_model),
                                  "Expected result of publication Ei release[releases][tender][items].")
                    assert actual_ei_release_after_updating['releases'][0]['tender']['items'] == \
                           expected_items_array_model

                with allure.step('Check correctness of publication Ei release[releases][tender][description].'):
                    allure.attach(str(actual_ei_release_after_updating['releases'][0]['planning']['rationale']),
                                  "Actual result of publication Ei release[releases][planning][rationale].")
                    allure.attach(str(update_ei_payload['planning']['rationale']),
                                  "Expected result of publication Ei release[releases][planning][rationale].")
                    assert str(actual_ei_release_after_updating['releases'][0]['planning']['rationale']) == \
                           str(update_ei_payload['planning']['rationale'])

    @allure.title('Warning - payload of updating Ei contains THE CRUTCH '
                  '(the payload contains tender.classificaion.id and buyer): navigate to expenditure_item_payload.py ->'
                  'def update_ei_full_data_model -> look at comments\n'
                  'Check Ei release data after Ei updating based on full data model with 3 items objects')
    def test_check_ei_release_three(self, get_hosts, parse_country, parse_language, parse_pmd, parse_environment,
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
            And save in variable ei_ocid and ei_token.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_full_data_model(quantity_of_tender_item_object=1)

            Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            ei_token = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['X-TOKEN']
            actual_ei_release_before_updating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: Update Ei'):
            """
            Tender platform authorization for update expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            update_ei_access_token = authorization.get_access_token_for_platform_one()
            update_ei_operation_id = authorization.get_x_operation_id(update_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to update Ei'):
            """
            Send api request on BPE host for expenditure item updating.
            """
            time.sleep(1)
            update_ei_payload = ei_payload_class.update_ei_full_data_model(
                create_ei_payload=create_ei_payload,
                quantity_of_tender_item_object=1)

            synchronous_result_of_sending_the_request = Requests().update_ei(
                host_of_request=get_hosts[1],
                access_token=update_ei_access_token,
                x_operation_id=update_ei_operation_id,
                ei_ocid=ei_ocid,
                ei_token=ei_token,
                payload=update_ei_payload,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result: update Ei'):
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
                    assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                update_ei_feed_point_message = KafkaMessage(update_ei_operation_id).get_message_from_kafka()
                allure.attach(str(update_ei_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    update_ei_operation_id).update_ei_message_is_successful(
                    environment=parse_environment,
                    kafka_message=update_ei_feed_point_message,
                    ei_ocid=ei_ocid,
                    test_mode=True)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check Ei release'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_updating)), "Actual Ei release before updating")

                actual_ei_release_after_updating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                allure.attach(str(json.dumps(actual_ei_release_after_updating)), "Actual Ei release after updating")

                compare_releases = dict(DeepDiff(actual_ei_release_before_updating, actual_ei_release_after_updating))

                expected_result = {
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            'new_value': f"{ei_ocid}-{actual_ei_release_after_updating['releases'][0]['id'][29:42]}",
                            'old_value': f"{ei_ocid}-{actual_ei_release_before_updating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': update_ei_feed_point_message['data']['operationDate'],
                            'old_value': create_ei_feed_point_message['data']['operationDate']
                        },
                        "root['releases'][0]['tender']['title']": {
                            'new_value': update_ei_payload['tender']['title'],
                            'old_value': create_ei_payload['tender']['title']
                        },
                        "root['releases'][0]['tender']['description']": {
                            'new_value': update_ei_payload['tender']['description'],
                            'old_value': create_ei_payload['tender']['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['id']": {
                            "new_value": actual_ei_release_after_updating['releases'][0]['tender']['items'][0]['id'],
                            "old_value": actual_ei_release_before_updating['releases'][0]['tender']['items'][0]['id']
                        },
                        "root['releases'][0]['tender']['items'][0]['description']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['description'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['classification']['id']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['classification']['id'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['classification']['id']
                        },
                        "root['releases'][0]['tender']['items'][0]['classification']['description']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['classification']['description'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['classification']['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]['id']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['additionalClassifications'][0]['id'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['additionalClassifications'][0]['id']
                        },
                        "root['releases'][0]['tender']['items'][0]['additionalClassifications'][0]['description']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['additionalClassifications'][0]['description'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['additionalClassifications'][0]['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['quantity']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['quantity'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['quantity']
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['name']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['unit']['name'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['unit']['name']
                        },
                        "root['releases'][0]['tender']['items'][0]['unit']['id']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['unit']['id'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['unit']['id']
                        },
                        "root['releases'][0]['tender']['items'][0]['deliveryAddress']['streetAddress']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['deliveryAddress']['streetAddress'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['deliveryAddress']['streetAddress']
                        },
                        "root['releases'][0]['tender']['items'][0]['deliveryAddress']['postalCode']": {
                            "new_value": actual_ei_release_after_updating[
                                'releases'][0]['tender']['items'][0]['deliveryAddress']['postalCode'],
                            "old_value": actual_ei_release_before_updating[
                                'releases'][0]['tender']['items'][0]['deliveryAddress']['postalCode']
                        },
                        "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                        "'region']['id']": {
                            "new_value": actual_ei_release_after_updating['releases'][0]['tender']['items'][0][
                                'deliveryAddress']['addressDetails']['region']['id'],
                            "old_value": actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                'deliveryAddress']['addressDetails']['region']['id']
                        },
                        "root['releases'][0]['tender']['items'][0]['deliveryAddress']["
                        "'addressDetails']['region']['description']": {
                            "new_value": actual_ei_release_after_updating['releases'][0]['tender']['items'][0][
                                'deliveryAddress']['addressDetails']['region']['description'],
                            "old_value": actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                'deliveryAddress']['addressDetails']['region']['description']
                        },
                        "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                        "'locality']['id']": {
                            "new_value": actual_ei_release_after_updating['releases'][0]['tender']['items'][0][
                                'deliveryAddress']['addressDetails']['locality']['id'],
                            "old_value": actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                'deliveryAddress']['addressDetails']['locality']['id']
                        },
                        "root['releases'][0]['tender']['items'][0]['deliveryAddress']['addressDetails']["
                        "'locality']['description']": {
                            "new_value": actual_ei_release_after_updating['releases'][0]['tender']['items'][0][
                                'deliveryAddress']['addressDetails']['locality']['description'],
                            "old_value": actual_ei_release_before_updating['releases'][0]['tender']['items'][0][
                                'deliveryAddress']['addressDetails']['locality']['description']
                        },
                        "root['releases'][0]['planning']['rationale']": {
                            "new_value": actual_ei_release_after_updating['releases'][0]['planning']['rationale'],
                            "old_value": create_ei_payload['planning']['rationale']
                        }
                    }
                }

                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=parse_environment,
                    language=parse_language,
                    ei_payload=update_ei_payload,
                    ei_feed_point_message=create_ei_feed_point_message,
                    actual_ei_release=actual_ei_release_after_updating))

                expected_items_array_model = expected_release_class.prepare_expected_items_array()

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditure_item(cp_id=ei_ocid)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=create_ei_operation_id)
                        connect_to_database.cleanup_orchestrator_operation_step_by_operationid(operation_id=update_ei_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=update_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before updating and after updating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before updating and after updating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before updating and after updating.")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Ei release[releases][tender][description].'):
                    allure.attach(str(actual_ei_release_after_updating['releases'][0]['tender']['description']),
                                  "Actual result of publication Ei release[releases][tender][description].")
                    allure.attach(str(update_ei_payload['tender']['description']),
                                  "Expected result of publication Ei release[releases][tender][description].")
                    assert actual_ei_release_after_updating['releases'][0]['tender']['description'] == \
                           update_ei_payload['tender']['description']

                with allure.step('Check correctness of publication Ei release[releases][tender][items].'):
                    allure.attach(str(actual_ei_release_after_updating['releases'][0]['tender']['items']),
                                  "Actual result of publication Ei release[releases][tender][items].")
                    allure.attach(str(expected_items_array_model),
                                  "Expected result of publication Ei release[releases][tender][items].")
                    assert actual_ei_release_after_updating['releases'][0]['tender']['items'] == \
                           expected_items_array_model

                with allure.step('Check correctness of publication Ei release[releases][tender][description].'):
                    allure.attach(str(actual_ei_release_after_updating['releases'][0]['planning']['rationale']),
                                  "Actual result of publication Ei release[releases][planning][rationale].")
                    allure.attach(str(update_ei_payload['planning']['rationale']),
                                  "Expected result of publication Ei release[releases][planning][rationale].")
                    assert str(actual_ei_release_after_updating['releases'][0]['planning']['rationale']) == \
                           str(update_ei_payload['planning']['rationale'])
