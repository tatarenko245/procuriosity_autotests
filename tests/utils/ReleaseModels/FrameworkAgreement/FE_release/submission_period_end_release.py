"""Prepare the expected releases of the submission period end process, framework agreement procedures."""
import copy

from tests.utils.functions_collection.functions import get_value_from_country_csv, get_value_from_region_csv, \
    get_value_from_locality_csv, is_it_uuid
from tests.utils.services.e_mdm_service import MdmService


class SubmissionPeriodEndRelease:
    """This class creates instance of release."""

    def __init__(self, environment, host_to_service, country, language, pmd, cpid, ocid, previous_fe_release,
                 list_of_submission_payloads, list_of_submission_messages, list_of_withdrawn_submission_id,
                 actual_fe_release, actual_message):

        self.__host = host_to_service
        self.__country = country
        self.__language = language
        self.__pmd = pmd
        self.__cpid = cpid
        self.__ocid = ocid
        self.__previous_fe_release = previous_fe_release
        self.__list_of_submission_payloads = list_of_submission_payloads
        self.__list_of_submission_messages = list_of_submission_messages
        self.__list_of_withdrawn_submission_id = list_of_withdrawn_submission_id
        self.__actual_fe_release = actual_fe_release
        self.__actual_message = actual_message

        self.__mdm_class = MdmService(host_to_service, environment)

        try:
            if environment == "dev":
                self.__metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"

                self.__extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
                ]

                self.__publisher_name = "M-Tender"
                self.__publisher_uri = "https://www.mtender.gov.md"
                self.__metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
                self.__metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"

            elif environment == "sandbox":
                self.__metadata_tender_url = "http://public.eprocurement.systems/tenders"

                self.__extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.json"
                ]

                self.__publisher_name = "Viešųjų pirkimų tarnyba"
                self.__publisher_uri = "https://vpt.lrv.lt"
                self.__metadata_document_url = "http://storage.eprocurement.systems/get"
                self.__metadata_budget_url = "http://public.eprocurement.systems/budgets"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

        self.__expected_fe_release = {
            "uri": f"{self.__metadata_tender_url}/{self.__cpid}/{self.__ocid}",
            "version": "1.1",
            "extensions": self.__extensions,
            "publisher": {
                "name": self.__publisher_name,
                "uri": self.__publisher_uri
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": self.__actual_fe_release['publishedDate'],
            "releases": [
                {
                    "ocid": "",
                    "id": "",
                    "date": "",
                    "tag": [
                        ""
                    ],
                    "initiationType": "",
                    "language": "",
                    "parties": [
                        {
                            "id": "",
                            "name": "",
                            "identifier": {
                                "scheme": "",
                                "id": "",
                                "legalName": "",
                                "uri": ""
                            },
                            "address": {
                                "streetAddress": "",
                                "postalCode": "",
                                "addressDetails": {
                                    "country": {
                                        "scheme": "",
                                        "id": "MD",
                                        "description": "",
                                        "uri": ""
                                    },
                                    "region": {
                                        "scheme": "",
                                        "id": "",
                                        "description": "",
                                        "uri": ""
                                    },
                                    "locality": {
                                        "scheme": "",
                                        "id": "",
                                        "description": ""
                                    }
                                }
                            },
                            "additionalIdentifiers": [
                                {
                                    "scheme": "",
                                    "id": "",
                                    "legalName": "",
                                    "uri": ""
                                }
                            ],
                            "contactPoint": {
                                "name": "",
                                "email": "",
                                "telephone": "",
                                "faxNumber": "",
                                "url": ""
                            },
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
                                "bankAccounts": [
                                    {
                                        "description": "",
                                        "bankName": "",
                                        "address": {
                                            "streetAddress": "",
                                            "postalCode": "",
                                            "addressDetails": {
                                                "country": {
                                                    "scheme": "",
                                                    "id": "MD",
                                                    "description": ""
                                                },
                                                "region": {
                                                    "scheme": "",
                                                    "id": "",
                                                    "description": ""
                                                },
                                                "locality": {
                                                    "scheme": "",
                                                    "id": "",
                                                    "description": ""
                                                }
                                            }
                                        },
                                        "identifier": {
                                            "id": "",
                                            "scheme": ""
                                        },
                                        "accountIdentification": {
                                            "id": "",
                                            "scheme": ""
                                        },
                                        "additionalAccountIdentifiers": [{
                                            "scheme": "",
                                            "id": ""
                                        }]
                                    }
                                ],
                                "legalForm": {
                                    "id": "",
                                    "scheme": "",
                                    "description": "",
                                    "uri": ""
                                },
                                "scale": ""
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
                                                    "description": "",
                                                    "url": "",
                                                    "datePublished": ""
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ],
                            "roles": [
                                "candidate"
                            ]
                        }
                    ],
                    "tender": {
                        "id": "",
                        "status": "",
                        "statusDetails": "",
                        "criteria": [
                            {
                                "id": "",
                                "title": "",
                                "source": "",
                                "description": "",
                                "requirementGroups": [
                                    {
                                        "id": "",
                                        "description": "",
                                        "requirements": [
                                            {
                                                "id": "",
                                                "title": "",
                                                "dataType": "",
                                                "status": "",
                                                "datePublished": "",
                                                "description": ""
                                            }
                                        ]
                                    }
                                ],
                                "relatesTo": "",
                                "classification": {
                                    "scheme": "",
                                    "id": ""
                                }
                            }
                        ],
                        "otherCriteria": {
                            "reductionCriteria": "",
                            "qualificationSystemMethods": [
                                ""
                            ]
                        },
                        "enquiryPeriod": {
                            "startDate": "",
                            "endDate": ""
                        },
                        "hasEnquiries": False,
                        "documents": [
                            {
                                "id": "",
                                "documentType": "",
                                "title": "",
                                "description": "",
                                "url": "",
                                "datePublished": ""
                            }
                        ],
                        "submissionMethod": [
                            ""
                        ],
                        "submissionMethodDetails": "",
                        "submissionMethodRationale": [
                            ""
                        ],
                        "requiresElectronicCatalogue": False,
                        "procurementMethodModalities": [
                            ""
                        ],
                        "secondStage": {
                            "minimumCandidates": 0,
                            "maximumCandidates": 0
                        }
                    },
                    "submissions": {
                        "details": [
                            {
                                "id": "",
                                "date": "",
                                "status": "",
                                "requirementResponses": [
                                    {
                                        "id": "",
                                        "value": "",
                                        "requirement": {
                                            "id": ""
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
                                        "id": "",
                                        "name": ""
                                    }
                                ],
                                "documents": [
                                    {
                                        "id": "",
                                        "documentType": "",
                                        "title": "",
                                        "description": "",
                                        "url": "",
                                        "datePublished": ""
                                    }
                                ]
                            }
                        ]
                    },
                    "qualifications": [
                        {
                            "id": "",
                            "date": "",
                            "status": "",
                            "statusDetails": "",
                            "relatedSubmission": ""
                        }
                    ],
                    "hasPreviousNotice": True,
                    "purposeOfNotice": {
                        "isACallForCompetition": True
                    },
                    "relatedProcesses": [
                        {
                            "id": "",
                            "relationship": [
                                ""
                            ],
                            "scheme": "",
                            "identifier": "",
                            "uri": ""
                        }
                    ],
                    "preQualification": {
                        "period": {
                            "startDate": "",
                            "endDate": ""
                        },
                        "qualificationPeriod": {
                            "startDate": ""
                        }
                    }
                }
            ]
        }

    def build_expected_fe_release(self):
        """Build FE release."""

        # Build 'releases[0]' section:
        # FR.COM-3.2.5 (https://ustudio.atlassian.net/wiki/spaces/ES/pages/1258717251/R10.3.2+eNotice+Create+FE+v1):
        self.__expected_fe_release['releases'][0]['ocid'] = self.__previous_fe_release['releases'][0]['ocid']

        # FR.COM-3.2.21 (https://ustudio.atlassian.net/wiki/spaces/ES/pages/1258717251/R10.3.2+eNotice+Create+FE+v1)
        self.__expected_fe_release['releases'][0]['id'] = \
            f"{self.__ocid}-{self.__actual_fe_release['releases'][0]['id'][46:59]}"

        # FR.COM-3.2.23 (https://ustudio.atlassian.net/wiki/spaces/ES/pages/1258717251/R10.3.2+eNotice+Create+FE+v1)
        self.__expected_fe_release['releases'][0]['language'] = self.__previous_fe_release['releases'][0]['language']

        # FR.COM-3.2.4 (https://ustudio.atlassian.net/wiki/spaces/ES/pages/1258717251/R10.3.2+eNotice+Create+FE+v1)
        self.__expected_fe_release['releases'][0]['initiationType'] = \
            self.__previous_fe_release['releases'][0]['initiationType']

        self.__expected_fe_release['releases'][0]['date'] = self.__actual_message['data']['operationDate']

        if self.__previous_fe_release['releases'][0]['tag'] == ["tender"]:
            # FR.COM-3.2.2 (https://ustudio.atlassian.net/wiki/spaces/ES/pages/1258717251/R10.3.2+eNotice+Create+FE+v1)
            self.__expected_fe_release['releases'][0]['tag'] = self.__previous_fe_release['releases'][0]['tag']
        elif self.__previous_fe_release['releases'][0]['tag'] == ["tenderAmendment"]:
            # FR.COM-3.2.1 (https://ustudio.atlassian.net/wiki/spaces/ES/pages/1266286655/R10.3.2+eNotice+Amend+FE+v1):
            self.__expected_fe_release['releases'][0]['tag'] = self.__previous_fe_release['releases'][0]['tag']
        else:
            raise ValueError("Incorrect value for 'releases[0].tag' of previous fe release.")

        # Build 'releases[0].parties' section:
        old_parties_array = list()

        for p_0 in range(len(self.__actual_fe_release['releases'][0]['parties'])):
            if self.__actual_fe_release['releases'][0]['parties'][p_0]['roles'] == ["buyer"]:
                old_parties_array.append(self.__actual_fe_release['releases'][0]['parties'][p_0])
            elif self.__actual_fe_release['releases'][0]['parties'][p_0]['roles'] == ["procuringEntity"]:
                old_parties_array.append(self.__actual_fe_release['releases'][0]['parties'][p_0])

        new_parties_array = list()
        for p_0 in range(len(self.__list_of_submission_payloads)):
            temp_new_parties_array = list()
            for p_1 in range(len(self.__list_of_submission_payloads[p_0]['submission']['candidates'])):
                temp_new_parties_array.append(copy.deepcopy(self.__expected_fe_release['releases'][0]['parties'][0]))
                candidate_from_payload = self.__list_of_submission_payloads[p_0]['submission']['candidates'][p_1]

                temp_new_parties_array[p_1]['id'] = \
                    f"{candidate_from_payload['identifier']['scheme']}-{candidate_from_payload['identifier']['id']}"

                temp_new_parties_array[p_1]['name'] = candidate_from_payload['name']

                # Prepare 'identifier' object:
                temp_new_parties_array[p_1]['identifier']['scheme'] = candidate_from_payload['identifier']['scheme']
                temp_new_parties_array[p_1]['identifier']['id'] = candidate_from_payload['identifier']['id']
                temp_new_parties_array[p_1]['identifier']['legalName'] = candidate_from_payload['identifier']['legalName']
                if "uri" in candidate_from_payload['identifier']:
                    temp_new_parties_array[p_1]['identifier']['uri'] = candidate_from_payload['identifier']['uri']
                else:
                    del temp_new_parties_array[p_1]['identifier']['uri']

                # Prepare 'address' object:
                temp_new_parties_array[p_1]['address']['streetAddress'] = candidate_from_payload['address']['streetAddress']
                if "postalCode" in candidate_from_payload['address']:
                    temp_new_parties_array[p_1]['address']['postalCode'] = candidate_from_payload['address']['postalCode']
                else:
                    del temp_new_parties_array[p_1]['address']['postalCode']

                try:
                    f"""
                    Prepare 'addressDetails' object for temp_new_parties_array[{p_1}]['address'].
                    """
                    country_data = get_value_from_country_csv(
                        country=candidate_from_payload['address']['addressDetails']['country']['id'],
                        language=self.__language
                    )
                    expected_country_object = [{
                        "scheme": country_data[2].upper(),
                        "id": candidate_from_payload['address']['addressDetails']['country']['id'],
                        "description": country_data[1],
                        "uri": country_data[3]
                    }]

                    region_data = get_value_from_region_csv(
                        region=candidate_from_payload['address']['addressDetails']['region']['id'],
                        country=candidate_from_payload['address']['addressDetails']['country']['id'],
                        language=self.__language
                    )
                    expected_region_object = [{
                        "scheme": region_data[2],
                        "id": candidate_from_payload['address']['addressDetails']['region']['id'],
                        "description": region_data[1],
                        "uri": region_data[3]
                    }]

                    if candidate_from_payload['address']['addressDetails']['locality']['scheme'] == "CUATM":

                        locality_data = get_value_from_locality_csv(
                            locality=candidate_from_payload['address']['addressDetails']['locality']['id'],
                            region=candidate_from_payload['address']['addressDetails']['region']['id'],
                            country=candidate_from_payload['address']['addressDetails']['country']['id'],
                            language=self.__language
                        )
                        expected_locality_object = [{
                            "scheme": locality_data[2],
                            "id": candidate_from_payload['address']['addressDetails']['locality']['id'],
                            "description": locality_data[1],
                            "uri": locality_data[3]
                        }]
                    else:
                        expected_locality_object = [{
                            "scheme": candidate_from_payload['address']['addressDetails']['locality']['scheme'],
                            "id": candidate_from_payload['address']['addressDetails']['locality']['id'],
                            "description": candidate_from_payload['address']['addressDetails']['locality'][
                                'description']
                        }]

                    temp_new_parties_array[p_1]['address']['addressDetails']['country'] = expected_country_object[0]
                    temp_new_parties_array[p_1]['address']['addressDetails']['region'] = expected_region_object[0]
                    temp_new_parties_array[p_1]['address']['addressDetails']['locality'] = expected_locality_object[0]
                except ValueError:
                    raise ValueError(f"Impossible to prepare Prepare 'addressDetails' object for "
                                     f"temp_new_parties_array[{p_0 + p_1}]['address']")

                # Prepare 'additionalIdentifiers' array:
                if "additionalIdentifiers" in candidate_from_payload:
                    additional_identifiers_array = list()
                    for p_2 in range(len(candidate_from_payload['additionalIdentifiers'])):
                        additional_identifiers_array.append(copy.deepcopy(
                            self.__expected_fe_release['releases'][0]['parties'][0]['additionalIdentifiers'][0]
                        ))

                        additional_identifiers_array[p_2]['scheme'] = \
                            candidate_from_payload['additionalIdentifiers'][p_2]['scheme']

                        additional_identifiers_array[p_2]['id'] = \
                            candidate_from_payload['additionalIdentifiers'][p_2]['id']

                        additional_identifiers_array[p_2]['legalName'] = \
                            candidate_from_payload['additionalIdentifiers'][p_2]['legalName']

                        if "uri" in candidate_from_payload['additionalIdentifiers'][p_2]:
                            additional_identifiers_array[p_2]['uri'] = \
                                candidate_from_payload['additionalIdentifiers'][p_2]['uri']
                        else:
                            del additional_identifiers_array[p_2]['uri']
                    temp_new_parties_array[p_1]['additionalIdentifiers'] = additional_identifiers_array
                else:
                    del temp_new_parties_array[p_1]['additionalIdentifiers']

                # Prepare 'contactPoint' object:
                temp_new_parties_array[p_1]['contactPoint']['name'] = candidate_from_payload['contactPoint']['name']
                temp_new_parties_array[p_1]['contactPoint']['email'] = candidate_from_payload['contactPoint']['email']

                temp_new_parties_array[p_1]['contactPoint']['telephone'] = \
                    candidate_from_payload['contactPoint']['telephone']

                if "faxNumber" in candidate_from_payload['contactPoint']:
                    temp_new_parties_array[p_1]['contactPoint']['faxNumber'] = \
                        candidate_from_payload['contactPoint']['faxNumber']
                else:
                    del temp_new_parties_array[p_1]['contactPoint']['faxNumber']

                if "url" in candidate_from_payload['contactPoint']:
                    temp_new_parties_array[p_1]['contactPoint']['url'] = \
                        candidate_from_payload['contactPoint']['url']
                else:
                    del temp_new_parties_array[p_1]['contactPoint']['url']

                # Prepare 'details' object:
                if "typeOfSupplier" in candidate_from_payload['details']:
                    temp_new_parties_array[p_1]['details']['typeOfSupplier'] = \
                        candidate_from_payload['details']['typeOfSupplier']
                else:
                    del temp_new_parties_array[p_1]['details']['typeOfSupplier']

                if "mainEconomicActivities" in candidate_from_payload['details']:
                    main_economic_activities_array = list()
                    for m_0 in range(len(candidate_from_payload['details']['mainEconomicActivities'])):
                        main_economic_activities_array.append(copy.deepcopy(
                            self.__expected_fe_release['releases'][0]['parties'][0]['details'][
                                'mainEconomicActivities'][0]
                        ))

                        main_economic_activities_array[m_0]['scheme'] = \
                            candidate_from_payload['details']['mainEconomicActivities'][m_0]['scheme']

                        main_economic_activities_array[m_0]['id'] = \
                            candidate_from_payload['details']['mainEconomicActivities'][m_0]['id']

                        main_economic_activities_array[m_0]['description'] = \
                            candidate_from_payload['details']['mainEconomicActivities'][m_0]['description']

                        if "uri" in candidate_from_payload['details']['mainEconomicActivities'][m_0]:
                            main_economic_activities_array[m_0]['uri'] = \
                                candidate_from_payload['details']['mainEconomicActivities'][m_0]['uri']
                        else:
                            del main_economic_activities_array[m_0]['uri']
                    temp_new_parties_array[p_1]['details']['mainEconomicActivities'] = main_economic_activities_array
                else:
                    del temp_new_parties_array[p_1]['details']['mainEconomicActivities']

                if "bankAccounts" in candidate_from_payload['details']:
                    bank_accounts_array = list()
                    for b_0 in range(len(candidate_from_payload['details']['bankAccounts'])):
                        bank_accounts_array.append(copy.deepcopy(
                            self.__expected_fe_release['releases'][0]['parties'][0]['details']['bankAccounts'][0]
                        ))

                        bank_accounts_array[b_0]['description'] = \
                            candidate_from_payload['details']['bankAccounts'][b_0]['description']

                        bank_accounts_array[b_0]['bankName'] = \
                            candidate_from_payload['details']['bankAccounts'][b_0]['bankName']

                        bank_accounts_array[b_0]['address']['streetAddress'] = \
                            candidate_from_payload['details']['bankAccounts'][b_0]['address']['streetAddress']

                        if "postalCode" in candidate_from_payload['details']['bankAccounts'][b_0]['address']:
                            bank_accounts_array[b_0]['address']['postalCode'] = \
                                candidate_from_payload['details']['bankAccounts'][b_0]['address']['postalCode']
                        else:
                            del bank_accounts_array[b_0]['address']['postalCode']

                        try:
                            """
                            Prepare 'addressDetails' object for ank_accounts_array[b_0]['address'].
                            """
                            country_data = get_value_from_country_csv(
                                country=candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                    'addressDetails']['country']['id'],
                                language=self.__language
                            )
                            expected_country_object = [{
                                "scheme": country_data[2].upper(),
                                "id": candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                    'addressDetails']['country']['id'],
                                "description": country_data[1],
                                "uri": country_data[3]
                            }]

                            region_data = get_value_from_region_csv(
                                region=candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                    'addressDetails']['region']['id'],
                                country=candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                    'addressDetails']['country']['id'],
                                language=self.__language
                            )
                            expected_region_object = [{
                                "scheme": region_data[2],
                                "id": candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                    'addressDetails']['region']['id'],
                                "description": region_data[1],
                                "uri": region_data[3]
                            }]

                            if candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                    'addressDetails']['locality']['scheme'] == "CUATM":

                                locality_data = get_value_from_locality_csv(
                                    locality=candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                        'addressDetails']['locality']['id'],
                                    region=candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                        'addressDetails']['region']['id'],
                                    country=candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                        'addressDetails']['country']['id'],
                                    language=self.__language
                                )

                                expected_locality_object = [{
                                    "scheme": locality_data[2],
                                    "id": candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                        'addressDetails']['locality']['id'],
                                    "description": locality_data[1],
                                    "uri": locality_data[3]
                                }]
                            else:
                                expected_locality_object = [{
                                    "scheme": candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                        'addressDetails']['locality']['scheme'],
                                    "id": candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                        'addressDetails']['locality']['id'],
                                    "description": candidate_from_payload['details']['bankAccounts'][b_0]['address'][
                                        'addressDetails']['locality']['description']
                                }]

                            bank_accounts_array[b_0]['address']['addressDetails']['country'] = \
                                expected_country_object[0]

                            bank_accounts_array[b_0]['address']['addressDetails']['region'] = \
                                expected_region_object[0]

                            bank_accounts_array[b_0]['address']['addressDetails']['locality'] = \
                                expected_locality_object[0]
                        except ValueError:
                            raise ValueError("Impossible to prepare Prepare 'addressDetails' object for "
                                             "ank_accounts_array[b_0]['address']")

                        bank_accounts_array[b_0]['identifier']['id'] = \
                            candidate_from_payload['details']['bankAccounts'][b_0]['identifier']['id']

                        bank_accounts_array[b_0]['identifier']['scheme'] = \
                            candidate_from_payload['details']['bankAccounts'][b_0]['identifier']['scheme']

                        bank_accounts_array[b_0]['accountIdentification']['id'] = \
                            candidate_from_payload['details']['bankAccounts'][b_0]['accountIdentification']['id']

                        bank_accounts_array[b_0]['accountIdentification']['scheme'] = \
                            candidate_from_payload['details']['bankAccounts'][b_0]['accountIdentification']['scheme']

                        if "additionalAccountIdentifiers" in candidate_from_payload['details']['bankAccounts'][b_0]:
                            additional_account_identifiers = list()
                            for b_1 in range(len(
                                    candidate_from_payload['details']['bankAccounts'][b_0][
                                        'additionalAccountIdentifiers']
                            )):
                                additional_account_identifiers.append(copy.deepcopy(
                                    self.__expected_fe_release['releases'][0]['parties'][0]['details'][
                                        'bankAccounts'][0]['additionalAccountIdentifiers'][0]
                                ))

                                additional_account_identifiers[b_1]['scheme'] = \
                                    candidate_from_payload['details']['bankAccounts'][b_0][
                                        'additionalAccountIdentifiers'][b_1]['scheme']

                                additional_account_identifiers[b_1]['id'] = \
                                    candidate_from_payload['details']['bankAccounts'][b_0][
                                        'additionalAccountIdentifiers'][b_1]['id']

                            bank_accounts_array[b_0]['additionalAccountIdentifiers'] = additional_account_identifiers
                        else:
                            del bank_accounts_array[b_0]['additionalAccountIdentifiers']

                    temp_new_parties_array[p_1]['details']['bankAccounts'] = bank_accounts_array
                else:
                    del temp_new_parties_array[p_1]['details']['bankAccounts']

                temp_new_parties_array[p_1]['details']['legalForm']['id'] = \
                    candidate_from_payload['details']['legalForm']['id']

                temp_new_parties_array[p_1]['details']['legalForm']['scheme'] = \
                    candidate_from_payload['details']['legalForm']['scheme']

                temp_new_parties_array[p_1]['details']['legalForm']['description'] = \
                    candidate_from_payload['details']['legalForm']['description']

                if "uri" in candidate_from_payload['details']['legalForm']:
                    temp_new_parties_array[p_1]['details']['legalForm']['uri'] = \
                        candidate_from_payload['details']['legalForm']['uri']
                else:
                    del temp_new_parties_array[p_1]['details']['legalForm']['uri']

                temp_new_parties_array[p_1]['details']['scale'] = candidate_from_payload['details']['scale']

                # Prepare 'persones' array:
                if "persones" in candidate_from_payload:
                    persones = list()
                    for cp_0 in range(len(candidate_from_payload['persones'])):
                        persones.append(copy.deepcopy(
                            self.__expected_fe_release['releases'][0]['parties'][0]['persones'][0]
                        ))

                        persones[cp_0]['id'] = \
                            f"{candidate_from_payload['persones'][cp_0]['identifier']['scheme']}-" \
                            f"{candidate_from_payload['persones'][cp_0]['identifier']['id']}"

                        persones[cp_0]['title'] = candidate_from_payload['persones'][cp_0]['title']
                        persones[cp_0]['name'] = candidate_from_payload['persones'][cp_0]['name']

                        persones[cp_0]['identifier']['scheme'] = \
                            candidate_from_payload['persones'][cp_0]['identifier']['scheme']

                        persones[cp_0]['identifier']['id'] = \
                            candidate_from_payload['persones'][cp_0]['identifier']['id']

                        if "uri" in candidate_from_payload['persones'][cp_0]['identifier']:
                            persones[cp_0]['identifier']['uri'] = \
                                candidate_from_payload['persones'][cp_0]['identifier']['uri']
                        else:
                            del persones[cp_0]['identifier']['uri']

                        business_functions = list()
                        for cp_1 in range(len(candidate_from_payload['persones'][cp_0]['businessFunctions'])):
                            business_functions.append(copy.deepcopy(
                                self.__expected_fe_release['releases'][0]['parties'][0]['persones'][0][
                                    'businessFunctions'][0]
                            ))

                            try:
                                """Set permanent id."""
                                for apwcr_0 in range(len(self.__actual_fe_release['releases'][0]['parties'])):
                                    if self.__actual_fe_release['releases'][0]['parties'][apwcr_0]['roles'] == \
                                            ["candidate"]:
                                        if self.__actual_fe_release['releases'][0]['parties'][apwcr_0]['id'] == \
                                                temp_new_parties_array[p_1]['id']:

                                            is_permanent_id_correct = is_it_uuid(
                                                self.__actual_fe_release['releases'][0]['parties'][apwcr_0][
                                                    'persones'][cp_0]['businessFunctions'][cp_1]['id']
                                            )
                                            if is_permanent_id_correct is True:

                                                business_functions[cp_1]['id'] = \
                                                    self.__actual_fe_release['releases'][0]['parties'][apwcr_0][
                                                        'persones'][cp_0]['businessFunctions'][cp_1]['id']
                                            else:
                                                raise ValueError(f"The 'self.__actual_fe_release['releases'][0]"
                                                                 f"['parties'][{apwcr_0}]['persones'][{cp_1}]['id']' "
                                                                 f"must be uuid.")
                            except KeyError:
                                raise KeyError("Mismatch key into path 'self.__actual_fe_release['releases'][0]["
                                               f"'parties'][*]['persones'][{cp_1}]['id']'")

                            business_functions[cp_1]['type'] = \
                                candidate_from_payload['persones'][cp_0]['businessFunctions'][cp_1]['type']

                            business_functions[cp_1]['jobTitle'] = \
                                candidate_from_payload['persones'][cp_0]['businessFunctions'][cp_1]['jobTitle']

                            business_functions[cp_1]['period']['startDate'] = \
                                candidate_from_payload['persones'][cp_0]['businessFunctions'][cp_1]['period'][
                                    'startDate']

                            if "documents" in candidate_from_payload['persones'][cp_0]['businessFunctions'][cp_1]:
                                bf_documents = list()
                                for cp_2 in range(len(
                                        candidate_from_payload['persones'][cp_0]['businessFunctions'][cp_1]['documents']
                                )):
                                    bf_documents.append(copy.deepcopy(
                                        self.__expected_fe_release['releases'][0]['parties'][0]['persones'][0][
                                            'businessFunctions'][0]['documents'][0]
                                    ))

                                    bf_documents[cp_2]['id'] = candidate_from_payload['persones'][cp_0][
                                        'businessFunctions'][cp_1]['documents'][cp_2]['id']

                                    bf_documents[cp_2]['documentType'] = candidate_from_payload['persones'][cp_0][
                                        'businessFunctions'][cp_1]['documents'][cp_2]['documentType']

                                    bf_documents[cp_2]['title'] = candidate_from_payload['persones'][cp_0][
                                        'businessFunctions'][cp_1]['documents'][cp_2]['title']

                                    if "description" in candidate_from_payload['persones'][cp_0][
                                            'businessFunctions'][cp_1]['documents'][cp_2]:
                                        bf_documents[cp_2]['description'] = candidate_from_payload['persones'][cp_0][
                                            'businessFunctions'][cp_1]['documents'][cp_2]['description']
                                    else:
                                        del bf_documents[cp_2]['description']

                                    bf_documents[cp_2]['url'] = \
                                        f"{self.__metadata_document_url}/{bf_documents[cp_2]['id']}"

                                    bf_documents[cp_2]['datePublished'] = self.__actual_message['data']['operationDate']

                                business_functions[cp_1]['documents'] = bf_documents
                            else:
                                del business_functions[cp_1]['documents']

                        persones[cp_0]['businessFunctions'] = business_functions
                    temp_new_parties_array[p_1]['persones'] = persones
                else:
                    del candidate_from_payload['persones']
                temp_new_parties_array[p_1]['roles'] = ["candidate"]

            new_parties_array += temp_new_parties_array

        # Sort 'releases[0].parties' array:
        temp_array = old_parties_array + new_parties_array
        expected_parties_array = list()
        if len(self.__actual_fe_release['releases'][0]['parties']) == len(temp_array):
            for act in range(len(self.__actual_fe_release['releases'][0]['parties'])):
                for exp in range(len(temp_array)):
                    if temp_array[exp]['id'] == self.__actual_fe_release['releases'][0]['parties'][act]['id']:
                        expected_parties_array.append(temp_array[exp])
        else:
            raise ValueError("The quantity of actual 'releases[0].parties' array != expected 'releases[0].parties'.")
        self.__expected_fe_release['releases'][0]['parties'] = expected_parties_array

        # Build 'releases[0].tender' object:
        # FR.COM-3.2.3 (https://ustudio.atlassian.net/wiki/spaces/ES/pages/1266286655/R10.3.2+eNotice+Amend+FE+v1):
        self.__expected_fe_release['releases'][0]['tender']['id'] = \
            self.__previous_fe_release['releases'][0]['tender']['id']

        # (https://ustudio.atlassian.net/wiki/spaces/ES/pages/2736128006/10.0.0.2+Modify+Tender):
        if "qualifications" in self.__expected_fe_release['releases'][0]:
            self.__expected_fe_release['releases'][0]['tender']['status'] = "active"
            self.__expected_fe_release['releases'][0]['tender']['statusDetails'] = "qualification"
        else:
            self.__expected_fe_release['releases'][0]['tender']['status'] = "unsuccessful"
            self.__expected_fe_release['releases'][0]['tender']['statusDetails'] = "lackOfSubmissions"

        # Prepare 'releases[0].tender.criteria' array:
        old_criteria_array = list()
        if "criteria" in self.__previous_fe_release['releases'][0]['tender']:
            old_criteria_array = self.__previous_fe_release['releases'][0]['tender']['criteria']

        # FR.COM-3.2.3 (https://ustudio.atlassian.net/wiki/spaces/ES/pages/1266286655/R10.3.2+eNotice+Amend+FE+v1):
        criteria_from_mdm = self.__mdm_class.get_criteria(
            language=self.__language,
            country=self.__country,
            pmd=self.__pmd,
            phase="qualification"
        )
        # (https://ustudio.atlassian.net/wiki/spaces/ES/pages/2739142677/10.0.0.13+Create+Criteria+For+
        # Procuring+Entity)
        new_criteria_array = list()
        if len(criteria_from_mdm['data']) > 0:
            for ec_0 in range(len(criteria_from_mdm['data'])):
                new_criteria_array.append(copy.deepcopy(
                    self.__expected_fe_release['releases'][0]['tender']['criteria'][0]
                ))

                new_criteria_array[ec_0]['id'] = criteria_from_mdm['data'][ec_0]['id']
                new_criteria_array[ec_0]['title'] = criteria_from_mdm['data'][ec_0]['title']

                # (https://ustudio.atlassian.net/wiki/spaces/ES/pages/915275865/R10.1.12+eAccess+
                # Create+Criteria+For+Procuring+Entity):
                # # FR.COM-1.12.1
                new_criteria_array[ec_0]['source'] = "procuringEntity"

                # FR.COM-1.12.5:
                new_criteria_array[ec_0]['relatesTo'] = "qualification"

                if "description" in criteria_from_mdm['data'][ec_0]:
                    new_criteria_array[ec_0]['description'] = \
                        criteria_from_mdm['data'][ec_0]['description']
                else:
                    del new_criteria_array[ec_0]['description']

                # FR.COM-1.12.6:
                new_criteria_array[ec_0]['classification'] = \
                    criteria_from_mdm['data'][ec_0]['classification']

                criteria_groups_from_mdm = self.__mdm_class.get_requirement_groups(
                    language=self.__language,
                    country=self.__country,
                    pmd=self.__pmd,
                    phase="qualification",
                    criterion_id=new_criteria_array[ec_0]['id']
                )
                del new_criteria_array[ec_0]['requirementGroups'][0]
                if len(criteria_groups_from_mdm['data']) > 0:
                    for ec_1 in range(len(criteria_groups_from_mdm['data'])):
                        new_criteria_array[ec_0]['requirementGroups'].append(copy.deepcopy(
                            self.__expected_fe_release['releases'][0]['tender']['criteria'][0]['requirementGroups'][0]
                        ))

                        new_criteria_array[ec_0]['requirementGroups'][ec_1]['id'] = \
                            criteria_groups_from_mdm['data'][ec_1]['id']

                        if "description" in criteria_groups_from_mdm['data'][ec_1]:
                            new_criteria_array[ec_0]['requirementGroups'][ec_1]['description'] = \
                                criteria_groups_from_mdm['data'][ec_1]['description']
                        else:
                            del new_criteria_array[ec_0]['requirementGroups'][ec_1]['description']

                        requirements_from_mdm = self.__mdm_class.get_requirements(
                            language=self.__language,
                            country=self.__country,
                            pmd=self.__pmd,
                            phase="qualification",
                            requirement_group_id=new_criteria_array[ec_0]['requirementGroups'][ec_1]['id']
                        )
                        del new_criteria_array[ec_0]['requirementGroups'][ec_1]['requirements'][0]
                        if len(requirements_from_mdm['data']) > 0:
                            for ec_2 in range(len(requirements_from_mdm['data'])):
                                new_criteria_array[ec_0]['requirementGroups'][ec_1]['requirements'].append(
                                    copy.deepcopy(self.__expected_fe_release['releases'][0]['tender']['criteria'][0][
                                                      'requirementGroups'][0]['requirements'][0]
                                                  )
                                )

                                new_criteria_array[ec_0]['requirementGroups'][ec_1]['requirements'][ec_2]['id'] = \
                                    requirements_from_mdm['data'][ec_2]['id']

                                if "description" in requirements_from_mdm['data'][ec_2]:

                                    new_criteria_array[ec_0]['requirementGroups'][ec_1]['requirements'][ec_2][
                                        'description'] = requirements_from_mdm['data'][ec_2]['description']
                                else:
                                    del new_criteria_array[ec_0]['requirementGroups'][ec_1]['requirements'][ec_2][
                                        'description']

                                new_criteria_array[ec_0]['requirementGroups'][ec_1]['requirements'][ec_2]['title'] = \
                                    requirements_from_mdm['data'][ec_2]['title']

                                # FR.COM-1.12.2:
                                new_criteria_array[ec_0]['requirementGroups'][ec_1]['requirements'][ec_2][
                                    'dataType'] = "boolean"

                                # FR.COM-1.12.7:
                                new_criteria_array[ec_0]['requirementGroups'][ec_1]['requirements'][ec_2][
                                    'status'] = "active"

                                # FR.COM-1.12.8:
                                new_criteria_array[ec_0]['requirementGroups'][ec_1]['requirements'][ec_2][
                                    'datePublished'] = self.__actual_message['data']['operationDate']

                        else:
                            raise ValueError(f"Empty array from MDM database: 'criteria[{ec_0}]."
                                             f"requirementGroups[{ec_1}].requirements[*]'.")
                else:
                    raise ValueError(f"Empty array from MDM database: 'criteria[{ec_0}].requirementGroups[*]'.")

        if len(old_criteria_array + new_criteria_array) > 0:
            self.__expected_fe_release['releases'][0]['tender']['criteria'] = old_criteria_array + new_criteria_array
        else:
            del self.__expected_fe_release['releases'][0]['tender']['criteria']

        # (https://ustudio.atlassian.net/wiki/spaces/ES/pages/1266286655/R10.3.2+eNotice+Amend+FE+v1):
        # FR.COM-3.2.3:
        self.__expected_fe_release['releases'][0]['tender']['otherCriteria']['reductionCriteria'] = \
            self.__previous_fe_release['releases'][0]['tender']['otherCriteria']['reductionCriteria']

        self.__expected_fe_release['releases'][0]['tender']['otherCriteria']['qualificationSystemMethods'] = \
            self.__previous_fe_release['releases'][0]['tender']['otherCriteria']['qualificationSystemMethods']

        self.__expected_fe_release['releases'][0]['tender']['enquiryPeriod']['startDate'] = \
            self.__previous_fe_release['releases'][0]['tender']['enquiryPeriod']['startDate']

        self.__expected_fe_release['releases'][0]['tender']['enquiryPeriod']['endDate'] = \
            self.__previous_fe_release['releases'][0]['tender']['enquiryPeriod']['endDate']

        self.__expected_fe_release['releases'][0]['tender']['hasEnquiries'] = \
            self.__previous_fe_release['releases'][0]['tender']['hasEnquiries']

        self.__expected_fe_release['releases'][0]['tender']['documents'] = \
            self.__previous_fe_release['releases'][0]['tender']['documents']

        self.__expected_fe_release['releases'][0]['tender']['submissionMethod'] = \
            self.__previous_fe_release['releases'][0]['tender']['submissionMethod']

        self.__expected_fe_release['releases'][0]['tender']['submissionMethodDetails'] = \
            self.__previous_fe_release['releases'][0]['tender']['submissionMethodDetails']

        self.__expected_fe_release['releases'][0]['tender']['submissionMethodRationale'] = \
            self.__previous_fe_release['releases'][0]['tender']['submissionMethodRationale']

        self.__expected_fe_release['releases'][0]['tender']['requiresElectronicCatalogue'] = \
            self.__previous_fe_release['releases'][0]['tender']['requiresElectronicCatalogue']

        self.__expected_fe_release['releases'][0]['tender']['procurementMethodModalities'] = \
            self.__previous_fe_release['releases'][0]['tender']['procurementMethodModalities']

        self.__expected_fe_release['releases'][0]['tender']['secondStage'] = \
            self.__previous_fe_release['releases'][0]['tender']['secondStage']

        # Build 'releases[0].submissions' object:
        # (https://ustudio.atlassian.net/wiki/spaces/ES/pages/875036832)
        # FR.COM-5.8.8, FR.COM-5.8.9:
        for s_withdrawn in range(len(self.__list_of_withdrawn_submission_id)):
            for s_some in range(len(self.__list_of_submission_messages)):
                if self.__list_of_withdrawn_submission_id[s_withdrawn] == \
                        self.__list_of_submission_messages[s_some]['data']['outcomes']['submissions'][0]['id']:
                    del self.__list_of_submission_messages[s_some]

        submission_details = list()
        if len(self.__actual_fe_release['releases'][0]['submissions']['details']) == \
                len(self.__list_of_submission_messages):

            for act_s in range(len(self.__actual_fe_release['releases'][0]['submissions']['details'])):
                for exp_s in range(len(self.__list_of_submission_messages)):

                    if self.__list_of_submission_messages[exp_s]['data']['outcomes']['submissions'][0]['id'] == \
                            self.__actual_fe_release['releases'][0]['submissions']['details'][act_s]['id']:

                        for q_0 in range(len(self.__list_of_submission_payloads)):
                            candidates_array = list()
                            for q_1 in range(len(self.__list_of_submission_payloads[q_0]['submission']['candidates'])):
                                candidates_array.append(
                                    copy.deepcopy(self.__expected_fe_release['releases'][0]['submissions'][
                                                      'details'][0]['candidates'][0]
                                                  )
                                )

                                candidate_scheme = \
                                    self.__list_of_submission_payloads[q_0]['submission']['candidates'][q_1][
                                        'identifier']['scheme']

                                candidate_id = \
                                    self.__list_of_submission_payloads[q_0]['submission']['candidates'][q_1][
                                        'identifier']['id']

                                candidates_array[q_1]['id'] = f"{candidate_scheme}-{candidate_id}"

                                candidates_array[q_1]['name'] = \
                                    self.__list_of_submission_payloads[q_0]['submission']['candidates'][q_1]['name']

                            if self.__actual_fe_release['releases'][0]['submissions']['details'][act_s][
                                    'candidates'] == candidates_array:

                                submission_details.append(copy.deepcopy(
                                    self.__expected_fe_release['releases'][0]['submissions']['details'][0]
                                ))
                                submission_details[act_s]['id'] = \
                                    self.__list_of_submission_messages[exp_s]['data']['outcomes'][
                                        'submissions'][0]['id']

                                # FR.COM-5.8.2:
                                submission_details[act_s]['date'] = \
                                    self.__list_of_submission_messages[exp_s]['data']['operationDate']

                                # FR.COM-5.8.1:
                                submission_details[act_s]['status'] = "pending"

                                # FR.COM-5.8.5:
                                submission_details[act_s]['candidates'] = candidates_array

                                del submission_details[act_s]['requirementResponses'][0]
                                if "requirementResponses" in self.__list_of_submission_payloads[q_0]['submission']:
                                    requirement_responses = list()
                                    for r_0 in range(len(self.__list_of_submission_payloads[q_0]['submission'][
                                                             'requirementResponses'])):
                                        requirement_responses.append(copy.deepcopy(
                                            self.__expected_fe_release['releases'][0]['submissions']['details'][0][
                                                'requirementResponses'][0]
                                        ))

                                        try:
                                            """Set permanent id."""
                                            is_permanent_id_correct = is_it_uuid(
                                                self.__actual_fe_release['releases'][0]['submissions'][
                                                    'details'][act_s]['requirementResponses'][r_0]['id']
                                            )
                                            if is_permanent_id_correct is True:

                                                requirement_responses[r_0]['id'] = \
                                                    self.__actual_fe_release['releases'][0]['submissions'][
                                                        'details'][act_s]['requirementResponses'][r_0]['id']
                                            else:
                                                raise ValueError(
                                                    f"The 'self.__actual_fe_release['releases'][0]['submissions']"
                                                    f"['details'][{act_s}]['requirementResponses']"
                                                    f"[{r_0}]['id']' must be uuid.")
                                        except KeyError:
                                            raise KeyError(
                                                f"Mismatch key into path 'self.__actual_fe_release['releases'][0]"
                                                f"['submissions']['details'][{act_s}]['requirementResponses']"
                                                f"[{r_0}]['id']'")

                                        requirement_responses[r_0]['value'] = \
                                            self.__list_of_submission_payloads[q_0]['submission'][
                                                'requirementResponses'][r_0]['value']

                                        requirement_responses[r_0]['requirement']['id'] = \
                                            self.__list_of_submission_payloads[q_0]['submission'][
                                                'requirementResponses'][r_0]['requirement']['id']

                                        del requirement_responses[r_0]['evidences'][0]
                                        if "evidences" in self.__list_of_submission_payloads[q_0]['submission'][
                                                'requirementResponses'][r_0]:

                                            evidences = list()
                                            for r_1 in range(len(self.__list_of_submission_payloads[q_0]['submission'][
                                                                     'requirementResponses'][r_0]['evidences'])):

                                                evidences.append(copy.deepcopy(
                                                    self.__expected_fe_release['releases'][0]['submissions'][
                                                        'details'][0]['requirementResponses'][0]['evidences'][0]
                                                ))

                                                try:
                                                    """Set permanent id."""
                                                    is_permanent_id_correct = is_it_uuid(
                                                        self.__actual_fe_release['releases'][0]['submissions'][
                                                            'details'][act_s]['requirementResponses'][r_0][
                                                            'evidences'][r_1]['id']
                                                    )
                                                    if is_permanent_id_correct is True:

                                                        evidences[r_1]['id'] = \
                                                            self.__actual_fe_release['releases'][0]['submissions'][
                                                                'details'][act_s]['requirementResponses'][r_0][
                                                                'evidences'][r_1]['id']
                                                    else:
                                                        raise ValueError(
                                                            f"The 'self.__actual_fe_release['releases'][0]"
                                                            f"['submissions']['details'][{act_s}]"
                                                            f"['requirementResponses'][{r_0}]['evidences']"
                                                            f"[{r_1}]['id']' must be uuid.")
                                                except KeyError:
                                                    raise KeyError(f"Mismatch key into path "
                                                                   f"'self.__actual_fe_release['releases'][0]"
                                                                   f"['submissions']['details'][{act_s}]"
                                                                   f"['requirementResponses'][{r_0}]['evidences']"
                                                                   f"[{r_1}]['id']'")

                                                evidences[r_1]['title'] = self.__list_of_submission_payloads[q_0][
                                                    'submission']['requirementResponses'][r_0]['evidences'][r_1][
                                                    'title']

                                                if "description" in self.__list_of_submission_payloads[q_0][
                                                        'submission']['requirementResponses'][r_0]['evidences'][r_1]:

                                                    evidences[r_1]['description'] = \
                                                        self.__list_of_submission_payloads[q_0]['submission'][
                                                            'requirementResponses'][r_0]['evidences'][r_1][
                                                            'description']
                                                else:
                                                    del evidences[r_1]['description']

                                                if "relatedDocument" in self.__list_of_submission_payloads[q_0][
                                                        'submission']['requirementResponses'][r_0]['evidences'][r_1]:

                                                    evidences[r_1]['relatedDocument']['id'] = \
                                                        self.__list_of_submission_payloads[q_0]['submission'][
                                                            'requirementResponses'][r_0]['evidences'][r_1][
                                                            'relatedDocument']['id']
                                                else:
                                                    del evidences[r_1]['relatedDocument']

                                            requirement_responses[r_0]['evidences'] = evidences

                                        else:
                                            del requirement_responses[r_0]['evidences']

                                    submission_details[act_s]['requirementResponses'] = requirement_responses
                                else:
                                    del submission_details[act_s]['requirementResponses']

                                del submission_details[act_s]['documents'][0]
                                if "documents" in self.__list_of_submission_payloads[q_0]['submission']:
                                    documents = list()
                                    for d_0 in range(len(
                                            self.__list_of_submission_payloads[q_0]['submission']['documents'])):

                                        documents.append(copy.deepcopy(
                                            self.__expected_fe_release['releases'][0]['submissions']['details'][0][
                                                'documents'][0]
                                        ))

                                        documents[d_0]['id'] = self.__list_of_submission_payloads[q_0]['submission'][
                                            'documents'][d_0]['id']

                                        documents[d_0]['documentType'] = self.__list_of_submission_payloads[q_0][
                                            'submission']['documents'][d_0]['documentType']

                                        documents[d_0]['title'] = self.__list_of_submission_payloads[q_0][
                                            'submission']['documents'][d_0]['title']

                                        if "description" in self.__list_of_submission_payloads[q_0][
                                                'submission']['documents'][d_0]:

                                            documents[d_0]['description'] = self.__list_of_submission_payloads[q_0][
                                                'submission']['documents'][d_0]['description']
                                        else:
                                            del documents[d_0]['description']

                                        documents[d_0]['url'] = f"{self.__metadata_document_url}/{documents[d_0]['id']}"
                                        documents[d_0]['datePublished'] = self.__actual_message['data']['operationDate']

                                    submission_details[act_s]['documents'] = documents
                                else:
                                    del submission_details[act_s]['documents']
        self.__expected_fe_release['releases'][0]['submissions']['details'] = submission_details
        return self.__expected_fe_release

        # def prepare_criteria_object_source_procuring_entity(self, phase, submission_period_end_message):
        #     expected_criteria_array_source_procuring_entity = {}
        #
        #     criteria_from_mdm = self.__mdm_class.get_criteria(
        #         language=self.__language,
        #         country=self.__country,
        #         pmd=self.__pmd,
        #         phase=phase
        #     )
        #
        #     try:
        #         """
        #         Check how many quantity of objects are contained into criteria_from_mdm.
        #         """
        #         list_of_mdm_tender_criteria_id = list()
        #         for criteria_object in criteria_from_mdm['data']:
        #             for i in criteria_object:
        #                 if i == "id":
        #                     list_of_mdm_tender_criteria_id.append(i)
        #         quantity_of_criteria_object_into_mdm = len(list_of_mdm_tender_criteria_id)
        #     except Exception:
        #         raise Exception("Impossible to check how many quantity of objects are contained into criteria_from_mdm.")
        #
        #     for c in range(quantity_of_criteria_object_into_mdm):
        #         criteria_framework = {
        #             "id": criteria_from_mdm['data'][c]['id'],
        #             "title": criteria_from_mdm['data'][c]['title'],
        #             "source": "procuringEntity",
        #             "relatesTo": "qualification",
        #             "description": criteria_from_mdm['data'][c]['description'],
        #             "classification": criteria_from_mdm['data'][c]['classification'],
        #             "requirementGroups": []
        #         }
        #
        #         criteria_groups_from_mdm = self.__mdm_class.get_requirement_groups(
        #             language=self.__language,
        #             country=self.__country,
        #             pmd=self.__pmd,
        #             phase=phase,
        #             criterion_id=criteria_from_mdm['data'][c]['id'])
        #
        #         try:
        #             """
        #             Check how many quantity of objects are contained into criteria_groups_from_mdm.
        #             """
        #             list_of_mdm_tender_criteria_groups_id = list()
        #             for group_object in criteria_groups_from_mdm['data']:
        #                 for i in group_object:
        #                     if i == "id":
        #                         list_of_mdm_tender_criteria_groups_id.append(i)
        #             quantity_of_criteria_groups_object_into_mdm = len(list_of_mdm_tender_criteria_groups_id)
        #         except Exception:
        #             raise Exception("Impossible to check how many quantity of objects are "
        #                             "contained into criteria_groups_from_mdm.")
        #
        #         for g in range(quantity_of_criteria_groups_object_into_mdm):
        #             requirement_groups_framework = {
        #                 "id": criteria_groups_from_mdm['data'][g]['id'],
        #                 "requirements": []
        #             }
        #             criteria_framework['requirementGroups'].append(requirement_groups_framework)
        #
        #             criteria_groups_requirements_from_mdm = self.__mdm_class.get_requirements(
        #                 language=self.__language,
        #                 country=self.__country,
        #                 pmd=self.__pmd,
        #                 phase=phase,
        #                 requirement_group_id=criteria_groups_from_mdm['data'][g]['id'])
        #
        #             try:
        #                 """
        #                 Check how many quantity of objects are contained into criteria_groups_requirements_from_mdm.
        #                 """
        #                 list_of_mdm_tender_criteria_groups_requirement_id = list()
        #                 for requirement_object in criteria_groups_requirements_from_mdm['data']:
        #                     for i in requirement_object:
        #                         if i == "id":
        #                             list_of_mdm_tender_criteria_groups_requirement_id.append(i)
        #                 quantity_of_criteria_groups_requirement_object_into_mdm = \
        #                     len(list_of_mdm_tender_criteria_groups_requirement_id)
        #             except Exception:
        #                 raise Exception("Impossible to check how many quantity of objects are "
        #                                 "contained into criteria_groups_requirements_from_mdm.")
        #
        #             for r in range(quantity_of_criteria_groups_requirement_object_into_mdm):
        #                 requirements_framework = {
        #                     "id": criteria_groups_requirements_from_mdm['data'][r]['id'],
        #                     "title": criteria_groups_requirements_from_mdm['data'][r]['title'],
        #                     "dataType": "boolean",
        #                     "status": "active",
        #                     "datePublished": submission_period_end_message['data']['operationDate']
        #                 }
        #                 criteria_framework['requirementGroups'][g]['requirements'].append(requirements_framework)
        #
        #                 expected_criteria_array_source_procuring_entity.update(criteria_framework)
        #
        #     return expected_criteria_array_source_procuring_entity
        #
        # def prepare_submission_object(self, submission_payload, create_submission_feed_point_message):
        #     final_submission_mapper = None
        #     correct_submission_id = None
        #     for i in self.__actual_fe_release['releases'][0]['submissions']['details']:
        #         if i['date'] == create_submission_feed_point_message['data']['operationDate']:
        #             try:
        #                 is_it_uuid(i['id'])
        #             except ValueError:
        #                 raise ValueError("Check your actual_tp_release['releases'][0]['submissions']['details'][i]['id']: "
        #                                  "id must be uuid.")
        #             correct_submission_id = i['id']
        #
        #     final_submissions_details_object = {
        #         "id": correct_submission_id,
        #         "date": create_submission_feed_point_message['data']['operationDate'],
        #         "status": "pending",
        #         "candidates": []
        #     }
        #
        #     try:
        #         """
        #         Calculate how many candidates contains into payload
        #         """
        #         candidates_identifier_id_list = list()
        #         for i in submission_payload['submission']['candidates']:
        #             for i_1 in i:
        #                 if i_1 == "identifier":
        #                     candidates_identifier_id_list.append(i['identifier']['id'])
        #     except Exception:
        #         raise Exception("Impossible to check calculate how many candidates contains into payload")
        #
        #     for i in range(len(candidates_identifier_id_list)):
        #         submission_details_candidates_object = {
        #             "id": f"{submission_payload['submission']['candidates'][i]['identifier']['scheme']}-"
        #                   f"{submission_payload['submission']['candidates'][i]['identifier']['id']}",
        #             "name": submission_payload['submission']['candidates'][i]['name']
        #         }
        #
        #         final_submissions_details_object['candidates'].append(submission_details_candidates_object)
        #
        #         final_submission_mapper = {
        #             "id": final_submissions_details_object['id'],
        #             "value": final_submissions_details_object
        #         }
        #     return final_submission_mapper
        #
        # def prepare_qualification_object(self, fe_payload, submission_id, submission_period_end_feed_point_message):
        #     status_details = None
        #     final_qualification_mapper = None
        #
        #     is_criteria_source_procuring_entity = False
        #     try:
        #         """
        #         FR.COM-7.13.1
        #         """
        #         if "criteria" in self.__actual_fe_release['releases'][0]['tender']:
        #             for c_0 in range(len(self.__actual_fe_release['releases'][0]['tender']['criteria'])):
        #                 if self.__actual_fe_release['releases'][0]['tender']['criteria'][c_0][
        #                         'source'] == "procuringEntity":
        #
        #                     is_criteria_source_procuring_entity = True
        #
        #         if fe_payload['tender']['otherCriteria']['reductionCriteria'] == "scoring" and \
        #                 fe_payload['tender']['otherCriteria']['qualificationSystemMethods'] == ["automated"] and \
        #                 is_criteria_source_procuring_entity is True:
        #             status_details = "awaiting"
        #         elif fe_payload['tender']['otherCriteria']['reductionCriteria'] == "scoring" and \
        #                 fe_payload['tender']['otherCriteria']['qualificationSystemMethods'] == ["manual"] and \
        #                 is_criteria_source_procuring_entity is True:
        #             status_details = "awaiting"
        #         elif fe_payload['tender']['otherCriteria']['reductionCriteria'] == "none" and \
        #                 fe_payload['tender']['otherCriteria']['qualificationSystemMethods'] == ["automated"] and \
        #                 is_criteria_source_procuring_entity is True:
        #             status_details = "awaiting"
        #         elif fe_payload['tender']['otherCriteria']['reductionCriteria'] == "none" and \
        #                 fe_payload['tender']['otherCriteria']['qualificationSystemMethods'] == ["manual"] and \
        #                 is_criteria_source_procuring_entity is True:
        #             status_details = "awaiting"
        #
        #         elif fe_payload['tender']['otherCriteria']['reductionCriteria'] == "scoring" and \
        #                 fe_payload['tender']['otherCriteria']['qualificationSystemMethods'] == ["automated"] and \
        #                 is_criteria_source_procuring_entity is False:
        #             status_details = "consideration"
        #         elif fe_payload['tender']['otherCriteria']['reductionCriteria'] == "scoring" and \
        #                 fe_payload['tender']['otherCriteria']['qualificationSystemMethods'] == ["manual"] and \
        #                 is_criteria_source_procuring_entity is False:
        #             status_details = "consideration"
        #         elif fe_payload['tender']['otherCriteria']['reductionCriteria'] == "none" and \
        #                 fe_payload['tender']['otherCriteria']['qualificationSystemMethods'] == ["automated"] and \
        #                 is_criteria_source_procuring_entity is False:
        #             status_details = "consideration"
        #         elif fe_payload['tender']['otherCriteria']['reductionCriteria'] == "none" and \
        #                 fe_payload['tender']['otherCriteria']['qualificationSystemMethods'] == ["manual"] and \
        #                 is_criteria_source_procuring_entity is False:
        #             status_details = "consideration"
        #     except Exception:
        #         raise Exception("Impossible to set correct statusDetails for qualification")
        #
        #     for i in self.__actual_fe_release['releases'][0]['qualifications']:
        #         for i_1 in i:
        #             if i_1 == "relatedSubmission":
        #                 if i['relatedSubmission'] == submission_id:
        #                     try:
        #                         is_it_uuid(i['id'])
        #                     except ValueError:
        #                         raise ValueError("Check your qualification['id']: id must be uuid.")
        #
        #                     qualification_object = {
        #                         "id": i['id'],
        #                         "date": submission_period_end_feed_point_message['data']['operationDate'],
        #                         "status": "pending",
        #                         "statusDetails": status_details,
        #                         "relatedSubmission": submission_id
        #                     }
        #
        #                     final_qualification_mapper = {
        #                         "id": qualification_object['id'],
        #                         "value": qualification_object
        #                     }
        #     return final_qualification_mapper
        #
        # def prepare_parties_object(self, submission_payload):
        #     final_parties_mapper = []
        #     for i in range(len(submission_payload['submission']['candidates'])):
        #         parties_object = {
        #             "id": f"{submission_payload['submission']['candidates'][i]['identifier']['scheme']}-"
        #                   f"{submission_payload['submission']['candidates'][i]['identifier']['id']}",
        #             "name": submission_payload['submission']['candidates'][i]['name'],
        #             "identifier": submission_payload['submission']['candidates'][i]['identifier'],
        #             "address": submission_payload['submission']['candidates'][i]['address'],
        #             "contactPoint": submission_payload['submission']['candidates'][i]['contactPoint'],
        #             "details": submission_payload['submission']['candidates'][i]['details'],
        #             "roles": ["candidate"]
        #         }
        #
        #         country_data = get_value_from_country_csv(
        #             country=submission_payload['submission']['candidates'][i]['address']['addressDetails']['country']['id'],
        #             language=self.__language
        #         )
        #         country_object = [{
        #             "scheme": country_data[2],
        #             "id": submission_payload['submission']['candidates'][i]['address']['addressDetails']['country']['id'],
        #             "description": country_data[1],
        #             "uri": country_data[3]
        #         }]
        #
        #         region_data = get_value_from_region_csv(
        #             region=submission_payload['submission']['candidates'][i]['address']['addressDetails']['region']['id'],
        #             country=submission_payload['submission']['candidates'][i]['address']['addressDetails']['country']['id'],
        #             language=self.__language
        #         )
        #         region_object = [{
        #             "scheme": region_data[2],
        #             "id": submission_payload['submission']['candidates'][i]['address']['addressDetails']['region']['id'],
        #             "description": region_data[1],
        #             "uri": region_data[3]
        #         }]
        #
        #         if \
        #                 submission_payload['submission']['candidates'][i]['address']['addressDetails']['locality'][
        #                     'scheme'] == "CUATM":
        #             locality_data = get_value_from_locality_csv(
        #                 locality=submission_payload['submission']['candidates'][i]['address']['addressDetails'][
        #                     'locality']['id'],
        #                 region=submission_payload['submission']['candidates'][i]['address']['addressDetails'][
        #                     'region']['id'],
        #                 country=submission_payload['submission']['candidates'][i]['address']['addressDetails'][
        #                     'country']['id'],
        #                 language=self.__language
        #             )
        #             locality_object = [{
        #                 "scheme": locality_data[3],
        #                 "id": submission_payload['submission']['candidates'][i]['address']['addressDetails'][
        #                     'locality']['id'],
        #                 "description": locality_data[1],
        #                 "uri": locality_data[2]
        #             }]
        #         else:
        #             locality_object = [{
        #                 "scheme": submission_payload['submission']['candidates'][i]['address']['addressDetails'][
        #                     'locality']['scheme'],
        #                 "id": submission_payload['submission']['candidates'][i]['address']['addressDetails'][
        #                     'locality']['id'],
        #                 "description": submission_payload['submission']['candidates'][i]['address']['addressDetails'][
        #                     'locality']['description']
        #             }]
        #
        #         parties_object['address']['addressDetails']['country'] = country_object[0]
        #         parties_object['address']['addressDetails']['region'] = region_object[0]
        #         parties_object['address']['addressDetails']['locality'] = locality_object[0]
        #
        #         parties_mapper = {
        #             "id": parties_object['id'],
        #             "value": parties_object
        #         }
        #
        #         final_parties_mapper.append(parties_mapper)
        #
        #     return final_parties_mapper
        #
        # @staticmethod
        # def prepare_pre_qualification_qualification_period_object(submission_period_end_feed_point_message):
        #     qualification_period_object = {
        #         "startDate": submission_period_end_feed_point_message['data']['operationDate']
        #     }
        #     return qualification_period_object
