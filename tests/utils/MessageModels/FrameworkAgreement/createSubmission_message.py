""" Prepare expected message for platform, the Create Submission process of Framework Agreement procedure."""
import copy
import fnmatch

from tests.utils.functions_collection.functions import is_it_uuid


class CreateSubmissionMessage:
    """ Class creates instance of message for platform."""

    def __init__(self, environment, actual_message, ap_cpid, fe_ocid, expected_quantity_of_outcomes_submission=1,
                 test_mode=False):

        self.__environment = environment
        self.__actual_message = actual_message
        self.__cpid = ap_cpid
        self.__ocid = fe_ocid
        self.__test_mode = test_mode
        self.__expected_quantity_of_outcomes_submission = expected_quantity_of_outcomes_submission

        if environment == "dev":
            self.tender_url = "http://dev.public.eprocurement.systems/tenders"
        elif environment == "sandbox":
            self.tender_url = "http://public.eprocurement.systems/tenders"

        self.__message = {
            "X-RESPONSE-ID": "",
            "X-OPERATION-ID": "",
            "initiator": "",
            "data": {
                "ocid": "",
                "url": "",
                "operationDate": "",
                "outcomes": {
                    "submissions": [
                        {
                            "id": "",
                            "X-TOKEN": ""
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
            if self.__test_mode is False:
                is_ocid_correct = fnmatch.fnmatch(self.__actual_message["data"]["ocid"], self.__ocid)
            else:
                is_ocid_correct = fnmatch.fnmatch(self.__actual_message["data"]["ocid"], self.__ocid)

            if is_ocid_correct is True:
                self.__message['data']['ocid'] = self.__actual_message['data']['ocid']
            else:
                raise ValueError("The message is not correct: 'data.ocid'.")
        else:
            raise KeyError("The message is not correct: mismatch key 'data.ocid'.")

        if "url" in self.__actual_message['data']:
            self.__message['data']['url'] = f"{self.tender_url}/{self.__cpid}/{self.__ocid}"
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

        outcomes_submissions_array = list()
        for obj in range(self.__expected_quantity_of_outcomes_submission):
            outcomes_submissions_array.append(copy.deepcopy(self.__message['data']['outcomes']['submissions'][0]))

            is_submission_id_correct = is_it_uuid(self.__actual_message["data"]["outcomes"]["submissions"][obj]["id"])

            if is_submission_id_correct is True:

                outcomes_submissions_array[obj]['id'] = \
                    self.__actual_message["data"]["outcomes"]["submissions"][obj]["id"]
            else:
                raise ValueError(f"The message is not correct: 'data.outcomes.submissions[{obj}].id'.")

            is_submission_token_correct = is_it_uuid(
                self.__actual_message["data"]["outcomes"]["submissions"][obj]["X-TOKEN"]
            )

            if is_submission_token_correct is True:

                outcomes_submissions_array[obj]['X-TOKEN'] = \
                    self.__actual_message["data"]["outcomes"]["submissions"][obj]["X-TOKEN"]
            else:
                raise ValueError(f"The message is not correct: 'data.outcomes.submissions[{obj}].X-TOKEN'.")

        self.__message['data']['outcomes']['submissions'] = outcomes_submissions_array
        return self.__message
