import datetime
import time


import requests

from tests.utils.functions_collection.functions import time_bot


def get_message_for_platform(operation_id=None, ocid=None, initiator=None):

    host = "http://82.144.223.29"
    port = "5000"
    url = None
    message = None

    if operation_id is not None:
        url = f"{host}:{port}/x-operation-id/{operation_id}"

    elif ocid is not None and initiator is not None:
        url = f"{host}:{port}/ocid/{ocid}/{initiator}"

    time.sleep(3)
    status_code = requests.get(url).status_code

    if status_code == 404:
        date_new = datetime.datetime.now() + datetime.timedelta(seconds=10)
        time_bot(datetime.datetime.strftime(date_new, "%Y-%m-%dT%H:%M:%SZ"))
        status_code = requests.get(url).status_code

        if status_code == 200:
            message = requests.get(url).json()
            if str(message) == str([]):
                raise ValueError("The message was not found in Kafka topic")
        raise ValueError("The message was not found in Kafka topic")

    if status_code == 200:
        message = requests.get(url).json()
        if str(message) == str([]):
            raise ValueError("The message was not found in Kafka topic")

    del message['_id']
    return message