import copy

import requests

from tests.utils.kafka_message import KafkaMessage
from tests.utils.payloads import Payload
from tests.utils.platform_authorization import PlatformAuthorization
from tests.utils.requests import Requests


class StateOfTender:
    def __init__(self, host_for_bpe, country, language):
        self.host_for_bpe = host_for_bpe
        self.country = country
        self.language = language

    def make_tender_process(self, state):
        access_token = PlatformAuthorization(self.host_for_bpe).get_access_token_for_platform_one()
        operation_id = PlatformAuthorization(self.host_for_bpe).get_x_operation_id(access_token)
        payload_for_create_ei = copy.deepcopy(Payload().for_create_ei_full_data_model())

        if state == "create EI":
            try:
                Requests().create_ei(
                    host_of_request=self.host_for_bpe,
                    access_token=access_token,
                    x_operation_id=operation_id,
                    country=self.country,
                    language=self.language,
                    payload=payload_for_create_ei
                )
                message = KafkaMessage(operation_id).get_message_from_kafka()
                ei_id = message['data']['outcomes']['ei'][0]['id']
                ei_token = message['data']['outcomes']['ei'][0]['X-TOKEN']

                previous_ei_release_model = requests.get(url=f"{message['data']['url']}/{ei_id}").json()
                return ei_id, ei_token, previous_ei_release_model
            except ValueError:
                print("Create EI process was failed")
        else:
            print("Choose the tender_process do you need")

