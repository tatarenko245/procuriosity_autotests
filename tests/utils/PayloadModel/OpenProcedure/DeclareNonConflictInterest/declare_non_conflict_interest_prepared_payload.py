import copy
import random
import uuid

from tests.utils.PayloadModel.OpenProcedure.DeclareNonConflictInterest.declare_non_conflict_interest_library import PayloadLibrary
from tests.utils.data_of_enum import person_title, business_function_type_for_declare
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class DeclarePreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())
        self.old_date = Date().old_period()[0]
        document_one = Document("API.pdf")
        self.document_one_was_uploaded = document_one.uploading_document()

    def create_declare_old_person_full_data_model(self, tenderer_id, requirement_id, actual_ms_release,
                                                  req_resp_id=str(uuid.uuid4()), value=True):
        payload = {
            "requirementResponse": {}
        }
        payload['requirementResponse'].update(self.constructor.requirement_response_object())

        payload['requirementResponse']['id'] = req_resp_id
        payload['requirementResponse']['value'] = value
        for p in actual_ms_release['releases'][0]['parties']:
            for p_1 in p:
                if p_1 == "roles":
                    if p['roles'] == ['procuringEntity']:
                        list_of_persones = list()
                        for p_2 in p['persones']:
                            for p_3 in p_2:
                                if p_3 == "id":
                                    list_of_persones.append(p_2['id'])
                        if "persones" in p:
                            for x in range(len(list_of_persones)):
                                payload['requirementResponse']['relatedTenderer']['id'] = tenderer_id
                                payload['requirementResponse']['responder']['title'] = p['persones'][x]['title']
                                payload['requirementResponse']['responder']['name'] = p['persones'][x]['name']
                                payload['requirementResponse']['responder']['identifier']['id'] = p['persones'][x][
                                    'identifier']['id']
                                payload['requirementResponse']['responder']['identifier']['scheme'] = p['persones'][x][
                                    'identifier']['scheme']
                                payload['requirementResponse']['responder']['identifier']['uri'] = p['persones'][x][
                                    'identifier']['uri']

                                list_of_business_function = list()
                                for bf in p['persones'][x]['businessFunctions']:
                                    for bf_1 in bf:
                                        if bf_1 == "id":
                                            list_of_business_function.append(bf['id'])

                                for y in range(len(list_of_business_function)):
                                    payload['requirementResponse']['responder']['businessFunctions'] = [{}]
                                    payload['requirementResponse']['responder']['businessFunctions'][y].update(
                                        self.constructor.requirement_response_business_functions_object())

                                    payload['requirementResponse']['responder']['businessFunctions'][y]['id'] = \
                                        p['persones'][x]['businessFunctions'][y]['id']
                                    payload['requirementResponse']['responder']['businessFunctions'][y]['type'] = \
                                        p['persones'][x]['businessFunctions'][y]['type']
                                    payload['requirementResponse']['responder']['businessFunctions'][y]['jobTitle'] = \
                                        p['persones'][x]['businessFunctions'][y]['jobTitle']
                                    payload['requirementResponse']['responder']['businessFunctions'][y]['period'][
                                        'startDate'] = p['persones'][x]['businessFunctions'][y]['period']['startDate']

                                    list_of_business_function_documents = list()
                                    for doc in p['persones'][x]['businessFunctions'][y]['documents']:
                                        for doc_1 in doc:
                                            if doc_1 == "id":
                                                list_of_business_function_documents.append(doc['id'])

                                    for z in range(len(list_of_business_function_documents)):
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'] = [{}]
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z].update(
                                            self.constructor.business_functions_documents_object())

                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z]['id'] = p['persones'][x]['businessFunctions'][y][
                                            'documents'][z]['id']
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z]['documentType'] = p['persones'][x]['businessFunctions'][y][
                                            'documents'][z]['documentType']
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z]['title'] = p['persones'][x]['businessFunctions'][y][
                                            'documents'][z]['title']
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z]['description'] = p['persones'][x]['businessFunctions'][y][
                                            'documents'][z]['description']

        payload['requirementResponse']['requirement']['id'] = requirement_id
        return payload

    def create_declare_new_person_full_data_model(self, tenderer_id, requirement_id, number_of_iteration,
                                                  req_resp_id=str(uuid.uuid4()), value=True):
        payload = {
            "requirementResponse": {}
        }
        payload['requirementResponse'].update(self.constructor.requirement_response_object())

        payload['requirementResponse']['id'] = req_resp_id
        payload['requirementResponse']['value'] = value

        payload['requirementResponse']['relatedTenderer']['id'] = tenderer_id
        payload['requirementResponse']['responder']['title'] = f"{random.choice(person_title)}"
        payload['requirementResponse']['responder']['name'] = f"{number_of_iteration} declare new person name"
        payload['requirementResponse']['responder']['identifier'][
            'id'] = f"{number_of_iteration} declare new person responder id"
        payload['requirementResponse']['responder']['identifier']['scheme'] = "MD-IDNO"
        payload['requirementResponse']['responder']['identifier'][
            'uri'] = f"{number_of_iteration}declare new person uri"

        payload['requirementResponse']['responder']['businessFunctions'] = [{}]
        payload['requirementResponse']['responder']['businessFunctions'][0].update(
            self.constructor.requirement_response_business_functions_object())

        payload['requirementResponse']['responder']['businessFunctions'][0][
            'id'] = f"{number_of_iteration} declare new person bf id"
        payload['requirementResponse']['responder']['businessFunctions'][0][
            'type'] = f"{random.choice(business_function_type_for_declare)}"
        payload['requirementResponse']['responder']['businessFunctions'][0]['jobTitle'] = \
            f"{number_of_iteration} declare new person bf jobTitle"
        payload['requirementResponse']['responder']['businessFunctions'][0]['period'][
            'startDate'] = self.old_date

        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'] = [{}]
        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'][0].update(self.constructor.business_functions_documents_object())

        payload['requirementResponse']['responder']['businessFunctions'][0]['documents'][0]['id'] = \
            self.document_one_was_uploaded[0]["data"]["id"]
        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'][0]['documentType'] = "regulatoryDocument"
        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'][0]['title'] = f"{number_of_iteration} declare new person bf doc title"
        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'][0]['description'] = f"{number_of_iteration} declare new person bf doc description"

        payload['requirementResponse']['requirement']['id'] = requirement_id
        return payload

    def create_declare_old_person_but_new_bf_new_doc_full_data_model(self, tenderer_id, requirement_id,
                                                                     number_of_iteration, actual_ms_release,
                                                                     req_resp_id=str(uuid.uuid4()),
                                                                     value=True):
        payload = {
            "requirementResponse": {}
        }
        payload['requirementResponse'].update(self.constructor.requirement_response_object())

        payload['requirementResponse']['id'] = req_resp_id
        payload['requirementResponse']['value'] = value
        for p in actual_ms_release['releases'][0]['parties']:
            for p_1 in p:
                if p_1 == "roles":
                    if p['roles'] == ['procuringEntity']:
                        list_of_persones = list()
                        for p_2 in p['persones']:
                            for p_3 in p_2:
                                if p_3 == "id":
                                    list_of_persones.append(p_2['id'])
                        if "persones" in p:
                            for x in range(len(list_of_persones)):
                                payload['requirementResponse']['relatedTenderer']['id'] = tenderer_id
                                payload['requirementResponse']['responder']['title'] = p['persones'][x]['title']
                                payload['requirementResponse']['responder']['name'] = p['persones'][x]['name']
                                payload['requirementResponse']['responder']['identifier']['id'] = p['persones'][x][
                                    'identifier']['id']
                                payload['requirementResponse']['responder']['identifier']['scheme'] = p['persones'][x][
                                    'identifier']['scheme']
                                payload['requirementResponse']['responder']['identifier']['uri'] = p['persones'][x][
                                    'identifier']['uri']

        payload['requirementResponse']['responder']['businessFunctions'] = [{}]
        payload['requirementResponse']['responder']['businessFunctions'][0].update(
            self.constructor.requirement_response_business_functions_object())

        payload['requirementResponse']['responder']['businessFunctions'][0]['id'] = \
            f"{number_of_iteration} declare new value bf id"
        payload['requirementResponse']['responder']['businessFunctions'][0]['type'] = \
            f"{random.choice(business_function_type_for_declare)}"
        payload['requirementResponse']['responder']['businessFunctions'][0]['jobTitle'] = \
            f"{number_of_iteration} declare new value bf jobTitle"
        payload['requirementResponse']['responder']['businessFunctions'][0]['period'][
            'startDate'] = self.old_date

        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'] = [{}]
        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'][0].update(self.constructor.business_functions_documents_object())

        payload['requirementResponse']['responder']['businessFunctions'][0]['documents'][0]['id'] = \
            self.document_one_was_uploaded[0]["data"]["id"]
        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'][0]['documentType'] = "regulatoryDocument"
        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'][0]['title'] = f"{number_of_iteration} declare new value bf doc title"
        payload['requirementResponse']['responder']['businessFunctions'][0][
            'documents'][0]['description'] = f"{number_of_iteration} declare new value bf doc description"

        payload['requirementResponse']['requirement']['id'] = requirement_id
        return payload

    def create_declare_new_responder_identifier_but_old_other_value_full(self, tenderer_id, requirement_id,
                                                                         number_of_iteration, actual_ms_release,
                                                                         req_resp_id=str(uuid.uuid4()),
                                                                         value=True):
        payload = {
            "requirementResponse": {}
        }
        payload['requirementResponse'].update(self.constructor.requirement_response_object())

        payload['requirementResponse']['id'] = req_resp_id
        payload['requirementResponse']['value'] = value
        payload['requirementResponse']['responder']['identifier'][
            'id'] = f"{number_of_iteration} declare new person responder id"
        payload['requirementResponse']['responder']['identifier']['scheme'] = "MD-IDNO"
        payload['requirementResponse']['responder']['identifier'][
            'uri'] = f"{number_of_iteration}declare new person uri"
        for p in actual_ms_release['releases'][0]['parties']:
            for p_1 in p:
                if p_1 == "roles":
                    if p['roles'] == ['procuringEntity']:
                        list_of_persones = list()
                        for p_2 in p['persones']:
                            for p_3 in p_2:
                                if p_3 == "id":
                                    list_of_persones.append(p_2['id'])
                        if "persones" in p:
                            for x in range(len(list_of_persones)):
                                payload['requirementResponse']['relatedTenderer']['id'] = tenderer_id
                                payload['requirementResponse']['responder']['title'] = p['persones'][x]['title']
                                payload['requirementResponse']['responder']['name'] = p['persones'][x]['name']

                                list_of_business_function = list()
                                for bf in p['persones'][x]['businessFunctions']:
                                    for bf_1 in bf:
                                        if bf_1 == "id":
                                            list_of_business_function.append(bf['id'])

                                for y in range(len(list_of_business_function)):
                                    payload['requirementResponse']['responder']['businessFunctions'] = [{}]
                                    payload['requirementResponse']['responder']['businessFunctions'][y].update(
                                        self.constructor.requirement_response_business_functions_object())

                                    payload['requirementResponse']['responder']['businessFunctions'][y]['id'] = \
                                        p['persones'][x]['businessFunctions'][y]['id']
                                    payload['requirementResponse']['responder']['businessFunctions'][y]['type'] = \
                                        p['persones'][x]['businessFunctions'][y]['type']
                                    payload['requirementResponse']['responder']['businessFunctions'][y]['jobTitle'] = \
                                        p['persones'][x]['businessFunctions'][y]['jobTitle']
                                    payload['requirementResponse']['responder']['businessFunctions'][y]['period'][
                                        'startDate'] = p['persones'][x]['businessFunctions'][y]['period']['startDate']

                                    list_of_business_function_documents = list()
                                    for doc in p['persones'][x]['businessFunctions'][y]['documents']:
                                        for doc_1 in doc:
                                            if doc_1 == "id":
                                                list_of_business_function_documents.append(doc['id'])

                                    for z in range(len(list_of_business_function_documents)):
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'] = [{}]
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z].update(
                                            self.constructor.business_functions_documents_object())

                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z]['id'] = p['persones'][x]['businessFunctions'][y][
                                            'documents'][z]['id']
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z]['documentType'] = p['persones'][x]['businessFunctions'][y][
                                            'documents'][z]['documentType']
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z]['title'] = p['persones'][x]['businessFunctions'][y][
                                            'documents'][z]['title']
                                        payload['requirementResponse']['responder']['businessFunctions'][y][
                                            'documents'][z]['description'] = p['persones'][x]['businessFunctions'][y][
                                            'documents'][z]['description']

        payload['requirementResponse']['requirement']['id'] = requirement_id
        return payload
