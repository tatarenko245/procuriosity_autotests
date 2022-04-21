""" Prepare expected message for platform, the Framework Establishment process of Framework Agreement procedure."""
import copy
import fnmatch

from tests.utils.functions_collection.functions import is_it_uuid


class FrameworkEstablishmentMessage:
    """ Class creates instance of message for platform."""

    def __init__(self, environment, actual_message, expected_quantity_of_outcomes_ap=1, testMode=False):
        self.__environment = environment
        self.__actual_message = actual_message
        self.__testMode = testMode
        self.__expected_quantity_of_outcomes_fe = expected_quantity_of_outcomes_ap

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
                "operationDate": "",
                "outcomes": {
                    "fe": [
                        {
                            "id": ""
                        }
                    ]
                }
            }
        }

    def build_expected_message(self):
        """ Build message."""

        if "X-OPERATION-ID" in self.__actual_message:
            is_operation_id_correct = is_it_uuid(self.__actual_message['X-OPERATION-ID'])

            if is_operation_id_correct is True:
                self.__message['X-OPERATION-ID'] = self.__actual_message['X-OPERATION-ID']
            else:
                raise ValueError("The message is not correct: 'X-OPERATION-ID' must be uuid.")
        else:
            raise KeyError("The message is not correct: mismatch key 'X-OPERATION-ID'.")

        if "X-RESPONSE-ID" in self.__actual_message:
            is_process_id_correct = is_it_uuid(self.__actual_message['X-RESPONSE-ID'])

            if is_process_id_correct is True:
                self.__message['X-RESPONSE-ID'] = self.__actual_message['X-RESPONSE-ID']
            else:
                raise ValueError("The message is not correct: 'X-RESPONSE-ID' must be uuid.")
        else:
            raise KeyError("The message is not correct: mismatch key 'X-RESPONSE-ID'.")

        if "initiator" in self.__actual_message:
            self.__message['initiator'] = "platform"
        else:
            raise KeyError("The message is not correct: mismatch key 'initiator'.")

        if "ocid" in self.__actual_message['data']:
            if self.__testMode is False:
                is_ocid_correct = fnmatch.fnmatch(self.__actual_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
            else:
                is_ocid_correct = fnmatch.fnmatch(self.__actual_message["data"]["ocid"], "test-t1s2t3-MD-*")

            if is_ocid_correct is True:
                self.__message['data']['ocid'] = self.__actual_message['data']['ocid']
            else:
                raise ValueError("The message is not correct: 'data.ocid'.")
        else:
            raise KeyError("The message is not correct: mismatch key 'data.ocid'.")

        if "url" in self.__actual_message['data']:
            self.__message['data']['url'] = f"{self.tender_url}/{self.__message['data']['ocid']}"
        else:
            raise KeyError("The message is not correct: mismatch key 'data.url'.")

        if "operationDate" in self.__actual_message['data']:
            is_date_correct = fnmatch.fnmatch(self.__actual_message["data"]["operationDate"], "202*-*-*T*:*:*Z")

            if is_date_correct is True:
                self.__message['data']['operationDate'] = self.__actual_message['data']['operationDate']
            else:
                raise ValueError("The message is not correct: 'data.operationDate'.")
        else:
            raise KeyError("The message is not correct: mismatch key 'data.operationDate'.")

        outcomes_fe_array = list()
        for obj in range(self.__expected_quantity_of_outcomes_fe):
            outcomes_fe_array.append(copy.deepcopy(self.__message['data']['outcomes']['fe'][0]))

            if self.__testMode is False:
                is_fe_id_correct = fnmatch.fnmatch(
                    self.__actual_message["data"]["outcomes"]["fe"][obj]["id"], "ocds-t1s2t3-MD-*-FE-*"
                )
            else:
                is_fe_id_correct = fnmatch.fnmatch(
                    self.__actual_message["data"]["outcomes"]["fe"][obj]["id"], "test-t1s2t3-MD-*-FE-*"
                )

            if is_fe_id_correct is True:
                outcomes_fe_array[obj]['id'] = self.__actual_message["data"]["outcomes"]["fe"][obj]["id"]
            else:
                raise ValueError("The message of AP_release process is not correct: 'data.outcomes.fe.id'.")

        self.__message['data']['outcomes']['fe'] = outcomes_fe_array
        return self.__message
