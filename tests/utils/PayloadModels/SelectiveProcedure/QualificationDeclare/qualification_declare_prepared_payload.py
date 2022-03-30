import copy
import random
import uuid

from tests.utils.PayloadModels.SelectiveProcedure.QualificationDeclare.qualification_declare_library import \
    PayloadLibrary
from tests.utils.data_of_enum import person_title_tuple, business_function_type_for_declare_tuple
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class DeclarePreparePayload:
    def __init__(self, host_for_services):
        self.constructor = copy.deepcopy(PayloadLibrary())
        self.old_date = Date().old_period()[0]
        document_one = Document(host=host_for_services, file_name="API.pdf")
        self.document_one_was_uploaded = document_one.uploading_document()

    def create_declare_new_person_obligatory_data_model(self, tenderer_id, requirement_id, value=True):
        payload = {
            "requirementResponse": {}
        }
        payload['requirementResponse'].update(self.constructor.requirement_response_object())
        del payload['requirementResponse']['responder']['identifier']['uri']

        payload['requirementResponse']['id'] = str(uuid.uuid4())
        payload['requirementResponse']['value'] = value
        payload['requirementResponse']['relatedTenderer']['id'] = tenderer_id
        payload['requirementResponse']['responder']['title'] = random.choice(person_title_tuple)
        payload['requirementResponse']['responder']['name'] = "responder.name"
        payload['requirementResponse']['responder']['identifier']['id'] = "responder.identifier.id"
        payload['requirementResponse']['responder']['identifier']['scheme'] = "MD-IDNO"

        payload['requirementResponse']['responder']['businessFunctions'] = [{}]
        payload['requirementResponse']['responder']['businessFunctions'][0].update(
            self.constructor.requirement_response_business_functions_object())
        del payload['requirementResponse']['responder']['businessFunctions'][0]['documents']

        payload['requirementResponse']['responder']['businessFunctions'][0]['id'] = \
            "responder.businessFunctions.id"
        payload['requirementResponse']['responder']['businessFunctions'][0]['type'] = \
            random.choice(business_function_type_for_declare_tuple)
        payload['requirementResponse']['responder']['businessFunctions'][0]['jobTitle'] = \
            "responder.businessFunctions.jobTitle"
        payload['requirementResponse']['responder']['businessFunctions'][0]['period'][
            'startDate'] = self.old_date

        payload['requirementResponse']['requirement']['id'] = requirement_id
        return payload
