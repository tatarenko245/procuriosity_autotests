import datetime
import fnmatch
import time
import allure
import requests
from tests.utils.functions import get_project_root, is_it_uuid, time_bot


class MessageForPlatform:
    def __init__(self, environment, operation_id=None, ocid=None, initiator=None):
        self.environment = environment
        host = "http://82.144.223.29"
        port = "5000"

        if operation_id is not None:
            self.url = f"{host}:{port}/x-operation-id/{operation_id}"

        elif ocid is not None and initiator is not None:
            self.url = f"{host}:{port}/ocid/{ocid}/{initiator}"

    def get_message_from_kafka_topic(self):
        message = None
        status_code = requests.get(self.url).status_code

        if status_code == 404:
            date_new = datetime.datetime.now() + datetime.timedelta(seconds=15)
            time_bot(datetime.datetime.strftime(date_new, "%Y-%m-%dT%H:%M:%SZ"))
            status_code = requests.get(self.url).status_code

            if status_code == 200:
                message = requests.get(self.url).json()
                if str(message) == str([]):
                    raise ValueError("The message was not found in Kafka topic")
            raise ValueError("The message was not found in Kafka topic")

        if status_code == 200:
            message = requests.get(self.url).json()
            if str(message) == str([]):
                raise ValueError("The message was not found in Kafka topic")

        del message['_id']
        return message
