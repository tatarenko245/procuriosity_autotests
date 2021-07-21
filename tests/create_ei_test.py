# файл з самим тестом
import copy
import json

import pytest
import requests
from deepdiff import DeepDiff

from tests.conftest import GlobalClassCreateEi, GlobalClassCreateFs
from tests.utils.cassandra_session import CassandraSession
from tests.utils.environment import Environment
from tests.utils.fixtures_and_functions import compare_actual_result_and_expected_result
from tests.utils.payloads import Payload, Ei
from tests.utils.kafka_message import KafkaMessage
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.releases_models import EiRelease, FsRelease
from tests.utils.requests import Requests
from tests.utils.state_of_tender_process import StateOfTender


class TestCreteExpenditureItemVariantOne:

    @pytest.mark.api
    def test_setup(self, environment, country, language, cassandra_username, cassandra_password):
        GlobalClassCreateEi.country = country
        GlobalClassCreateEi.language = language
        GlobalClassCreateEi.cassandra_username = cassandra_username
        GlobalClassCreateEi.cassandra_password = cassandra_password
        GlobalClassCreateEi.environment = environment
        GlobalClassCreateEi.hosts = Environment().choose_environment(GlobalClassCreateEi.environment)
        host_for_bpe = GlobalClassCreateEi.hosts[1]
        GlobalClassCreateEi.host_for_service = GlobalClassCreateEi.hosts[2]
        GlobalClassCreateEi.cassandra_cluster = GlobalClassCreateEi.hosts[0]
        access_token = PlatformAuthorization(host_for_bpe).get_access_token_for_platform_one()
        GlobalClassCreateEi.operation_id = PlatformAuthorization(host_for_bpe).get_x_operation_id(access_token)
        GlobalClassCreateEi.payload_for_create_ei = copy.deepcopy(Ei().obligatory_model())
        GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
            host_of_request=host_for_bpe,
            access_token=access_token,
            x_operation_id=GlobalClassCreateEi.operation_id,
            country=GlobalClassCreateEi.country,
            language=GlobalClassCreateEi.language,
            payload=GlobalClassCreateEi.payload_for_create_ei
        )

    @pytest.mark.api
    def test_check_status_code_of_request_22133_1(self):
        print(GlobalClassCreateEi.send_the_request_create_ei.status_code)
        assert compare_actual_result_and_expected_result(
            expected_result=str(202),
            actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
        )

    @pytest.mark.api
    def test_check_message_in_kafka_topic_22133_2(self):
        GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
        check_message = KafkaMessage(GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
            environment=GlobalClassCreateEi.environment,
            kafka_message=GlobalClassCreateEi.message
        )
        assert compare_actual_result_and_expected_result(
            expected_result=str(True),
            actual_result=str(check_message)
        )

    @pytest.mark.api
    def test_check_ei_release_in_public_point_22133_3(self):
        actual_ei_release_model = requests.get(url=f"{GlobalClassCreateEi.message['data']['url']}/"
                                                   f"{GlobalClassCreateEi.message['data']['ocid']}").json()
        expected_ei_release_model = EiRelease().for_create_ei_full_data_model(
            ei_id=GlobalClassCreateEi.message['data']['ocid'],
            operation_date=GlobalClassCreateEi.message['data']['operationDate'],
            release_id=actual_ei_release_model['releases'][0]['id'],
            language=GlobalClassCreateEi.language,
            tender_id=actual_ei_release_model['releases'][0]['tender']['id'],
            item_id=actual_ei_release_model['releases'][0]['tender']['items'][0]['id'],
            country=GlobalClassCreateEi.country
        )
        compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
        assert compare_actual_result_and_expected_result(
            expected_result=str({}),
            actual_result=str(compare_releases)
        )

    @pytest.mark.api
    def test_teardown(self):
        database = CassandraSession(
            cassandra_username=GlobalClassCreateEi.cassandra_username,
            cassandra_password=GlobalClassCreateEi.cassandra_password,
            cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
        )
        database.create_ei_process_cleanup_table_of_services(
            ei_id=GlobalClassCreateEi.message['data']['ocid']
        )
        database.cleanup_steps_of_process(
            operation_id=GlobalClassCreateEi.operation_id
        )


