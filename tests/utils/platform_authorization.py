import json

import allure
import requests


class PlatformAuthorization:
    def __init__(self, host):
        self.host = host

    @allure.step('Get access token for platform one')
    def get_access_token_for_platform_one(self):
        access_token = requests.get(
            url=self.host + '/auth/signin',
            headers={
                'Authorization': 'Basic dXNlcjpwYXNzd29yZA=='
            }).json()
        access_token = access_token['data']['tokens']['access']
        allure.attach(self.host + '/auth/signin', 'HOST')
        allure.attach('Basic dXNlcjpwYXNzd29yZA==', 'Platform credentials for authorization')
        allure.attach(json.dumps(access_token), 'Response from auth service')
        allure.attach(str(access_token), 'Access token')
        return access_token

    @allure.step('Get access token for platform two')
    def get_access_token_for_platform_two(self):
        access_token = requests.get(
            url=self.host + '/auth/signin',
            headers={
                'Authorization': 'Basic YXV0b21hdGlvbl91c2VyOnBhc3N3b3Jk='
            }).json()
        access_token = access_token['data']['tokens']['access']
        access_token = access_token['data']['tokens']['access']
        allure.attach(self.host + '/auth/signin', 'HOST')
        allure.attach('Basic YXV0b21hdGlvbl91c2VyOnBhc3N3b3Jk=', 'Platform credentials for authorization')
        allure.attach(str(access_token), 'Access token')
        allure.attach(str(access_token), 'Access token')
        return access_token

    @allure.step('Get X-OPERATION-ID')
    def get_x_operation_id(self, access_token):
        x_operation_id = requests.post(
            url=self.host + '/operations',
            headers={
                'Authorization': 'Bearer ' + access_token
            }).json()
        print(x_operation_id)
        x_operation_id = x_operation_id['data']['operationId']
        allure.attach(self.host + '/operations', 'HOST')
        allure.attach(access_token, 'Platform access token')
        allure.attach(json.dumps(x_operation_id), 'Response from auth service')
        allure.attach(str(x_operation_id), 'X-OPERATION-ID')
        return x_operation_id
