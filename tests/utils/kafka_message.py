import datetime
import fnmatch
import json

import allure
import requests

from tests.utils.functions import is_it_uuid


class KafkaMessage:
    def __init__(self, operation_id):
        self.operation_id = operation_id

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
        with allure.step('Receive message in feed-point'):
            allure.attach(json.dumps(kafka_message), 'Message in feed-point')
        return kafka_message

    @staticmethod
    def create_ei_message_is_successful(environment, kafka_message):
        budget_url = None
        if environment == "dev":
            budget_url = "http://dev.public.eprocurement.systems/budgets/"
        if environment == "sandbox":
            budget_url = "http://public.eprocurement.systems/budgets/"

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None
        check_ei_id = None
        check_ei_token = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:

            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            if "ocid" in kafka_message["data"]:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{budget_url}{kafka_message['data']['ocid']}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if "id" in kafka_message["data"]["outcomes"]["ei"][0]:
                check_ei_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["ei"][0]["id"], "ocds-t1s2t3-MD-*")
        except KeyError:
            raise KeyError('KeyError: id')
        try:
            if "X-TOKEN" in kafka_message["data"]["outcomes"]["ei"][0]:
                check_ei_token = is_it_uuid(kafka_message["data"]["outcomes"]["ei"][0]["X-TOKEN"], 4)
        except KeyError:
            raise KeyError('KeyError: X-TOKEN')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and \
                check_ei_id is True and check_ei_token is True:
            return True
        else:
            return False

    @staticmethod
    def update_ei_message_is_successful(environment, kafka_message, ei_ocid):
        budget_url = None
        if environment == "dev":
            budget_url = "http://dev.public.eprocurement.systems/budgets/"
        if environment == "sandbox":
            budget_url = "http://public.eprocurement.systems/budgets/"

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            if "ocid" in kafka_message["data"]:
                check_oc_id = fnmatch.fnmatch(ei_ocid, "ocds-t1s2t3-MD-*")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{budget_url}{ei_ocid}/{ei_ocid}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
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

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None
        check_fs_id = None
        check_fs_token = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            if "ocid" in kafka_message["data"]:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{budget_url}{kafka_message['data']['ocid']}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if "id" in kafka_message["data"]["outcomes"]["fs"][0]:
                check_fs_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["fs"][0]["id"],
                                              f"{kafka_message['data']['ocid']}-FS-*")
        except KeyError:
            raise KeyError('KeyError: id')
        try:
            if "X-TOKEN" in kafka_message["data"]["outcomes"]["fs"][0]:
                check_fs_token = is_it_uuid(kafka_message["data"]["outcomes"]["fs"][0]["X-TOKEN"], 4)
        except KeyError:
            raise KeyError('KeyError: X-TOKEN')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and \
                check_fs_id is True and check_fs_token is True:
            return True
        else:
            return False

    @staticmethod
    def update_fs_message_is_successful(environment, kafka_message, ei_ocid, fs_id):
        budget_url = None
        if environment == "dev":
            budget_url = "http://dev.public.eprocurement.systems/budgets/"
        if environment == "sandbox":
            budget_url = "http://public.eprocurement.systems/budgets/"

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            if "ocid" in kafka_message["data"]:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{fs_id}")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{budget_url}{ei_ocid}/{fs_id}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            return True
        else:
            return False

    @staticmethod
    def create_pn_message_is_successful(environment, kafka_message):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders/"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders/"

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None
        check_pn_id = None
        check_pn_token = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            if "ocid" in kafka_message["data"]:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{tender_url}{kafka_message['data']['ocid']}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if "id" in kafka_message["data"]["outcomes"]["pn"][0]:
                check_pn_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["pn"][0]["id"],
                                              f"{kafka_message['data']['ocid']}-PN-*")
        except KeyError:
            raise KeyError('KeyError: id')
        try:
            if "X-TOKEN" in kafka_message["data"]["outcomes"]["pn"][0]:
                check_pn_token = is_it_uuid(kafka_message["data"]["outcomes"]["pn"][0]["X-TOKEN"], 4)
        except KeyError:
            raise KeyError('KeyError: X-TOKEN')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and \
                check_pn_id is True and check_pn_token is True:
            return True
        else:
            return False

    @staticmethod
    def update_pn_message_is_successful(environment, kafka_message, pn_ocid, pn_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders/"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders/"

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            if "ocid" in kafka_message["data"]:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{pn_id}")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{tender_url}{pn_ocid}/{pn_id}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            return True
        else:
            return False

    @staticmethod
    def cancel_pn_message_is_successful(environment, kafka_message, pn_ocid):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders/"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders/"

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            if "ocid" in kafka_message["data"]:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{pn_ocid}")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{tender_url}{pn_ocid}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            return True
        else:
            return False

    @staticmethod
    def create_cnonpn_message_is_successful(environment, kafka_message, pn_ocid):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders/"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders/"

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None
        check_ev_id = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            if "ocid" in kafka_message["data"]:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{pn_ocid}")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{tender_url}{pn_ocid}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if "id" in kafka_message["data"]["outcomes"]["ev"][0]:
                check_ev_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["ev"][0]["id"],
                                              f"{kafka_message['data']['ocid']}-EV-*")
        except KeyError:
            raise KeyError('KeyError: id')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and check_ev_id is True:
            return True
        else:
            return False

    @staticmethod
    def update_cnonpn_message_is_successful(environment, kafka_message, pn_ocid, ev_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders/"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders/"

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None
        check_id = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            if "ocid" in kafka_message["data"]:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{ev_id}")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{tender_url}{pn_ocid}/{ev_id}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if "id" in kafka_message["data"]["outcomes"]["amendments"][0]:
                check_id = is_it_uuid(kafka_message["data"]["outcomes"]["amendments"][0]["id"], 4)
        except KeyError:
            raise KeyError('KeyError: id')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and check_id is True:
            return True
        else:
            return False
