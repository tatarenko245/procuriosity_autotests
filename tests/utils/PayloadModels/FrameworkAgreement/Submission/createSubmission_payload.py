"""Prepare the expected payloads of the create submission process, framework agreement procedures."""
import copy
import random

from tests.utils.data_of_enum import locality_scheme_tuple, person_title_tuple, business_function_type_1_tuple, \
    type_of_supplier_tuple, scale_tuple, region_id_tuple, documentType_for_create_submission_framework_agreement
from tests.utils.date_class import Date
from tests.utils.functions_collection.functions import get_locality_id_according_with_region_id, \
    set_unique_temporary_id_for_requirement_responses_evidences
from tests.utils.iStorage import Document


class CreateSubmissionPayload:
    """This class creates instance of payload."""

    def __init__(self, host_to_service, actual_fe_release, ):

        self.__host = host_to_service
        self.__actual_fe_release = actual_fe_release
        self.__document = Document(self.__host)
        self.__date = Date()

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
                                    "accountIdentification": {
                                        "scheme": "",
                                        "id": ""
                                    },
                                    "additionalAccountIdentifiers": [{
                                        "scheme": "",
                                        "id": ""
                                    }]
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

    def build_create_submission_payload(self):
        """Build payload."""
        return self.__payload

    def delete_optional_fields(
            self, *args, requirement_responses_position=0, candidates_position=0,
            candidates_additional_identifiers_position=0, persones_position=0, business_functions_position=0,
            business_functions_documents_position=0,
            main_economic_activities_position=0, bank_accounts_position=0, submission_documents=0):
        """Call this method last! Delete optional fields from payload."""

        for a in args:
            if a == "submission.requirementResponses":
                del self.__payload['submission']['requirementResponses']

            elif a == "submission.requirementResponses.evidences":
                del self.__payload['submission']['requirementResponses'][requirement_responses_position]['evidences']

            elif a == "submission.requirementResponses.evidences.description":
                del self.__payload['submission']['requirementResponses'][requirement_responses_position][
                    'evidences']['description']

            elif a == "submission.requirementResponses.evidences.relatedDocument":
                del self.__payload['submission']['requirementResponses'][requirement_responses_position][
                    'evidences']['relatedDocument']

            elif a == "submission.candidates.identifier.uri":
                del self.__payload['submission']['candidates'][candidates_position]['identifier']['uri']

            elif a == "submission.candidates.additionalIdentifiers":
                del self.__payload['submission']['candidates'][candidates_position]['additionalIdentifiers']

            elif a == "submission.candidates.additionalIdentifiers.uri":
                del self.__payload['submission']['candidates'][candidates_position][
                    'additionalIdentifiers'][candidates_additional_identifiers_position]['uri']

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
                    'businessFunctions'][business_functions_position]['documents']

            elif a == "submission.candidates.persones.businessFunctions.documents.description":
                del self.__payload['submission']['candidates'][candidates_position]['persones'][persones_position][
                    'businessFunctions'][business_functions_position][
                    'documents'][business_functions_documents_position]['description']

            elif a == "submission.candidates.details.typeOfSupplier":
                del self.__payload['submission']['candidates'][candidates_position]['details']['typeOfSupplier']

            elif a == "submission.candidates.details.mainEconomicActivities":
                del self.__payload['submission']['candidates'][candidates_position]['details']['mainEconomicActivities']

            elif a == "submission.candidates.details.mainEconomicActivities.uri":
                del self.__payload['submission']['candidates'][candidates_position]['details'][
                    'mainEconomicActivities'][main_economic_activities_position]['uri']

            elif a == "submission.candidates.details.bankAccounts":
                del self.__payload['submission']['candidates'][candidates_position]['details']['bankAccounts']

            elif a == "submission.candidates.details.bankAccounts.address.postalCode":
                del self.__payload['submission']['candidates'][candidates_position]['details'][
                    'bankAccounts'][bank_accounts_position]['address']['postalCode']

            elif a == "submission.candidates.details.bankAccounts.additionalAccountIdentifiers":
                del self.__payload['submission']['candidates'][candidates_position]['details'][
                    'bankAccounts'][bank_accounts_position]['additionalAccountIdentifiers']

            elif a == "submission.candidates.details.legalForm.uri":
                del self.__payload['submission']['candidates'][candidates_position]['details']['legalForm']['uri']

            elif a == "submission.documents":
                del self.__payload['submission']['documents']

            elif a == "submission.documents.description":
                del self.__payload['submission']['documents'][submission_documents]['description']

            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def prepare_submission_object(
                self, position, quantity_of_candidates=1, quantity_of_additional_identifiers=1, quantity_of_persones=1,
            quantity_of_evidences=1, quantity_of_business_functions=1, quantity_of_bf_documents=1,
            quantity_of_main_economic_activities=1, quantity_of_bank_accounts=1,
            quantity_of_additional_account_identifiers=1, quantity_of_documents=1):
        """Prepare 'submission' object."""

        # Enrich 'submission.candidates' array:
        candidates_array = list()
        for c_0 in range(quantity_of_candidates):
            candidates_array.append(copy.deepcopy(self.__payload['submission']['candidates'][0]))

            candidates_array[c_0]['name'] = f"create submission[{position}]: submission.candidates[{c_0}].name"
            candidates_array[c_0]['identifier']['id'] = f"create submission[{position}]: submission.candidates[{c_0}].identifier.id"

            candidates_array[c_0]['identifier']['legalName'] = \
                f"create submission[{position}]: submission.candidates[{c_0}].identifier.legalName"

            candidates_array[c_0]['identifier']['scheme'] = "MD-IDNO"

            if "uri" in candidates_array[c_0]['identifier']:
                candidates_array[c_0]['identifier']['uri'] = \
                    f"create submission[{position}]: submission.candidates[{c_0}].identifier.uri"

            if "additionalIdentifiers" in candidates_array[c_0]:
                additional_identifier_array = list()
                for q_0 in range(quantity_of_additional_identifiers):

                    additional_identifier_array.append(copy.deepcopy(
                        self.__payload['submission']['candidates'][0]['additionalIdentifiers'][0]
                    ))

                    additional_identifier_array[q_0]['id'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].additionalIdentifiers[{q_0}]['id']"

                    additional_identifier_array[q_0]['legalName'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].additionalIdentifiers[{q_0}]['legalName']"

                    additional_identifier_array[q_0]['scheme'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].additionalIdentifiers[{q_0}]['scheme']"

                    if "uri" in additional_identifier_array[q_0]:
                        additional_identifier_array[q_0]['uri'] = \
                            f"create submission[{position}]: submission.candidates[{c_0}].additionalIdentifiers[{q_0}]['uri']"

                candidates_array[c_0]['additionalIdentifiers'] = additional_identifier_array

            candidates_array[c_0]['address']['streetAddress'] = \
                f"create submission[{position}]: submission.candidates[{c_0}].address.streetAddress"

            if "postalCode" in candidates_array[c_0]['address']:
                candidates_array[c_0]['address']['postalCode'] = \
                    f"create submission[{position}]: submission.candidates[{c_0}].address.postalCode"

            candidates_array[c_0]['address']['addressDetails']['country']['id'] = "MD"
            candidates_array[c_0]['address']['addressDetails']['country']['scheme'] = "ISO-ALPHA2"

            candidates_array[c_0]['address']['addressDetails']['country']['description'] = \
                f"create submission[{position}]: submission.candidates[{c_0}].address.addressDetails.country.description"

            candidates_array[c_0]['address']['addressDetails']['region']['id'] = f"{random.choice(region_id_tuple)}"
            candidates_array[c_0]['address']['addressDetails']['region']['scheme'] = "CUATM"

            candidates_array[c_0]['address']['addressDetails']['region']['description'] = \
                f"create submission[{position}]: submission.candidates[{c_0}].address.addressDetails.region.description"

            candidates_array[c_0]['address']['addressDetails']['locality']['id'] = \
                get_locality_id_according_with_region_id(
                    candidates_array[c_0]['address']['addressDetails']['region']['id']
                )

            candidates_array[c_0]['address']['addressDetails']['locality']['scheme'] = \
                f"{random.choice(locality_scheme_tuple)}"

            candidates_array[c_0]['address']['addressDetails']['locality']['description'] = \
                f"create submission[{position}]: submission.candidates[{c_0}].address.addressDetails.locality." \
                f"description"

            candidates_array[c_0]['contactPoint']['name'] = \
                f"create submission[{position}]: submission.candidates[{c_0}].contactPoint.name"

            candidates_array[c_0]['contactPoint']['email'] = \
                f"create submission[{position}]: submission.candidates[{c_0}].contactPoint.email"

            candidates_array[c_0]['contactPoint']['telephone'] = \
                f"create submission[{position}]: submission.candidates[{c_0}].contactPoint.telephone"

            if "faxNumber" in candidates_array[c_0]['contactPoint']:
                candidates_array[c_0]['contactPoint']['faxNumber'] = \
                    f"create submission[{position}]: submission.candidates[{c_0}].contactPoint.faxNumber"

            if "url" in candidates_array[c_0]['contactPoint']:
                candidates_array[c_0]['contactPoint']['url'] = \
                    f"create submission[{position}]: submission.candidates[{c_0}].contactPoint.url"

            if "persones" in candidates_array[c_0]:
                persones_array = list()
                for p_0 in range(quantity_of_persones):

                    persones_array.append(copy.deepcopy(
                        self.__payload['submission']['candidates'][0]['persones'][0]
                    ))

                    persones_array[p_0]['id'] = f"{c_0 + p_0}"

                    persones_array[p_0]['title'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].persones[{p_0}].title"

                    persones_array[p_0]['title'] = f"{random.choice(person_title_tuple)}"

                    persones_array[p_0]['name'] = f"create submission[{position}]: submission.candidates[{c_0}]." \
                                                  f"perones[{p_0}].name"

                    persones_array[p_0]['identifier']['scheme'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].perones[{p_0}].identifier.scheme"

                    persones_array[p_0]['identifier']['id'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].perones[{p_0}].identifier.id"

                    if "uri" in persones_array[p_0]['identifier']:
                        persones_array[p_0]['identifier']['uri'] = \
                            f"create submission[{position}]: submission.candidates[{c_0}].perones[{p_0}].identifier.uri"

                    business_functions_array = list()
                    for bf_0 in range(quantity_of_business_functions):
                        business_functions_array.append(copy.deepcopy(
                            self.__payload['submission']['candidates'][0]['persones'][0]['businessFunctions'][0]
                        ))

                        business_functions_array[bf_0]['id'] = f"{c_0 + p_0 + bf_0}"
                        business_functions_array[bf_0]['type'] = f"{random.choice(business_function_type_1_tuple)}"

                        business_functions_array[bf_0]['jobTitle'] = \
                            f"create submission[{position}]: submission.candidates[{c_0}].perones[{p_0}]." \
                            f"businessFunctions[{bf_0}].jobTitle"

                        business_functions_array[bf_0]['period']['startDate'] = self.__date.old_period()[0]

                        if "documents" in business_functions_array[bf_0]:
                            bf_documents_array = list()
                            for bf_1 in range(quantity_of_bf_documents):

                                bf_documents_array.append(copy.deepcopy(
                                    self.__payload['submission']['candidates'][0]['persones'][0][
                                        'businessFunctions'][0]['documents'][0]
                                ))

                                bf_documents_array[bf_1]['id'] = self.__document.uploading_document()[0]["data"]["id"]
                                bf_documents_array[bf_1]['documentType'] = "regulatoryDocument"

                                bf_documents_array[bf_1]['title'] = \
                                    f"create submission[{position}]n: submission.candidates[{c_0}].perones[{p_0}]." \
                                    f"businessFunctions[{bf_0}].documents[{bf_1}].title"

                                if "description" in bf_documents_array[bf_1]:
                                    bf_documents_array[bf_1]['description'] = \
                                        f"create submission[{position}]: submission.candidates[{c_0}].perones[{p_0}]." \
                                        f"businessFunctions[{bf_0}].documents[{bf_1}].description"

                            business_functions_array[bf_0]['documents'] = bf_documents_array
                    persones_array[p_0]['businessFunctions'] = business_functions_array
                candidates_array[c_0]['persones'] = persones_array

            candidates_array[c_0]['details']['typeOfSupplier'] = f"{random.choice(type_of_supplier_tuple)}"
            if "mainEconomicActivities" in candidates_array[c_0]['details']:
                main_economic_activities_array = list()
                for d_0 in range(quantity_of_main_economic_activities):

                    main_economic_activities_array.append(copy.deepcopy(
                        self.__payload['submission']['candidates'][0]['details']['mainEconomicActivities'][0]
                    ))

                    main_economic_activities_array[d_0]['scheme'] = "MD-CAEM"
                    main_economic_activities_array[d_0]['id'] = f"{c_0 + d_0}"

                    main_economic_activities_array[d_0]['description'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].details." \
                        f"mainEconomicActivities[{d_0}].description"

                    if "uri" in main_economic_activities_array[d_0]:

                        main_economic_activities_array[d_0]['uri'] = \
                            f"create submission[{position}]: submission.candidates[{c_0}].details." \
                            f"mainEconomicActivities[{d_0}].uri"

                candidates_array[c_0]['details']['mainEconomicActivities'] = main_economic_activities_array
            candidates_array[c_0]['details']['scale'] = f"{random.choice(scale_tuple)}"

            if "bankAccounts" in candidates_array[c_0]['details']:
                bank_accounts_array = list()
                for d_1 in range(quantity_of_bank_accounts):

                    bank_accounts_array.append(copy.deepcopy(
                        self.__payload['submission']['candidates'][0]['details']['bankAccounts'][0]
                    ))

                    bank_accounts_array[d_1]['description'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].details.bankAccounts[{d_1}].description"

                    bank_accounts_array[d_1]['bankName'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].details.bankAccounts[{d_1}].bankName"

                    bank_accounts_array[d_1]['address']['streetAddress'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].details.bankAccounts[{d_1}].address." \
                        f"streetAddress"

                    if "postalCode" in bank_accounts_array[d_1]['address']:
                        bank_accounts_array[d_1]['address']['postalCode'] = \
                            f"create submission[{position}]: submission.candidates[{c_0}].details.bankAccounts[{d_1}].address." \
                            f"postalCode"

                    bank_accounts_array[d_1]['address']['addressDetails']['country']['id'] = "MD"

                    bank_accounts_array[d_1]['address']['addressDetails']['country']['description'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].details.bankAccounts[{d_1}].address." \
                        f"addressDetails.country.description"

                    bank_accounts_array[d_1]['address']['addressDetails']['country']['scheme'] = "ISO-ALPHA2"

                    bank_accounts_array[d_1]['address']['addressDetails']['region'][
                        'id'] = f"{random.choice(region_id_tuple)}"

                    bank_accounts_array[d_1]['address']['addressDetails']['region']['description'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].details.bankAccounts[{d_1}].address." \
                        f"addressDetails.region.description"

                    bank_accounts_array[d_1]['address']['addressDetails']['region']['scheme'] = "CUATM"

                    bank_accounts_array[d_1]['address']['addressDetails']['locality']['id'] = \
                        get_locality_id_according_with_region_id(
                            bank_accounts_array[d_1]['address']['addressDetails']['region']['id']
                        )

                    bank_accounts_array[d_1]['address']['addressDetails']['locality']['description'] = \
                        f"create submission[{position}]: submission.candidates[{c_0}].details.bankAccounts[{d_1}].address." \
                        f"addressDetails.locality.description"

                    bank_accounts_array[d_1]['address']['addressDetails']['locality']['scheme'] = "CUATM"

                    bank_accounts_array[d_1]['identifier']['scheme'] = "UA-MFO"
                    bank_accounts_array[d_1]['identifier']['id'] = f"{c_0 + d_1}"

                    bank_accounts_array[d_1]['accountIdentification']['scheme'] = "IBAN"
                    bank_accounts_array[d_1]['accountIdentification']['id'] = f"{c_0 + d_1}"

                    if "additionalAccountIdentifiers" in bank_accounts_array[d_1]:
                        additional_account_identifiers_array = list()
                        for d_2 in range(quantity_of_additional_account_identifiers):
                            additional_account_identifiers_array.append(copy.deepcopy(
                                self.__payload['submission']['candidates'][0]['details'][
                                    'bankAccounts'][0]['additionalAccountIdentifiers'][0]
                            ))

                            bank_accounts_array[d_1]['additionalAccountIdentifiers'][d_2]['scheme'] = "fiscal"
                            bank_accounts_array[d_1]['additionalAccountIdentifiers'][d_2]['id'] = f"{c_0 + d_1 + d_2}"
                candidates_array[c_0]['details']['bankAccounts'] = bank_accounts_array

            candidates_array[c_0]['details']['legalForm']['scheme'] = 'MD-CFOJ'
            candidates_array[c_0]['details']['legalForm']['id'] = f"{c_0}"

            candidates_array[c_0]['details']['legalForm']['description'] = \
                f"create submission[{position}]: submission.candidates[{c_0}].details.legalForm.description"

            if "uri" in candidates_array[c_0]['details']['legalForm']:
                candidates_array[c_0]['details']['legalForm']['uri'] = \
                    f"create submission[{position}]: submission.candidates[{c_0}].details.legalForm.uri"

        self.__payload['submission']['candidates'] = candidates_array

        # Enrich 'submission.requirementResponses' array:
        if "requirementResponses" in self.__payload['submission']:
            requirement_responses_array = list()
            for c_0 in range(quantity_of_candidates):
                for q_0 in range(len(self.__actual_fe_release['releases'][0]['tender']['criteria'])):

                    for q_1 in range(len(self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                             'requirementGroups'][0]['requirements'])):

                        requirement_responses_object = copy.deepcopy(
                            self.__payload['submission']['requirementResponses'][0])

                        requirement_responses_object['id'] = f"{len(requirement_responses_array)}"

                        if "expectedValue" in self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                'requirementGroups'][0]['requirements'][q_1]:

                            requirement_responses_object['value'] = self.__actual_fe_release['releases'][0]['tender'][
                                'criteria'][q_0]['requirementGroups'][0]['requirements'][q_1]['expectedValue']

                        elif "minValue" in self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                'requirementGroups'][0]['requirements'][q_1]:

                            requirement_responses_object['value'] = self.__actual_fe_release['releases'][0]['tender'][
                                'criteria'][q_0]['requirementGroups'][0]['requirements'][q_1]['minValue']

                        elif "maxValue" in self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                'requirementGroups'][0]['requirements'][q_1]:

                            requirement_responses_object['value'] = self.__actual_fe_release['releases'][0]['tender'][
                                'criteria'][q_0]['requirementGroups'][0]['requirements'][q_1]['maxValue']

                        requirement_responses_object['requirement']['id'] = \
                            self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                'requirementGroups'][0]['requirements'][q_1]['id']

                        requirement_responses_object['relatedCandidate']['name'] = \
                            self.__payload['submission']['candidates'][c_0]['name']

                        requirement_responses_object['relatedCandidate']['identifier']['id'] = \
                            self.__payload['submission']['candidates'][c_0]['identifier']['id']

                        requirement_responses_object['relatedCandidate']['identifier']['scheme'] = \
                            self.__payload['submission']['candidates'][c_0]['identifier']['scheme']

                        if "evidences" in requirement_responses_object:
                            evidences_array = list()
                            for q_2 in range(quantity_of_evidences):
                                evidences_array.append(copy.deepcopy(
                                    self.__payload['submission']['requirementResponses'][0]['evidences'][0]))

                                evidences_array[q_2]['id'] = f"{c_0+q_0+q_1+q_2}"

                                evidences_array[q_2]['title'] = \
                                    f"create submission[{position}]: submission.requirementResponses[{q_0}].evidences[{q_2}].title"

                                evidences_array[q_2]['description'] = \
                                    f"create submission[{position}]: submission.requirementResponses[{q_0}].evidences[{q_2}]." \
                                    f"description"

                                document_was_uploaded = self.__document.uploading_document()

                                evidences_array[q_2]['relatedDocument']['id'] = \
                                    f"{document_was_uploaded[0]['data']['id']}"

                            requirement_responses_object['evidences'] = evidences_array
                        requirement_responses_array.append(requirement_responses_object)

                        requirement_responses_array = \
                            set_unique_temporary_id_for_requirement_responses_evidences(requirement_responses_array)

            self.__payload['submission']['requirementResponses'] = requirement_responses_array

        # Enrich 'submission.documents' array:
        if "documents" in self.__payload['submission']:
            documents_array = list()
            for sd_0 in range(quantity_of_documents):
                documents_array.append(copy.deepcopy(self.__payload['submission']['documents'][0]))

                documents_array[sd_0]['documentType'] = \
                    f"{random.choice(documentType_for_create_submission_framework_agreement)}"

                documents_array[sd_0]['id'] = self.__document.uploading_document()[0]["data"]["id"]
                documents_array[sd_0]['title'] = f"create submission[{position}]: submission.documents[{sd_0}].title"
                if "description" in documents_array[sd_0]:

                    documents_array[sd_0]['description'] = \
                        f"create submission[{position}]: submission.documents[{sd_0}].description"

            evidences_documents_array = list()
            if "requirementResponses" in self.__payload['submission']:
                for e_0 in range(len(self.__payload['submission']['requirementResponses'])):
                    if "evidences" in self.__payload['submission']['requirementResponses'][e_0]:
                        for e_1 in range(len(self.__payload['submission']['requirementResponses'][e_0]['evidences'])):

                            if "relatedDocument" in self.__payload['submission']['requirementResponses'][e_0][
                                    'evidences'][e_1]:
                                evidences_document_object = copy.deepcopy(self.__payload['submission']['documents'][0])

                                evidences_document_object['id'] = \
                                    self.__payload['submission']['requirementResponses'][e_0][
                                        'evidences'][e_1]['relatedDocument']['id']

                                evidences_document_object['documentType'] = \
                                    f"{random.choice(documentType_for_create_submission_framework_agreement)}"

                                evidences_document_object['title'] = \
                                    f"create fe: tender.documents{len(evidences_documents_array)}.title"

                                evidences_document_object['description'] = \
                                    f"create fe: tender.documents{len(evidences_documents_array)}.description"

                                evidences_documents_array.append(evidences_document_object)

            self.__payload['submission']['documents'] = documents_array + evidences_documents_array

    def __del__(self):
        print(f"The instance of CreateSubmissionPayload class: {__name__} was deleted.")
