import configparser
import logging

import requests
from allure_commons._allure import step


class Requests:
    @staticmethod
    def create_ei(host_of_request, access_token, x_operation_id, country, language, payload):
        with step('Create EI'):
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
        return ei

    @staticmethod
    def create_fs(host_of_request, ei_id, access_token, x_operation_id, payload):
        with step('Create FS'):
            fs = requests.post(
                url=host_of_request + "/do/fs/" + ei_id,
                headers={
                    'Authorization': 'Bearer ' + access_token,
                    'X-OPERATION-ID': x_operation_id,
                    'Content-Type': 'application/json'},
                json=payload)
        return fs
