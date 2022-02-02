from tests.utils.functions import is_it_uuid
from tests.utils.services.e_mdm_service import MdmService


class QualificationDeclarationRelease:
    def __init__(self, qualification_id, tenderer_id, qualification_declaration_payload):
        self.qualification_id = qualification_id
        self.tenderer_id = tenderer_id
        self.qualification_declaration_payload = qualification_declaration_payload

    def prepare_qualifications_requirement_response_mapper(self, actual_tp_release):
        requirement_response_mapper = None
        for qualification in actual_tp_release['releases'][0]['qualifications']:
            if qualification['id'] == self.qualification_id:
                for response in qualification['requirementResponses']:
                    if response['relatedTenderer']['id'] == self.tenderer_id:

                        try:
                            is_it_uuid(
                                uuid_to_test=response['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your actual_tp_release['releases'][0]['qualification']["
                                             "'requirementResponses']: id must be uuid version 4")

                        responder_scheme = self.qualification_declaration_payload[
                            'requirementResponse']['responder']['identifier']['scheme']

                        responder_id = self.qualification_declaration_payload[
                            'requirementResponse']['responder']['identifier']['id']

                        requirement_response_array = {
                            "id": response['id'],
                            "value": self.qualification_declaration_payload['requirementResponse']['value'],
                            "requirement": {
                                "id": self.qualification_declaration_payload['requirementResponse']['requirement']['id']
                            },
                            "responder": {
                                "id": f"{responder_scheme}-{responder_id}",
                                "name": self.qualification_declaration_payload[
                                    'requirementResponse']['responder']['name']
                            },
                            "relatedTenderer": {
                                "id": self.tenderer_id
                            }
                        }

                        requirement_response_mapper = {
                            "qualification_id": self.qualification_id,
                            "requirement_response": requirement_response_array
                        }
        return requirement_response_mapper

    def prepare_expected_parties_persones_object(self, actual_ms_release):
        persones_object = {
            "id": "MD-IDNO-responder.identifier.id",
            "title": "Mr.",
            "name": "responder.name",
            "identifier": {
                "scheme": "MD-IDNO",
                "id": "responder.identifier.id"
            },
            "businessFunctions": [{
                "id": "c4707d95-baae-4a36-b235-2c0f9304e922",
                "type": "priceEvaluator",
                "jobTitle": "responder.businessFunctions.jobTitle",
                "period": {
                    "startDate": "2021-02-01T19:58:08Z"
                }
            }, {
                "id": "f58140d6-791c-4e81-a62c-263799d888e9",
                "type": "contactPoint",
                "jobTitle": "responder.businessFunctions.jobTitle",
                "period": {
                    "startDate": "2021-02-01T19:58:11Z"
                }
            }, {
                "id": "087acf91-ee41-433e-a432-8ec0a3b65668",
                "type": "chairman",
                "jobTitle": "responder.businessFunctions.jobTitle",
                "period": {
                    "startDate": "2021-02-01T19:58:13Z"
                }
            }]
        }
        return
