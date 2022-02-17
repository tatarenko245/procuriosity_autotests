import datetime
import fnmatch
import time
import allure
import requests
from tests.utils.functions import is_it_uuid, get_project_root


class KafkaMessage:
    def __init__(self, operation_id=None, ocid=None, initiation="initiator"):
        self.operation_id = operation_id
        self.ocid = ocid
        self.initiation = initiation

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

                    if str(kafka_message) == str([]):
                        with allure.step('Receive message in feed-point'):
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = kafka_message.py -> \n" \
                                          f"Class = KafkaMessage -> \n" \
                                          f"Method = get_message_from_kafka -> \n" \
                                          f"Message: Could not get message: {kafka_message}.\n" \
                                          f"Check message into Kafka topic.\n" \
                                          f"Probably, there is an error.\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            assert str(kafka_message) != str([])

                    del kafka_message['_id']
                    return kafka_message
            print('The message was not found in Kafka topic')

        if kafka_message.status_code == 200:
            kafka_message = requests.get(
                url=kafka_host + '/x-operation-id/' + self.operation_id
            ).json()

            if str(kafka_message) == str([]):
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = get_message_from_kafka -> \n" \
                              f"Message: Could not get message: {kafka_message}.\n" \
                              f"Check message into Kafka topic.\n" \
                              f"Probably, there is an error.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                assert str(kafka_message) != str([])
        del kafka_message['_id']
        return kafka_message

    def get_message_from_kafka_by_ocid_and_initiator(self):
        time.sleep(5)
        kafka_host = 'http://82.144.223.29:5000'
        url = f"{kafka_host}/ocid/{self.ocid}/{self.initiation}"
        kafka_message = requests.get(
            url=url
        )
        if kafka_message.status_code == 404:
            date = datetime.datetime.now()
            date_new = datetime.datetime.now() + datetime.timedelta(seconds=15)

            while date < date_new:
                kafka_message = requests.get(
                    url=url
                )
                date = datetime.datetime.now()
                if kafka_message.status_code == 200:
                    kafka_message = requests.get(
                        url=url
                    ).json()
                    if str(kafka_message) == str([]):
                        log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                      f"File = kafka_message.py -> \n" \
                                      f"Class = KafkaMessage -> \n" \
                                      f"Method = get_message_from_kafka_by_ocid_and_initiator -> \n" \
                                      f"Message: Could not get message: {kafka_message}.\n" \
                                      f"Check message into Kafka topic.\n" \
                                      f"Probably, there is an error.\n"
                        with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                            logfile.write(log_msg_one)
                        print(f"\n{datetime.datetime.now()}\n"
                              f"File = kafka_message.py -> \n"
                              f"Class = KafkaMessage -> \n"
                              f"Method = get_message_from_kafka_by_ocid_and_initiator -> \n"
                              f"Message: Could not get message: {kafka_message}.\n"
                              f"Check message into Kafka topic.\n"
                              f"Probably, there is an error.\n")
                        assert str(kafka_message) != str([])

                    for i in kafka_message:
                        del i['_id']
                    return kafka_message
            print('The message was not found in Kafka topic')

        if kafka_message.status_code == 200:
            kafka_message = requests.get(
                url=url
            ).json()
            if str(kafka_message) == str([]):
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = get_message_from_kafka_by_ocid_and_initiator -> \n" \
                              f"Message: Could not get message: {kafka_message}.\n" \
                              f"Check message into Kafka topic.\n" \
                              f"Probably, there is an error.\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                print(f"\n{datetime.datetime.now()}\n"
                      f"File = kafka_message.py -> \n"
                      f"Class = KafkaMessage -> \n"
                      f"Method = get_message_from_kafka_by_ocid_and_initiator -> \n"
                      f"Message: Could not get message: {kafka_message}.\n"
                      f"Check message into Kafka topic.\n"
                      f"Probably, there is an error.\n")
                assert str(kafka_message) != str([])
        for i in kafka_message:
            del i['_id']
        return kafka_message

    @staticmethod
    def create_ei_message_is_successful(environment, kafka_message, test_mode=False):
        budget_url = None
        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_url = None
        check_operation_date = None
        check_ei_token = None

        if environment == "dev":
            budget_url = "http://dev.public.eprocurement.systems/budgets/"
        if environment == "sandbox":
            budget_url = "http://public.eprocurement.systems/budgets/"

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
            if test_mode is False:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
            else:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "test-t1s2t3-MD-*")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
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
            if test_mode is False:
                check_ei_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["ei"][0]["id"], "ocds-t1s2t3-MD-*")
            else:
                check_ei_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["ei"][0]["id"], "test-t1s2t3-MD-*")

            if check_ei_id is True:
                pass
            else:
                raise Exception("check_ei_id is False")
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
    def update_ei_message_is_successful(environment, kafka_message, ei_ocid, test_mode=False):
        budget_url = None
        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_url = None
        check_operation_date = None

        if environment == "dev":
            budget_url = "http://dev.public.eprocurement.systems/budgets/"
        if environment == "sandbox":
            budget_url = "http://public.eprocurement.systems/budgets/"

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
            if test_mode is False:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
            else:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "test-t1s2t3-MD-*")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
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
    def create_fs_message_is_successful(environment, kafka_message, test_mode=False):
        budget_url = None
        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_url = None
        check_operation_date = None
        check_fs_id = None
        check_fs_token = None

        if environment == "dev":
            budget_url = "http://dev.public.eprocurement.systems/budgets/"
        if environment == "sandbox":
            budget_url = "http://public.eprocurement.systems/budgets/"

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
            if test_mode is False:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
            else:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "test-t1s2t3-MD-*")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
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
    def create_pn_message_is_successful(environment, kafka_message, test_mode=False):
        tender_url = None
        check_pn_id = None
        check_pn_token = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"
        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                raise Exception("check_x_operation_id is False")
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')
        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
            if check_x_response_id is True:
                pass
            else:
                raise Exception("check_x_response_id is False")
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                raise Exception("initiator is False")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            """
            Check data.ocid into message from feed point.
            """
            if test_mode is False:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
            else:
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], "test-t1s2t3-MD-*")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
        except KeyError:
            raise KeyError('KeyError: data.ocid')
        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"], f"{tender_url}/{kafka_message['data']['ocid']}")
            if check_url is True:
                pass
            else:
                raise Exception("check_url is False")
        except KeyError:
            raise KeyError('KeyError: data.url')
        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                raise Exception("check_operation_date is False")
        except KeyError:
            raise KeyError('KeyError: data.operationDate')

        if "pn" in kafka_message['data']['outcomes']:
            for i in kafka_message['data']['outcomes']['pn']:
                for i_1 in i:
                    if i_1 == "id":
                        check_pn_id = fnmatch.fnmatch(i['id'], f"{kafka_message['data']['ocid']}-PN-*")
                        if check_pn_id is True:
                            pass
                        else:
                            raise Exception("check_pn_id is False")

                    if i_1 == "X-TOKEN":
                        check_pn_token = is_it_uuid(i["X-TOKEN"], 4)
                        if check_pn_token is True:
                            pass
                        else:
                            raise Exception("check_pn_token is False")

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and check_pn_id is True \
                and check_pn_token is True:
            pass
        else:
            return False
        return True

    @staticmethod
    def update_pn_message_is_successful(environment, kafka_message, pn_ocid, pn_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

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
                                            f"{tender_url}/{pn_ocid}/{pn_id}")
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
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

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
                                            f"{tender_url}/{pn_ocid}")
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
    def create_cnonpn_message_is_successful(environment, kafka_message, pn_ocid, pmd):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

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
                                            f"{tender_url}/{pn_ocid}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if pmd == "TEST_OT" or pmd == "TEST_SV" or pmd == "TEST_MV" or pmd == "OT" or pmd == "SV" or pmd == "MV":
                if "id" in kafka_message["data"]["outcomes"]["ev"][0]:
                    check_ev_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["ev"][0]["id"],
                                                  f"{kafka_message['data']['ocid']}-EV-*")
            elif pmd == "TEST_RT" or pmd == "TEST_GPA" or pmd == "RT" or pmd == "GPA":
                if "id" in kafka_message["data"]["outcomes"]["tp"][0]:
                    check_ev_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["tp"][0]["id"],
                                                  f"{kafka_message['data']['ocid']}-TP-*")
            elif pmd == "TEST_CD" or pmd == "TEST_DC" or pmd == "CD" or pmd == "DC" or pmd == "IP" or pmd == "TEST_IP" \
                    or pmd == "NP" or pmd == "TEST_NP":
                if "id" in kafka_message["data"]["outcomes"]["np"][0]:
                    check_ev_id = fnmatch.fnmatch(kafka_message["data"]["outcomes"]["np"][0]["id"],
                                                  f"{kafka_message['data']['ocid']}-NP-*")
            else:
                raise ValueError(f"Unknown pmd:{pmd}")
        except KeyError:
            raise KeyError('KeyError: id')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and check_ev_id is True:
            return True
        else:
            return False

    @staticmethod
    def update_cnonpn_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

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
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{tender_url}/{pn_ocid}/{tender_id}")
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

    @staticmethod
    def create_enquiry_message_initiator_bpe_is_successful(environment, kafka_message, pn_ocid, ev_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

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
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "bpe")
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
                                            f"{tender_url}/{pn_ocid}/{ev_id}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if "id" in kafka_message["data"]["outcomes"]["enquiries"][0]:
                check_id = is_it_uuid(kafka_message["data"]["outcomes"]["enquiries"][0]["id"], 4)
        except KeyError:
            raise KeyError('KeyError: id')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and check_id is True:
            return True
        else:
            return False

    @staticmethod
    def create_enquiry_message_initiator_platform_is_successful(environment, kafka_message, pn_ocid, ev_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

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
                                            f"{tender_url}/{pn_ocid}/{ev_id}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if "id" in kafka_message["data"]["outcomes"]["enquiries"][0]:
                check_id = is_it_uuid(kafka_message["data"]["outcomes"]["enquiries"][0]["id"], 4)
        except KeyError:
            raise KeyError('KeyError: id')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and check_id is True:
            return True
        else:
            return False

    @staticmethod
    def create_answer_message_is_successful(environment, kafka_message, pn_ocid, ev_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

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
                check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{ev_id}")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                            f"{tender_url}/{pn_ocid}/{ev_id}")
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
    def create_bid_message_is_successful(environment, kafka_message, pn_ocid, ev_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_oc_id = None
        check_url = None
        check_operation_date = None
        check_bid_id = None
        check_bid_token = None

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
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
                                            f"{tender_url}/{pn_ocid}/{ev_id}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if "id" in kafka_message["data"]["outcomes"]["bids"][0]:
                check_bid_id = is_it_uuid(kafka_message["data"]["outcomes"]["bids"][0]["id"], 4)
        except KeyError:
            raise KeyError('KeyError: id')
        try:
            if "X-TOKEN" in kafka_message["data"]["outcomes"]["bids"][0]:
                check_bid_token = is_it_uuid(kafka_message["data"]["outcomes"]["bids"][0]["X-TOKEN"], 4)
        except KeyError:
            raise KeyError('KeyError: token')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and check_bid_id is True \
                and check_bid_token is True:
            return True
        else:
            return False

    @staticmethod
    def withdraw_bid_message_is_successful(environment, kafka_message, pn_ocid, ev_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

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
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
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
                                            f"{tender_url}/{pn_ocid}/{ev_id}")
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
    def tender_period_end_no_auction_message_is_successful(environment, kafka_message, pn_ocid, ev_id):
        tender_url = None
        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        check_award_id = None
        check_award_token = None

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 1)
            if check_x_operation_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                              f"Actual result: check_x_operation_id = {kafka_message['X-OPERATION-ID']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual result must be UUID v.1\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_x_operation_id is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                          f"KeyError: X-OPERATION-ID\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
            if check_x_response_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                              f"Actual result: X-RESPONSE-ID = {kafka_message['X-RESPONSE-ID']} is not correct.\n" \
                              f"Expected result: actual result must be UUID v.1\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_x_response_id is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                          f"KeyError: X-RESPONSE-ID\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "bpe")
            if check_initiator is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                              f"Actual result: initiator = {kafka_message['initiator']} is not correct.\n" \
                              f"Expected result: bpe\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "initiator is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                          f"KeyError: initiator\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{ev_id}")
            if check_oc_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                              f"Actual result: data.ocid  = {kafka_message['data']['ocid']} is not correct.\n" \
                              f"Expected result: {ev_id}\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_oc_id is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                          f"KeyError: data.ocid\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{ev_id}")
            if check_url is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                              f"Actual result: data.url = {kafka_message['data']['url']} is not correct.\n" \
                              f"Expected result: {tender_url}/{pn_ocid}/{ev_id}\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_url is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                          f"KeyError: data.url\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                              f"Actual result: data.operationDate = {kafka_message['data']['operationDate']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual  result must be compared with 202*-*-*T*:*:*\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_operation_date is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                          f"KeyError: data.operationDate\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            pass
        else:
            return False

        try:
            """
            Check data.outcomes.awards into message from feed point.
            """
            for i in kafka_message["data"]["outcomes"]["awards"]:
                for i_1 in i:
                    if i_1 == "id":
                        check_award_id = is_it_uuid(i["id"], 4)
                        if check_award_id is True:
                            pass
                        else:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = kafka_message.py -> \n" \
                                          f"Class = KafkaMessage -> \n" \
                                          f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                                          f"Actual result: data.outcomes.awards.id = {i['id']} " \
                                          f"is not correct.\n" \
                                          f"Expected result: actual  result must be UUID v.4\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            return "check_award_id is False"

                    if i_1 == "X-TOKEN":
                        check_award_token = is_it_uuid(i["X-TOKEN"], 4)
                        if check_award_token is True:
                            pass
                        else:
                            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                          f"File = kafka_message.py -> \n" \
                                          f"Class = KafkaMessage -> \n" \
                                          f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                                          f"Actual result: data.outcomes.awards.token = {i['token']} " \
                                          f"is not correct.\n" \
                                          f"Expected result: actual  result must be UUID v.4\n"
                            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                logfile.write(log_msg_one)
                            return "check_award_token is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                          f"KeyError: data.outcomes.awards\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.outcomes.awards')

        if check_award_token is not None:
            if check_award_id is True and check_award_token is True:
                pass
            else:
                return False
        elif check_award_token is None:
            if check_award_id is True:
                pass
            else:
                return False
        return True

    @staticmethod
    def tender_period_end_auction_message_is_successful(environment, kafka_message, pn_ocid, ev_id):
        tender_url = None
        auction_url = None
        check_award_id = None
        check_award_token = None
        check_link_id = None
        check_url_first_part = None
        check_url_second_part = None
        check_url_third_part = None
        check_url_fourth_part = None
        check_url_fifth_part = None
        check_url_sixth_part = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
            auction_url = "http://auction.eprocurement.systems/auctions"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"
            auction_url = "https://eauction.eprocurement.systems/auctions"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 1)
            if check_x_operation_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_auction_message_is_successful -> \n" \
                              f"Actual result: check_x_operation_id = {kafka_message['X-OPERATION-ID']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual result must be UUID v.1\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_x_operation_id is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_auction_message_is_successful -> \n" \
                          f"KeyError: X-OPERATION-ID\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
            if check_x_response_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_no_auction_message_is_successful -> \n" \
                              f"Actual result: check_x_response_id = {kafka_message['X-RESPONSE-ID']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual result must be UUID v.1\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_x_response_id is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_auction_message_is_successful -> \n" \
                          f"KeyError: X-RESPONSE-ID\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "bpe")
            if check_initiator is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_auction_message_is_successful -> \n" \
                              f"Actual result: initiator = {kafka_message['initiator']} is not correct.\n" \
                              f"Expected result: bpe\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "initiator is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_auction_message_is_successful -> \n" \
                          f"KeyError: initiator\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{ev_id}")
            if check_oc_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_auction_message_is_successful -> \n" \
                              f"Actual result: data.ocid = {kafka_message['data']['ocid']} is not correct.\n" \
                              f"Expected result: {ev_id}\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_oc_id is False"
        except KeyError:
            log_msg_one = f"{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_auction_message_is_successful -> \n" \
                          f"KeyError: data.ocid\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{ev_id}")
            if check_url is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_auction_message_is_successful -> \n" \
                              f"Actual result: data.url = {kafka_message['data']['url']} is not correct.\n" \
                              f"Expected result: {tender_url}/{pn_ocid}/{ev_id}\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_url is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_auction_message_is_successful -> \n" \
                          f"KeyError: data.url\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = tender_period_end_auction_message_is_successful -> \n" \
                              f"Actual result: data.operationDate = {kafka_message['data']['operationDate']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual  result must be compared with 202*-*-*T*:*:*\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_operation_date is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_auction_message_is_successful -> \n" \
                          f"KeyError: data.operationDate\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            pass
        else:
            return False

        try:
            """
            Check kafka_message['data']['outcomes'].
            """
            if environment == "dev":
                if "links" in kafka_message['data']['outcomes']:
                    for i in kafka_message['data']['outcomes']['links']:
                        for i_1 in i:
                            if i_1 == "relatedBid":
                                check_link_id = is_it_uuid(i["relatedBid"], 4)
                                if check_link_id is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: data.outcomes.links.relatedBid = " \
                                                  f"{i['relatedBid']}" \
                                                  f"is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                            if i_1 == "url":
                                url = i['url']
                                check_url_first_part = \
                                    fnmatch.fnmatch(url[0:90], f"{auction_url}/{ev_id}")
                                if check_url_first_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_first_part = {url[0:90]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: {auction_url}{ev_id}\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_second_part = \
                                    is_it_uuid(url[91:127], 4)
                                if check_url_second_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_second_part = {url[91:127]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_third_part = \
                                    fnmatch.fnmatch(url[127:135], "?bid_id=")
                                if check_url_third_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_third_part = {url[127:135]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: ?bid_id=\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_fourth_part = \
                                    fnmatch.fnmatch(url[135:171], i['relatedBid'])
                                if check_url_fourth_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_fourth_part = {url[135:171]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: {i['relatedBid']}\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_fifth_part = \
                                    fnmatch.fnmatch(url[171:177], "&sign=")
                                if check_url_fifth_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_fifth_part = {url[171:177]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: &sign=\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_sixth_part = is_it_uuid(url[177:213], 4)
                                if check_url_sixth_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_sixth_part = {url[177:213]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False
                else:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = kafka_message.py -> \n" \
                                  f"Class = KafkaMessage -> \n" \
                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                  f"KeyError: data.outcomes.links\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)

                if "awards" in kafka_message['data']['outcomes']:
                    for i in kafka_message['data']['outcomes']['awards']:
                        for i_1 in i:
                            if i_1 == "id":
                                check_award_id = is_it_uuid(i["id"], 4)
                                if check_award_id is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_award_id = {i['id']} is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                            if i_1 == "X-TOKEN":
                                check_award_token = is_it_uuid(i["X-TOKEN"], 4)
                                if check_award_token is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_award_token = {i['X-TOKEN']} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False
                else:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = kafka_message.py -> \n" \
                                  f"Class = KafkaMessage -> \n" \
                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                  f"KeyError: data.outcomes.awards\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)

            elif environment == "sandbox":
                if "links" in kafka_message['data']['outcomes']:
                    for i in kafka_message['data']['outcomes']['links']:
                        for i_1 in i:
                            if i_1 == "relatedBid":
                                check_link_id = is_it_uuid(i["relatedBid"], 4)
                                if check_link_id is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_link_id = {i['relatedBid']} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                            if i_1 == "url":
                                url = i['url']
                                check_url_first_part = \
                                    fnmatch.fnmatch(url[0:92], f"{auction_url}/{ev_id}")
                                if check_url_first_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_first_part = {url[0:92]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: {auction_url}{ev_id}\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_second_part = \
                                    is_it_uuid(url[93:129], 4)
                                if check_url_second_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_second_part = {url[91:127]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_third_part = \
                                    fnmatch.fnmatch(url[129:137], "?bid_id=")
                                if check_url_third_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_third_part = {url[129:137]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: ?bid_id=\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_fourth_part = \
                                    fnmatch.fnmatch(url[137:173], i['relatedBid'])
                                if check_url_fourth_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_fourth_part = {url[137:173]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: {i['relatedBid']}\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_fifth_part = \
                                    fnmatch.fnmatch(url[173:179], "&sign=")
                                if check_url_fifth_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_fifth_part = {url[173:179]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: &sign=\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                                check_url_sixth_part = is_it_uuid(url[179:215], 4)
                                if check_url_sixth_part is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_url_sixth_part = {url[179:215]} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False
                else:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = kafka_message.py -> \n" \
                                  f"Class = KafkaMessage -> \n" \
                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                  f"KeyError: data.outcomes.links\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)

                if "awards" in kafka_message['data']['outcomes']:
                    for i in kafka_message['data']['outcomes']['awards']:
                        for i_1 in i:
                            if i_1 == "id":
                                check_award_id = is_it_uuid(i["id"], 4)
                                if check_award_id is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_award_id = {i['id']} is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

                            if i_1 == "X-TOKEN":
                                check_award_token = is_it_uuid(i["X-TOKEN"], 4)
                                if check_award_token is True:
                                    pass
                                else:
                                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                                  f"File = kafka_message.py -> \n" \
                                                  f"Class = KafkaMessage -> \n" \
                                                  f"Method = tender_period_end_message_is_successful -> \n" \
                                                  f"Actual result: check_award_token = {i['X-TOKEN']} " \
                                                  f"is not correct.\n" \
                                                  f"Expected result: actual result must be UUID v.4\n"
                                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                                        logfile.write(log_msg_one)
                                    return False

        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = tender_period_end_auction_message_is_successful -> \n" \
                          f"KeyError: data.outcomes\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.outcomes')

        if check_link_id is not None:
            if check_link_id is True and check_url_first_part is True and check_url_second_part is True \
                    and check_url_third_part is True and check_url_fourth_part is True \
                    and check_url_fifth_part is True and check_url_sixth_part is True:
                pass
            else:
                return False

        if check_award_id is not None:
            if check_award_token is not None:
                if check_award_id is True and check_award_token is True:
                    pass
                else:
                    return False
            elif check_award_token is None:
                if check_award_id is True:
                    pass
                else:
                    return False
        return True

    @staticmethod
    def declare_non_confl_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: check_x_operation_id = {kafka_message['X-OPERATION-ID']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual result must be UUID v.4\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_x_operation_id is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: X-OPERATION-ID\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
            if check_x_response_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: check_x_response_id = {kafka_message['X-RESPONSE-ID']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual result must be UUID v.4\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_x_response_id is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: X-RESPONSE-ID\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: initiator = {kafka_message['initiator']} is not correct.\n" \
                              f"Expected result: platform\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "initiator is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: initiator\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
            if check_oc_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: data.ocid = {kafka_message['data']['ocid']} is not correct.\n" \
                              f"Expected result: {tender_id}\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_oc_id is False"
        except KeyError:
            log_msg_one = f"{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: data.ocid\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{tender_id}")
            if check_url is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: data.url = {kafka_message['data']['url']} is not correct.\n" \
                              f"Expected result: {tender_url}/{pn_ocid}/{tender_id}\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_url is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: data.url\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: data.operationDate = {kafka_message['data']['operationDate']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual  result must be compared with 202*-*-*T*:*:*\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_operation_date is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: data.operationDate\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            pass
        else:
            return False
        return True

    @staticmethod
    def award_evaluating_message_is_successful(environment, kafka_message, pn_ocid, ev_id):
        tender_url = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: check_x_operation_id = {kafka_message['X-OPERATION-ID']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual result must be UUID v.4\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_x_operation_id is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: X-OPERATION-ID\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
            if check_x_response_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: check_x_response_id = {kafka_message['X-RESPONSE-ID']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual result must be UUID v.4\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_x_response_id is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: X-RESPONSE-ID\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: initiator = {kafka_message['initiator']} is not correct.\n" \
                              f"Expected result: platform\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "initiator is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: initiator\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{ev_id}")
            if check_oc_id is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: data.ocid = {kafka_message['data']['ocid']} is not correct.\n" \
                              f"Expected result: {ev_id}\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_oc_id is False"
        except KeyError:
            log_msg_one = f"{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: data.ocid\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{ev_id}")
            if check_url is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: data.url = {kafka_message['data']['url']} is not correct.\n" \
                              f"Expected result: {tender_url}/{pn_ocid}/{ev_id}\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_url is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: data.url\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                log_msg_one = f"\n{datetime.datetime.now()}\n" \
                              f"File = kafka_message.py -> \n" \
                              f"Class = KafkaMessage -> \n" \
                              f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                              f"Actual result: data.operationDate = {kafka_message['data']['operationDate']} " \
                              f"is not correct.\n" \
                              f"Expected result: actual  result must be compared with 202*-*-*T*:*:*\n"
                with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                    logfile.write(log_msg_one)
                return "check_operation_date is False"
        except KeyError:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = kafka_message.py -> \n" \
                          f"Class = KafkaMessage -> \n" \
                          f"Method = declare_non_conflict_interest_message_is_successful -> \n" \
                          f"KeyError: data.operationDate\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            pass
        else:
            return False
        return True

    @staticmethod
    def award_or_qualification_consideration_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                return "check_x_operation_id is False"
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
            if check_x_response_id is True:
                pass
            else:
                return "check_x_response_id is False"
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                return "initiator is False"
        except KeyError:
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
            if check_oc_id is True:
                pass
            else:
                return "check_oc_id is False"
        except KeyError:
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{tender_id}")
            if check_url is True:
                pass
            else:
                return "check_url is False"
        except KeyError:
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                return "check_operation_date is False"
        except KeyError:
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            pass
        else:
            return False
        return True

    @staticmethod
    def protocol_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                return "check_x_operation_id is False"
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 1)
            if check_x_response_id is True:
                pass
            else:
                return "check_x_response_id is False"
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                return "initiator is False"
        except KeyError:
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
            if check_oc_id is True:
                pass
            else:
                return "check_oc_id is False"
        except KeyError:
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{tender_id}")
            if check_url is True:
                pass
            else:
                return "check_url is False"
        except KeyError:
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                return "check_operation_date is False"
        except KeyError:
            raise KeyError('KeyError: data.operationDate')

        if "cans" in kafka_message['data']['outcomes']:
            for i in kafka_message['data']['outcomes']['cans']:
                for i_1 in i:
                    if i_1 == "id":
                        check_can_id = is_it_uuid(i["id"], 4)
                        if check_can_id is True:
                            pass
                        else:
                            return False

                    if i_1 == "X-TOKEN":
                        check_can_token = is_it_uuid(i["X-TOKEN"], 4)
                        if check_can_token is True:
                            pass
                        else:
                            return False

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            pass
        else:
            return False
        return True

    @staticmethod
    def create_submission_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None
        check_x_operation_id = None
        check_x_response_id = None
        check_initiator = None
        check_url = None
        check_operation_date = None
        check_submission_id = None
        check_submission_token = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            if "X-OPERATION-ID" in kafka_message:
                check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
        except KeyError:

            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            if "X-RESPONSE-ID" in kafka_message:
                check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')
        try:
            if "initiator" in kafka_message:
                check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
        except KeyError:
            raise KeyError('KeyError: initiator')
        try:
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], tender_id)
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
        except KeyError:
            raise KeyError('KeyError: ocid')
        try:
            if "url" in kafka_message["data"]:
                check_url = fnmatch.fnmatch(kafka_message["data"]["url"], f"{tender_url}/{pn_ocid}/{tender_id}")
        except KeyError:
            raise KeyError('KeyError: url')
        try:
            if "operationDate" in kafka_message["data"]:
                check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
        except KeyError:
            raise KeyError('KeyError: operationDate')
        try:
            if "id" in kafka_message["data"]["outcomes"]["submissions"][0]:
                check_submission_id = is_it_uuid(kafka_message["data"]["outcomes"]["submissions"][0]["id"], 4)
        except KeyError:
            raise KeyError('KeyError: id')
        try:
            if "X-TOKEN" in kafka_message["data"]["outcomes"]["submissions"][0]:
                check_submission_token = is_it_uuid(kafka_message["data"]["outcomes"]["submissions"][0]["X-TOKEN"], 4)
        except KeyError:
            raise KeyError('KeyError: X-TOKEN')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True and \
                check_submission_id is True and check_submission_token is True:
            return True
        else:
            return False

    @staticmethod
    def submission_period_end_no_auction_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None
        check_qualification_id = None
        check_qualification_token = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                raise Exception("check_x_operation_id is False")
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
            if check_x_response_id is True:
                pass
            else:
                raise Exception("check_x_response_id is False")
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "bpe")
            if check_initiator is True:
                pass
            else:
                raise Exception("initiator is False")
        except KeyError:
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
        except KeyError:
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{tender_id}")
            if check_url is True:
                pass
            else:
                raise Exception("check_url is False")
        except KeyError:
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                raise Exception("check_operation_date is False")
        except KeyError:
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            pass
        else:
            return False

        try:
            """
            Check data.outcomes.qualifications into message from feed point.
            """
            for i in kafka_message["data"]["outcomes"]["qualifications"]:
                for i_1 in i:
                    if i_1 == "id":
                        check_qualification_id = is_it_uuid(i["id"], 4)
                        if check_qualification_id is True:
                            pass
                        else:
                            raise Exception("check_qualification_id is False")

                    if i_1 == "X-TOKEN":
                        check_qualification_token = is_it_uuid(i["X-TOKEN"], 4)
                        if check_qualification_token is True:
                            pass
                        else:
                            raise Exception("check_qualification_token is False")
        except KeyError:
            raise KeyError('KeyError: data.outcomes.qualifications')

        if check_qualification_id is True and check_qualification_token is True:
            return True
        else:
            return False

    @staticmethod
    def qualification_process_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                raise Exception("check_x_operation_id is False")
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
            if check_x_response_id is True:
                pass
            else:
                raise Exception("check_x_response_id is False")
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                raise Exception("initiator is False")
        except KeyError:
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
        except KeyError:
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{tender_id}")
            if check_url is True:
                pass
            else:
                raise Exception("check_url is False")
        except KeyError:
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                raise Exception("check_operation_date is False")
        except KeyError:
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            return True
        else:
            return False

    @staticmethod
    def qualification_protocol_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                raise Exception("check_x_operation_id is False")
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
            if check_x_response_id is True:
                pass
            else:
                raise Exception("check_x_response_id is False")
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                raise Exception("initiator is False")
        except KeyError:
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
        except KeyError:
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{tender_id}")
            if check_url is True:
                pass
            else:
                raise Exception("check_url is False")
        except KeyError:
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                raise Exception("check_operation_date is False")
        except KeyError:
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            return True
        else:
            return False

    @staticmethod
    def withdraw_qualification_protocol_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                raise Exception("check_x_operation_id is False")
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
            if check_x_response_id is True:
                pass
            else:
                raise Exception("check_x_response_id is False")
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                raise Exception("initiator is False")
        except KeyError:
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
        except KeyError:
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{tender_id}")
            if check_url is True:
                pass
            else:
                raise Exception("check_url is False")
        except KeyError:
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                raise Exception("check_operation_date is False")
        except KeyError:
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            return True
        else:
            return False

    @staticmethod
    def apply_qualification_protocol_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                raise Exception("check_x_operation_id is False")
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
            if check_x_response_id is True:
                pass
            else:
                raise Exception("check_x_response_id is False")
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                raise Exception("initiator is False")
        except KeyError:
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
        except KeyError:
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{tender_id}")
            if check_url is True:
                pass
            else:
                raise Exception("check_url is False")
        except KeyError:
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                raise Exception("check_operation_date is False")
        except KeyError:
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            return True
        else:
            return False

    @staticmethod
    def start_second_stage_message_is_successful(environment, kafka_message, pn_ocid, tender_id):
        tender_url = None

        if environment == "dev":
            tender_url = "http://dev.public.eprocurement.systems/tenders"
        if environment == "sandbox":
            tender_url = "http://public.eprocurement.systems/tenders"

        try:
            """
            Check X-OPERATION-ID into message from feed point.
            """
            check_x_operation_id = is_it_uuid(kafka_message["X-OPERATION-ID"], 4)
            if check_x_operation_id is True:
                pass
            else:
                raise Exception("check_x_operation_id is False")
        except KeyError:
            raise KeyError('KeyError: X-OPERATION-ID')

        try:
            """
            Check X-RESPONSE-ID into message from feed point.
            """
            check_x_response_id = is_it_uuid(kafka_message["X-RESPONSE-ID"], 4)
            if check_x_response_id is True:
                pass
            else:
                raise Exception("check_x_response_id is False")
        except KeyError:
            raise KeyError('KeyError: X-RESPONSE-ID')

        try:
            """
            Check initiator into message from feed point.
            """
            check_initiator = fnmatch.fnmatch(kafka_message["initiator"], "platform")
            if check_initiator is True:
                pass
            else:
                raise Exception("initiator is False")
        except KeyError:
            raise KeyError('KeyError: initiator')

        try:
            """
            Check data.ocid into message from feed point.
            """
            check_oc_id = fnmatch.fnmatch(kafka_message["data"]["ocid"], f"{tender_id}")
            if check_oc_id is True:
                pass
            else:
                raise Exception("check_oc_id is False")
        except KeyError:
            raise KeyError('KeyError: data.ocid')

        try:
            """
            Check data.url into message from feed point.
            """
            check_url = fnmatch.fnmatch(kafka_message["data"]["url"],
                                        f"{tender_url}/{pn_ocid}/{tender_id}")
            if check_url is True:
                pass
            else:
                raise Exception("check_url is False")
        except KeyError:
            raise KeyError('KeyError: data.url')

        try:
            """
            Check data.operationDate into message from feed point.
            """
            check_operation_date = fnmatch.fnmatch(kafka_message["data"]["operationDate"], "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
            else:
                raise Exception("check_operation_date is False")
        except KeyError:
            raise KeyError('KeyError: data.operationDate')

        if check_x_operation_id is True and check_x_response_id is True and check_initiator is True and \
                check_oc_id is True and check_url is True and check_operation_date is True:
            return True
        else:
            return False
