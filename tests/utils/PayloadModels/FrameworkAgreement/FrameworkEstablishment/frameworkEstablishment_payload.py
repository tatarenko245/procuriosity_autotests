"""Prepare payload for Framework Establishment process of Framework Agreement procedure."""
import copy
import random

from tests.utils.data_of_enum import person_title_tuple, documentType_tuple, business_function_type_2_tuple, \
    qualificationSystemMethod_tuple, reductionCriteria_tuple
from tests.utils.date_class import Date
from tests.utils.functions_collection.functions import \
    set_eligibility_evidences_unique_temporary_id, set_criteria_array_unique_temporary_id
from tests.utils.functions_collection.generate_criteria_array import CriteriaArray
from tests.utils.iStorage import Document
from tests.utils.services.e_mdm_service import MdmService


class FrameworkEstablishmentPayload:
    """This class prepares payload."""
    def __init__(self, ap_payload, host_to_service, country, language, environment):
        __document_one = Document(host=host_to_service)
        self.__document_one_was_uploaded = __document_one.uploading_document()
        self.__document_two_was_uploaded = __document_one.uploading_document()
        self.__host = host_to_service

        date = Date()
        self.__businessFunctions_period_startDate = date.old_period()[0]
        self.__requirements_period = date.old_period()

        self.__country = country
        self.__language = language
        self.__environment = environment

        self.__payload = {
            "preQualification": {
                "period": {
                    "endDate": date.preQualificationPeriod_endDate(900)
                }
            },
            "tender": {
                "secondStage": {
                    "minimumCandidates": 1,
                    "maximumCandidates": 2
                },
                "procurementMethodModalities": ["electronicAuction"],
                "procurementMethodRationale": "create fe: tender.procurementMethodRationale",
                "procuringEntity": {
                    "id": f"{ap_payload['tender']['procuringEntity']['identifier']['scheme']}-"
                          f"{ap_payload['tender']['procuringEntity']['identifier']['id']}",

                    "persones": [{
                        "title": f"{random.choice(person_title_tuple)}",
                        "name": "create fe: tender.procuringEntity.persones[0].name",
                        "identifier": {
                            "scheme": "MD-IDNO",
                            "id": "create fe: tender.procuringEntity.persones[0].identifier.id",
                            "uri": "create fe: tender.procuringEntity.persones[0].identifier.uri"
                        },
                        "businessFunctions": [{
                            "id": "0",
                            "type": f"{random.choice(business_function_type_2_tuple)}",
                            "jobTitle": "create fe: tender.procuringEntity.persones[0].businessFunctions[0].jobTitle",
                            "period": {
                                "startDate": self.__businessFunctions_period_startDate
                            },
                            "documents": [{
                                "id": self.__document_one_was_uploaded[0]["data"]["id"],
                                "documentType": "regulatoryDocument",

                                "title": "create fe: tender.procuringEntity.persones[0].businessFunctions[0]."
                                         "documents[0].title",

                                "description": "create fe: tender.procuringEntity.persones[0].businessFunctions[0]."
                                               "documents[0].description"
                            }]
                        }]
                    }]
                },
                "criteria": [{
                    "id": "0",
                    "title": "create fe: tender.criteria[0].title",
                    "description": "create fe: tender.criteria[0].description",
                    "relatesTo": "tenderer",
                    "requirementGroups": [{
                        "id": "0-0",
                        "description": "create fe: tender.criteria[0].requirementGroups[0].description",
                        "requirements": [{
                            "id": "0-0-0",
                            "title": "create fe: tender.criteria[0].requirementGroups[0].requirements[0].title",

                            "description": "create fe: tender.criteria[0].requirementGroups[0]."
                                           "requirements[0].description",
                            "dataType": "",
                            "period": {
                                "startDate": self.__requirements_period[0],
                                "endDate": self.__requirements_period[1]
                            },
                            "expectedValue": "",
                            "minValue": "",
                            "maxValue": "",
                            "eligibleEvidences": [{
                                "id": "0-0-0-0",

                                "title": "create fe: tender.criteria[0].requirementGroups[0]."
                                         "requirements[0].eligibleEvidences[0].title",

                                "description": "create fe: tender.criteria[0].requirementGroups[0]."
                                               "requirements[0].eligibleEvidences[0].description",

                                "type": "document",
                                "relatedDocument": {
                                    "id": self.__document_two_was_uploaded[0]['data']['id']
                                }
                            }]
                        }]
                    }],
                    "classification": {
                        "id": "",
                        "scheme": ""
                    }
                }],
                "otherCriteria": {
                    "qualificationSystemMethods": [f"{random.choice(qualificationSystemMethod_tuple)}"],
                    "reductionCriteria": f"{random.choice(reductionCriteria_tuple)}"
                },
                "documents": [{
                    "documentType": f"{random.choice(documentType_tuple)}",
                    "id": self.__document_one_was_uploaded[0]['data']['id'],
                    "title": "create fe: tender.document[0].title",
                    "description": "create fe: tender.document[0].description"
                }]
            }
        }

    def build_frameworkEstablishment_payload(self):
        """Build payload."""
        return self.__payload

    def delete_optional_fields(
            self, *args, tender_procuringEntity_persones_position=0,
            tender_procuringEntity_persones_businessFunctions_position=0,
            tender_procuringEntity_persones_businessFunctions_documents_position=0,
            tender_criteria_position=0, tender_criteria_requirementGroups_position=0,
            tender_criteria_requirementGroups_requirements_position=0,
            tender_criteria_requirementGroups_requirements_eligibleEvidences_position=0,
            tender_documents_position=0):
        """Delete optional fields from payload."""

        for a in args:
            if a == "tender.secondStage":
                del self.__payload['tender']['secondStage']
            elif a == "tender.secondStage.minimumCandidates":
                del self.__payload['tender']['secondStage']['minimumCandidates']
            elif a == "tender.secondStage.maximumCandidates":
                del self.__payload['tender']['secondStage']['maximumCandidates']

            elif a == "tender.procurementMethodModalities":
                del self.__payload['tender']['procurementMethodModalities']

            elif a == "tender.procurementMethodRationale":
                del self.__payload['tender']['procurementMethodRationale']

            elif a == "tender.procuringEntity":
                del self.__payload['tender']['procuringEntity']
            elif a == "tender.procuringEntity.persones.identifier.uri":

                del self.__payload['tender']['procuringEntity'][
                    'persones'][tender_procuringEntity_persones_position]['identifier']['uri']

            elif a == "tender.procuringEntity.persones.businessFunctions.documents":
                del self.__payload[
                    'tender']['procuringEntity']['persones'][tender_procuringEntity_persones_position][
                    'businessFunctions'][tender_procuringEntity_persones_businessFunctions_position]['documents']

            elif a == "tender.procuringEntity.persones.businessFunctions.documents.description":
                del self.__payload[
                    'tender']['procuringEntity']['persones'][tender_procuringEntity_persones_position][
                    'businessFunctions'][tender_procuringEntity_persones_businessFunctions_position][
                    'documents'][tender_procuringEntity_persones_businessFunctions_documents_position]['description']

            elif a == "tender.criteria":
                del self.__payload['tender']['criteria']

            elif a == "tender.criteria.requirementGroups.requirements.period":
                del self.__payload['tender']['criteria'][tender_criteria_position][
                    'requirementGroups'][tender_criteria_requirementGroups_position][
                    'requirements'][tender_criteria_requirementGroups_requirements_position]['period']

            elif a == "tender.criteria.requirementGroups.requirements.expectedValue":
                del self.__payload['tender']['criteria'][tender_criteria_position][
                    'requirementGroups'][tender_criteria_requirementGroups_position][
                    'requirements'][tender_criteria_requirementGroups_requirements_position]['expectedValue']

            elif a == "tender.criteria.requirementGroups.requirements.minValue":
                del self.__payload['tender']['criteria'][tender_criteria_position][
                    'requirementGroups'][tender_criteria_requirementGroups_position][
                    'requirements'][tender_criteria_requirementGroups_requirements_position]['minValue']

            elif a == "tender.criteria.requirementGroups.requirements.maxValue":
                del self.__payload['tender']['criteria'][tender_criteria_position][
                    'requirementGroups'][tender_criteria_requirementGroups_position][
                    'requirements'][tender_criteria_requirementGroups_requirements_position]['maxValue']

            elif a == "tender.criteria.requirementGroups.requirements.eligibleEvidences":
                del self.__payload['tender']['criteria'][tender_criteria_position][
                    'requirementGroups'][tender_criteria_requirementGroups_position][
                    'requirements'][tender_criteria_requirementGroups_requirements_position][
                    'eligibleEvidences'][tender_criteria_requirementGroups_requirements_eligibleEvidences_position][
                    'relatedDocument']

            elif a == "tender.documents":
                del self.__payload['tender']['documents']

            elif a == "tender.documents.description":
                del self.__payload['tender']['documents'][tender_documents_position]['description']

            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def customize_tender_procuringEntity_persones(
            self, quantity_of_persones_objects, quantity_of_businessFunctions_objects,
            quantity_of_businessFunctions_documents_objects):
        """Customize tender.procuringEntity.persones array."""

        new_persones_array = list()
        for q_0 in range(quantity_of_persones_objects):
            new_persones_array.append(copy.deepcopy(
                self.__payload['tender']['procuringEntity']['persones'][0])
            )

            new_persones_array[q_0]['title'] = f"{random.choice(person_title_tuple)}"
            new_persones_array[q_0]['name'] = f"create fe: tender.procuringEntity.persones[{q_0}].name"
            new_persones_array[q_0]['identifier']['scheme'] = "MD-IDNO"
            new_persones_array[q_0]['identifier']['id'] = f"create fe: tender.procuringEntity.persones[{q_0}].id"
            new_persones_array[q_0]['identifier']['uri'] = f"create fe: tender.procuringEntity.persones[{q_0}].uri"

            new_persones_array[q_0]['businessFunctions'] = list()
            for q_1 in range(quantity_of_businessFunctions_objects):

                new_persones_array[q_0]['businessFunctions'].append(copy.deepcopy(
                    self.__payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0])
                )

                new_persones_array[q_0]['businessFunctions'][q_1]['id'] = f"{q_1}"

                new_persones_array[q_0]['businessFunctions'][q_1]['type'] = \
                    f"{random.choice(business_function_type_2_tuple)}"

                new_persones_array[q_0]['businessFunctions'][q_1]['jobTitle'] = \
                    f"create fe: tender.procuringEntity.persones[{q_0}].['businessFunctions'][{q_1}].jobTitle"

                new_persones_array[q_0]['businessFunctions'][q_1]['period']['startDate'] = \
                    self.__businessFunctions_period_startDate

                new_persones_array[q_0]['businessFunctions'][q_1]['documents'] = list()
                for q_2 in range(quantity_of_businessFunctions_documents_objects):
                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'].append(copy.deepcopy(
                        self.__payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0][
                            'documents'][0])
                    )

                    document_three = Document(host=self.__host)
                    document_three_was_uploaded = document_three.uploading_document()

                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'][q_2]['id'] = \
                        document_three_was_uploaded[0]["data"]["id"]

                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'][q_2]['documentType'] = \
                        "regulatoryDocument"

                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'][q_2]['title'] = \
                        f"create fe: tender.procuringEntity.persones[{q_0}].['businessFunctions'][{q_1}]." \
                        f"documents[{q_2}.title"

                    new_persones_array[q_0]['businessFunctions'][q_1]['documents'][q_2]['description'] = \
                        f"create fe: tender.procuringEntity.persones[{q_0}].['businessFunctions'][{q_1}]." \
                        f"documents[{q_2}.description"

        self.__payload['tender']['procuringEntity']['persones'] = new_persones_array

    def customize_tender_criteria(self):
        """Customize tender.criteria array."""

        # Get all 'standard' criteria from eMDM service.
        mdm_service = MdmService(
            host_to_service=self.__host,
            environment=self.__environment)

        standard_criteria = mdm_service.get_standard_criteria(
            self.__country,
            self.__language
        )

        # Prepare 'exclusion' criteria for payload.
        some_criteria = CriteriaArray(
            host_to_service=self.__host,
            country=self.__country,
            language=self.__language,
            environment=self.__environment,
            quantity_of_criteria_objects=len(standard_criteria[1]),
            quantity_of_requirementGroups_objects=1,
            quantity_of_requirements_objects=2,
            quantity_of_eligibleEvidences_objects=2,
            type_of_standardCriteria=1
        )

        some_criteria.delete_optional_fields(
            "criteria.description",
            "criteria.requirementGroups.description",
            "criteria.requirementGroups.requirements.description",
            "criteria.requirementGroups.requirements.period",
            "criteria.requirementGroups.requirements.minValue",
            "criteria.requirementGroups.requirements.maxValue",
            "criteria.requirementGroups.requirements.eligibleEvidences"
        )

        some_criteria.prepare_criteria_array(criteria_relatesTo="tenderer")
        some_criteria.set_unique_temporary_id_for_eligibleEvidences()
        some_criteria.set_unique_temporary_id_for_criteria()
        exclusion_criteria_array = some_criteria.build_criteria_array()

        # Prepare 'selection' criteria for payload.
        some_criteria = CriteriaArray(
            host_to_service=self.__host,
            country=self.__country,
            language=self.__language,
            environment=self.__environment,
            quantity_of_criteria_objects=len(standard_criteria[2]),
            quantity_of_requirementGroups_objects=2,
            quantity_of_requirements_objects=2,
            quantity_of_eligibleEvidences_objects=2,
            type_of_standardCriteria=2
        )

        some_criteria.delete_optional_fields(
            "criteria.description",
            "criteria.requirementGroups.description",
            "criteria.requirementGroups.requirements.description",
            "criteria.requirementGroups.requirements.period",
            "criteria.requirementGroups.requirements.expectedValue",
            "criteria.requirementGroups.requirements.eligibleEvidences"
        )

        some_criteria.prepare_criteria_array(criteria_relatesTo="tenderer")
        some_criteria.set_unique_temporary_id_for_eligibleEvidences()
        some_criteria.set_unique_temporary_id_for_criteria()
        selection_criteria_array = some_criteria.build_criteria_array()

        # Prepare new criteria array.
        new_criteria_array = exclusion_criteria_array + selection_criteria_array
        new_criteria_array = set_eligibility_evidences_unique_temporary_id(new_criteria_array)
        new_criteria_array = set_criteria_array_unique_temporary_id(new_criteria_array)

        self.__payload['tender']['criteria'] = new_criteria_array

    def customize_tender_documents(self, quantity_of_new_documents):
        """Customize tender.documents array."""

        new_documents_array = list()
        for q_0 in range(quantity_of_new_documents):
            new_documents_array.append(copy.deepcopy(self.__payload['tender']['documents'][0]))

            document_four = Document(host=self.__host)
            document_four_was_uploaded = document_four.uploading_document()

            new_documents_array[q_0]['id'] = document_four_was_uploaded[0]["data"]["id"]
            new_documents_array[q_0]['documentType'] = f"{random.choice(documentType_tuple)}"
            new_documents_array[q_0]['title'] = f"create fe: tender.documents{q_0}.title"
            new_documents_array[q_0]['description'] = f"create fe: tender.documents{q_0}.description"

        eligibleEvidences_documents_array = list()
        if "criteria" in self.__payload['tender']:
            for e_0 in range(len(self.__payload['tender']['criteria'])):
                for e_1 in range(len(self.__payload['tender']['criteria'][e_0]['requirementGroups'])):

                    for e_2 in range(len(self.__payload['tender']['criteria'][e_0]['requirementGroups'][e_1][
                                             'requirements'])):

                        if "eligibleEvidences" in self.__payload['tender']['criteria'][e_0][
                                'requirementGroups'][e_1]['requirements'][e_2]:

                            for e_3 in range(len(self.__payload['tender']['criteria'][e_0][
                                    'requirementGroups'][e_1]['requirements'][e_2]['eligibleEvidences'])):

                                if "relatedDocument" in self.__payload['tender']['criteria'][e_0][
                                        'requirementGroups'][e_1]['requirements'][e_2]['eligibleEvidences'][e_3]:

                                    eligibleEvidences_document_object = copy.deepcopy(
                                        self.__payload['tender']['documents'][0])

                                    eligibleEvidences_document_object['id'] = \
                                        self.__payload['tender']['criteria'][e_0]['requirementGroups'][e_1][
                                            'requirements'][e_2]['eligibleEvidences'][e_3]['relatedDocument']['id']

                                    eligibleEvidences_document_object['documentType'] = \
                                        f"{random.choice(documentType_tuple)}"

                                    eligibleEvidences_document_object['title'] = \
                                        f"create fe: tender.documents{len(eligibleEvidences_documents_array)}.title"

                                    eligibleEvidences_document_object['description'] = \
                                        f"create fe: tender.documents{len(eligibleEvidences_documents_array)}." \
                                        f"description"

                                    eligibleEvidences_documents_array.append(eligibleEvidences_document_object)

        self.__payload['tender']['documents'] = new_documents_array + eligibleEvidences_documents_array

    def __del__(self):
        print(f"The instance of FrameworkEstablishmentPayload class: {__name__} was deleted.")
