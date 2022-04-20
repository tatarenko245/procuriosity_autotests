"""Prepare the expected payloads of the amend framework establishment process, framework agreement procedures."""
import copy
import random

from tests.utils.PayloadModels.FrameworkAgreement.FrameworkEstablishment.frameworkEstablishment_payload import \
    FrameworkEstablishmentPayload
from tests.utils.data_of_enum import person_title_tuple, documentType_tuple, business_function_type_2_tuple
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class AmendFrameworkEstablishmentPayload:
    """This class creates instance of payload."""

    def __init__(self, ap_payload, fe_payload, fe_release, host_to_service, country, language, environment):

        __document_one = Document(host=host_to_service)
        self.__document_one_was_uploaded = __document_one.uploading_document()
        self.__document_two_was_uploaded = __document_one.uploading_document()
        self.__host = host_to_service

        self.__date = Date()
        self.__businessFunctions_period_startDate = self.__date.old_period()[0]
        self.__requirements_period = self.__date.old_period()

        self.__country = country
        self.__language = language
        self.__environment = environment

        self.__ap_payload = ap_payload
        self.__fe_release = fe_payload
        self.__fe_release = fe_release

        fe_payload_class = (copy.deepcopy(FrameworkEstablishmentPayload(
            ap_payload=self.__ap_payload,
            host_to_service=self.__host,
            country=self.__country,
            language=self.__language,
            environment=self.__environment
        )))
        self.__fe_payload_model = fe_payload_class.build_frameworkEstablishment_payload()

        for q_0 in range(len(self.__fe_release['releases'][0]['parties'])):

            if fe_payload['tender']['procuringEntity']['id'] == self.__fe_release['releases'][0]['parties'][q_0]['id']:

                for q_1 in range(len(self.__fe_release['releases'][0]['parties'][q_0]['persones'])):

                    del self.__fe_release['releases'][0]['parties'][q_0]['persones'][q_1]['id']

                    for q_2 in range(len(
                            self.__fe_release['releases'][0]['parties'][q_0]['persones'][q_1]['businessFunctions']
                    )):
                        for q_3 in range(len(
                                self.__fe_release['releases'][0]['parties'][q_0]['persones'][q_1][
                                    'businessFunctions'][q_2]['documents']
                        )):
                            del self.__fe_release['releases'][0]['parties'][q_0]['persones'][q_1][
                                'businessFunctions'][q_2]['documents'][q_3]['url']

                            del self.__fe_release['releases'][0]['parties'][q_0]['persones'][q_1][
                                'businessFunctions'][q_2]['documents'][q_3]['datePublished']

                self.__old_persones_array = self.__fe_release['releases'][0]['parties'][q_0]['persones']

        self.__payload = {
            "preQualification": {
                "period": {
                    "endDate": self.__date.preQualificationPeriod_endDate(960)
                }
            },
            "tender": {
                "procuringEntity": {
                    "id": fe_payload['tender']['procuringEntity']['id'],
                    "persones": self.__old_persones_array

                },
                "documents": fe_payload['tender']['documents'],
                "procurementMethodRationale": "amend fe: tender.procurementMethodRationale"
            }
        }

    def build_amendFrameworkEstablishment_payload(self):
        """Build payload."""
        return self.__payload

    def delete_optional_fields(
            self, *args, persones_position=0,
            businessFunctions_position=0,
            businessFunctions_documents_position=0,
            tender_documents_position=0):
        """Delete optional fields from payload."""

        for a in args:
            if a == "tender.procuringEntity":
                del self.__payload['tender']['procuringEntity']

            elif a == "tender.procuringEntity.persones.identifier.uri":
                del self.__payload['tender']['procuringEntity'][
                    'persones'][persones_position]['identifier']['uri']

            elif a == "tender.procuringEntity.persones.businessFunctions.documents":
                del self.__payload['tender']['procuringEntity'][
                    'persones'][persones_position]['businessFunctions'][businessFunctions_position]['documents']

            elif a == "tender.procuringEntity.persones.businessFunctions.documents.description":
                del self.__payload['tender']['procuringEntity'][
                    'persones'][persones_position]['businessFunctions'][businessFunctions_position][
                    'documents'][businessFunctions_documents_position]['description']

            elif a == "tender.documents":
                del self.__payload['tender']['documents']

            elif a == "tender.documents.description":
                del self.__payload['tender']['documents'][tender_documents_position]['description']

            elif a == "tender.procurementMethodRationale":
                del self.__payload['tender']['procurementMethodRationale']

            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def customize_old_persones(
            self, *list_of_persones_id,
            need_to_add_new_businessFunctions, quantity_of_new_businessFunctions_objects,
            need_to_add_new_document, quantity_of_new_documents_objects):
        """Customize old persones. Call this method before 'add_new_persones'."""

        for a in list_of_persones_id:
            for p in range(len(self.__old_persones_array)):

                if a == f"{self.__old_persones_array[p]['identifier']['scheme']}-" \
                        f"{self.__old_persones_array[p]['identifier']['id']}":

                    persones_object = copy.deepcopy(self.__fe_payload_model['tender']['procuringEntity']['persones'][0])

                    persones_object['title'] = "Ms."
                    persones_object['name'] = f"amend fe: new value for old person, " \
                                              f"tender.procuringEntity.persones[{p}].name"

                    persones_object['identifier']['scheme'] = self.__old_persones_array[p]['identifier']['scheme']
                    persones_object['identifier']['id'] = self.__old_persones_array[p]['identifier']['id']

                    persones_object['identifier']['uri'] = \
                        f"amend fe: new value for old person, tender.procuringEntity.persones[{p}].identifier.uri"

                    businessFunctions_array = list()
                    for q_0 in range(len(self.__old_persones_array[p]['businessFunctions'])):

                        businessFunctions_array.append(copy.deepcopy(
                            self.__fe_payload_model['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]
                        ))

                        businessFunctions_array[q_0]['id'] = \
                            self.__old_persones_array[p]['businessFunctions'][q_0]['id']

                        businessFunctions_array[q_0]['type'] = "contactPoint"

                        businessFunctions_array[q_0]['jobTitle'] = \
                            f"amend fe: new value for old person, tender.procuringEntity.persones[{p}]." \
                            f"businessFunctions[{q_0}].jobTitle"

                        businessFunctions_array[q_0]['period']['startDate'] = self.__date.old_period()[0]

                        documents_array = list()
                        if "documents" in self.__old_persones_array[p]['businessFunctions'][q_0]:
                            for q_1 in range(len(self.__old_persones_array[p]['businessFunctions'][q_0]['documents'])):
                                documents_array.append(copy.deepcopy(
                                    self.__fe_payload_model['tender']['procuringEntity']['persones'][0][
                                        'businessFunctions'][0]['documents'][0]
                                ))
                                documents_array[q_1]['id'] = \
                                    self.__old_persones_array[p]['businessFunctions'][q_0]['documents'][q_1]['id']

                                documents_array[q_1]['documentType'] = "regulatoryDocument"

                                documents_array[q_1]['title'] = \
                                    f"amend fe: new value for old person, tender.procuringEntity.persones[{p}]." \
                                    f"businessFunctions[{q_0}].documents[{q_1}].title"

                                documents_array[q_1]['description'] = \
                                    f"amend fe: new value for old person, tender.procuringEntity.persones[{p}]." \
                                    f"businessFunctions[{q_0}].documents[{q_1}].description"

                        if need_to_add_new_document is True:
                            new_documents_array = list()
                            for n_1 in range(quantity_of_new_documents_objects):

                                new_documents_array.append(copy.deepcopy(
                                    self.__fe_payload_model['tender']['procuringEntity']['persones'][0][
                                        'businessFunctions'][0]['documents'][0]
                                ))

                                document_two = Document(host=self.__host)
                                document_two_was_uploaded = document_two.uploading_document()

                                new_documents_array[n_1]['id'] = document_two_was_uploaded[0]["data"]["id"]

                                new_documents_array[n_1]['documentType'] = "regulatoryDocument"

                                new_documents_array[n_1]['title'] = \
                                    f"amend fe: new object, tender.procuringEntity.persones[{p}]." \
                                    f"['businessFunctions'][{q_0}].documents[{n_1}.title"

                                new_documents_array[n_1]['description'] = \
                                    f"amend fe: new object, tender.procuringEntity.persones[{p}]." \
                                    f"['businessFunctions'][{q_0}].documents[{n_1}.description"

                            documents_array += new_documents_array

                        businessFunctions_array[q_0]['documents'] = documents_array

                    if need_to_add_new_businessFunctions is True:
                        new_businessFunctions_array = list()
                        for n_0 in range(quantity_of_new_businessFunctions_objects):

                            new_businessFunctions_array.append(copy.deepcopy(
                                self.__fe_payload_model['tender']['procuringEntity']['persones'][0][
                                    'businessFunctions'][0]
                            ))

                            new_businessFunctions_array[n_0]['id'] = f"{len(businessFunctions_array)+ n_0}"

                            new_businessFunctions_array[n_0]['type'] = \
                                f"{random.choice(business_function_type_2_tuple)}"

                            new_businessFunctions_array[n_0]['jobTitle'] = \
                                f"amend fe: new object, tender.procuringEntity.persones[{p}]." \
                                f"['businessFunctions'][{n_0}].jobTitle"

                            new_businessFunctions_array[n_0]['period']['startDate'] = \
                                self.__businessFunctions_period_startDate

                            new_businessFunctions_array[n_0]['documents'] = list()
                            for d in range(quantity_of_new_documents_objects):
                                new_businessFunctions_array[n_0]['documents'].append(copy.deepcopy(
                                    self.__fe_payload_model['tender']['procuringEntity']['persones'][0][
                                        'businessFunctions'][0]['documents'][0]
                                ))

                                document_three = Document(host=self.__host)
                                document_three_was_uploaded = document_three.uploading_document()

                                new_businessFunctions_array[n_0]['documents'][d]['id'] = \
                                    document_three_was_uploaded[0]["data"]["id"]

                                new_businessFunctions_array[n_0]['documents'][d]['documentType'] = "regulatoryDocument"

                                new_businessFunctions_array[n_0]['documents'][d]['title'] = \
                                    f"amend fe: new object, tender.procuringEntity.persones[{p}]." \
                                    f"['businessFunctions'][{n_0}].documents[{d}.title"

                                new_businessFunctions_array[n_0]['documents'][d]['description'] = \
                                    f"amend fe: new object, tender.procuringEntity.persones[{p}]." \
                                    f"['businessFunctions'][{n_0}].documents[{d}.description"

                        businessFunctions_array += new_businessFunctions_array

                    persones_object['businessFunctions'] = businessFunctions_array

                    self.__old_persones_array[p] = persones_object

            self.__payload['tender']['procuringEntity']['persones'] = self.__old_persones_array

    def add_new_persones(
            self, quantity_of_persones_objects, quantity_of_businessFunctions_objects, quantity_of_documents_objects):
        """Add new oblects to tender.procuringEntity.persones array."""

        new_persones_array = list()
        for q_0 in range(quantity_of_persones_objects):
            new_persones_array.append(copy.deepcopy(
                self.__fe_payload_model['tender']['procuringEntity']['persones'][0]
            ))

            new_persones_array[q_0]['title'] = f"{random.choice(person_title_tuple)}"
            new_persones_array[q_0]['name'] = f"amend fe: tender.procuringEntity.persones[{q_0}].name"
            new_persones_array[q_0]['identifier']['scheme'] = "MD-IDNO"
            new_persones_array[q_0]['identifier']['id'] = f"amend fe: tender.procuringEntity.persones[{q_0}].id"
            new_persones_array[q_0]['identifier']['uri'] = f"amend fe: tender.procuringEntity.persones[{q_0}].uri"

            new_persones_array[q_0]['businessFunctions'] = list()
            for q_1 in range(quantity_of_businessFunctions_objects):

                new_persones_array[q_0]['businessFunctions'].append(copy.deepcopy(
                    self.__fe_payload_model['tender']['procuringEntity']['persones'][0]['businessFunctions'][0])
                )

                new_persones_array[q_0]['businessFunctions'][q_1]['id'] = f"{q_1}"

                new_persones_array[q_0]['businessFunctions'][q_1]['type'] = \
                    f"{random.choice(business_function_type_2_tuple)}"

                new_persones_array[q_0]['businessFunctions'][q_1]['jobTitle'] = \
                    f"amend fe: tender.procuringEntity.persones[{q_0}].['businessFunctions'][{q_1}].jobTitle"

                new_persones_array[q_0]['businessFunctions'][q_1]['period']['startDate'] = \
                    self.__businessFunctions_period_startDate

                new_persones_array[q_0]['businessFunctions'][q_1]['documents'] = list()
                for q_2 in range(quantity_of_documents_objects):
                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'].append(copy.deepcopy(
                        self.__fe_payload_model['tender']['procuringEntity']['persones'][0]['businessFunctions'][0][
                            'documents'][0])
                    )

                    document_three = Document(host=self.__host)
                    document_three_was_uploaded = document_three.uploading_document()

                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'][q_2]['id'] = \
                        document_three_was_uploaded[0]["data"]["id"]

                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'][q_2]['documentType'] = \
                        "regulatoryDocument"

                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'][q_2]['title'] = \
                        f"amend fe: tender.procuringEntity.persones[{q_0}].['businessFunctions'][{q_1}]." \
                        f"documents[{q_2}.title"

                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'][q_2]['description'] = \
                        f"amend fe: tender.procuringEntity.persones[{q_0}].['businessFunctions'][{q_1}]." \
                        f"documents[{q_2}.description"

        self.__payload['tender']['procuringEntity']['persones'] += new_persones_array

    def customize_old_tender_documents(self, *list_of_documents_id):
        """Customize old documents. Call this method before 'add_new_documents'."""

        for a in list_of_documents_id:
            for d in range(len(self.__fe_release['releases'][0]['tender']['documents'])):
                if a == self.__fe_release['releases'][0]['tender']['documents'][d]['id']:
                    documents_object = copy.deepcopy(self.__fe_payload_model['tender']['documents'][0])

                    documents_object['id'] = self.__fe_release['releases'][0]['tender']['documents'][d]['id']
                    documents_object['documentType'] = "clarifications"
                    documents_object['title'] = f"amend fe: new value for old object, tender.documents[{d}].title"

                    documents_object['description'] = \
                        f"amend fe: new value for old object, tender.documents[{d}].description"

                    self.__payload['tender']['documents'][d] = documents_object

    def add_new_tender_documents(self, quantity_of_new_documents):
        """Add new documents to the 'tender' object."""

        new_documents_array = list()
        for q_0 in range(quantity_of_new_documents):
            new_documents_array.append(copy.deepcopy(self.__fe_payload_model['tender']['documents'][0]))

            document_four = Document(host=self.__host)
            document_four_was_uploaded = document_four.uploading_document()

            new_documents_array[q_0]['id'] = document_four_was_uploaded[0]["data"]["id"]
            new_documents_array[q_0]['documentType'] = f"{random.choice(documentType_tuple)}"
            new_documents_array[q_0]['title'] = f"amend fe: new object, tender.documents{q_0}.title"
            new_documents_array[q_0]['description'] = f"amend fe: new object, tender.documents{q_0}.description"

        self.__payload['tender']['documents'] += new_documents_array

    def __del__(self):
        print(f"The instance of FrameworkEstablishmentPayload class: {__name__} was deleted.")
