import copy
from tests.utils.PayloadModels.SelectiveProcedure.Qualification.qualification_library import PayloadLibrary
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class QualificationPreparePayload:
    def __init__(self, host_for_services):
        self.constructor = copy.deepcopy(PayloadLibrary())
        self.old_date = Date().old_period()[0]
        document_one = Document(host=host_for_services, file_name="API.pdf")
        self.document_one_was_uploaded = document_one.uploading_document()

    def create_qualification_obligatory_data_model(self, status):
        payload = {
            "qualification": {}
        }
        payload['qualification'].update(self.constructor.qualification_object())
        del payload['qualification']['internalId']
        del payload['qualification']['description']
        del payload['qualification']['documents']

        payload['qualification']['statusDetails'] = status

        return payload
