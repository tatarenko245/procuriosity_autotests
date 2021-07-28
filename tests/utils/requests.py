import configparser
import json
import logging

import allure
import requests
from allure_commons._allure import step


class Requests:
    @staticmethod
    @allure.step('Prepared request: create EI')
    def create_ei(host_of_request, access_token, x_operation_id, country, language, payload):
        ei = requests.post(
            url=host_of_request + "/do/ei",
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json'},
            params={
                'country': country,
                'lang': language
            },
            json=payload)
        allure.attach(host_of_request + "/do/ei", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return ei

