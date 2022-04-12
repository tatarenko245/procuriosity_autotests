import fnmatch

from tests.utils.functions_collection.functions import is_it_uuid


class UpdateApMessage:
    def __init__(self, environment, actual_message, ap_cpid, ap_ocid, testMode=False):

        self.__environment = environment
        self.__actual_message = actual_message
        self.__ap_cpid = ap_cpid
        self.__ap_ocid = ap_ocid
        self.__testMode = testMode

        if environment == "dev":
            self.tender_url = "http://dev.public.eprocurement.systems/tenders"
        elif environment == "sandbox":
            self.tender_url = "http://public.eprocurement.systems/tenders"

        self.__message = {
            "X-OPERATION-ID": "",
            "X-RESPONSE-ID": "",
            "initiator": "",
            "data": {
                "ocid": "",
                "url": "",
                "operationDate": ""
            }
        }

    def build_expected_message_for_updateAp_process(self):
        if "X-OPERATION-ID" in self.__actual_message:
            is_operation_id_correct = is_it_uuid(self.__actual_message['X-OPERATION-ID'])

            if is_operation_id_correct is True:
                self.__message['X-OPERATION-ID'] = self.__actual_message['X-OPERATION-ID']
            else:
                raise ValueError("The message of UpdateAp process is not correct: "
                                 "'X-OPERATION-ID' must be uuid.")
        else:
            raise KeyError("The message of UpdateAp process is not correct: mismatch key 'X-OPERATION-ID'.")

        if "X-RESPONSE-ID" in self.__actual_message:
            is_process_id_correct = is_it_uuid(self.__actual_message['X-RESPONSE-ID'])

            if is_process_id_correct is True:
                self.__message['X-RESPONSE-ID'] = self.__actual_message['X-RESPONSE-ID']
            else:
                raise ValueError("The message of UpdateAp process is not correct: 'X-RESPONSE-ID' must be uuid.")
        else:
            raise KeyError("The message of UpdateAp process is not correct: mismatch key 'X-RESPONSE-ID'.")

        if "initiator" in self.__actual_message:
            self.__message['initiator'] = "platform"
        else:
            raise KeyError("The message of UpdateAp process is not correct: mismatch key 'initiator'.")

        if "ocid" in self.__actual_message['data']:
            self.__message['data']['ocid'] = self.__ap_ocid
        else:
            raise KeyError("The message of UpdateAp process is not correct: mismatch key 'data.ocid'.")

        if "url" in self.__actual_message['data']:
            self.__message['data']['url'] = f"{self.tender_url}/{self.__ap_cpid}/{self.__ap_ocid}"
        else:
            raise KeyError("The message of UpdateAp process is not correct: mismatch key 'data.url'.")

        if "operationDate" in self.__actual_message['data']:
            is_date_correct = fnmatch.fnmatch(self.__actual_message["data"]["operationDate"], "202*-*-*T*:*:*Z")

            if is_date_correct is True:
                self.__message['data']['operationDate'] = self.__actual_message['data']['operationDate']
            else:
                raise ValueError("The message of UpdateAp process is not correct: 'data.operationDate'.")
        else:
            raise KeyError("The message of UpdateAp process is not correct: mismatch key 'data.operationDate'.")

        return self.__message
