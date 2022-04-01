import copy

import requests

from tests.utils.functions_collection.functions import get_value_from_cpv_dictionary_xls, \
    get_value_from_cpvs_dictionary_csv, get_value_from_classification_unit_dictionary_csv, get_value_from_country_csv, \
    get_value_from_region_csv, get_value_from_locality_csv, is_it_uuid, get_contract_period_for_ms_release, \
    get_sum_of_lot, generate_tender_classification_id


class PlanningNoticeRelease:
    def __init__(self, environment, host_to_service, language, pmd, pn_payload, pn_message, actual_pn_release,
                 actual_ms_release):

        self.__environment = environment
        self.__host = host_to_service
        self.__language = language
        self.__pmd = pmd
        self.__pn_payload = pn_payload
        self.__message = pn_message
        self.__actual_pn_release = actual_pn_release
        self.__actual_ms_release = actual_ms_release

        extensions = None
        publisher_name = None
        publisher_uri = None
        self.__metadata_document_url = None
        try:
            if environment == "dev":
                self.__metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"

                extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
                ]

                publisher_name = "M-Tender"
                publisher_uri = "https://www.mtender.gov.md"
                self.__metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"

            elif environment == "sandbox":
                self.__metadata_tender_url = "http://public.eprocurement.systems/tenders"

                extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.json"
                ]

                publisher_name = "Viešųjų pirkimų tarnyba"
                publisher_uri = "https://vpt.lrv.lt"
                self.__metadata_document_url = "http://storage.eprocurement.systems/get"
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

        self.__expected_pn_release = {
            "uri": f"{self.__metadata_tender_url}/{pn_message['data']['ocid']}/"
                   f"{pn_message['data']['outcomes']['pn'][0]['id']}",

            "version": "1.1",
            "extensions": extensions,
            "publisher": {
                "name": publisher_name,
                "uri": publisher_uri
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": pn_message['data']['operationDate'],
            "releases": [
                {
                    "ocid": pn_message['data']['outcomes']['pn'][0]['id'],

                    "id": f"{pn_message['data']['outcomes']['pn'][0]['id']}-"
                          f"{actual_pn_release['releases'][0]['id'][46:59]}",

                    "date": pn_message['data']['operationDate'],
                    "tag": [
                        "planning"
                    ],
                    "language": language,
                    "initiationType": "tender",
                    "tender": {
                        "id": "",
                        "status": "planning",
                        "statusDetails": "planning",
                        "items": [
                            {
                                "id": "",
                                "internalId": "",
                                "description": "",
                                "classification": {
                                    "scheme": "",
                                    "id": "",
                                    "description": ""
                                },
                                "additionalClassifications": [
                                    {
                                        "scheme": "",
                                        "id": "",
                                        "description": ""
                                    }
                                ],
                                "quantity": "",
                                "unit": {
                                    "name": "",
                                    "id": ""
                                },
                                "relatedLot": ""
                            }
                        ],
                        "lots": [
                            {
                                "id": "",
                                "internalId": "",
                                "title": "",
                                "description": "",
                                "status": "planning",
                                "statusDetails": "empty",
                                "value": {
                                    "amount": 0,
                                    "currency": ""
                                },
                                "recurrentProcurement": [
                                    {
                                        "isRecurrent": False
                                    }
                                ],
                                "renewals": [
                                    {
                                        "hasRenewals": False
                                    }
                                ],
                                "variants": [
                                    {
                                        "hasVariants": False
                                    }
                                ],
                                "contractPeriod": {
                                    "startDate": "",
                                    "endDate": ""
                                },
                                "placeOfPerformance": {
                                    "address": {
                                        "streetAddress": "",
                                        "postalCode": "",
                                        "addressDetails": {
                                            "country": {
                                                "scheme": "",
                                                "id": "",
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
                                                "description": "",
                                                "uri": ""
                                            }
                                        }
                                    },
                                    "description": ""
                                },
                                "options": [
                                    {
                                        "hasOptions": False
                                    }
                                ]
                            }
                        ],
                        "lotGroups": [
                            {
                                "optionToCombine": False
                            }
                        ],
                        "tenderPeriod": {
                            "startDate": ""
                        },
                        "hasEnquiries": False,
                        "documents": [
                            {
                                "id": "",
                                "documentType": "",
                                "title": "",
                                "description": "",
                                "url": "",
                                "datePublished": "",
                                "relatedLots": [
                                    ""
                                ]
                            }
                        ],
                        "submissionMethod": [
                            ""
                        ],
                        "submissionMethodDetails": "",
                        "submissionMethodRationale": [
                            ""
                        ],
                        "requiresElectronicCatalogue": False
                    },
                    "hasPreviousNotice": False,
                    "purposeOfNotice": {
                        "isACallForCompetition": False
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
                    ]
                }
            ]
        }

        self.__expected_ms_release = {
            "uri": f"{self.__metadata_tender_url}/{pn_message['data']['ocid']}/{pn_message['data']['ocid']}",
            "version": "1.1",
            "extensions": extensions,
            "publisher": {
                "name": publisher_name,
                "uri": publisher_uri
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": pn_message['data']['operationDate'],
            "releases": [
                {
                    "ocid": pn_message['data']['ocid'],
                    "id": f"{pn_message['data']['ocid']}-{actual_ms_release['releases'][0]['id'][29:42]}",
                    "date": pn_message['data']['operationDate'],
                    "tag": [
                        "compiled"
                    ],
                    "language": language,
                    "initiationType": "tender",
                    "planning": {
                        "budget": {
                            "description": "",
                            "amount": {
                                "amount": 0,
                                "currency": ""
                            },
                            "isEuropeanUnionFunded": True,
                            "budgetBreakdown": [
                                {
                                    "id": "",
                                    "description": "",
                                    "amount": {
                                        "amount": 0,
                                        "currency": ""
                                    },
                                    "period": {
                                        "startDate": "",
                                        "endDate": ""
                                    },
                                    "sourceParty": {
                                        "id": "",
                                        "name": ""
                                    },
                                    "europeanUnionFunding": {
                                        "projectIdentifier": "",
                                        "projectName": "",
                                        "uri": ""
                                    }
                                }
                            ]
                        },
                        "rationale": ""
                    },
                    "tender": {
                        "id": "",
                        "title": "",
                        "description": "",
                        "status": "planning",
                        "statusDetails": "planning",
                        "value": {
                            "amount": 0,
                            "currency": ""
                        },
                        "procurementMethod": "",
                        "procurementMethodDetails": "",
                        "procurementMethodRationale": "",
                        "mainProcurementCategory": "",
                        "hasEnquiries": False,
                        "eligibilityCriteria": "",
                        "contractPeriod": {
                            "startDate": "",
                            "endDate": ""
                        },
                        "acceleratedProcedure": {
                            "isAcceleratedProcedure": False
                        },
                        "classification": {
                            "scheme": "",
                            "id": "",
                            "description": ""
                        },
                        "designContest": {
                            "serviceContractAward": False
                        },
                        "electronicWorkflows": {
                            "useOrdering": False,
                            "usePayment": False,
                            "acceptInvoicing": False
                        },
                        "jointProcurement": {
                            "isJointProcurement": False
                        },
                        "legalBasis": "",
                        "procedureOutsourcing": {
                            "procedureOutsourced": False
                        },
                        "procurementMethodAdditionalInfo": "",
                        "dynamicPurchasingSystem": {
                            "hasDynamicPurchasingSystem": False
                        },
                        "framework": {
                            "isAFramework": False
                        }
                    },
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
                                        "id": "",
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
                                        "description": "",
                                        "uri": ""
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
                                "typeOfBuyer": "",
                                "mainGeneralActivity": "",
                                "mainSectoralActivity": ""
                            },
                            "roles": [
                                ""
                            ]
                        }
                    ],
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
                    ]
                }
            ]
        }

    def build_expected_pn_release(self):
        # Build or delete optional fields.
        if "lots" in self.__pn_payload['tender']:
            try:
                """
                Build the releases.tender.lots array.
                """
                new_lots_array = list()
                for q_0 in range(len(self.__pn_payload['tender']['lots'])):
                    new_lots_array.append(copy.deepcopy(self.__expected_pn_release['releases'][0]['tender']['lots'][0]))

                    # Enrich or delete optional fields:
                    if "internalId" in self.__pn_payload['tender']['lots'][q_0]:
                        new_lots_array[q_0]['internalId'] = self.__pn_payload['tender']['lots'][q_0]['internalId']
                    else:
                        del new_lots_array[q_0]['internalId']

                    if "postalCode" in self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address']:

                        new_lots_array[q_0]['placeOfPerformance']['address']['postalCode'] = \
                            self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address']['postalCode']
                    else:
                        del new_lots_array[q_0]['placeOfPerformance']['address']['postalCode']

                    if "description" in self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']:

                        new_lots_array[q_0]['placeOfPerformance']['description'] = \
                            self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['description']
                    else:
                        del new_lots_array[q_0]['placeOfPerformance']['description']

                    # Enrich required fields:
                    is_permanent_lot_id_correct = is_it_uuid(
                        self.__actual_pn_release['releases'][0]['tender']['lots'][q_0]['id'])

                    if is_permanent_lot_id_correct is True:
                        new_lots_array[q_0]['id'] = self.__actual_pn_release['releases'][0]['tender']['lots'][q_0]['id']
                    else:
                        raise ValueError(f"The relases0.tender.lots{q_0}.id must be uuid.")

                    new_lots_array[q_0]['title'] = self.__pn_payload['tender']['lots'][q_0]['title']
                    new_lots_array[q_0]['description'] = self.__pn_payload['tender']['lots'][q_0]['description']
                    new_lots_array[q_0]['value']['amount'] = self.__pn_payload['tender']['lots'][q_0]['value']['amount']
                    new_lots_array[q_0]['value']['currency'] = self.__pn_payload['tender']['lots'][q_0]['value'][
                        'currency']

                    new_lots_array[q_0]['contractPeriod']['startDate'] = \
                        self.__pn_payload['tender']['lots'][q_0]['contractPeriod']['startDate']

                    new_lots_array[q_0]['contractPeriod']['endDate'] = \
                        self.__pn_payload['tender']['lots'][q_0]['contractPeriod']['endDate']

                    new_lots_array[q_0]['placeOfPerformance']['address']['streetAddress'] = \
                        self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address']['streetAddress']

                    try:
                        """
                        Prepare releases.tender.lots.placeOfPerformance.address.addressDetails object.
                        """
                        lot_country_data = get_value_from_country_csv(
                            country=self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                'addressDetails']['country']['id'],

                            language=self.__language
                        )
                        expected_lot_country_object = {
                            "scheme": lot_country_data[2],

                            "id":
                                self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails'][
                                    'country']['id'],

                            "description": lot_country_data[1],
                            "uri": lot_country_data[3]
                        }

                        lot_region_data = get_value_from_region_csv(
                            region=self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                'addressDetails']['region']['id'],

                            country=self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                'addressDetails']['country']['id'],

                            language=self.__language
                        )
                        expected_lot_region_object = {
                            "scheme": lot_region_data[2],

                            "id":
                                self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails'][
                                    'region']['id'],

                            "description": lot_region_data[1],
                            "uri": lot_region_data[3]
                        }

                        if self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address']['addressDetails'][
                            'locality']['scheme'] == "CUATM":

                            lot_locality_data = get_value_from_locality_csv(

                                locality=self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['locality']['id'],

                                region=self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['region']['id'],

                                country=self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['country']['id'],

                                language=self.__language
                            )
                            expected_lot_locality_object = {
                                "scheme": lot_locality_data[2],

                                "id": self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails'][
                                    'locality']['id'],

                                "description": lot_locality_data[1],
                                "uri": lot_locality_data[3]
                            }
                        else:
                            expected_lot_locality_object = {
                                "scheme":
                                    self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                        'addressDetails'][
                                        'locality']['scheme'],

                                "id": self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails'][
                                    'locality']['id'],

                                "description":
                                    self.__pn_payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                        'addressDetails'][
                                        'locality']['description']
                            }
                    except ValueError:
                        raise ValueError(
                            "Impossible to prepare the expected releases.tender.lots.placeOfPerformance.address."
                            "addressDetails object.")

                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails'][
                        'country'] = expected_lot_country_object
                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['region'] = expected_lot_region_object
                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails'][
                        'locality'] = expected_lot_locality_object
                self.__expected_pn_release['releases'][0]['tender']['lots'] = new_lots_array
            except ValueError:
                raise ValueError("Impossible to build the expected releases.tender.lots array.")
        else:
            del self.__expected_pn_release['releases'][0]['tender']['lots']

        if "items" in self.__pn_payload['tender']:
            try:
                """
                Build the releases.tender.items array.
                """
                new_items_array = list()
                for q_0 in range(len(self.__pn_payload['tender']['items'])):

                    new_items_array.append(copy.deepcopy(
                        self.__expected_pn_release['releases'][0]['tender']['items'][0]))

                    # Enrich or delete optional fields:
                    if "internalId" in self.__pn_payload['tender']['items'][q_0]:
                        new_items_array[q_0]['internalId'] = self.__pn_payload['tender']['items'][q_0]['internalId']
                    else:
                        del new_items_array[q_0]['internalId']

                    if "additionalClassifications" in self.__pn_payload['tender']['items'][q_0]:
                        new_item_additionalclassifications_array = list()
                        for q_1 in range(len(self.__pn_payload['tender']['items'][q_0]['additionalClassifications'])):
                            new_item_additionalclassifications_array.append(copy.deepcopy(
                                self.__expected_pn_release['releases'][0]['tender']['items'][0][
                                    'additionalClassifications'][0]))

                            expected_cpvs_data = get_value_from_cpvs_dictionary_csv(
                                cpvs=self.__pn_payload['tender']['items'][q_0]['additionalClassifications'][q_1]['id'],
                                language=self.__language
                            )

                            new_item_additionalclassifications_array[q_1]['scheme'] = "CPVS"
                            new_item_additionalclassifications_array[q_1]['id'] = expected_cpvs_data[0]
                            new_item_additionalclassifications_array[q_1]['description'] = expected_cpvs_data[2]

                        new_items_array[q_0]['additionalClassifications'] = \
                            new_item_additionalclassifications_array
                    else:
                        del new_items_array[q_0]['additionalClassifications']

                    # Enrich required fields:
                    is_permanent_item_id_correct = is_it_uuid(
                        self.__actual_pn_release['releases'][0]['tender']['items'][q_0]['id'])

                    if is_permanent_item_id_correct is True:
                        new_items_array[q_0]['id'] = self.__actual_pn_release['releases'][0]['tender']['items'][q_0][
                            'id']
                    else:
                        raise ValueError(f"The relases0.tender.items{q_0}.id must be uuid.")

                    new_items_array[q_0]['description'] = self.__pn_payload['tender']['items'][q_0]['description']

                    expected_cpv_data = get_value_from_cpv_dictionary_xls(
                        cpv=self.__pn_payload['tender']['items'][q_0]['classification']['id'],
                        language=self.__language
                    )

                    new_items_array[q_0]['classification']['scheme'] = "CPV"
                    new_items_array[q_0]['classification']['id'] = expected_cpv_data[0]
                    new_items_array[q_0]['classification']['description'] = expected_cpv_data[1]
                    new_items_array[q_0]['quantity'] = float(self.__pn_payload['tender']['items'][q_0]['quantity'])

                    expected_unit_data = get_value_from_classification_unit_dictionary_csv(
                        unit_id=self.__pn_payload['tender']['items'][q_0]['unit']['id'],
                        language=self.__language
                    )

                    new_items_array[q_0]['unit']['id'] = expected_unit_data[0]
                    new_items_array[q_0]['unit']['name'] = expected_unit_data[1]

                    new_items_array[q_0]['relatedLot'] = \
                        self.__actual_pn_release['releases'][0]['tender']['lots'][q_0]['id']

                self.__expected_pn_release['releases'][0]['tender']['items'] = new_items_array
            except ValueError:
                raise ValueError("Impossible to build the expected releases.tender.items array.")
        else:
            del self.__expected_pn_release['releases'][0]['tender']['items']

        if "documents" in self.__pn_payload['tender']:
            try:
                """
                Build the releases.tender.documents array.
                """
                new_documents_array = list()
                for q_0 in range(len(self.__pn_payload['tender']['documents'])):

                    new_documents_array.append(copy.deepcopy(
                        self.__expected_pn_release['releases'][0]['tender']['documents'][0]))

                    # Enrich or delete optional fields:
                    if "description" in self.__pn_payload['tender']['documents'][q_0]:
                        new_documents_array[q_0]['description'] = self.__pn_payload['tender']['documents'][q_0][
                            'description']
                    else:
                        del new_documents_array[q_0]['description']

                    if "relatedLots" in self.__pn_payload['tender']['documents'][q_0]:

                        new_documents_array[q_0]['relatedLots'] = \
                            [self.__actual_pn_release['releases'][0]['tender']['lots'][q_0]['id']]
                    else:
                        del new_documents_array[q_0]['relatedLots']

                    # Enrich required fields:
                    new_documents_array[q_0]['id'] = self.__pn_payload['tender']['documents'][q_0]['id']
                    new_documents_array[q_0]['documentType'] = self.__pn_payload['tender']['documents'][q_0][
                        'documentType']
                    new_documents_array[q_0]['title'] = self.__pn_payload['tender']['documents'][q_0]['title']

                    new_documents_array[q_0]['url'] = \
                        f"{self.__metadata_document_url}/{self.__pn_payload['tender']['documents'][q_0]['id']}"

                    new_documents_array[q_0]['datePublished'] = self.__message['data']['operationDate']
                self.__expected_pn_release['releases'][0]['tender']['documents'] = new_documents_array
            except ValueError:
                raise ValueError("Impossible to build the expected releases.tender.documents array.")
        else:
            del self.__expected_pn_release['releases'][0]['tender']['documents']

        # Enrich required fields:
        is_permanent_tender_id_correct = is_it_uuid(
            self.__actual_pn_release['releases'][0]['tender']['id'])

        if is_permanent_tender_id_correct is True:

            self.__expected_pn_release['releases'][0]['tender']['id'] = \
                self.__actual_pn_release['releases'][0]['tender']['id']
        else:
            raise ValueError(f"The relases0.relatedProcess0.id must be uuid.")

        self.__expected_pn_release['releases'][0]['tender']['tenderPeriod']['startDate'] = \
            self.__pn_payload['tender']['tenderPeriod']['startDate']

        self.__expected_pn_release['releases'][0]['tender']['submissionMethod'][0] = "electronicSubmission"

        self.__expected_pn_release['releases'][0]['tender']['submissionMethodDetails'] = \
            "Lista platformelor: achizitii, ebs, licitatie, yptender"

        self.__expected_pn_release['releases'][0]['tender']['submissionMethodRationale'][0] = \
            "Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"

        is_permanent_releatedprocess_id_correct = is_it_uuid(
            self.__actual_pn_release['releases'][0]['relatedProcesses'][0]['id'])

        if is_permanent_releatedprocess_id_correct is True:

            self.__expected_pn_release['releases'][0]['relatedProcesses'][0]['id'] = \
                self.__actual_pn_release['releases'][0]['relatedProcesses'][0]['id']
        else:
            raise ValueError(f"The relases0.relatedProcess0.id must be uuid.")

        self.__expected_pn_release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        self.__expected_pn_release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        self.__expected_pn_release['releases'][0]['relatedProcesses'][0]['identifier'] = self.__message['data']['ocid']

        self.__expected_pn_release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.__metadata_tender_url}/{self.__message['data']['ocid']}/{self.__message['data']['ocid']}"

        return self.__expected_pn_release

    def build_expected_ms_release(self, fs_budget_cpid_ocid_list, tender_classification_id):
        print(f"\nПрокинули параметр tender.classifiacation.id = {tender_classification_id}")
        # Build the releases.planning object. Enrich or delete optional fields and enrich required fields:
        if "rationale" in self.__pn_payload['planning']:
            self.__expected_ms_release['releases'][0]['planning']['rationale'] = self.__pn_payload['planning'][
                'rationale']
        else:
            del self.__expected_ms_release['releases'][0]['planning']['rationale']

        if "description" in self.__pn_payload['planning']['budget']:

            self.__expected_ms_release['releases'][0]['planning']['budget']['description'] = \
                self.__pn_payload['planning']['budget']['description']
        else:
            del self.__expected_ms_release['releases'][0]['planning']['budget']['description']

        if "procurementMethodRationale" in self.__pn_payload['tender']:

            self.__expected_ms_release['releases'][0]['tender']['procurementMethodRationale'] = \
                self.__pn_payload['tender']['procurementMethodRationale']
        else:
            del self.__expected_ms_release['releases'][0]['tender']['procurementMethodRationale']

        if "procurementMethodAdditionalInfo" in self.__pn_payload['tender']:

            self.__expected_ms_release['releases'][0]['tender']['procurementMethodAdditionalInfo'] = \
                self.__pn_payload['tender']['procurementMethodAdditionalInfo']
        else:
            del self.__expected_ms_release['releases'][0]['tender']['procurementMethodAdditionalInfo']

        sum_of_budgetbreakdown_amount_list = list()
        new_budgetbreakdown_array = list()
        for q_0 in range(len(self.__pn_payload['planning']['budget']['budgetBreakdown'])):

            new_budgetbreakdown_array.append(copy.deepcopy(
                self.__expected_ms_release['releases'][0]['planning']['budget']['budgetBreakdown'][0]))

            new_budgetbreakdown_array[q_0]['id'] = \
                self.__pn_payload['planning']['budget']['budgetBreakdown'][q_0]['id']

            actual_fs_release = requests.get(url=f"{self.metadata_budget_url}/{fs_budget_cpid_ocid_list[q_0]}").json()
            if "description" in actual_fs_release['releases'][0]['planning']['budget']:

                new_budgetbreakdown_array[q_0]['description'] = \
                    actual_fs_release['releases'][0]['planning']['budget']['description']
            else:
                del new_budgetbreakdown_array[q_0]['description']

            new_budgetbreakdown_array[q_0]['amount']['amount'] = \
                round(self.__pn_payload['planning']['budget']['budgetBreakdown'][q_0]['amount']['amount'], 2)

            sum_of_budgetbreakdown_amount_list.append(new_budgetbreakdown_array[q_0]['amount']['amount'])

            new_budgetbreakdown_array[q_0]['amount']['currency'] = \
                actual_fs_release['releases'][0]['planning']['budget']['amount']['currency']

            new_budgetbreakdown_array[q_0]['period']['startDate'] = \
                actual_fs_release['releases'][0]['planning']['budget']['period']['startDate']

            new_budgetbreakdown_array[q_0]['period']['endDate'] = \
                actual_fs_release['releases'][0]['planning']['budget']['period']['endDate']

            new_budgetbreakdown_array[q_0]['sourceParty']['id'] = \
                actual_fs_release['releases'][0]['planning']['budget']['sourceEntity']['id']

            new_budgetbreakdown_array[q_0]['sourceParty']['name'] = \
                actual_fs_release['releases'][0]['planning']['budget']['sourceEntity']['name']

            if "europeanUnionFunding" in actual_fs_release['releases'][0]['planning']['budget']:

                new_budgetbreakdown_array[q_0]['europeanUnionFunding'] = \
                    actual_fs_release['releases'][0]['planning']['budget']['europeanUnionFunding']

                if "uri" in actual_fs_release['releases'][0]['planning']['budget']['europeanUnionFunding']:

                    new_budgetbreakdown_array[q_0]['europeanUnionFunding']['uri'] = \
                        actual_fs_release['releases'][0]['planning']['budget']['europeanUnionFunding']['uri']
                else:
                    del new_budgetbreakdown_array[q_0]['planning']['budget']['europeanUnionFunding']['uri']
            else:
                del self.__expected_ms_release['releases'][0]['planning']['budget']['europeanUnionFunding']

        self.__expected_ms_release['releases'][0]['planning']['budget']['budgetBreakdown'] = new_budgetbreakdown_array

        self.__expected_ms_release['releases'][0]['planning']['budget']['amount']['amount'] = \
            round(sum(sum_of_budgetbreakdown_amount_list), 2)

        self.__expected_ms_release['releases'][0]['planning']['budget']['amount']['currency'] = \
            self.__pn_payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']

        # Build the releases.tender object. Enrich or delete optional fields and enrich required fields:
        is_permanent_tender_id_correct = is_it_uuid(
            self.__actual_ms_release['releases'][0]['tender']['id'])

        if is_permanent_tender_id_correct is True:

            self.__expected_ms_release['releases'][0]['tender']['id'] = \
                self.__actual_ms_release['releases'][0]['tender']['id']
        else:
            raise ValueError(f"The relases0.tender.id must be uuid.")

        self.__expected_ms_release['releases'][0]['tender']['title'] = self.__pn_payload['tender']['title']
        self.__expected_ms_release['releases'][0]['tender']['description'] = self.__pn_payload['tender']['description']

        try:
            """
            Enrich releases.tender.classification object, depends on items into pn_payload.
            """
            if "items" in self.__pn_payload['tender']:

                expected_cpv_data = get_value_from_cpv_dictionary_xls(
                    cpv=generate_tender_classification_id(self.__pn_payload['tender']['items']),
                    language=self.__language
                )
            else:
                expected_cpv_data = get_value_from_cpv_dictionary_xls(
                    cpv=tender_classification_id,
                    language=self.__language
                )

            self.__expected_ms_release['releases'][0]['tender']['classification']['id'] = expected_cpv_data[0]
            self.__expected_ms_release['releases'][0]['tender']['classification']['description'] = expected_cpv_data[1]
            self.__expected_ms_release['releases'][0]['tender']['classification']['scheme'] = "CPV"
        except ValueError:
            raise ValueError("Impossible to enrich releases.tender.classification object.")

        self.__expected_ms_release['releases'][0]['tender']['legalBasis'] = self.__pn_payload['tender']['legalBasis']

        self.__expected_ms_release['releases'][0]['tender']['procurementMethodRationale'] = \
            self.__pn_payload['tender']['procurementMethodRationale']

        try:
            """
           Enrich mainProcurementCategory, depends on tender.classification.id.
           """
            if \
                    tender_classification_id == "03" or \
                    tender_classification_id[0] == "1" or \
                    tender_classification_id[0] == "2" or \
                    tender_classification_id[0] == "3" or \
                    tender_classification_id[0:2] == "44" or \
                    tender_classification_id[0:2] == "48":
                expected_main_procurement_category = "goods"

            elif \
                    tender_classification_id[0:2] == "45":
                expected_main_procurement_category = "works"

            elif \
                    tender_classification_id[0] == "5" or \
                    tender_classification_id[0] == "6" or \
                    tender_classification_id[0] == "7" or \
                    tender_classification_id[0] == "8" or \
                    tender_classification_id[0:2] == "92" or \
                    tender_classification_id[0:2] == "98":
                expected_main_procurement_category = "services"

            else:
                raise ValueError("Check your tender.classification.id")

            self.__expected_ms_release['releases'][0]['tender']['mainProcurementCategory'] = expected_main_procurement_category
        except KeyError:
            raise KeyError("Could not parse tender.classification.id.")

        try:
            """
            Enrich procurementMethod and procurementMethodDetails, depends on pmd.
            """
            if self.__pmd == "TEST_DCO":
                expected_procurementmethod = 'selective'
                expected_procurementmethoddetails = "testDirectCallOff"
            elif self.__pmd == "DCO":
                expected_procurementmethod = 'selective'
                expected_procurementmethoddetails = "directCallOff"
            elif self.__pmd == "TEST_RFQ":
                expected_procurementmethod = 'selective'
                expected_procurementmethoddetails = "testRequestForQuotations"
            elif self.__pmd == "RFQ":
                expected_procurementmethod = 'selective'
                expected_procurementmethoddetails = "requestForQuotations"
            elif self.__pmd == "TEST_MC":
                expected_procurementmethod = 'selective'
                expected_procurementmethoddetails = "testMiniCompetition"
            elif self.__pmd == "MC":
                expected_procurementmethod = 'selective'
                expected_procurementmethoddetails = "miniCompetition"
            else:
                raise ValueError("Check your pmd: You must use 'TEST_DCO', "
                                 "'TEST_RFQ', 'TEST_MC', 'DCO', 'RFQ', 'MC' in pytest command")

            self.__expected_ms_release['releases'][0]['tender']['procurementMethod'] = expected_procurementmethod
            self.__expected_ms_release['releases'][0]['tender']['procurementMethodDetails'] = expected_procurementmethoddetails
        except KeyError:
            raise KeyError("Could not parse a pmd into pytest command.")

        try:
            """
            Enrich eligibilityCriteria, depends on language.
            """
            expected_eligibilitycriteria = None
            if self.__language == "ro":
                expected_eligibilitycriteria = "Regulile generale privind naționalitatea și originea, precum și " \
                                       "alte criterii de eligibilitate sunt enumerate în Ghidul practic privind " \
                                       "procedurile de contractare a acțiunilor externe ale UE (PRAG)"
            elif self.__language == "en":
                expected_eligibilitycriteria = "The general rules on nationality and origin, as well as other eligibility " \
                                       "criteria are listed in the Practical Guide to Contract Procedures for EU " \
                                       "External Actions (PRAG)"
            else:
                raise ValueError("Check your language: You must use 'ro', "
                                 "'en' in pytest command.")

            self.__expected_ms_release['releases'][0]['tender']['eligibilityCriteria'] = expected_eligibilitycriteria
        except KeyError:
            raise KeyError("Could not parse a language into pytest command.")

        expected_contractperiod = get_contract_period_for_ms_release(lots_array=self.__pn_payload['tender']['lots'])
        self.__expected_ms_release['releases'][0]['tender']['contractPeriod']['startDate'] = expected_contractperiod[0]
        self.__expected_ms_release['releases'][0]['tender']['contractPeriod']['endDate'] = expected_contractperiod[1]

        self.__expected_ms_release['releases'][0]['tender']['procurementMethodAdditionalInfo'] = \
            self.__pn_payload['tender']['procurementMethodAdditionalInfo']

        try:
            """
            Enrich releases.tender.value.amount, depends on lots into pn_payload.
            """
            if "lots" in self.__pn_payload['tender']:

                self.__expected_ms_release['releases'][0]['tender']['value']['amount'] = \
                    round(get_sum_of_lot(lots_array=self.__pn_payload['tender']['lots']), 2)

                self.__expected_ms_release['releases'][0]['tender']['value']['currency'] = \
                    self.__pn_payload['tender']['lots'][0]['value']['currency']
            else:
                self.__expected_ms_release['releases'][0]['tender']['value']['amount'] = round(
                    sum(sum_of_budgetbreakdown_amount_list), 2)

                self.__expected_ms_release['releases'][0]['tender']['value']['currency'] = \
                    self.__pn_payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        except ValueError:
            raise ValueError("Impossible to enrich releases.tender.value.amount.")

        # Build the releases.parties array. Enrich or delete optional fields and enrich required fields:

        return self.__expected_ms_release
