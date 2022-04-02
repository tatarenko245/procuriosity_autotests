import copy


from tests.utils.functions_collection.functions import get_value_from_cpv_dictionary_xls, \
    get_value_from_cpvs_dictionary_csv, get_value_from_classification_unit_dictionary_csv, get_value_from_country_csv, \
    get_value_from_region_csv, get_value_from_locality_csv, is_it_uuid, get_contract_period_for_ms_release, \
    get_sum_of_lot, generate_tender_classification_id, get_unique_party_from_list_by_id


class PlanningNoticeRelease:
    def __init__(self, environment, host_to_service, language, pmd, pn_payload, pn_message, actual_pn_release,
                 actual_ms_release):

        self.__environment = environment
        self.__host = host_to_service
        self.__language = language
        self.__pmd = pmd
        self.__pn_payload = pn_payload
        self.__pn_message = pn_message
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
                self.__metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"

            elif environment == "sandbox":
                self.__metadata_tender_url = "http://public.eprocurement.systems/tenders"

                extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.json"
                ]

                publisher_name = "Viešųjų pirkimų tarnyba"
                publisher_uri = "https://vpt.lrv.lt"
                self.__metadata_document_url = "http://storage.eprocurement.systems/get"
                self.__metadata_budget_url = "http://public.eprocurement.systems/budgets"
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
                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails'][
                        'region'] = expected_lot_region_object
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

                    new_documents_array[q_0]['datePublished'] = self.__pn_message['data']['operationDate']
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

        self.__expected_pn_release['releases'][0]['relatedProcesses'][0]['identifier'] = \
            self.__pn_message['data']['ocid']

        self.__expected_pn_release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.__metadata_tender_url}/{self.__pn_message['data']['ocid']}/{self.__pn_message['data']['ocid']}"

        return self.__expected_pn_release

    def build_expected_ms_release(self, ei_payload, ei_message, fs_payloads_list, fs_message_list,
                                  tender_classification_id):

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

            # actual_fs_release = requests.get(url=f"{self.metadata_budget_url}/{fs_budget_cpid_ocid_list[q_0]}").json()
            if "description" in fs_payloads_list[q_0]['planning']['budget']:

                new_budgetbreakdown_array[q_0]['description'] = \
                    fs_payloads_list[q_0]['planning']['budget']['description']
            else:
                del new_budgetbreakdown_array[q_0]['description']

            new_budgetbreakdown_array[q_0]['amount']['amount'] = \
                round(self.__pn_payload['planning']['budget']['budgetBreakdown'][q_0]['amount']['amount'], 2)

            sum_of_budgetbreakdown_amount_list.append(new_budgetbreakdown_array[q_0]['amount']['amount'])

            new_budgetbreakdown_array[q_0]['amount']['currency'] = \
                fs_payloads_list[q_0]['planning']['budget']['amount']['currency']

            new_budgetbreakdown_array[q_0]['period']['startDate'] = \
                fs_payloads_list[q_0]['planning']['budget']['period']['startDate']

            new_budgetbreakdown_array[q_0]['period']['endDate'] = \
                fs_payloads_list[q_0]['planning']['budget']['period']['endDate']

            if "buyer" in fs_payloads_list[q_0]:
                new_budgetbreakdown_array[q_0]['sourceParty']['id'] = \
                    f"{fs_payloads_list[q_0]['buyer']['identifier']['scheme']}-" \
                    f"{fs_payloads_list[q_0]['buyer']['identifier']['id']}"

                new_budgetbreakdown_array[q_0]['sourceParty']['name'] = fs_payloads_list[q_0]['buyer']['name']
            else:

                new_budgetbreakdown_array[q_0]['sourceParty']['id'] = \
                    f"{ei_payload['buyer']['identifier']['scheme']}-" \
                    f"{ei_payload['buyer']['identifier']['id']}"

                new_budgetbreakdown_array[q_0]['sourceParty']['name'] = ei_payload['buyer']['name']

            if "europeanUnionFunding" in fs_payloads_list[q_0]['planning']['budget']:

                new_budgetbreakdown_array[q_0]['europeanUnionFunding'] = \
                    fs_payloads_list[q_0]['planning']['budget']['europeanUnionFunding']

                if "uri" in fs_payloads_list[q_0]['planning']['budget']['europeanUnionFunding']:

                    new_budgetbreakdown_array[q_0]['europeanUnionFunding']['uri'] = \
                        fs_payloads_list[q_0]['planning']['budget']['europeanUnionFunding']['uri']
                else:
                    del new_budgetbreakdown_array[q_0]['europeanUnionFunding']['uri']
            else:
                del new_budgetbreakdown_array[q_0]['europeanUnionFunding']

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
                    tender_classification_id[0:2] == "03" or \
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

            self.__expected_ms_release['releases'][0]['tender']['mainProcurementCategory'] = \
                expected_main_procurement_category

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
            self.__expected_ms_release['releases'][0]['tender'][
                'procurementMethodDetails'] = expected_procurementmethoddetails
        except KeyError:
            raise KeyError("Could not parse a pmd into pytest command.")

        try:
            """
            Enrich eligibilityCriteria, depends on language.
            """
            if self.__language == "ro":
                expected_eligibilitycriteria = "Regulile generale privind naționalitatea și originea, precum și " \
                                               "alte criterii de eligibilitate sunt enumerate în " \
                                               "Ghidul practic privind procedurile de contractare " \
                                               "a acțiunilor externe ale UE (PRAG)"
            elif self.__language == "en":
                expected_eligibilitycriteria = "The general rules on nationality and origin, " \
                                               "as well as other eligibility criteria are listed " \
                                               "in the Practical Guide to Contract Procedures for EU " \
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
        buyer_role_array = list()
        payer_role_array = list()
        funder_role_array = list()

        buyer_role_array.append(copy.deepcopy(self.__expected_ms_release['releases'][0]['parties'][0]))

        buyer_role_array[0]['id'] = f"{ei_payload['buyer']['identifier']['scheme']}-" \
                                    f"{ei_payload['buyer']['identifier']['id']}"

        buyer_role_array[0]['name'] = ei_payload['buyer']['name']
        buyer_role_array[0]['identifier']['scheme'] = ei_payload['buyer']['identifier']['scheme']
        buyer_role_array[0]['identifier']['id'] = ei_payload['buyer']['identifier']['id']
        buyer_role_array[0]['identifier']['legalName'] = ei_payload['buyer']['identifier']['legalName']
        buyer_role_array[0]['address']['streetAddress'] = ei_payload['buyer']['address']['streetAddress']

        if "postalCode" in ei_payload['buyer']['address']:
            buyer_role_array[0]['address']['postalCode'] = ei_payload['buyer']['address']['postalCode']
        else:
            del buyer_role_array[0]['address']['postalCode']

        try:
            """
            Prepare addressDetails object for party with buyer role.
            """
            buyer_country_data = get_value_from_country_csv(
                country=ei_payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.__language
            )
            expected_buyer_country_object = {
                "scheme": buyer_country_data[2],
                "id": ei_payload['buyer']['address']['addressDetails']['country']['id'],
                "description": buyer_country_data[1],
                "uri": buyer_country_data[3]
            }

            buyer_region_data = get_value_from_region_csv(
                region=ei_payload['buyer']['address']['addressDetails']['region']['id'],
                country=ei_payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.__language
            )
            expected_buyer_region_object = {
                "scheme": buyer_region_data[2],
                "id": ei_payload['buyer']['address']['addressDetails']['region']['id'],
                "description": buyer_region_data[1],
                "uri": buyer_region_data[3]
            }

            if ei_payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":

                buyer_locality_data = get_value_from_locality_csv(
                    locality=ei_payload['buyer']['address']['addressDetails']['locality']['id'],
                    region=ei_payload['buyer']['address']['addressDetails']['region']['id'],
                    country=ei_payload['buyer']['address']['addressDetails']['country']['id'],
                    language=self.__language
                )
                expected_buyer_locality_object = {
                    "scheme": buyer_locality_data[2],
                    "id": ei_payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": buyer_locality_data[1],
                    "uri": buyer_locality_data[3]
                }
            else:
                expected_buyer_locality_object = {
                    "scheme": ei_payload['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": ei_payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": ei_payload['buyer']['address']['addressDetails']['locality']['description']
                }

            buyer_role_array[0]['address']['addressDetails']['country'] = expected_buyer_country_object
            buyer_role_array[0]['address']['addressDetails']['region'] = expected_buyer_region_object
            buyer_role_array[0]['address']['addressDetails']['locality'] = expected_buyer_locality_object
        except ValueError:
            raise ValueError(
                "Impossible to prepare addressDetails object for party with buyer role.")

        if "uri" in ei_payload['buyer']['identifier']:
            buyer_role_array[0]['identifier']['uri'] = ei_payload['buyer']['identifier']['uri']
        else:
            del buyer_role_array[0]['identifier']['uri']

        if "additionalIdentifiers" in ei_payload['buyer']:
            for q_1 in range(len(ei_payload['buyer']['additionalIdentifiers'])):
                buyer_role_array[0]['additionalIdentifiers'][q_1]['scheme'] = \
                    ei_payload['buyer']['additionalIdentifiers'][q_1]['scheme']

                buyer_role_array[0]['additionalIdentifiers'][q_1]['id'] = \
                    ei_payload['buyer']['additionalIdentifiers'][q_1]['id']

                buyer_role_array[0]['additionalIdentifiers'][q_1]['legalName'] = \
                    ei_payload['buyer']['additionalIdentifiers'][q_1]['legalName']

                buyer_role_array[0]['additionalIdentifiers'][q_1]['uri'] = \
                    ei_payload['buyer']['additionalIdentifiers'][q_1]['uri']
        else:
            del buyer_role_array[0]['additionalIdentifiers']

        if "faxNumber" in ei_payload['buyer']['contactPoint']:
            buyer_role_array[0]['contactPoint']['faxNumber'] = ei_payload['buyer']['contactPoint']['faxNumber']
        else:
            del buyer_role_array[0]['contactPoint']['faxNumber']

        if "url" in ei_payload['buyer']['contactPoint']:
            buyer_role_array[0]['contactPoint']['url'] = ei_payload['buyer']['contactPoint']['url']
        else:
            del buyer_role_array[0]['contactPoint']['url']

        buyer_role_array[0]['contactPoint']['name'] = ei_payload['buyer']['contactPoint']['name']
        buyer_role_array[0]['contactPoint']['email'] = ei_payload['buyer']['contactPoint']['email']
        buyer_role_array[0]['contactPoint']['telephone'] = ei_payload['buyer']['contactPoint']['telephone']

        if "details" in ei_payload['buyer']:
            if "typeOfBuyer" in ei_payload['buyer']['details']:
                buyer_role_array[0]['details']['typeOfBuyer'] = ei_payload['buyer']['details']['typeOfBuyer']
            else:
                del buyer_role_array['buyer']['details']['typeOfBuyer']

            if "mainGeneralActivity" in ei_payload['buyer']['details']:

                buyer_role_array[0]['details']['mainGeneralActivity'] = \
                    ei_payload['buyer']['details']['mainGeneralActivity']
            else:
                del buyer_role_array[0]['details']['mainGeneralActivity']

            if "mainSectoralActivity" in ei_payload['buyer']['details']:

                buyer_role_array[0]['details']['mainSectoralActivity'] = \
                    ei_payload['buyer']['details']['mainSectoralActivity']
            else:
                del buyer_role_array[0]['details']['mainSectoralActivity']
        else:
            del buyer_role_array[0]['details']

        buyer_role_array[0]['roles'] = ["buyer"]

        for q_2 in range(len(fs_payloads_list)):
            if "buyer" in fs_payloads_list[q_2]:
                funder_role_array.append(copy.deepcopy(self.__expected_ms_release['releases'][0]['parties'][0]))

                funder_role_array[q_2]['id'] = f"{fs_payloads_list[q_2]['buyer']['identifier']['scheme']}-" \
                                               f"{fs_payloads_list[q_2]['buyer']['identifier']['id']}"

                funder_role_array[q_2]['name'] = fs_payloads_list[q_2]['buyer']['name']
                funder_role_array[q_2]['identifier']['scheme'] = fs_payloads_list[q_2]['buyer']['identifier']['scheme']
                funder_role_array[q_2]['identifier']['id'] = fs_payloads_list[q_2]['buyer']['identifier']['id']

                funder_role_array[q_2]['identifier']['legalName'] = \
                    fs_payloads_list[q_2]['buyer']['identifier']['legalName']

                funder_role_array[q_2]['address']['streetAddress'] = fs_payloads_list[q_2]['buyer']['address'][
                    'streetAddress']

                if "postalCode" in fs_payloads_list[q_2]['buyer']['address']:

                    funder_role_array[q_2]['address']['postalCode'] = \
                        fs_payloads_list[q_2]['buyer']['address']['postalCode']
                else:
                    del funder_role_array[q_2]['address']['postalCode']

                try:
                    """
                    Prepare addressDetails object for party with funder role.
                    """
                    funder_country_data = get_value_from_country_csv(
                        country=fs_payloads_list[q_2]['buyer']['address']['addressDetails']['country']['id'],
                        language=self.__language
                    )
                    expected_funder_country_object = {
                        "scheme": funder_country_data[2],
                        "id": fs_payloads_list[q_2]['buyer']['address']['addressDetails']['country']['id'],
                        "description": funder_country_data[1],
                        "uri": funder_country_data[3]
                    }

                    funder_region_data = get_value_from_region_csv(
                        region=fs_payloads_list[q_2]['buyer']['address']['addressDetails']['region']['id'],
                        country=fs_payloads_list[q_2]['buyer']['address']['addressDetails']['country']['id'],
                        language=self.__language
                    )
                    expected_funder_region_object = {
                        "scheme": funder_region_data[2],
                        "id": fs_payloads_list[q_2]['buyer']['address']['addressDetails']['region']['id'],
                        "description": funder_region_data[1],
                        "uri": funder_region_data[3]
                    }

                    if fs_payloads_list[q_2]['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":

                        funder_locality_data = get_value_from_locality_csv(
                            locality=fs_payloads_list[q_2]['buyer']['address']['addressDetails']['locality']['id'],
                            region=fs_payloads_list[q_2]['buyer']['address']['addressDetails']['region']['id'],
                            country=fs_payloads_list[q_2]['buyer']['address']['addressDetails']['country']['id'],
                            language=self.__language
                        )
                        expected_funder_locality_object = {
                            "scheme": funder_locality_data[2],
                            "id": fs_payloads_list[q_2]['buyer']['address']['addressDetails']['locality']['id'],
                            "description": funder_locality_data[1],
                            "uri": funder_locality_data[3]
                        }
                    else:
                        expected_funder_locality_object = {
                            "scheme": fs_payloads_list[q_2]['buyer']['address']['addressDetails']['locality']['scheme'],
                            "id": fs_payloads_list[q_2]['buyer']['address']['addressDetails']['locality']['id'],

                            "description":
                                fs_payloads_list[q_2]['buyer']['address']['addressDetails']['locality']['description']
                        }

                    funder_role_array[q_2]['address']['addressDetails']['country'] = expected_funder_country_object
                    funder_role_array[q_2]['address']['addressDetails']['region'] = expected_funder_region_object
                    funder_role_array[q_2]['address']['addressDetails']['locality'] = expected_funder_locality_object
                except ValueError:
                    raise ValueError(
                        "Impossible to prepare addressDetails object for party with funder role.")

                if "uri" in fs_payloads_list[q_2]['buyer']['identifier']:
                    funder_role_array[q_2]['identifier']['uri'] = fs_payloads_list[q_2]['buyer']['identifier']['uri']
                else:
                    del funder_role_array[q_2]['identifier']['uri']

                if "additionalIdentifiers" in fs_payloads_list[q_2]['buyer']:
                    for q_3 in range(len(fs_payloads_list[q_2]['buyer']['additionalIdentifiers'])):
                        funder_role_array[q_2]['additionalIdentifiers'][q_3]['scheme'] = \
                            fs_payloads_list[q_2]['buyer']['additionalIdentifiers'][q_3]['scheme']

                        funder_role_array[q_2]['additionalIdentifiers'][q_3]['id'] = \
                            fs_payloads_list[q_2]['buyer']['additionalIdentifiers'][q_3]['id']

                        funder_role_array[q_2]['additionalIdentifiers'][q_3]['legalName'] = \
                            fs_payloads_list[q_2]['buyer']['additionalIdentifiers'][q_3]['legalName']

                        funder_role_array[q_2]['additionalIdentifiers'][q_3]['uri'] = \
                            fs_payloads_list[q_2]['buyer']['additionalIdentifiers'][q_3]['uri']
                else:
                    del funder_role_array[q_2]['additionalIdentifiers']

                if "faxNumber" in fs_payloads_list[q_2]['buyer']['contactPoint']:

                    funder_role_array[q_2]['contactPoint']['faxNumber'] = \
                        fs_payloads_list[q_2]['buyer']['contactPoint']['faxNumber']
                else:
                    del funder_role_array[q_2]['contactPoint']['faxNumber']

                if "url" in fs_payloads_list[q_2]['buyer']['contactPoint']:
                    funder_role_array[q_2]['contactPoint']['url'] = fs_payloads_list[q_2]['buyer']['contactPoint'][
                        'url']
                else:
                    del funder_role_array[q_2]['contactPoint']['url']

                funder_role_array[q_2]['contactPoint']['name'] = \
                    fs_payloads_list[q_2]['buyer']['contactPoint']['name']

                funder_role_array[q_2]['contactPoint']['email'] = \
                    fs_payloads_list[q_2]['buyer']['contactPoint']['email']

                funder_role_array[q_2]['contactPoint']['telephone'] = \
                    fs_payloads_list[q_2]['buyer']['contactPoint']['telephone']

                del funder_role_array[q_2]['details']
                funder_role_array[q_2]['roles'] = ["funder"]

        for q_3 in range(len(fs_payloads_list)):
            payer_role_array.append(copy.deepcopy(self.__expected_ms_release['releases'][0]['parties'][0]))

            payer_role_array[q_3]['id'] = \
                f"{fs_payloads_list[q_3]['tender']['procuringEntity']['identifier']['scheme']}-" \
                f"{fs_payloads_list[q_3]['tender']['procuringEntity']['identifier']['id']}"

            payer_role_array[q_3]['name'] = fs_payloads_list[q_3]['tender']['procuringEntity']['name']

            payer_role_array[q_3]['identifier']['scheme'] = \
                fs_payloads_list[q_3]['tender']['procuringEntity']['identifier']['scheme']

            payer_role_array[q_3]['identifier']['id'] = \
                fs_payloads_list[q_3]['tender']['procuringEntity']['identifier']['id']

            payer_role_array[q_3]['identifier']['legalName'] = \
                fs_payloads_list[q_3]['tender']['procuringEntity']['identifier']['legalName']

            payer_role_array[q_3]['address']['streetAddress'] = \
                fs_payloads_list[q_3]['tender']['procuringEntity']['address']['streetAddress']

            if "postalCode" in fs_payloads_list[q_3]['tender']['procuringEntity']['address']:

                payer_role_array[q_3]['address']['postalCode'] = \
                    fs_payloads_list[q_3]['tender']['procuringEntity']['address']['postalCode']
            else:
                del payer_role_array[q_3]['address']['postalCode']

            try:
                """
                Prepare addressDetails object for party with payer role.
                """
                payer_country_data = get_value_from_country_csv(
                    country=fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                        'country']['id'],

                    language=self.__language
                )
                expected_payer_country_object = {
                    "scheme": payer_country_data[2],

                    "id": fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                        'country']['id'],

                    "description": payer_country_data[1],
                    "uri": payer_country_data[3]
                }

                payer_region_data = get_value_from_region_csv(
                    region=fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                        'region']['id'],

                    country=fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                        'country']['id'],

                    language=self.__language
                )
                expected_payer_region_object = {
                    "scheme": payer_region_data[2],

                    "id": fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                        'region']['id'],

                    "description": payer_region_data[1],
                    "uri": payer_region_data[3]
                }

                if fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                        'locality']['scheme'] == "CUATM":

                    payer_locality_data = get_value_from_locality_csv(
                        locality=fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['id'],

                        region=fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                            'region']['id'],

                        country=fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                            'country']['id'],

                        language=self.__language
                    )
                    expected_payer_locality_object = {
                        "scheme": payer_locality_data[2],
                        "id": fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['id'],

                        "description": payer_locality_data[1],
                        "uri": payer_locality_data[3]
                    }
                else:
                    expected_payer_locality_object = {
                        "scheme": fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['scheme'],

                        "id": fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['id'],

                        "description": fs_payloads_list[q_3]['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['description']
                    }

                payer_role_array[q_3]['address']['addressDetails']['country'] = expected_payer_country_object
                payer_role_array[q_3]['address']['addressDetails']['region'] = expected_payer_region_object
                payer_role_array[q_3]['address']['addressDetails']['locality'] = expected_payer_locality_object
            except ValueError:
                raise ValueError(
                    "Impossible to prepare addressDetails object for party with funder role.")

            if "uri" in fs_payloads_list[q_3]['tender']['procuringEntity']['identifier']:

                payer_role_array[q_3]['identifier']['uri'] = \
                    fs_payloads_list[q_3]['tender']['procuringEntity']['identifier']['uri']
            else:
                del payer_role_array[q_3]['identifier']['uri']

            if "additionalIdentifiers" in fs_payloads_list[q_3]['tender']['procuringEntity']:
                for q_4 in range(len(fs_payloads_list[q_3]['tender']['procuringEntity']['additionalIdentifiers'])):
                    payer_role_array[q_3]['additionalIdentifiers'][q_4]['scheme'] = \
                        fs_payloads_list[q_3]['tender']['procuringEntity']['additionalIdentifiers'][q_4]['scheme']

                    payer_role_array[q_3]['additionalIdentifiers'][q_4]['id'] = \
                        fs_payloads_list[q_3]['tender']['procuringEntity']['additionalIdentifiers'][q_4]['id']

                    payer_role_array[q_3]['additionalIdentifiers'][q_4]['legalName'] = \
                        fs_payloads_list[q_3]['tender']['procuringEntity']['additionalIdentifiers'][q_4]['legalName']

                    payer_role_array[q_3]['additionalIdentifiers'][q_4]['uri'] = \
                        fs_payloads_list[q_3]['tender']['procuringEntity']['additionalIdentifiers'][q_4]['uri']
            else:
                del payer_role_array[q_3]['additionalIdentifiers']

            if "faxNumber" in fs_payloads_list[q_3]['tender']['procuringEntity']['contactPoint']:

                payer_role_array[q_3]['contactPoint']['faxNumber'] = \
                    fs_payloads_list[q_3]['tender']['procuringEntity']['contactPoint']['faxNumber']
            else:
                del payer_role_array[q_3]['contactPoint']['faxNumber']

            if "url" in fs_payloads_list[q_3]['tender']['procuringEntity']['contactPoint']:

                payer_role_array[q_3]['contactPoint']['url'] = \
                    fs_payloads_list[q_3]['tender']['procuringEntity']['contactPoint']['url']
            else:
                del payer_role_array[q_3]['contactPoint']['url']

            payer_role_array[q_3]['contactPoint']['name'] = \
                fs_payloads_list[q_3]['tender']['procuringEntity']['contactPoint']['name']

            payer_role_array[q_3]['contactPoint']['email'] = \
                fs_payloads_list[q_3]['tender']['procuringEntity']['contactPoint']['email']

            payer_role_array[q_3]['contactPoint']['telephone'] = \
                fs_payloads_list[q_3]['tender']['procuringEntity']['contactPoint']['telephone']

            del payer_role_array[q_3]['details']
            payer_role_array[q_3]['roles'] = ["payer"]

        unique_buyer_role_array = get_unique_party_from_list_by_id(buyer_role_array)
        unique_payer_role_array = get_unique_party_from_list_by_id(payer_role_array)
        unique_funder_role_array = get_unique_party_from_list_by_id(funder_role_array)

        unique_buyer_id_role_array = list()
        for buyer in range(len(unique_buyer_role_array)):
            unique_buyer_id_role_array.append(unique_buyer_role_array[buyer]['id'])

        unique_payer_id_role_array = list()
        for payer in range(len(unique_payer_role_array)):
            unique_payer_id_role_array.append(unique_payer_role_array[payer]['id'])

        unique_funder_id_role_array = list()
        for funder in range(len(unique_funder_role_array)):
            unique_funder_id_role_array.append(unique_funder_role_array[funder]['id'])

        same_id_into_payer_and_funder = list(set(unique_payer_id_role_array) & set(unique_funder_id_role_array))

        temp_parties_with_payer_role_array = list()
        temp_parties_with_funder_role_array = list()

        for payer in range(len(unique_payer_role_array)):
            for i_1 in range(len(same_id_into_payer_and_funder)):
                for funder in range(len(unique_funder_role_array)):
                    if unique_payer_role_array[payer]['id'] == same_id_into_payer_and_funder[i_1] == \
                            unique_funder_role_array[funder]['id']:

                        unique_payer_role_array[payer]['roles'] = \
                            unique_payer_role_array[payer]['roles'] + unique_funder_role_array[funder]['roles']

                        temp_parties_with_payer_role_array.append(unique_payer_role_array[payer])

                for funder in range(len(unique_funder_role_array)):
                    if unique_payer_role_array[payer]['id'] != same_id_into_payer_and_funder[i_1]:
                        temp_parties_with_payer_role_array.append(unique_payer_role_array[payer])

                    if unique_funder_role_array[funder]['id'] != same_id_into_payer_and_funder[i_1]:
                        temp_parties_with_funder_role_array.append(unique_payer_role_array[funder])

        unique_parties_id_with_payer_role_array = list()
        for payer in range(len(temp_parties_with_payer_role_array)):
            unique_parties_id_with_payer_role_array.append(temp_parties_with_payer_role_array[payer]['id'])

        same_id_into_buyer_and_payer = \
            list(set(unique_buyer_id_role_array) & set(unique_parties_id_with_payer_role_array))

        parties_with_buyer_role_array = list()
        parties_with_payer_role_array = list()
        parties_with_funder_role_array = list()
        for buyer in range(len(unique_buyer_role_array)):
            for i_1 in range(len(same_id_into_buyer_and_payer)):
                for payer in range(len(temp_parties_with_payer_role_array)):

                    if unique_buyer_role_array[buyer]['id'] == same_id_into_buyer_and_payer[i_1] == \
                            temp_parties_with_payer_role_array[payer]['id']:

                        unique_buyer_role_array[buyer]['roles'] = \
                            unique_buyer_role_array[buyer]['roles'] + temp_parties_with_payer_role_array[payer]['roles']

                        parties_with_buyer_role_array.append(unique_buyer_role_array[buyer])

                for payer in range(len(temp_parties_with_payer_role_array)):
                    if temp_parties_with_payer_role_array[payer]['id'] != same_id_into_buyer_and_payer[i_1]:
                        parties_with_payer_role_array.append(temp_parties_with_payer_role_array[payer])

        unique_parties_id_with_funder_role_array = list()
        for funder in range(len(temp_parties_with_funder_role_array)):
            unique_parties_id_with_funder_role_array.append(temp_parties_with_funder_role_array[funder]['id'])

        same_id_into_buyer_and_funder = \
            list(set(unique_buyer_id_role_array) & set(unique_parties_id_with_funder_role_array))

        for buyer in range(len(unique_buyer_role_array)):
            for i_1 in range(len(same_id_into_buyer_and_funder)):
                for funder in range(len(temp_parties_with_funder_role_array)):

                    if unique_buyer_role_array[buyer]['id'] == same_id_into_buyer_and_funder[i_1] == \
                            temp_parties_with_funder_role_array[funder]['id']:

                        unique_buyer_role_array[buyer]['roles'] = \
                            unique_buyer_role_array[buyer]['roles'] + \
                            temp_parties_with_funder_role_array[funder]['roles']

                        parties_with_buyer_role_array.append(unique_buyer_role_array[buyer])

                for funder in range(len(temp_parties_with_funder_role_array)):
                    if temp_parties_with_funder_role_array[funder]['id'] != same_id_into_buyer_and_funder[i_1]:
                        parties_with_funder_role_array.append(temp_parties_with_funder_role_array[funder])

        parties_array = parties_with_buyer_role_array + parties_with_payer_role_array + parties_with_funder_role_array

        expected_parties_array = list()
        if len(self.__actual_ms_release['releases'][0]['parties']) == len(parties_array):
            for act in range(len(self.__actual_ms_release['releases'][0]['parties'])):
                for exp in range(len(parties_array)):
                    if parties_array[exp]['id'] == self.__actual_ms_release['releases'][0]['parties'][act]['id']:
                        expected_parties_array.append(parties_array[exp])
        else:
            raise ValueError("Quantity of objects into actual ms release doesn't equal "
                             "quantity of objects into prepared parties arry")

        self.__expected_ms_release['releases'][0]['parties'] = expected_parties_array

        # Build the releases.relatedProcesses array. Enrich required fields:

        new_relatedprocesses_array = list()
        for q_0 in range(2):
            new_relatedprocesses_array.append(
                copy.deepcopy(self.__expected_ms_release['releases'][0]['relatedProcesses'][0])
            )

        new_relatedprocesses_array[0]['relationship'] = ["planning"]
        new_relatedprocesses_array[0]['scheme'] = "ocid"
        new_relatedprocesses_array[0]['identifier'] = self.__pn_message['data']['outcomes']['pn'][0]['id']

        new_relatedprocesses_array[0]['uri'] = \
            f"{self.__metadata_tender_url}/{self.__pn_message['data']['ocid']}/" \
            f"{self.__pn_message['data']['outcomes']['pn'][0]['id']}"

        new_relatedprocesses_array[1]['relationship'] = ["x_expenditureItem"]
        new_relatedprocesses_array[1]['scheme'] = "ocid"
        new_relatedprocesses_array[1]['identifier'] = ei_message['data']['outcomes']['ei'][0]['id']

        new_relatedprocesses_array[1]['uri'] = \
            f"{self.__metadata_budget_url}/{ei_message['data']['outcomes']['ei'][0]['id']}/" \
            f"{ei_message['data']['outcomes']['ei'][0]['id']}"

        fs_relatedprocesses_array = list()
        for q_0 in range(len(fs_message_list)):

            fs_relatedprocesses_array.append(
                copy.deepcopy(self.__expected_ms_release['releases'][0]['relatedProcesses'][0])
            )

            fs_relatedprocesses_array[q_0]['relationship'] = ["x_fundingSource"]
            fs_relatedprocesses_array[q_0]['scheme'] = "ocid"

            fs_relatedprocesses_array[q_0]['identifier'] = \
                fs_message_list[q_0]['data']['outcomes']['fs'][0]['id']

            fs_relatedprocesses_array[q_0]['uri'] = \
                f"{self.__metadata_budget_url}/{ei_message['data']['outcomes']['ei'][0]['id']}/" \
                f"{fs_message_list[q_0]['data']['outcomes']['fs'][0]['id']}"

        expected_relatedprocesses_array = new_relatedprocesses_array + fs_relatedprocesses_array
        if len(self.__actual_ms_release['releases'][0]['relatedProcesses']) == len(expected_relatedprocesses_array):
            for act in range(len(self.__actual_ms_release['releases'][0]['relatedProcesses'])):
                for exp in range(len(expected_relatedprocesses_array)):

                    is_permanent_releatedprocess_id_correct = is_it_uuid(
                        self.__actual_ms_release['releases'][0]['relatedProcesses'][act]['id'])

                    if is_permanent_releatedprocess_id_correct is True:

                        if self.__actual_ms_release['releases'][0]['relatedProcesses'][act]['identifier'] == \
                                expected_relatedprocesses_array[exp]['identifier']:

                            expected_relatedprocesses_array[exp]['id'] = \
                                self.__actual_ms_release['releases'][0]['relatedProcesses'][act]['id']
                    else:
                        raise ValueError(f"The relases0.relatedProcess.id must be uuid.")
        else:
            raise ValueError("The quantity of actual relatedProcesses array != "
                             "quantity of expected relatedProcess array")

        self.__expected_ms_release['releases'][0]['relatedProcesses'] = expected_relatedprocesses_array
        return self.__expected_ms_release
