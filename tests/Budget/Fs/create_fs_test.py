# файл з самим тестом
import copy
import json
import time

import allure
import requests
from deepdiff import DeepDiff
from tests.utils.PayloadModel.Budget.Ei.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.fs_prepared_payload import FsPreparePayload
from tests.utils.ReleaseModel.Budget.Fs.fs_prepared_release import FsExpectedRelease
from tests.utils.functions import check_uuid_version
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization

from tests.utils.my_requests import Requests


@allure.parent_suite('Budget')
@allure.suite('Fs')
@allure.sub_suite('BPE: Create Fs')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/'
                     'edit#gid=1455075741',
                 name='Google sheets: Create Fs')
class TestCreateFs:
    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check status code and message from Kafka topic after Fs creating')
    def test_check_result_of_sending_the_request(self, get_hosts, country, language, pmd, environment,
                                                 connection_to_database):
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
                country=country,
                language=language,
                payload=create_ei_payload,
                test_mode=True)

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
            fs_payload_class = copy.deepcopy(FsPreparePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_full_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
                test_mode=True)

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
                create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
                allure.attach(str(create_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_fs_operation_id).create_fs_message_is_successful(
                    environment=environment,
                    kafka_message=create_fs_feed_point_message,
                    test_mode=True)

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is True:
                        connection_to_database.ei_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_ei_operation_id)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
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
                  'Check Fs release data after Fs creation:'
                  'ei -> model without optional fields '
                  'and fs -> full data model own money')
    def test_check_fs_release_one(self, get_hosts, country, language, pmd, environment, connection_to_database,
                                  metadata_budget_url):

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
                country=country,
                language=language,
                payload=create_ei_payload,
                test_mode=True)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            actual_ei_release_before_fs_creating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
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
            fs_payload_class = copy.deepcopy(FsPreparePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_full_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
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
                create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
                allure.attach(str(create_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_fs_operation_id).create_fs_message_is_successful(
                    environment=environment,
                    kafka_message=create_fs_feed_point_message,
                    test_mode=True)

                actual_ei_release_after_fs_creating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
                actual_fs_release = requests.get(url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check Fs release'):
                """
                Compare actual first financial source release with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release)), "Actual Fs release")

                expected_release_class = copy.deepcopy(FsExpectedRelease(
                    environment=environment,
                    language=language,
                    ei_ocid=ei_ocid,
                    fs_payload=create_fs_payload,
                    fs_feed_point_message=create_fs_feed_point_message,
                    actual_fs_release=actual_fs_release))

                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_full_data_model_own_money_payer_id_is_not_equal_funder_id())

                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected Fs release")

                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release_model))
                expected_result = {}

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release and expected Fs release and '
                                 'expected result of comparing Fs release and expected Fs release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release and expected Fs release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release and expected Fs release.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.4. Check Ei release after Fs creating'):
                """
                Compare actual second expenditure item release after fs creating with
                first expenditure item release before fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_creating)),
                              "Actual Ei release before fs creating")

                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")

                compare_releases = DeepDiff(actual_ei_release_before_fs_creating, actual_ei_release_after_fs_creating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': create_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_ei_feed_point_message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes_model = [{
                    "id": actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": fs_id,
                    "uri": f"{metadata_budget_url}/{ei_ocid}/{fs_id}"
                }]

                try:
                    """
                    Check actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'].
                    If actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'] is uuid v.1,
                    then pass.
                    ELSE return exception.
                    """
                    check_uuid_version(
                        uuid_to_test=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your relatedProcesses.id in Ei release: relatedProcesses.id in Ei release "
                        "must be uuid version 1")

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        connection_to_database.ei_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_ei_operation_id)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs creating and '
                                 'after Fs creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before Fs creating and after Fs creating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs creating and after Fs creating")
                    assert compare_releases == expected_result

                with allure.step('Compare actual result of comparing Ei release before Fs creating and '
                                 'after Fs creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before Fs creating and after Fs creating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs creating and after Fs creating")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][amount].'):
                    allure.attach(str(actual_ei_release_after_fs_creating[
                                          'releases'][0]['planning']['budget']['amount']),
                                  "Actual result of publication Fs release[releases][tender][description].")
                    allure.attach(str(create_fs_payload['planning']['budget']['amount']),
                                  "Expected result of publication Fs release[releases][tender][description].")
                    assert actual_ei_release_after_fs_creating['releases'][0]['planning']['budget']['amount'] == \
                           create_fs_payload['planning']['budget']['amount']

                with allure.step('Check correctness of publication Fs release[releases][relatedProcesses].'):
                    allure.attach(str(actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses']),
                                  "Actual result of publication Fs release[releases][relatedProcesses].")
                    allure.attach(str(expected_related_processes_model),
                                  "Expected result of publication Fs release[releases][relatedProcesses].")
                    assert actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'] == \
                           expected_related_processes_model

    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs creation:'
                  'ei -> full data model and '
                  'fs -> full data model treasury money')
    def test_check_fs_release_two(self, get_hosts, country, language, pmd, environment, connection_to_database,
                                  metadata_budget_url):

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
                country=country,
                language=language,
                payload=create_ei_payload,
                test_mode=True)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            actual_ei_release_before_fs_creating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
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
            fs_payload_class = copy.deepcopy(FsPreparePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_full_data_model_treasury_money()
            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
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
                create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
                allure.attach(str(create_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_fs_operation_id).create_fs_message_is_successful(
                    environment=environment,
                    kafka_message=create_fs_feed_point_message,
                    test_mode=True)

                actual_ei_release_after_fs_creating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
                actual_fs_release = requests.get(url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check Fs release'):
                """
                Compare actual first financial source release with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release)), "Actual Fs release")

                expected_release_class = copy.deepcopy(FsExpectedRelease(
                    environment=environment,
                    language=language,
                    ei_ocid=ei_ocid,
                    fs_payload=create_fs_payload,
                    fs_feed_point_message=create_fs_feed_point_message,
                    actual_fs_release=actual_fs_release))

                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_full_data_model_treasury_money(ei_payload=create_ei_payload))

                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected Fs release")

                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release_model))
                expected_result = {}

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release and expected Fs release and '
                                 'expected result of comparing Fs release and expected Fs release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release and expected Fs release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release and expected Fs release.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.4. Check Ei release after Fs creating'):
                """
                Compare actual second expenditure item release after fs creating with
                first expenditure item release before fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_creating)),
                              "Actual Ei release before fs creating")

                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")

                compare_releases = DeepDiff(actual_ei_release_before_fs_creating, actual_ei_release_after_fs_creating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': create_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_ei_feed_point_message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes_model = [{
                    "id": actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": fs_id,
                    "uri": f"{metadata_budget_url}/{ei_ocid}/{fs_id}"
                }]

                try:
                    """
                    Check actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'].
                    If actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'] is uuid v.1,
                    then pass.
                    ELSE return exception.
                    """
                    check_uuid_version(
                        uuid_to_test=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your relatedProcesses.id in Ei release: relatedProcesses.id in Ei release "
                        "must be uuid version 1")

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        connection_to_database.ei_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_ei_operation_id)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs creating and '
                                 'after Fs creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before Fs creating and after Fs creating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs creating and after Fs creating")
                    assert compare_releases == expected_result

                with allure.step('Compare actual result of comparing Ei release before Fs creating and '
                                 'after Fs creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before Fs creating and after Fs creating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs creating and after Fs creating")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][amount].'):
                    allure.attach(str(actual_ei_release_after_fs_creating[
                                          'releases'][0]['planning']['budget']['amount']),
                                  "Actual result of publication Fs release[releases][tender][description].")
                    allure.attach(str(create_fs_payload['planning']['budget']['amount']),
                                  "Expected result of publication Fs release[releases][tender][description].")
                    assert actual_ei_release_after_fs_creating['releases'][0]['planning']['budget']['amount'] == \
                           create_fs_payload['planning']['budget']['amount']

                with allure.step('Check correctness of publication Fs release[releases][relatedProcesses].'):
                    allure.attach(str(actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses']),
                                  "Actual result of publication Fs release[releases][relatedProcesses].")
                    allure.attach(str(expected_related_processes_model),
                                  "Expected result of publication Fs release[releases][relatedProcesses].")
                    assert actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'] == \
                           expected_related_processes_model

    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs creation:'
                  'ei -> full data model and '
                  'fs -> model without optional fields own money')
    def test_check_fs_release_three(self, get_hosts, country, language, pmd, environment, connection_to_database,
                                    metadata_budget_url):

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
                country=country,
                language=language,
                payload=create_ei_payload,
                test_mode=True)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            actual_ei_release_before_fs_creating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
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
            fs_payload_class = copy.deepcopy(FsPreparePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_own_money()
            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
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
                create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
                allure.attach(str(create_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_fs_operation_id).create_fs_message_is_successful(
                    environment=environment,
                    kafka_message=create_fs_feed_point_message,
                    test_mode=True)

                actual_ei_release_after_fs_creating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
                actual_fs_release = requests.get(url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check Fs release'):
                """
                Compare actual first financial source release with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release)), "Actual Fs release")

                expected_release_class = copy.deepcopy(FsExpectedRelease(
                    environment=environment,
                    language=language,
                    ei_ocid=ei_ocid,
                    fs_payload=create_fs_payload,
                    fs_feed_point_message=create_fs_feed_point_message,
                    actual_fs_release=actual_fs_release))

                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_own_money_payer_id_is_not_equal_funder_id())

                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected Fs release")

                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release_model))
                expected_result = {}

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release and expected Fs release and '
                                 'expected result of comparing Fs release and expected Fs release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release and expected Fs release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release and expected Fs release.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.4. Check Ei release after Fs creating'):
                """
                Compare actual second expenditure item release after fs creating with
                first expenditure item release before fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_creating)),
                              "Actual Ei release before fs creating")

                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")

                compare_releases = DeepDiff(actual_ei_release_before_fs_creating, actual_ei_release_after_fs_creating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': create_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_ei_feed_point_message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes_model = [{
                    "id": actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": fs_id,
                    "uri": f"{metadata_budget_url}/{ei_ocid}/{fs_id}"
                }]

                try:
                    """
                    Check actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'].
                    If actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'] is uuid v.1,
                    then pass.
                    ELSE return exception.
                    """
                    check_uuid_version(
                        uuid_to_test=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your relatedProcesses.id in Ei release: relatedProcesses.id in Ei release "
                        "must be uuid version 1")

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        connection_to_database.ei_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_ei_operation_id)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs creating and '
                                 'after Fs creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before Fs creating and after Fs creating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs creating and after Fs creating")
                    assert compare_releases == expected_result

                with allure.step('Compare actual result of comparing Ei release before Fs creating and '
                                 'after Fs creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before Fs creating and after Fs creating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs creating and after Fs creating")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][amount].'):
                    allure.attach(str(actual_ei_release_after_fs_creating[
                                          'releases'][0]['planning']['budget']['amount']),
                                  "Actual result of publication Fs release[releases][tender][description].")
                    allure.attach(str(create_fs_payload['planning']['budget']['amount']),
                                  "Expected result of publication Fs release[releases][tender][description].")
                    assert actual_ei_release_after_fs_creating['releases'][0]['planning']['budget']['amount'] == \
                           create_fs_payload['planning']['budget']['amount']

                with allure.step('Check correctness of publication Fs release[releases][relatedProcesses].'):
                    allure.attach(str(actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses']),
                                  "Actual result of publication Fs release[releases][relatedProcesses].")
                    allure.attach(str(expected_related_processes_model),
                                  "Expected result of publication Fs release[releases][relatedProcesses].")
                    assert actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'] == \
                           expected_related_processes_model

    @allure.title('Warning - release of creating Fs contains THE CRUTCH '
                  '(the release does not contain release.languages): navigate to fs_prepared_release.py ->'
                  ' look at comments\n'
                  'Check Fs release data after Fs creation:'
                  'ei -> model without optional fields and '
                  'fs -> model without optional fields treasury money')
    def test_check_fs_release_four(self, get_hosts, country, language, pmd, environment, connection_to_database,
                                   metadata_budget_url):

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
                country=country,
                language=language,
                payload=create_ei_payload,
                test_mode=True)

            create_ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = create_ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            actual_ei_release_before_fs_creating = requests.get(
                url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
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
            fs_payload_class = copy.deepcopy(FsPreparePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=create_ei_payload)
            synchronous_result_of_sending_the_request = Requests().createFs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
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
                create_fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
                allure.attach(str(create_fs_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_fs_operation_id).create_fs_message_is_successful(
                    environment=environment,
                    kafka_message=create_fs_feed_point_message,
                    test_mode=True)

                actual_ei_release_after_fs_creating = requests.get(
                    url=f"{create_ei_feed_point_message['data']['url']}/{ei_ocid}").json()
                fs_id = create_fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
                actual_fs_release = requests.get(url=f"{create_fs_feed_point_message['data']['url']}/{fs_id}").json()

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing asynchronous result and expected result and '
                                 'expected result of comparing asynchronous result and expected result'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual status code of sending the request.")
                    allure.attach(str(True), "Expected status code of sending request.")
                    assert asynchronous_result_of_sending_the_request_was_checked is True

            with allure.step(f'# {step_number}.3. Check Fs release'):
                """
                Compare actual first financial source release with expected financial source
                release model.
                """
                allure.attach(str(json.dumps(actual_fs_release)), "Actual Fs release")

                expected_release_class = copy.deepcopy(FsExpectedRelease(
                    environment=environment,
                    language=language,
                    ei_ocid=ei_ocid,
                    fs_payload=create_fs_payload,
                    fs_feed_point_message=create_fs_feed_point_message,
                    actual_fs_release=actual_fs_release))

                expected_fs_release_model = copy.deepcopy(
                    expected_release_class.fs_release_obligatory_data_model_treasury_money(
                        ei_payload=create_ei_payload))

                allure.attach(str(json.dumps(expected_fs_release_model)), "Expected Fs release")

                compare_releases = dict(DeepDiff(actual_fs_release, expected_fs_release_model))
                expected_result = {}

                try:
                    """
                    If compare_releases !=expected_result, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Fs release and expected Fs release and '
                                 'expected result of comparing Fs release and expected Fs release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Fs release and expected Fs release.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Fs release and expected Fs release.")
                    assert compare_releases == expected_result

            with allure.step(f'# {step_number}.4. Check Ei release after Fs creating'):
                """
                Compare actual second expenditure item release after fs creating with
                first expenditure item release before fs creating.
                """
                allure.attach(str(json.dumps(actual_ei_release_before_fs_creating)),
                              "Actual Ei release before fs creating")

                allure.attach(str(json.dumps(actual_ei_release_after_fs_creating)),
                              "Actual Ei release after fs creating")

                compare_releases = DeepDiff(actual_ei_release_before_fs_creating, actual_ei_release_after_fs_creating)
                dictionary_item_added_was_cleaned = \
                    str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
                compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
                compare_releases = dict(compare_releases)

                expected_result = {
                    'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                             "['releases'][0]['planning']['budget']['amount']",
                    'values_changed': {
                        "root['releases'][0]['id']": {
                            "new_value": f"{ei_ocid}-{actual_ei_release_after_fs_creating['releases'][0]['id'][29:42]}",
                            "old_value": f"{ei_ocid}-{actual_ei_release_before_fs_creating['releases'][0]['id'][29:42]}"
                        },
                        "root['releases'][0]['date']": {
                            'new_value': create_fs_feed_point_message['data']['operationDate'],
                            'old_value': create_ei_feed_point_message['data']['operationDate']
                        }
                    }
                }

                expected_related_processes_model = [{
                    "id": actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                    "relationship": ["x_fundingSource"],
                    "scheme": "ocid",
                    "identifier": fs_id,
                    "uri": f"{metadata_budget_url}/{ei_ocid}/{fs_id}"
                }]

                try:
                    """
                    Check actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'].
                    If actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'] is uuid v.1,
                    then pass.
                    ELSE return exception.
                    """
                    check_uuid_version(
                        uuid_to_test=actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'][0]['id'],
                        version=1
                    )
                except ValueError:
                    raise ValueError(
                        "Check your relatedProcesses.id in Ei release: relatedProcesses.id in Ei release "
                        "must be uuid version 1")

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        connection_to_database.ei_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_ei_operation_id)
                        connection_to_database.cleanup_steps_of_process(operation_id=create_fs_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_fs_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual result of comparing Ei release before Fs creating and '
                                 'after Fs creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before Fs creating and after Fs creating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs creating and after Fs creating")
                    assert compare_releases == expected_result

                with allure.step('Compare actual result of comparing Ei release before Fs creating and '
                                 'after Fs creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Ei release before Fs creating and after Fs creating.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ei release before Fs creating and after Fs creating")
                    assert compare_releases == expected_result

                with allure.step('Check correctness of publication Fs release[releases][planning][budget][amount].'):
                    allure.attach(str(actual_ei_release_after_fs_creating[
                                          'releases'][0]['planning']['budget']['amount']),
                                  "Actual result of publication Fs release[releases][tender][description].")
                    allure.attach(str(create_fs_payload['planning']['budget']['amount']),
                                  "Expected result of publication Fs release[releases][tender][description].")
                    assert actual_ei_release_after_fs_creating['releases'][0]['planning']['budget']['amount'] == \
                           create_fs_payload['planning']['budget']['amount']

                with allure.step('Check correctness of publication Fs release[releases][relatedProcesses].'):
                    allure.attach(str(actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses']),
                                  "Actual result of publication Fs release[releases][relatedProcesses].")
                    allure.attach(str(expected_related_processes_model),
                                  "Expected result of publication Fs release[releases][relatedProcesses].")
                    assert actual_ei_release_after_fs_creating['releases'][0]['relatedProcesses'] == \
                           expected_related_processes_model
