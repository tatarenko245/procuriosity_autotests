from tests.utils.functions import is_it_uuid, get_value_from_classification_cpv_dictionary_xls, \
    get_value_from_country_csv, get_value_from_region_csv, \
    get_value_from_locality_csv


class PnExpectedRelease:
    def __init__(self, environment, language, pmd, pn_feed_point_message, pn_payload):
        self.language = language
        self.pn_ocid = pn_feed_point_message['data']['ocid']
        self.pn_id = pn_feed_point_message['data']['outcomes']['pn'][0]['id']
        self.pn_feed_point_message = pn_feed_point_message
        self.pn_payload = pn_payload
        self.metadata_tender_url = None
        self.procurement_method_details = None

        try:
            if pmd == "TEST_NP":
                self.procurement_method_details = "testNegotiatedProcedure"
            elif pmd == "TEST_IP":
                self.procurement_method_details = "innovativePartnership"
            elif pmd == "TEST_DA":
                self.procurement_method_details = "testDirectAward"
            elif pmd == "TEST_CD":
                self.procurement_method_details = "competetiveDialogue"
            elif pmd == "TEST_DC":
                self.procurement_method_details = "designContest"
            elif pmd == "NP":
                self.procurement_method_details = "NegotiatedProcedure"
            elif pmd == "IP":
                self.procurement_method_details = "innovativePartnership"
            elif pmd == "DA":
                self.procurement_method_details = "directAward"
            elif pmd == "CD":
                self.procurement_method_details = "competetiveDialogue"
            elif pmd == "DC":
                self.procurement_method_details = "designContest"
            else:
                raise ValueError("Check your pmd: You must use 'TEST_NP', "
                                 "'TEST_IP', 'TEST_DA', 'TEST_CD', 'TEST_DC',"
                                 " 'NP', 'IP', 'DA', 'CD', 'DC' in pytest command")
        except Exception:
            raise Exception("Check your pmd!")

        try:
            if environment == "dev":
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.publisher_name = "M-Tender"
                self.publisher_uri = "https://www.mtender.gov.md"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"]
            elif environment == "sandbox":
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.publisher_name = "Viešųjų pirkimų tarnyba"
                self.publisher_uri = "https://vpt.lrv.lt"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.json"]
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

    def pn_release_obligatory_data_model_without_lots_and_items_based_on_one_fs(self, actual_pn_release):
        try:
            is_it_uuid(
                uuid_to_test=actual_pn_release['releases'][0]['tender']['id'],
                version=4
            )
        except ValueError:
            raise ValueError("Check your actual_pn_release['releases'][0]['tender']['id']: "
                             "id must be uuid version 4")
        try:
            is_it_uuid(
                uuid_to_test=actual_pn_release['releases'][0]['relatedProcesses'][0]['id'],
                version=1
            )
        except ValueError:
            raise ValueError("Check your actual_pn_release['releases'][0]['relatedProcesses'][0]['id']: "
                             "id must be uuid version 1")

        release = {
            "uri": f"{self.metadata_tender_url}/{self.pn_ocid}/{self.pn_id}",
            "version": "1.1",
            "extensions": self.extensions,
            "publisher": {
                "name": self.publisher_name,
                "uri": self.publisher_uri
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": self.pn_feed_point_message['data']['operationDate'],
            "releases": [
                {
                    "ocid": self.pn_id,
                    "id": f"{self.pn_id}-{actual_pn_release['releases'][0]['id'][46:59]}",
                    "date": self.pn_feed_point_message['data']['operationDate'],
                    "tag": [
                        "planning"
                    ],
                    "language": self.language,
                    "initiationType": "tender",
                    "tender": {
                        "id": actual_pn_release['releases'][0]['tender']['id'],
                        "status": "planning",
                        "statusDetails": "planning",
                        "lotGroups": [
                            {
                                "optionToCombine": False
                            }
                        ],
                        "tenderPeriod": {
                            "startDate": self.pn_payload['tender']['tenderPeriod']['startDate']
                        },
                        "hasEnquiries": False,
                        "submissionMethod": [
                            "electronicSubmission"
                        ],
                        "submissionMethodDetails": "Lista platformelor: achizitii, ebs, licitatie, yptender",
                        "submissionMethodRationale": [
                            "Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"
                        ],
                        "requiresElectronicCatalogue": False
                    },
                    "hasPreviousNotice": False,
                    "purposeOfNotice": {
                        "isACallForCompetition": False
                    },
                    "relatedProcesses": [
                        {
                            "id": actual_pn_release['releases'][0]['relatedProcesses'][0]['id'],
                            "relationship": [
                                "parent"
                            ],
                            "scheme": "ocid",
                            "identifier": self.pn_ocid,
                            "uri": f"{self.metadata_tender_url}/{self.pn_ocid}/{self.pn_ocid}"
                        }
                    ]
                }
            ]
        }
        return release

    def ms_release_obligatory_data_model_without_lots_and_items_based_on_one_fs(
            self, actual_ms_release, actual_fs_release, actual_ei_release, ei_ocid, fs_id):
        try:
            is_it_uuid(
                uuid_to_test=actual_ms_release['releases'][0]['tender']['id'],
                version=4
            )
        except ValueError:
            raise ValueError("Check your actual_ms_release['releases'][0]['tender']['id']: "
                             "id must be uuid version 4")

        try:
            for r in actual_ms_release['releases'][0]['relatedProcesses']:
                for r_1 in r:
                    if r_1 == "id":
                        is_it_uuid(
                            uuid_to_test=r['id'],
                            version=1)
        except ValueError:
            raise ValueError("Check your actual_ms_release['releases'][0]['relatedProcesses'][?]['id']: "
                             "id must be uuid version 1")

        try:
            eligibility_criteria = None
            if self.language == "ro":
                eligibility_criteria = "Regulile generale privind naționalitatea și originea, precum și " \
                                       "alte criterii de eligibilitate sunt enumerate în Ghidul practic privind " \
                                       "procedurile de contractare a acțiunilor externe ale UE (PRAG)"
            elif self.language == "en":
                eligibility_criteria = "The general rules on nationality and origin, as well as other eligibility " \
                                       "criteria are listed in the Practical Guide to Contract Procedures for EU " \
                                       "External Actions (PRAG)"
        except ValueError:
            raise ValueError("Check language")

        cpv_data = get_value_from_classification_cpv_dictionary_xls(
            cpv=actual_ei_release['releases'][0]['tender']['classification']['id'],
            language=self.language
        )

        try:
            procuring_entity_country_data = get_value_from_country_csv(
                country=self.pn_payload['tender']['procuringEntity']['address'][
                    'addressDetails']['country']['id'],
                language=self.language
            )
            procuring_entity_country_object = {
                "scheme": procuring_entity_country_data[2],
                "id": self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": procuring_entity_country_data[1],
                "uri": procuring_entity_country_data[3]
            }

            procuring_entity_region_data = get_value_from_region_csv(
                region=self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'],
                country=self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            procuring_entity_region_object = {
                "scheme": procuring_entity_region_data[2],
                "id": self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'],
                "description": procuring_entity_region_data[1],
                "uri": procuring_entity_region_data[3]
            }

            if \
                    self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'scheme'] == "CUATM":
                procuring_entity_locality_data = get_value_from_locality_csv(
                    locality=self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'id'],
                    region=self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'],
                    country=self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'],
                    language=self.language
                )
                procuring_entity_locality_object = {
                    "scheme": procuring_entity_locality_data[2],
                    "id": self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'],
                    "description": procuring_entity_locality_data[1],
                    "uri": procuring_entity_locality_data[3]
                }
            else:
                procuring_entity_locality_object = {
                    "scheme":
                        self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'],
                    "id": self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'],
                    "description":
                        self.pn_payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                            'description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        release = {
            "uri": f"{self.metadata_tender_url}/{self.pn_ocid}/{self.pn_ocid}",
            "version": "1.1",
            "extensions": self.extensions,
            "publisher": {
                "name": self.publisher_name,
                "uri": self.publisher_uri
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": self.pn_feed_point_message['data']['operationDate'],
            "releases": [
                {
                    "ocid": self.pn_ocid,
                    "id": f"{self.pn_ocid}-{actual_ms_release['releases'][0]['id'][29:42]}",
                    "date": self.pn_feed_point_message['data']['operationDate'],
                    "tag": [
                        "compiled"
                    ],
                    "language": self.language,
                    "initiationType": "tender",
                    "planning": {
                        "budget": {
                            "amount": {
                                "amount": self.pn_payload['planning']['budget']['budgetBreakdown'][0]['amount'][
                                    'amount'],
                                "currency": self.pn_payload['planning']['budget']['budgetBreakdown'][0]['amount'][
                                    'currency']
                            },
                            "isEuropeanUnionFunded": False,
                            "budgetBreakdown": [
                                {
                                    "id": self.pn_payload['planning']['budget']['budgetBreakdown'][0]['id'],
                                    "amount": {
                                        "amount": self.pn_payload['planning']['budget']['budgetBreakdown'][0]['amount'][
                                            'amount'],
                                        "currency":
                                            self.pn_payload['planning']['budget']['budgetBreakdown'][0]['amount'][
                                                'currency']
                                    },
                                    "period": {
                                        "startDate": actual_fs_release['releases'][0]['planning']['budget']['period'][
                                            'startDate'],
                                        "endDate": actual_fs_release['releases'][0]['planning']['budget']['period'][
                                            'endDate']
                                    },
                                    "sourceParty": {
                                        "id": actual_fs_release['releases'][0]['planning']['budget']['sourceEntity'][
                                            'id'],
                                        "name": actual_fs_release['releases'][0]['planning']['budget']['sourceEntity'][
                                            'name']
                                    }
                                }
                            ]
                        }
                    },
                    "tender": {
                        "id": actual_ms_release['releases'][0]['tender']['id'],
                        "title": self.pn_payload['tender']['title'],
                        "description": self.pn_payload['tender']['description'],
                        "status": "planning",
                        "statusDetails": "planning",
                        "value": {
                            "amount": self.pn_payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount'],
                            "currency": self.pn_payload['planning']['budget']['budgetBreakdown'][0]['amount'][
                                'currency']
                        },
                        "procurementMethod": "limited",
                        "procurementMethodDetails": self.procurement_method_details,
                        "mainProcurementCategory": actual_ei_release['releases'][0]['tender'][
                            'mainProcurementCategory'],
                        "hasEnquiries": False,
                        "eligibilityCriteria": eligibility_criteria,
                        "procuringEntity": {
                            "id": f"{self.pn_payload['tender']['procuringEntity']['identifier']['scheme']}-"
                                  f"{self.pn_payload['tender']['procuringEntity']['identifier']['id']}",
                            "name": self.pn_payload['tender']['procuringEntity']['name']
                        },
                        "acceleratedProcedure": {
                            "isAcceleratedProcedure": False
                        },
                        "classification": {
                            "scheme": "CPV",
                            "id": cpv_data[0],
                            "description": cpv_data[1]
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
                        "legalBasis": self.pn_payload['tender']['legalBasis'],
                        "procedureOutsourcing": {
                            "procedureOutsourced": False
                        },
                        "dynamicPurchasingSystem": {
                            "hasDynamicPurchasingSystem": False
                        },
                        "framework": {
                            "isAFramework": False
                        }
                    },
                    "parties": [
                        actual_ei_release['releases'][0]['parties'][0],
                        actual_fs_release['releases'][0]['parties'][0],
                        {
                            "id": f"{self.pn_payload['tender']['procuringEntity']['identifier']['scheme']}-"
                                  f"{self.pn_payload['tender']['procuringEntity']['identifier']['id']}",
                            "name": self.pn_payload['tender']['procuringEntity']['name'],
                            "identifier": {
                                "scheme": self.pn_payload['tender']['procuringEntity']['identifier']['scheme'],
                                "id": self.pn_payload['tender']['procuringEntity']['identifier']['id'],
                                "legalName": self.pn_payload['tender']['procuringEntity']['identifier']['legalName']
                            },
                            "address": {
                                "streetAddress": self.pn_payload['tender']['procuringEntity']['address'][
                                    'streetAddress'],
                                "addressDetails": {
                                    "country": procuring_entity_country_object,
                                    "region": procuring_entity_region_object,
                                    "locality": procuring_entity_locality_object
                                }
                            },
                            "contactPoint": {
                                "name": self.pn_payload['tender']['procuringEntity']['contactPoint']['name'],
                                "email": self.pn_payload['tender']['procuringEntity']['contactPoint']['email'],
                                "telephone": self.pn_payload['tender']['procuringEntity']['contactPoint']['telephone']
                            },
                            "roles": [
                                "procuringEntity"
                            ]
                        }
                    ],
                    "relatedProcesses": [
                        {
                            "id": actual_ms_release['releases'][0]['relatedProcesses'][0]['id'],
                            "relationship": [
                                "planning"
                            ],
                            "scheme": "ocid",
                            "identifier": self.pn_id,
                            "uri": f"{self.metadata_tender_url}/{self.pn_ocid}/{self.pn_id}"
                        },
                        {
                            "id": actual_ms_release['releases'][0]['relatedProcesses'][1]['id'],
                            "relationship": [
                                "x_expenditureItem"
                            ],
                            "scheme": "ocid",
                            "identifier": ei_ocid,
                            "uri": f"{self.metadata_budget_url}/{ei_ocid}/{ei_ocid}"
                        },
                        {
                            "id": actual_ms_release['releases'][0]['relatedProcesses'][2]['id'],
                            "relationship": [
                                "x_fundingSource"
                            ],
                            "scheme": "ocid",
                            "identifier": fs_id,
                            "uri": f"{self.metadata_budget_url}/{ei_ocid}/{fs_id}"
                        }
                    ]
                }
            ]
        }
        return release
