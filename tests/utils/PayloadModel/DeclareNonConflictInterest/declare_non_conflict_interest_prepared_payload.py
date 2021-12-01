import copy

from tests.utils.PayloadModel.DeclareNonConflictInterest.declare_non_conflict_interest_library import PayloadLibrary


class DeclarePreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())

    def create_declare_old_person_full_data_model(self):
        payload = {
            "requirementResponses": {}
        }
        payload['requirementResponses'].update(self.constructor.requirement_response_object())
        payload['requirementResponses']['businessFunctions'].append(
            self.constructor.requirement_response_business_functions_object())
        payload['requirementResponses']['businessFunctions']['documents'].append(
            self.constructor.business_functions_documents_object()
        )

        payload['requirementResponses']['id'] = "declare: requirementResponses.id"
        payload['requirementResponses']['value'] = True
        payload['requirementResponses']['relatedTenderer']['id']