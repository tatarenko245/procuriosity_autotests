import datetime
import fnmatch
import json

import allure
import requests

from tests.utils.functions import is_it_uuid


class KafkaMessage:
    def __init__(self, operation_id):
        self.operation_id = operation_id

    @allure.step('Receive message in feed-point')
    def get_message_from_kafka(self):
        kafka_host = 'http://82.144.223.29:5000'
        kafka_message = requests.get(
            url=kafka_host + '/x-operation-id/' + self.operation_id
        )
        if kafka_message.status_code == 404:
            date = datetime.datetime.now()
            date_new = datetime.datetime.now() + datetime.timedelta(seconds=15)

            while date < date_new:
                kafka_message = requests.get(
                    url=kafka_host + '/x-operation-id/' + self.operation_id
                )
                date = datetime.datetime.now()
                if kafka_message.status_code == 200:
                    kafka_message = requests.get(
                        url=kafka_host + '/x-operation-id/' + self.operation_id
                    ).json()
                    del kafka_message['_id']
                    return kafka_message
            print('The message was not found in Kafka topic')

        if kafka_message.status_code == 200:
            kafka_message = requests.get(
                url=kafka_host + '/x-operation-id/' + self.operation_id
            ).json()
        del kafka_message['_id']
        allure.attach(json.dumps(kafka_message), 'Message in feed-point')
        return kafka_message


    @staticmethod
    def create_ei_message_is_successful(environment, kafka_message):
        budget_url = None
        if environment == "dev":
            budget_url = "http://dev.public.eprocurement.systems/budgets/"
        if environment == "sandbox":
            budget_url = "http://public.eprocurement.systems/budgets/"
        check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
        check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                    f"{budget_url}{kafka_message['data']['ocid']}")
        check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        check_ei_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["ei"][0]["id"], "ocds-t1s2t3-MD-*")
        check_ei_token = is_it_uuid(kafka_message["data"]["outcomes"]["ei"][0]["X-TOKEN"], 4)
        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and \
                check_ei_id is True and check_ei_token is True:
            return True
        else:
            return False


    @staticmethod
    def create_fs_message_is_successful(environment, kafka_message):
        budget_url = None
        if environment == "dev":
            budget_url = "http://dev.public.eprocurement.systems/budgets/"
        if environment == "sandbox":
            budget_url = "http://public.eprocurement.systems/budgets/"
        check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
        check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                    f"{budget_url}{kafka_message['data']['ocid']}")
        check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        check_fs_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["fs"][0]["id"], "ocds-t1s2t3-MD-*")
        check_fs_token = is_it_uuid(kafka_message["data"]["outcomes"]["fs"][0]["X-TOKEN"], 4)
        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and \
                check_fs_id is True and check_fs_token is True:
            return True
        else:
            return False
