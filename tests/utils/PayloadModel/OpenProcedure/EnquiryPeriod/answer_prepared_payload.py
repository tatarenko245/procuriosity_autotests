import copy

from tests.utils.PayloadModel.OpenProcedure.EnquiryPeriod.answer_payload_library import PayloadLibrary


class AnswerPreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())

    def create_answer_full_data_model(self):
        payload = {}

        try:
            """
            Update payload dictionary.
            """
            payload.update(self.constructor.answer_object())
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

        payload['enquiry']['answer'] = "create answer: enquiry.answer"
        return payload
