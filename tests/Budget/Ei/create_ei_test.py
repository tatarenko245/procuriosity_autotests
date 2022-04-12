# файл з самим тестом
import copy
import json
import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassCreateEi, GlobalClassMetadata
from tests.utils.PayloadModels.Budget.ExpenditureItem.expenditure_item_payload__ import EiPreparePayload
from tests.utils.ReleaseModels.Budget.ExpenditureItem.ei_prepared_release import EiExpectedRelease
from tests.utils.message_for_platform import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization

from tests.utils.platform_query_library import Requests


@allure.parent_suite('PN_release')
@allure.suite('ExpenditureItem')
@allure.sub_suite('BPE: Create ExpenditureItem')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/edit#gid=0',
                 name='Google sheets: Create ExpenditureItem')
class TestCreateEi:
    @allure.title('Check status code and message from Kafka topic after ExpenditureItem creation')
    def test_check_result_of_sending_the_request(self, get_hosts, parse_country, parse_language, parse_environment,
                                                 connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create ExpenditureItem'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create ExpenditureItem'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid and ei_token.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_full_data_model()

            synchronous_result_of_sending_the_request = Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

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
                    assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
                allure.attach(str(ei_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_ei_operation_id).create_ei_message_is_successful(
                    environment=parse_environment,
                    kafka_message=ei_feed_point_message,
                    test_mode=True)

                ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is True:
                        connect_to_database.cleanup_table_of_services_for_expenditureItem(cp_id=ei_ocid)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_ei_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

    @allure.title('Check ExpenditureItem release data after ExpenditureItem creation based on full data model')
    def test_check_ei_release_one(self, get_hosts, parse_country, parse_language, parse_environment,
                                  connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create ExpenditureItem'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step('# 2. Send request to create ExpenditureItem'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid and ei_token.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            ei_payload = ei_payload_class.create_ei_full_data_model()

            synchronous_result_of_sending_the_request = Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=ei_payload,
                test_mode=True)

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
                    assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
                allure.attach(str(ei_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_ei_operation_id).create_ei_message_is_successful(
                    environment=parse_environment,
                    kafka_message=ei_feed_point_message,
                    test_mode=True)

                ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
                actual_ei_release = requests.get(url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check ExpenditureItem release'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(actual_ei_release)), "Actual ExpenditureItem release")

                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=parse_environment,
                    language=parse_language,
                    ei_payload=ei_payload,
                    ei_feed_point_message=ei_feed_point_message,
                    actual_ei_release=actual_ei_release))

                expected_ei_release_model = copy.deepcopy(expected_release_class.ei_release_full_data_model())

                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected ExpenditureItem release")

                compare_releases = dict(DeepDiff(actual_ei_release, expected_ei_release_model))
                expected_result = {}

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditureItem(cp_id=ei_ocid)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_ei_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing ExpenditureItem release and expected EI release and '
                                 'expected result of comparing EI release and expected EI release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release and expected EI release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing EI release and expected ExpenditureItem release.")
                    assert compare_releases == expected_result

    @allure.title('Check ExpenditureItem release after ExpenditureItem creation on model without optional fields')
    def test_check_ei_release_two(self, get_hosts, parse_country, parse_language, parse_environment,
                                  connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create ExpenditureItem'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create ExpenditureItem'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid and ei_token.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_obligatory_data_model()

            synchronous_result_of_sending_the_request = Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=create_ei_payload,
                test_mode=True)

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
                    assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
                allure.attach(str(ei_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_ei_operation_id).create_ei_message_is_successful(
                    environment=parse_environment,
                    kafka_message=ei_feed_point_message,
                    test_mode=True)

                ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
                actual_ei_release = requests.get(url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check ExpenditureItem release'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(actual_ei_release)), "Actual ExpenditureItem release")

                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=parse_environment,
                    language=parse_language,
                    ei_payload=create_ei_payload,
                    ei_feed_point_message=ei_feed_point_message,
                    actual_ei_release=actual_ei_release))

                expected_ei_release_model = copy.deepcopy(
                    expected_release_class.ei_release_obligatory_data_model())

                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected ExpenditureItem release")

                compare_releases = dict(DeepDiff(actual_ei_release, expected_ei_release_model))
                expected_result = {}

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditureItem(cp_id=ei_ocid)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=create_ei_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing ExpenditureItem release and expected EI release and '
                                 'expected result of comparing EI release and expected EI release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release and expected EI release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing EI release and expected ExpenditureItem release.")
                    assert compare_releases == expected_result

    @allure.title('Check ExpenditureItem release data after ExpenditureItem creation based on full data model with 3 items objects')
    def test_check_ei_release_three(self, get_hosts, parse_country, parse_language, parse_environment,
                                    connect_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        with allure.step(f'# {step_number}. Authorization platform one: create ExpenditureItem'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            ei_access_token = authorization.get_access_token_for_platform_one()
            ei_operation_id = authorization.get_x_operation_id(ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create ExpenditureItem'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid and ei_token.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            ei_payload = ei_payload_class.create_ei_full_data_model(quantity_of_tender_item_object=3)

            synchronous_result_of_sending_the_request = Requests().createEi(
                host_of_request=get_hosts[1],
                access_token=ei_access_token,
                x_operation_id=ei_operation_id,
                country=parse_country,
                language=parse_language,
                payload=ei_payload,
                test_mode=True)

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
                    assert synchronous_result_of_sending_the_request.status_code == 202

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                ei_feed_point_message = KafkaMessage(ei_operation_id).get_message_from_kafka()
                allure.attach(str(ei_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    ei_operation_id).create_ei_message_is_successful(
                    environment=parse_environment,
                    kafka_message=ei_feed_point_message,
                    test_mode=True)

                ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
                actual_ei_release = requests.get(url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check ExpenditureItem release'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(actual_ei_release)), "Actual ExpenditureItem release")

                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=parse_environment,
                    language=parse_language,
                    ei_payload=ei_payload,
                    ei_feed_point_message=ei_feed_point_message,
                    actual_ei_release=actual_ei_release))

                expected_ei_release_model = copy.deepcopy(
                    expected_release_class.ei_release_full_data_model())

                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected ExpenditureItem release")

                compare_releases = dict(DeepDiff(actual_ei_release, expected_ei_release_model))
                expected_result = {}

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        connect_to_database.cleanup_table_of_services_for_expenditureItem(cp_id=ei_ocid)

                        connect_to_database.cleanup_ocds_orchestratorOperationStep_by_operationId(operation_id=ei_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connect_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=ei_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing ExpenditureItem release and expected EI release and '
                                 'expected result of comparing EI release and expected EI release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing EI release and expected EI release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing EI release and expected ExpenditureItem release.")
                    assert compare_releases == expected_result
