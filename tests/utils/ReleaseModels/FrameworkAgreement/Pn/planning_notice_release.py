import copy
import json

from tests.utils.functions_collection.functions import get_value_from_classification_cpv_dictionary_xls, \
    get_value_from_cpvs_dictionary_csv, get_value_from_classification_unit_dictionary_csv, get_value_from_country_csv, \
    get_value_from_region_csv, get_value_from_locality_csv, is_it_uuid


class PlanningNoticeRelease:
    def __init__(self, environment, host_to_service, language, pmd, pn_payload, pn_message, actual_pn_release):
        self.__environment = environment
        self.__host = host_to_service
        self.__language = language
        self.__pmd = pmd
        self.__payload = pn_payload
        self.__message = pn_message
        self.__actual_pn_release = actual_pn_release

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
                metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"

            elif environment == "sandbox":
                self.__metadata_tender_url = "http://public.eprocurement.systems/tenders"

                extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.json"
                ]

                publisher_name = "Viešųjų pirkimų tarnyba"
                publisher_uri = "https://vpt.lrv.lt"
                self.__metadata_document_url = "http://storage.eprocurement.systems/get"
                metadata_budget_url = "http://public.eprocurement.systems/budgets"
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
                                "parent"
                            ],
                            "scheme": "ocid",
                            "identifier": "",
                            "uri": ""
                        }
                    ]
                }
            ]
        }

    def build_expected_pn_release(self):
        # Build or delete optioanl fields.
        if "lots" in self.__payload['tender']:
            try:
                """
                Build the releases.tender.lots array.
                """
                new_lots_array = list()
                for q_0 in range(len(self.__payload['tender']['lots'])):
                    new_lots_array.append(copy.deepcopy(self.__expected_pn_release['releases'][0]['tender']['lots'][0]))

                    # Enrich or delete optional fields:
                    if "internalId" in self.__payload['tender']['lots'][q_0]:
                        new_lots_array[q_0]['internalId'] = self.__payload['tender']['lots'][q_0]['internalId']
                    else:
                        del new_lots_array[q_0]['internalId']

                    if "postalCode" in self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address']:

                        new_lots_array[q_0]['placeOfPerformance']['address']['postalCode'] = \
                            self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address']['postalCode']
                    else:
                        del new_lots_array[q_0]['placeOfPerformance']['address']['postalCode']

                    if "description" in self.__payload['tender']['lots'][q_0]['placeOfPerformance']:

                        new_lots_array[q_0]['placeOfPerformance']['description'] = \
                            self.__payload['tender']['lots'][q_0]['placeOfPerformance']['description']
                    else:
                        del new_lots_array[q_0]['placeOfPerformance']['description']

                    # Enrich required fields:
                    is_permanent_lot_id_correct = is_it_uuid(
                        self.__actual_pn_release['releases'][0]['tender']['lots'][q_0]['id'])

                    if is_permanent_lot_id_correct is True:
                        new_lots_array[q_0]['id'] = self.__actual_pn_release['releases'][0]['tender']['lots'][q_0]['id']
                    else:
                        raise ValueError(f"The relases0.tender.lots{q_0}.id must be uuid.")

                    new_lots_array[q_0]['title'] = self.__payload['tender']['lots'][q_0]['title']
                    new_lots_array[q_0]['description'] = self.__payload['tender']['lots'][q_0]['description']
                    new_lots_array[q_0]['value']['amount'] = self.__payload['tender']['lots'][q_0]['value']['amount']
                    new_lots_array[q_0]['value']['currency'] = self.__payload['tender']['lots'][q_0]['value'][
                        'currency']

                    new_lots_array[q_0]['contractPeriod']['startDate'] = \
                        self.__payload['tender']['lots'][q_0]['contractPeriod']['startDate']

                    new_lots_array[q_0]['contractPeriod']['endDate'] = \
                        self.__payload['tender']['lots'][q_0]['contractPeriod']['endDate']

                    new_lots_array[q_0]['placeOfPerformance']['address']['streetAddress'] = \
                        self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address']['streetAddress']

                    try:
                        """
                        Prepare releases.tender.lots.placeOfPerformance.address.addressDetails object.
                        """
                        lot_country_data = get_value_from_country_csv(
                            country=self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                'addressDetails']['country']['id'],

                            language=self.__language
                        )
                        lot_country_object = {
                            "scheme": lot_country_data[2],

                            "id":
                                self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address']['addressDetails'][
                                    'country']['id'],

                            "description": lot_country_data[1],
                            "uri": lot_country_data[3]
                        }

                        lot_region_data = get_value_from_region_csv(
                            region=self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                'addressDetails']['region']['id'],

                            country=self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                'addressDetails']['country']['id'],

                            language=self.__language
                        )
                        lot_region_object = {
                            "scheme": lot_region_data[2],

                            "id":
                                self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address']['addressDetails'][
                                    'region']['id'],

                            "description": lot_region_data[1],
                            "uri": lot_region_data[3]
                        }

                        if self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address']['addressDetails'][
                                'locality']['scheme'] == "CUATM":

                            lot_locality_data = get_value_from_locality_csv(

                                locality=self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['locality']['id'],

                                region=self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['region']['id'],

                                country=self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails']['country']['id'],

                                language=self.__language
                            )
                            lot_locality_object = {
                                "scheme": lot_locality_data[2],

                                "id": self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails'][
                                    'locality']['id'],

                                "description": lot_locality_data[1],
                                "uri": lot_locality_data[3]
                            }
                        else:
                            lot_locality_object = {
                                "scheme":
                                    self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                        'addressDetails'][
                                        'locality']['scheme'],

                                "id": self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                    'addressDetails'][
                                    'locality']['id'],

                                "description":
                                    self.__payload['tender']['lots'][q_0]['placeOfPerformance']['address'][
                                        'addressDetails'][
                                        'locality']['description']
                            }
                    except ValueError:
                        raise ValueError(
                            "Impossible to prepare the expected releases.tender.lots.placeOfPerformance.address."
                            "addressDetails object.")

                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails'][
                        'country'] = lot_country_object
                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['region'] = lot_region_object
                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails'][
                        'locality'] = lot_locality_object
                self.__expected_pn_release['releases'][0]['tender']['lots'] = new_lots_array
            except ValueError:
                raise ValueError("Impossible to build the expected releases.tender.lots array.")
        else:
            del self.__expected_pn_release['releases'][0]['tender']['lots']

        if "items" in self.__payload['tender']:
            try:
                """
                Build the releases.tender.items array.
                """
                new_items_array = list()
                for q_0 in range(len(self.__payload['tender']['items'])):

                    new_items_array.append(copy.deepcopy(
                        self.__expected_pn_release['releases'][0]['tender']['items'][0]))

                    # Enrich or delete optional fields:
                    if "internalId" in self.__payload['tender']['items'][q_0]:
                        new_items_array[q_0]['internalId'] = self.__payload['tender']['items'][q_0]['internalId']
                    else:
                        del new_items_array[q_0]['internalId']

                    if "additionalClassifications" in self.__payload['tender']['items'][q_0]:
                        new_item_additionalclassifications_array = list()
                        for q_1 in range(len(self.__payload['tender']['items'][q_0]['additionalClassifications'])):
                            new_item_additionalclassifications_array.append(copy.deepcopy(
                                self.__expected_pn_release['releases'][0]['tender']['items'][0][
                                    'additionalClassifications'][0]))

                            cpvs_data = get_value_from_cpvs_dictionary_csv(
                                cpvs=self.__payload['tender']['items'][q_0]['additionalClassifications'][q_1]['id'],
                                language=self.__language
                            )

                            new_item_additionalclassifications_array[q_1]['scheme'] = "CPVS"
                            new_item_additionalclassifications_array[q_1]['id'] = cpvs_data[0]
                            new_item_additionalclassifications_array[q_1]['description'] = cpvs_data[2]

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

                    new_items_array[q_0]['description'] = self.__payload['tender']['items'][q_0]['description']

                    cpv_data = get_value_from_classification_cpv_dictionary_xls(
                        cpv=self.__payload['tender']['items'][q_0]['classification']['id'],
                        language=self.__language
                    )

                    new_items_array[q_0]['classification']['scheme'] = "CPV"
                    new_items_array[q_0]['classification']['id'] = cpv_data[0]
                    new_items_array[q_0]['classification']['description'] = cpv_data[1]
                    new_items_array[q_0]['quantity'] = float(self.__payload['tender']['items'][q_0]['quantity'])

                    unit_data = get_value_from_classification_unit_dictionary_csv(
                        unit_id=self.__payload['tender']['items'][q_0]['unit']['id'],
                        language=self.__language
                    )

                    new_items_array[q_0]['unit']['id'] = unit_data[0]
                    new_items_array[q_0]['unit']['name'] = unit_data[1]

                    new_items_array[q_0]['relatedLot'] = \
                        self.__actual_pn_release['releases'][0]['tender']['lots'][q_0]['id']

                self.__expected_pn_release['releases'][0]['tender']['items'] = new_items_array
            except ValueError:
                raise ValueError("Impossible to build the expected releases.tender.items array.")
        else:
            del self.__expected_pn_release['releases'][0]['tender']['items']

        if "documents" in self.__payload['tender']:
            try:
                """
                Build the releases.tender.documents array.
                """
                new_documents_array = list()
                for q_0 in range(len(self.__payload['tender']['documents'])):

                    new_documents_array.append(copy.deepcopy(
                        self.__expected_pn_release['releases'][0]['tender']['documents'][0]))

                    # Enrich or delete optional fields:
                    if "description" in self.__payload['tender']['documents'][q_0]:
                        new_documents_array[q_0]['description'] = self.__payload['tender']['documents'][q_0][
                            'description']
                    else:
                        del new_documents_array[q_0]['description']

                    if "relatedLots" in self.__payload['tender']['documents'][q_0]:

                        new_documents_array[q_0]['relatedLots'] = \
                            [self.__actual_pn_release['releases'][0]['tender']['lots'][q_0]['id']]
                    else:
                        del new_documents_array[q_0]['relatedLots']

                    # Enrich required fields:
                    new_documents_array[q_0]['id'] = self.__payload['tender']['documents'][q_0]['id']
                    new_documents_array[q_0]['documentType'] = self.__payload['tender']['documents'][q_0][
                        'documentType']
                    new_documents_array[q_0]['title'] = self.__payload['tender']['documents'][q_0]['title']

                    new_documents_array[q_0]['url'] = \
                        f"{self.__metadata_document_url}/{self.__payload['tender']['documents'][q_0]['id']}"

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
            self.__payload['tender']['tenderPeriod']['startDate']

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