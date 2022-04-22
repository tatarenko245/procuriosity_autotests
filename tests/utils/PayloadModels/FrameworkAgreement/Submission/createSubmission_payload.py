"""Prepare the expected payloads of the create submission process, framework agreement procedures."""
import copy
from tests.utils.iStorage import Document


class CreateSubmissionPayload:
    """This class creates instance of payload."""

    def __init__(self, host_to_service, actual_fe_release, quantity_of_candidates):

        self.__host = host_to_service
        self.__actual_fe_release = actual_fe_release
        self.__quantity_of_candidates = quantity_of_candidates
        self.__document = Document(self.__host)

        self.__payload = {
            "submission": {
                "requirementResponses": [
                    {
                        "id": "",
                        "value": "",
                        "requirement": {
                            "id": ""
                        },
                        "relatedCandidate": {
                            "name": "",
                            "identifier": {
                                "id": "",
                                "scheme": ""
                            }
                        },
                        "evidences": [
                            {
                                "id": "",
                                "title": "",
                                "description": "",
                                "relatedDocument": {
                                    "id": ""
                                }
                            }
                        ]

                    }
                ],
                "candidates": [
                    {
                        "name": "",
                        "identifier": {
                            "id": "",
                            "legalName": "",
                            "scheme": "",
                            "uri": ""
                        },
                        "additionalIdentifiers": [
                            {
                                "id": "",
                                "legalName": "",
                                "scheme": "",
                                "uri": ""
                            }
                        ],
                        "address": {
                            "streetAddress": "",
                            "postalCode": "",
                            "addressDetails": {
                                "country": {
                                    "id": "",
                                    "scheme": "",
                                    "description": ""
                                },
                                "region": {
                                    "id": "",
                                    "scheme": "",
                                    "description": ""
                                },
                                "locality": {
                                    "id": "",
                                    "scheme": "",
                                    "description": ""
                                }
                            }
                        },
                        "contactPoint": {
                            "name": "",
                            "email": "",
                            "telephone": "",
                            "faxNumber": "",
                            "url": ""
                        },
                        "persones": [
                            {
                                "id": "",
                                "title": "",
                                "name": "",
                                "identifier": {
                                    "scheme": "",
                                    "id": "",
                                    "uri": ""
                                },
                                "businessFunctions": [
                                    {
                                        "id": "",
                                        "type": "",
                                        "jobTitle": "",
                                        "period": {
                                            "startDate": ""
                                        },
                                        "documents": [
                                            {
                                                "id": "",
                                                "documentType": "",
                                                "title": "",
                                                "description": ""
                                            }
                                        ]
                                    }
                                ]
                            }
                        ],
                        "details": {
                            "typeOfSupplier": "",
                            "mainEconomicActivities": [
                                {
                                    "scheme": "",
                                    "id": "",
                                    "description": "",
                                    "uri": ""
                                }
                            ],
                            "scale": "",
                            "bankAccounts": [
                                {
                                    "description": "",
                                    "bankName": "",
                                    "address": {
                                        "streetAddress": "",
                                        "postalCode": "",
                                        "addressDetails": {
                                            "country": {
                                                "id": "",
                                                "scheme": "",
                                                "description": ""
                                            },
                                            "region": {
                                                "id": "",
                                                "scheme": "",
                                                "description": ""
                                            },
                                            "locality": {
                                                "id": "",
                                                "scheme": "",
                                                "description": ""
                                            }
                                        }
                                    },
                                    "identifier": {
                                        "sheme": "",
                                        "id": ""
                                    },
                                    "accountIdentification": [
                                        {
                                            "scheme": "",
                                            "id": ""
                                        }
                                    ]
                                }
                            ],
                            "legalForm": {
                                "scheme": "MD-CFOJ",
                                "id": "",
                                "description": "",
                                "uri": ""
                            }
                        }
                    }
                ],
                "documents": [
                    {
                        "documentType": "",
                        "id": "",
                        "title": "",
                        "description": ""
                    }
                ]
            }
        }

    def build_createSubmission_payload(self):
        """Build payload."""
        return self.__payload

    def delete_optional_fields(
            self, *args, requirementResponses_position=0, candidates_position=0,
            candidates_additionalIdentifiers_position=0, persones_position=0, businessFunctions_documents_position=0,
            mainEconomicActivities_position=0, bankAccounts_position=0, submission_documents=0):
        """Delete optional fields from payload."""

        for a in args:
            if a == "submission.requirementResponses":
                del self.__payload['submission']['requirementResponses']

            elif a == "submission.requirementResponses.evidences":
                del self.__payload['submission']['requirementResponses'][requirementResponses_position]['evidences']

            elif a == "submission.requirementResponses.evidences.description":
                del self.__payload['submission']['requirementResponses'][requirementResponses_position][
                    'evidences']['description']

            elif a == "submission.requirementResponses.evidences.relatedDocument":
                del self.__payload['submission']['requirementResponses'][requirementResponses_position][
                    'evidences']['relatedDocument']

            elif a == "submission.candidates.identifier.uri":
                del self.__payload['submission']['candidates'][candidates_position]['identifier']['uri']

            elif a == "submission.candidates.additionalIdentifiers":
                del self.__payload['submission']['candidates'][candidates_position]['additionalIdentifiers']

            elif a == "submission.candidates.additionalIdentifiers.uri":
                del self.__payload['submission']['candidates'][candidates_position][
                    'additionalIdentifiers'][candidates_additionalIdentifiers_position]['uri']

            elif a == "submission.candidates.address.postalCode":
                del self.__payload['submission']['candidates'][candidates_position]['address']['postalCode']

            elif a == "submission.candidates.contactPoint.faxNumber":
                del self.__payload['submission']['candidates'][candidates_position]['contactPoint']['faxNumber']

            elif a == "submission.candidates.contactPoint.url":
                del self.__payload['submission']['candidates'][candidates_position]['contactPoint']['url']

            elif a == "submission.candidates.persones":
                del self.__payload['submission']['candidates'][candidates_position]['persones']

            elif a == "submission.candidates.persones.identifier.uri":
                del self.__payload['submission']['candidates'][candidates_position]['persones'][persones_position][
                    'identifier']['uri']

            elif a == "submission.candidates.persones.businessFunctions.documents":
                del self.__payload['submission']['candidates'][candidates_position]['persones'][persones_position][
                    'businessFunctions'][businessFunctions_documents_position]['description']

            elif a == "submission.candidates.details.typeOfSupplier":
                del self.__payload['submission']['candidates'][candidates_position]['details']['typeOfSupplier']

            elif a == "submission.candidates.details.mainEconomicActivities":
                del self.__payload['submission']['candidates'][candidates_position]['details']['mainEconomicActivities']

            elif a == "submission.candidates.details.mainEconomicActivities.uri":
                del self.__payload['submission']['candidates'][candidates_position]['details'][
                    'mainEconomicActivities'][mainEconomicActivities_position]['uri']

            elif a == "submission.candidates.details.bankAccounts":
                del self.__payload['submission']['candidates'][candidates_position]['details']['bankAccounts']

            elif a == "submission.candidates.details.bankAccounts.address.postalCode":
                del self.__payload['submission']['candidates'][candidates_position]['details'][
                    'bankAccounts'][bankAccounts_position]['address']['postalCode']

            elif a == "submission.candidates.details.bankAccounts.additionalAccountIdentifiers":
                del self.__payload['submission']['candidates'][candidates_position]['details'][
                    'bankAccounts'][bankAccounts_position]['additionalAccountIdentifiers']

            elif a == "submission.candidates.details.legalForm.uri":
                del self.__payload['submission']['candidates'][candidates_position]['details']['legalForm']['uri']

            elif a == "submission.documents":
                del self.__payload['submission']['documents']

            elif a == "submission.documents.description":
                del self.__payload['submission']['documents'][submission_documents]['description']

            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def prepare_submission_requirementResponses_array(self, quantity_of_evidences):
        """Prepare 'submissions.requirementResponses' array.
        Call this method after 'prepare_submission_candidates_array' method."""

        requirementResponses_array = list()
        for c_0 in range(self.__quantity_of_candidates):
            for q_0 in range(len(self.__actual_fe_release['releases'][0]['tender']['criteria'])):

                for q_1 in range(len(self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                         'requirementGroups'][0]['requirements'])):

                    requirementResponses_object = copy.deepcopy(self.__payload['submission']['requirementResponses'][0])

                    requirementResponses_object['id'] = f"{len(requirementResponses_array)}"

                    if "expectedValue" in self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                            'requirementGroups'][0]['requirements'][q_1]:

                        requirementResponses_object['value'] = self.__actual_fe_release['releases'][0]['tender'][
                            'criteria'][q_0]['requirementGroups'][0]['requirements'][q_1]['expectedValue']

                    elif "minValue" in self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                            'requirementGroups'][0]['requirements'][q_1]:

                        requirementResponses_object['value'] = self.__actual_fe_release['releases'][0]['tender'][
                            'criteria'][q_0]['requirementGroups'][0]['requirements'][q_1]['minValue']

                    elif "maxValue" in self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                            'requirementGroups'][0]['requirements'][q_1]:

                        requirementResponses_object['value'] = self.__actual_fe_release['releases'][0]['tender'][
                            'criteria'][q_0]['requirementGroups'][0]['requirements'][q_1]['maxValue']

                    requirementResponses_object['requirement']['id'] = \
                        self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                            'requirementGroups'][0]['requirements'][q_1]['id']

                    requirementResponses_object['relatedCandidate']['name'] = \
                        self.__payload['submission']['candidates'][c_0]['name']

                    requirementResponses_object['relatedCandidate']['identifier']['id'] = \
                        self.__payload['submission']['candidates'][c_0]['identifier']['id']

                    requirementResponses_object['relatedCandidate']['identifier']['scheme'] = \
                        self.__payload['submission']['candidates'][c_0]['identifier']['scheme']

                    if "evidences" in requirementResponses_object:
                        evidences_array = list()
                        for q_2 in range(quantity_of_evidences):
                            evidences_array.append(copy.deepcopy(
                                self.__payload['submission']['requirementResponses'][0]['evidences'][0]))

                            evidences_array[q_2]['id'] = f"{q_2}"

                            evidences_array[q_2]['title'] = \
                                f"create submission: submission.requirementResponses[{q_0}].evidences[{q_2}].title"

                            evidences_array[q_2]['description'] = \
                                f"create submission: submission.requirementResponses[{q_0}].evidences[{q_2}]." \
                                f"description"

                            document_was_uploaded = self.__document.uploading_document()
                            evidences_array[q_2]['relatedDocument']['id'] = f"{document_was_uploaded[0]['data']['id']}"

                        requirementResponses_object['evidences'] = evidences_array
                    requirementResponses_array.append(requirementResponses_object)
        self.__payload['submission']['requirementResponses'] = requirementResponses_array

    # def customize_tender_documents(self, quantity_of_new_documents):
    #     """Customize tender.documents array."""
    #
    #     new_documents_array = list()
    #     for q_0 in range(quantity_of_new_documents):
    #         new_documents_array.append(copy.deepcopy(self.__payload['tender']['documents'][0]))
    #
    #         document_four = Document(host=self.__host)
    #         document_four_was_uploaded = document_four.uploading_document()
    #
    #         new_documents_array[q_0]['id'] = document_four_was_uploaded[0]["data"]["id"]
    #         new_documents_array[q_0]['documentType'] = self.__tender_documents_type
    #         new_documents_array[q_0]['title'] = f"create fe: tender.documents{q_0}.title"
    #         new_documents_array[q_0]['description'] = f"create fe: tender.documents{q_0}.description"
    #
    #     self.__payload['tender']['documents'] = new_documents_array

    def __del__(self):
        print(f"The instance of FrameworkEstablishmentPayload class: {__name__} was deleted.")
