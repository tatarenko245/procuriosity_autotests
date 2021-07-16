import requests
from allure_commons._allure import step


class PlatformAuthorization:
    def __init__(self, host):
        self.host = host

    def get_access_token_for_platform_one(self):
        with step('Get access token for platform one'):
            access_token = requests.get(
                url=self.host + '/auth/signin',
                headers={
                    'Authorization': 'Basic dXNlcjpwYXNzd29yZA=='
                }).json()
            access_token = access_token['data']['tokens']['access']
        return access_token

    def get_access_token_for_platform_two(self):
        with step('Get access token for platform two'):
            access_token = requests.get(
                url=self.host + '/auth/signin',
                headers={
                    'Authorization': 'Basic YXV0b21hdGlvbl91c2VyOnBhc3N3b3Jk='
                }).json()
            access_token = access_token['data']['tokens']['access']
        return access_token

    def get_x_operation_id(self, access_token):
        with step('Get X-OPERATION-ID'):
            x_operation_id = requests.post(
                url=self.host + '/operations',
                headers={
                    'Authorization': 'Bearer ' + access_token
                }).json()
            x_operation_id = x_operation_id['data']['operationId']
        return x_operation_id