class TestCreteExpenditureItemVariantTwo:

    @pytest.mark.api
    def test_setup(self, environment, country, language, cassandra_username, cassandra_password):
        GlobalClassCreateEi.country = country
        GlobalClassCreateEi.language = language
        GlobalClassCreateEi.cassandra_username = cassandra_username
        GlobalClassCreateEi.cassandra_password = cassandra_password
        GlobalClassCreateEi.environment = environment
        GlobalClassCreateEi.hosts = Environment().choose_environment(GlobalClassCreateEi.environment)
        host_for_bpe = GlobalClassCreateEi.hosts[1]
        GlobalClassCreateEi.host_for_service = GlobalClassCreateEi.hosts[2]
        GlobalClassCreateEi.cassandra_cluster = GlobalClassCreateEi.hosts[0]
        access_token = PlatformAuthorization(host_for_bpe).get_access_token_for_platform_one()
        GlobalClassCreateEi.operation_id = PlatformAuthorization(host_for_bpe).get_x_operation_id(access_token)
        GlobalClassCreateEi.payload_for_create_ei = copy.deepcopy(Ei().add_items(quantity=3))
        GlobalClassCreateEi.send_the_request_create_ei = Requests().create_ei(
            host_of_request=host_for_bpe,
            access_token=access_token,
            x_operation_id=GlobalClassCreateEi.operation_id,
            country=GlobalClassCreateEi.country,
            language=GlobalClassCreateEi.language,
            payload=GlobalClassCreateEi.payload_for_create_ei
        )

    @pytest.mark.api
    def test_check_status_code_of_request_22133_1(self):
        assert compare_actual_result_and_expected_result(
            expected_result=str(202),
            actual_result=str(GlobalClassCreateEi.send_the_request_create_ei.status_code)
        )

    @pytest.mark.api
    def test_check_message_in_kafka_topic_22133_2(self):
        GlobalClassCreateEi.message = KafkaMessage(GlobalClassCreateEi.operation_id).get_message_from_kafka()
        check_message = KafkaMessage(GlobalClassCreateEi.operation_id).create_ei_message_is_successful(
            environment=GlobalClassCreateEi.environment,
            kafka_message=GlobalClassCreateEi.message
        )
        assert compare_actual_result_and_expected_result(
            expected_result=str(True),
            actual_result=str(check_message)
        )

    @pytest.mark.api
    def test_check_ei_release_in_public_point_22133_3(self):
        actual_ei_release_model = requests.get(url=f"{GlobalClassCreateEi.message['data']['url']}/"
                                                   f"{GlobalClassCreateEi.message['data']['ocid']}").json()
        expected_ei_release_model = EiRelease().for_create_ei_full_data_model(
            ei_id=GlobalClassCreateEi.message['data']['ocid'],
            operation_date=GlobalClassCreateEi.message['data']['operationDate'],
            release_id=actual_ei_release_model['releases'][0]['id'],
            language=GlobalClassCreateEi.language,
            tender_id=actual_ei_release_model['releases'][0]['tender']['id'],
            item_id=actual_ei_release_model['releases'][0]['tender']['items'][0]['id'],
            country=GlobalClassCreateEi.country
        )
        compare_releases = DeepDiff(actual_ei_release_model, expected_ei_release_model)
        assert compare_actual_result_and_expected_result(
            expected_result=str({}),
            actual_result=str(compare_releases)
        )

    @pytest.mark.api
    def test_teardown(self):
        database = CassandraSession(
            cassandra_username=GlobalClassCreateEi.cassandra_username,
            cassandra_password=GlobalClassCreateEi.cassandra_password,
            cassandra_cluster=GlobalClassCreateEi.cassandra_cluster
        )
        database.create_ei_process_cleanup_table_of_services(
            ei_id=GlobalClassCreateEi.message['data']['ocid']
        )
        database.cleanup_steps_of_process(
            operation_id=GlobalClassCreateEi.operation_id
        )
