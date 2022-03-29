import copy
import random

from tests.conftest import GlobalClassMetadata
from tests.utils.PayloadModel.OpenProcedure.EvaluateAward.evaluate_award_library import PayloadLibrary
from tests.utils.data_of_enum import documentType_for_evaluate_award
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class EvaluateAwardPreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())
        self.old_date = Date().old_period()[0]
        document_one = Document(host=GlobalClassMetadata.host_for_services, file_name="API.pdf")
        self.document_one_was_uploaded = document_one.uploading_document()

    def create_evaluate_award_full_data_model(self, award_status_details, based_stage_release):
        payload = {
            "award": {}
        }
        payload['award'].update(self.constructor.award_object())
        payload['award']['documents'].append(self.constructor.award_document_object())

        payload['award']['statusDetails'] = award_status_details
        payload['award']['description'] = "evaluate award: award.description"
        payload['award']['documents'][0]['documentType'] = f"{random.choice(documentType_for_evaluate_award)}"
        payload['award']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['award']['documents'][0]['title'] = "evaluate award: award.documents.title"
        payload['award']['documents'][0]['description'] = "evaluate award: award.documents.description"
        payload['award']['documents'][0]['relatedLots'] = \
            [based_stage_release['releases'][0]['tender']['lots'][0]['id']]

        return payload

    def create_evaluate_award_obligatory_data_model_with_obligatory_documents(
            self, award_status_details):
        payload = {
            "award": {}
        }
        payload['award'].update(self.constructor.award_object())
        payload['award']['documents'].append(self.constructor.award_document_object())
        del payload['award']['documents'][0]['description']
        del payload['award']['documents'][0]['relatedLots']

        payload['award']['statusDetails'] = award_status_details
        payload['award']['documents'][0]['documentType'] = f"{random.choice(documentType_for_evaluate_award)}"
        payload['award']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['award']['documents'][0]['title'] = "evaluate award: award.documents.title"

        return payload

    def create_evaluate_award_obligatory_data_model(
            self, award_status_details):
        payload = {
            "award": {}
        }
        payload.update(self.constructor.award_object())

        payload['award']['statusDetails'] = award_status_details

        return payload
