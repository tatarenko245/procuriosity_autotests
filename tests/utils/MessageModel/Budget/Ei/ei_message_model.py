import copy
import fnmatch

from tests.utils.MessageModel.Budget.Ei.ei_message_library import MessageLibrary
from tests.utils.functions import is_it_uuid


class ExpectedMessageModel:
    def __init__(self, environment, actual_message, quantity_of_requests=1, test_mode=False):
        self.environment = environment
        self.actual_message = actual_message
        self.test_mode = test_mode
        self.quantity_of_requests = quantity_of_requests
        self.constructor = copy.deepcopy(MessageLibrary())

        if environment == "dev":
            self.budget_url = "http://dev.public.eprocurement.systems/budgets/"
        elif environment == "sandbox":
            self.budget_url = "http://public.eprocurement.systems/budgets/"

    def create_message_of_create_ei_process(self):
        message = self.constructor.ei_message_model()

        if "X-OPERATION-ID" in self.actual_message:
            is_operation_id_correct = is_it_uuid(self.actual_message['X-OPERATION-ID'])

            if is_operation_id_correct is True:
                message['X-OPERATION-ID'] = self.actual_message['X-OPERATION-ID']
            else:
                raise ValueError("The message of CreateEi process is not correct: 'X-OPERATION-ID' must be uuid.")
        else:
            raise KeyError("The message of CreateEi process is not correct: mismatch key 'X-OPERATION-ID'.")

        if "X-RESPONSE-ID" in self.actual_message:
            is_process_id_correct = is_it_uuid(self.actual_message['X-RESPONSE-ID'])

            if is_process_id_correct is True:
                message['X-RESPONSE-ID'] = self.actual_message['X-RESPONSE-ID']
            else:
                raise ValueError("The message of CreateEi process is not correct: 'X-RESPONSE-ID' must be uuid.")
        else:
            raise KeyError("The message of CreateEi process is not correct: mismatch key 'X-RESPONSE-ID'.")

        if "initiator" in self.actual_message:
            message['initiator'] = "platform"
        else:
            raise KeyError("The message of CreateEi process is not correct: mismatch key 'initiator'.")

        if "ocid" in self.actual_message['data']:
            if self.test_mode is False:
                is_ocid_correct = fnmatch.fnmatch(self.actual_message["data"]["ocid"], "ocds-t1s2t3-MD-*")
            else:
                is_ocid_correct = fnmatch.fnmatch(self.actual_message["data"]["ocid"], "test-t1s2t3-MD-*")

            if is_ocid_correct is True:
                message['data']['ocid'] = self.actual_message['data']['ocid']
            else:
                raise ValueError("The message of CreateEi process is not correct: 'data.ocid'.")
        else:
            raise KeyError("The message of CreateEi process is not correct: mismatch key 'data.ocid'.")

        if "url" in self.actual_message['data']:
            message['data']['url'] = f"{self.budget_url}{message['data']['ocid']}"
        else:
            raise KeyError("The message of CreateEi process is not correct: mismatch key 'data.url'.")

        if "operationDate" in self.actual_message['data']:
            is_date_correct = fnmatch.fnmatch(self.actual_message["data"]["operationDate"], "202*-*-*T*:*:*Z")

            if is_date_correct is True:
                message['data']['operationDate'] = self.actual_message['data']['operationDate']
            else:
                raise ValueError("The message of CreateEi process is not correct: 'data.operationDate'.")
        else:
            raise KeyError("The message of CreateEi process is not correct: mismatch key 'data.operationDate'.")

        message['outcomes']['ei'] = list()
        for obj in range(len(self.quantity_of_requests)):
            message['outcomes']['ei'].append(self.constructor.ei_message_model_outcomes_ei_object())

            is_ei_id_correct = fnmatch.fnmatch(
                self.actual_message["data"]["outcomes"]["ei"][obj]["id"], "ocds-t1s2t3-MD-*")

            is_ei_token_correct = is_it_uuid(self.actual_message["data"]["outcomes"]["ei"][obj]["X-TOKEN"])

            if is_ei_id_correct is True:
                message['outcomes']['ei'][obj]['id'] = self.actual_message["data"]["outcomes"]["ei"][obj]["id"]
            else:
                raise ValueError("The message of CreateEi process is not correct: 'data.outcomes.ei.id'.")

            if is_ei_token_correct is True:
                message['outcomes']['ei'][obj]['X-TOKEN'] = \
                    self.actual_message["data"]["outcomes"]["ei"][obj]["X-TOKEN"]
            else:
                raise ValueError("The message of CreateEi process is not correct: 'data.outcomes.ei.id'.")
        return message