class TestCreteFinancialSource:
    @pytest.mark.api
    def test_setup(self, environment, country, language, cassandra_username, cassandra_password):
        host_for_bpe = Environment().choose_environment(environment)[1]
        tender_process = StateOfTender(
            host_for_bpe=host_for_bpe,
            country=country,
            language=language
        )
        GlobalClassCreateFs.create_ei_process = tender_process.make_tender_process(state="create EI")
        GlobalClassCreateFs.country = country
        GlobalClassCreateFs.language = language
        GlobalClassCreateFs.cassandra_username = cassandra_username
        GlobalClassCreateFs.cassandra_password = cassandra_password
        GlobalClassCreateFs.environment = environment
        GlobalClassCreateFs.hosts = Environment().choose_environment(GlobalClassCreateEi.environment)
        GlobalClassCreateFs.host_for_bpe = GlobalClassCreateFs.hosts[1]
        GlobalClassCreateFs.host_for_service = GlobalClassCreateFs.hosts[2]
        GlobalClassCreateFs.cassandra_cluster = GlobalClassCreateFs.hosts[0]
        access_token = PlatformAuthorization(host_for_bpe).get_access_token_for_platform_one()
        GlobalClassCreateFs.operation_id = PlatformAuthorization(host_for_bpe).get_x_operation_id(access_token)
        GlobalClassCreateFs.payload_for_create_fs = copy.deepcopy(Payload().for_create_fs_full_own_money_data_model())
        GlobalClassCreateFs.send_the_request_create_fs = Requests().create_fs(
            host_of_request=GlobalClassCreateFs.host_for_bpe,
            ei_id=GlobalClassCreateFs.create_ei_process[0],
            access_token=access_token,
            x_operation_id=GlobalClassCreateFs.operation_id,
            payload=GlobalClassCreateFs.payload_for_create_fs
        )

    @pytest.mark.api
    def test_check_status_code_of_request_27545_1(self):
        assert compare_actual_result_and_expected_result(
            expected_result=str(202),
            actual_result=str(GlobalClassCreateFs.send_the_request_create_fs.status_code)
        )

    @pytest.mark.api
    def test_check_message_in_kafka_topic_27545_2(self):
        GlobalClassCreateFs.message = KafkaMessage(GlobalClassCreateFs.operation_id).get_message_from_kafka()
        check_message = KafkaMessage(GlobalClassCreateFs.operation_id).create_fs_message_is_successful(
            environment=GlobalClassCreateFs.environment,
            kafka_message=GlobalClassCreateFs.message
        )
        assert compare_actual_result_and_expected_result(
            expected_result=str(True),
            actual_result=str(check_message)
        )

    @pytest.mark.api
    def test_check_fs_release_in_public_point_27545_3(self):
        actual_fs_release_model = requests.get(url=f"{GlobalClassCreateFs.message['data']['url']}/"
                                                   f"{GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id']}"
                                                   f"").json()
        expected_fs_release_model = FsRelease().for_create_fs_full_own_money_data_model(
            ei_id=GlobalClassCreateFs.create_ei_process[0],
            fs_id=GlobalClassCreateFs.message['data']['outcomes']['fs'][0]['id'],
            operation_date=GlobalClassCreateFs.message['data']['operationDate'],
            release_id=actual_fs_release_model['releases'][0]['id'],
            language=GlobalClassCreateFs.language,
            tender_id=actual_fs_release_model['releases'][0]['tender']['id'],
            country=GlobalClassCreateFs.country,
            related_process_id=actual_fs_release_model['releases'][0]['relatedProcesses'][0]['id']
        )
        compare_releases = DeepDiff(actual_fs_release_model, expected_fs_release_model)
        assert compare_actual_result_and_expected_result(
            expected_result=str({}),
            actual_result=str(compare_releases)
        )

    @pytest.mark.api
    def test_check_ei_release_in_public_point_27545_4(self):
        actual_ei_release_model = requests.get(url=f"{GlobalClassCreateFs.message['data']['url']}/"
                                                   f"{GlobalClassCreateFs.create_ei_process[0]}").json()
        previous_ei_release_model = GlobalClassCreateFs.create_ei_process[2]
        compare_releases = DeepDiff(previous_ei_release_model, actual_ei_release_model)
        dictionary_item_added_was_cleaned = str(compare_releases['dictionary_item_added']).replace('root', '')[1:-1]
        compare_releases['dictionary_item_added'] = dictionary_item_added_was_cleaned
        assert compare_actual_result_and_expected_result(
            expected_result=str({
                'dictionary_item_added': "['releases'][0]['relatedProcesses'], "
                                         "['releases'][0]['planning']['budget']['amount']",
                'values_changed': {
                    "root['releases'][0]['id']": {
                        'new_value': actual_ei_release_model['releases'][0]['id'],
                        'old_value': previous_ei_release_model['releases'][0]['id']
                    },
                    "root['releases'][0]['date']": {
                        'new_value': actual_ei_release_model['releases'][0]['date'],
                        'old_value': previous_ei_release_model['releases'][0]['date']
                    }
                }
            }),
            actual_result=str(compare_releases)
        )

    @pytest.mark.api
    def test_teardown(self):
        database = CassandraSession(
            cassandra_username=GlobalClassCreateFs.cassandra_username,
            cassandra_password=GlobalClassCreateFs.cassandra_password,
            cassandra_cluster=GlobalClassCreateFs.cassandra_cluster
        )
        database.create_fs_process_cleanup_table_of_services(
            ei_id=GlobalClassCreateFs.create_ei_process[0]
        )
        database.cleanup_steps_of_process(
            operation_id=GlobalClassCreateFs.operation_id
        )
