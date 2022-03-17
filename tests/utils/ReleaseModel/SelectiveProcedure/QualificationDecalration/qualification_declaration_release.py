from tests.utils.functions import check_uuid_version


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
                            check_uuid_version(
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

    def prepare_expected_parties_new_person_object(self, actual_ms_release):
        person_object_id = \
            f"{self.qualification_declaration_payload['requirementResponse']['responder']['identifier']['scheme']}-" \
            f"{self.qualification_declaration_payload['requirementResponse']['responder']['identifier']['id']}"

        person_permanent_id_list = list()
        try:
            for p in actual_ms_release['releases'][0]['parties']:
                if p['roles'][0] == "procuringEntity":
                    for p_1 in p['persones']:
                        if p_1['id'] == person_object_id:
                            if "businessFunctions" in p_1:
                                for p_2 in p_1['businessFunctions']:
                                    check = check_uuid_version(
                                        uuid_to_test=p_2['id'],
                                        version=4
                                    )
                                    if check is True:
                                        d = {
                                            "business_func_id": p_2['id'],
                                            "value": p_2
                                        }
                                        person_permanent_id_list.append(d)

        except ValueError:
            raise ValueError("Check your actual_ms_release['releases'][0]['parties']["
                             "*]['businessFunctions'][*]['id;]: id must be uuid version 4")

        person_object = {
            "id": person_object_id,
            "title": self.qualification_declaration_payload['requirementResponse']['responder']['title'],
            "name": self.qualification_declaration_payload['requirementResponse']['responder']['name'],
            "identifier": {
                "scheme": self.qualification_declaration_payload['requirementResponse']['responder']['identifier'][
                    'scheme'],
                "id": self.qualification_declaration_payload['requirementResponse']['responder']['identifier']['id']
            },
            "businessFunctions": self.qualification_declaration_payload['requirementResponse']['responder'][
                'businessFunctions']
        }

        for a in range(len(person_permanent_id_list)):
            for b in range(len(person_object['businessFunctions'])):
                if person_object['businessFunctions'][b]['type'] == person_permanent_id_list[a]['value']['type'] and \
                        person_object['businessFunctions'][b]['jobTitle'] == person_permanent_id_list[a]['value'][
                    'jobTitle'] and person_object['businessFunctions'][b]['period']['startDate'] == \
                        person_permanent_id_list[a]['value']['period']['startDate']:
                    person_object['businessFunctions'][b]['id'] = person_permanent_id_list[a]['business_func_id']
        return person_object
