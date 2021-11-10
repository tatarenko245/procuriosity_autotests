# файл з самим тестом
import copy
import json
import allure
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassCreateEi, GlobalClassMetadata
from tests.utils.PayloadModel.EI.ei_prepared_payload import EiPreparePayload
from tests.utils.ReleaseModel.EI.ei_prepared_release import EiExpectedRelease
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment


from tests.utils.functions import compare_actual_result_and_expected_result
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization


from tests.utils.my_requests import Requests


@allure.parent_suite('Budgets')
@allure.suite('EI')
@allure.sub_suite('BPE: Create EI')
@allure.severity('Critical')
@allure.testcase(url='https://docs.google.com/spreadsheets/d/1IDNt49YHGJzozSkLWvNl3N4vYRyutDReeOOG2VWAeSQ/edit#gid=0',
                 name='Google sheets: Create EI')
class TestCreateEi:
    def test_setup(self, environment, country, language, cassandra_username, cassandra_password):
        """
        Get 'country', 'language', 'cassandra_username', 'cassandra_password', 'environment' parameters
        from test run command.
        Then choose BPE host.
        Then choose host for Database connection.
        """
        GlobalClassMetadata.country = country
        GlobalClassMetadata.language = language
        GlobalClassMetadata.cassandra_username = cassandra_username
        GlobalClassMetadata.cassandra_password = cassandra_password
        GlobalClassMetadata.environment = environment
        GlobalClassMetadata.hosts = Environment().choose_environment(GlobalClassMetadata.environment)
        GlobalClassMetadata.host_for_bpe = GlobalClassMetadata.hosts[1]
        GlobalClassMetadata.cassandra_cluster = GlobalClassMetadata.hosts[0]
        GlobalClassMetadata.database = CassandraSession(
            cassandra_username=GlobalClassMetadata.cassandra_username,
            cassandra_password=GlobalClassMetadata.cassandra_password,
            cassandra_cluster=GlobalClassMetadata.cassandra_cluster)

    @allure.title('Check status code and message from Kafka topic after EI creation')
    def test_check_result_of_sending_the_request(self):

        with allure.step('# 1. Authorization platform one: create EI'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)

        with allure.step('# 2. Send request to create EI'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid and ei_token.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model()
            synchronous_result_of_sending_the_request = Requests().create_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                payload=GlobalClassCreateEi.payload
            )

        with allure.step('# 3. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 3.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 3.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassCreateEi.feed_point_message = \
                    KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCreateEi.feed_point_message), 'Message in feed point')
                GlobalClassCreateEi.ei_ocid = GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEi.feed_point_message
                )

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is True:
                        GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

    @allure.title('Check EI release data after Ei creation based on full data model')
    def test_check_ei_release_one(self):

        with allure.step('# 1. Authorization platform one: create EI'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)

        with allure.step('# 2. Send request to create EI'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid and ei_token.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model()
            synchronous_result_of_sending_the_request = Requests().create_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                payload=GlobalClassCreateEi.payload
            )

        with allure.step('# 3. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 3.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 3.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassCreateEi.feed_point_message = \
                    KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCreateEi.feed_point_message), 'Message in feed point')

                GlobalClassCreateEi.ei_ocid = \
                    GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

                GlobalClassCreateEi.actual_ei_release = requests.get(
                    url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateEi.ei_ocid}").json()

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEi.feed_point_message
                )

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

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 3.3. Check EI release'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateEi.actual_ei_release)), "Actual EI release")

                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ei_release_model = copy.deepcopy(
                    expected_release_class.ei_release_full_data_model())

                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected EI release")

                compare_releases = dict(DeepDiff(GlobalClassCreateEi.actual_ei_release, expected_ei_release_model))
                expected_result = {}

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check EI release after Ei creation on model without optional fields')
    def test_check_ei_release_two(self):
        with allure.step('# 1. Authorization platform one: create EI'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)

        with allure.step('# 2. Send request to create EI'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid and ei_token.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_obligatory_data_model()
            synchronous_result_of_sending_the_request = Requests().create_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                payload=GlobalClassCreateEi.payload
            )

        with allure.step('# 3. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 3.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 3.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassCreateEi.feed_point_message = \
                    KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCreateEi.feed_point_message), 'Message in feed point')

                GlobalClassCreateEi.ei_ocid = \
                    GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

                GlobalClassCreateEi.actual_ei_release = requests.get(
                    url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateEi.ei_ocid}").json()

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEi.feed_point_message
                )

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

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 3.3. Check EI release'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateEi.actual_ei_release)), "Actual EI release")

                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ei_release_model = copy.deepcopy(
                    expected_release_class.ei_release_obligatory_data_model())

                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected EI release")

                compare_releases = dict(DeepDiff(GlobalClassCreateEi.actual_ei_release, expected_ei_release_model))
                expected_result = {}

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)

    @allure.title('Check EI release data after Ei creation based on full data model with 3 items objects')
    def test_check_ei_release_three(self):
        with allure.step('# 1. Authorization platform one: create EI'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            GlobalClassCreateEi.access_token = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_access_token_for_platform_one()

            GlobalClassCreateEi.operation_id = PlatformAuthorization(
                GlobalClassMetadata.host_for_bpe).get_x_operation_id(GlobalClassCreateEi.access_token)

        with allure.step('# 2. Send request to create EI'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid and ei_token.
            """
            ei_payload = copy.deepcopy(EiPreparePayload())
            GlobalClassCreateEi.payload = ei_payload.create_ei_full_data_model(quantity_of_tender_item_object=3)
            synchronous_result_of_sending_the_request = Requests().create_ei(
                host_of_request=GlobalClassMetadata.host_for_bpe,
                access_token=GlobalClassCreateEi.access_token,
                x_operation_id=GlobalClassCreateEi.operation_id,
                country=GlobalClassMetadata.country,
                language=GlobalClassMetadata.language,
                payload=GlobalClassCreateEi.payload
            )

        with allure.step('# 3. See result'):
            """
            Check the results of TestCase.
            """
            with allure.step('# 3.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                assert compare_actual_result_and_expected_result(
                    expected_result=202,
                    actual_result=synchronous_result_of_sending_the_request.status_code
                )
            with allure.step('# 3.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                GlobalClassCreateEi.feed_point_message = \
                    KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
                allure.attach(str(GlobalClassCreateEi.feed_point_message), 'Message in feed point')

                GlobalClassCreateEi.ei_ocid = \
                    GlobalClassCreateEi.feed_point_message["data"]["outcomes"]["ei"][0]['id']

                GlobalClassCreateEi.actual_ei_release = requests.get(
                    url=f"{GlobalClassCreateEi.feed_point_message['data']['url']}/"
                        f"{GlobalClassCreateEi.ei_ocid}").json()

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
                    environment=GlobalClassMetadata.environment,
                    kafka_message=GlobalClassCreateEi.feed_point_message
                )

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

                assert compare_actual_result_and_expected_result(
                    expected_result=True,
                    actual_result=asynchronous_result_of_sending_the_request_was_checked
                )

            with allure.step('# 3.3. Check EI release'):
                """
                Compare actual first expenditure item release with expected expenditure item
                release model.
                """
                allure.attach(str(json.dumps(GlobalClassCreateEi.actual_ei_release)), "Actual EI release")

                expected_release_class = copy.deepcopy(EiExpectedRelease(
                    environment=GlobalClassMetadata.environment,
                    language=GlobalClassMetadata.language))
                expected_ei_release_model = copy.deepcopy(
                    expected_release_class.ei_release_full_data_model())

                allure.attach(str(json.dumps(expected_ei_release_model)), "Expected EI release")

                compare_releases = dict(DeepDiff(GlobalClassCreateEi.actual_ei_release, expected_ei_release_model))
                expected_result = {}

                try:
                    """
                    If TestCase was passed, then cLean up the database.
                    If TestCase was failed, then return process steps by operation-id.
                    """
                    if compare_releases == expected_result:
                        GlobalClassMetadata.database.ei_process_cleanup_table_of_services(
                            ei_id=GlobalClassCreateEi.ei_ocid)

                        GlobalClassMetadata.database.cleanup_steps_of_process(
                            operation_id=GlobalClassCreateEi.operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = GlobalClassMetadata.database.get_bpe_operation_step_by_operation_id(
                                operation_id=GlobalClassCreateEi.operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                assert str(compare_actual_result_and_expected_result(
                    expected_result=expected_result,
                    actual_result=compare_releases
                )) == str(True)
