"""Prepare the expected releases of the framework establishment process, framework agreement procedures."""
import copy
import json

from tests.utils.cassandra_session import CassandraSession
from tests.utils.date_class import Date
from tests.utils.functions_collection.functions import is_it_uuid, get_value_from_locality_csv, \
    get_value_from_country_csv, get_value_from_region_csv
from tests.utils.services.e_mdm_service import MdmService


class FrameworkEstablishmentRelease:
    """This class creates instance of release."""

    def __init__(self, environment, host_to_service, country, language, pmd, fe_payload, fe_message, actual_fe_release,
                 actual_ms_release, connect_to_clarification, operation_type, parameter, actual_ap_release,
                 ap_cpid, ap_ocid):

        self.__environment = environment
        self.__host = host_to_service
        self.__language = language
        self.__country = country
        self.__pmd = pmd
        self.__fe_payload = fe_payload
        self.__fe_message = fe_message
        self.__actual_fe_release = actual_fe_release
        self.__actual_ms_release = actual_ms_release
        self.__actual_ap_release = actual_ap_release
        self.__ap_cpid = ap_cpid
        self.__ap_ocid = ap_ocid

        database = CassandraSession()
        self.__period_shift = database.get_parameter_from_clarification_rules(
            connect_to_clarification, country, pmd, operation_type, parameter)

        self.__mdm_class = MdmService(host_to_service, environment)

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

        self.__expected_fe_release = {
            "uri": f"{self.__metadata_tender_url}/{fe_message['data']['ocid']}/"
                   f"{fe_message['data']['outcomes']['fe'][0]['id']}",

            "version": "1.1",
            "extensions": extensions,
            "publisher": {
                "name": publisher_name,
                "uri": publisher_uri
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": fe_message['data']['operationDate'],
            "releases": [
                {
                    "ocid": "",

                    "id": "",

                    "date": "",
                    "tag": [
                        ""
                    ],
                    "language": "",
                    "initiationType": "",
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
                                ""
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
                                                "description": "",
                                                "period": {
                                                    "startDate": "",
                                                    "endDate": ""
                                                },
                                                "eligibleEvidences": [
                                                    {
                                                        "id": "",
                                                        "title": "",
                                                        "type": "",
                                                        "description": "",
                                                        "relatedDocument": {
                                                            "id": ""
                                                        }
                                                    }
                                                ],
                                                "expectedValue": "",
                                                "minValue": "",
                                                "maxValue": ""
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
                            "qualificationSystemMethods": ""
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
                        "procurementMethodModalities": [""],
                        "secondStage": {
                            "minimumCandidates": 1,
                            "maximumCandidates": 2
                        }
                    },
                    "preQualification": {
                        "period": {
                            "startDate": "",
                            "endDate": ""
                        }
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

        # self.__expected_ms_release = {
        #     "uri": f"{self.__metadata_tender_url}/{ap_message['data']['ocid']}/{ap_message['data']['ocid']}",
        #     "version": "1.1",
        #     "extensions": extensions,
        #     "publisher": {
        #         "name": publisher_name,
        #         "uri": publisher_uri
        #     },
        #     "license": "http://opendefinition.org/licenses/",
        #     "publicationPolicy": "http://opendefinition.org/licenses/",
        #     "publishedDate": ap_message['data']['operationDate'],
        #     "releases": [
        #         {
        #             "ocid": ap_message['data']['ocid'],
        #             "id": f"{ap_message['data']['ocid']}-{actual_ms_release['releases'][0]['id'][29:42]}",
        #             "date": ap_message['data']['operationDate'],
        #             "tag": [
        #                 "compiled"
        #             ],
        #             "language": language,
        #             "initiationType": "tender",
        #             "tender": {
        #                 "id": "",
        #                 "title": "",
        #                 "description": "",
        #                 "status": "planning",
        #                 "statusDetails": "aggregatePlanning",
        #                 "value": {
        #                     "currency": ""
        #                 },
        #                 "procurementMethod": "",
        #                 "procurementMethodDetails": "",
        #                 "procurementMethodRationale": "",
        #                 "hasEnquiries": False,
        #                 "eligibilityCriteria": "",
        #                 "contractPeriod": {
        #                     "startDate": "",
        #                     "endDate": ""
        #                 },
        #                 "acceleratedProcedure": {
        #                     "isAcceleratedProcedure": False
        #                 },
        #                 "classification": {
        #                     "scheme": "",
        #                     "id": "",
        #                     "description": ""
        #                 },
        #                 "designContest": {
        #                     "serviceContractAward": False
        #                 },
        #                 "electronicWorkflows": {
        #                     "useOrdering": False,
        #                     "usePayment": False,
        #                     "acceptInvoicing": False
        #                 },
        #                 "jointProcurement": {
        #                     "isJointProcurement": False
        #                 },
        #                 "legalBasis": "",
        #                 "procedureOutsourcing": {
        #                     "procedureOutsourced": False
        #                 },
        #                 "dynamicPurchasingSystem": {
        #                     "hasDynamicPurchasingSystem": False
        #                 },
        #                 "framework": {
        #                     "isAFramework": True
        #                 }
        #             },
        #             "relatedProcesses": [
        #                 {
        #                     "id": "",
        #                     "relationship": [
        #                         ""
        #                     ],
        #                     "scheme": "",
        #                     "identifier": "",
        #                     "uri": ""
        #                 }
        #             ]
        #         }
        #     ]
        # }

    def build_expected_fe_release(self):
        """Build FE release."""

        # Enrich 'releases[0]' section:

        # FR.COM-3.2.5
        self.__expected_fe_release['releases'][0]['ocid'] = self.__fe_message['data']['outcomes']['fe'][0]['id']

        # FR.COM-3.2.21
        self.__expected_fe_release['releases'][0]['id'] = \
            f"{self.__fe_message['data']['outcomes']['fe'][0]['id']}-" \
            f"{self.__actual_fe_release['releases'][0]['id'][46:59]}"

        # FR.COM-3.2.23
        self.__expected_fe_release['releases'][0]['language'] = self.__language

        # FR.COM-3.2.4
        self.__expected_fe_release['releases'][0]['initiationType'] = "tender"

        self.__expected_fe_release['releases'][0]['date'] = self.__fe_message['data']['operationDate']

        # FR.COM-3.2.2
        self.__expected_fe_release['releases'][0]['tag'] = ["tender"]

        # Enrich 'releases[0].tender' section:
        # FR.COM-3.2.8

        # FR.COM-1.28.1
        try:
            """Set permanent id."""

            is_permanent_id_correct = is_it_uuid(
                self.__actual_fe_release['releases'][0]['tender']['id'])

            if is_permanent_id_correct is True:

                self.__expected_fe_release['releases'][0]['tender']['id'] = \
                    self.__actual_fe_release['releases'][0]['tender']['id']
            else:
                raise ValueError(f"The 'releases[0].tender.id' must be uuid.")
        except KeyError:
            raise KeyError("Mismatch key into path 'releases[0].tender.id'")

        # BR-1.0.1.4.2
        self.__expected_fe_release['releases'][0]['tender']['status'] = "active"
        self.__expected_fe_release['releases'][0]['tender']['statusDetails'] = "submission"

        # FR.COM-1.28.1
        if "criteria" in self.__fe_payload['tender']:
            expected_criteria_array = list()

            try:
                """Prepare criteria array for expected FE release."""
                for q_0 in range(len(self.__fe_payload['tender']['criteria'])):

                    expected_criteria_array.append(copy.deepcopy(
                        self.__expected_fe_release['releases'][0]['tender']['criteria'][0]
                    ))

                    # BR-1.0.1.16.1
                    try:
                        """Set permanent id."""

                        is_permanent_id_correct = is_it_uuid(
                            self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0]['id'])

                        if is_permanent_id_correct is True:

                            expected_criteria_array[q_0]['id'] = \
                                self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0]['id']
                        else:
                            raise ValueError(f"The 'releases[0].tender.criteria[{q_0}].id' must be uuid.")
                    except KeyError:
                        raise KeyError(f"Mismatch key into path 'releases[0].tender.criteria[{q_0}].id'")

                    expected_criteria_array[q_0]['title'] = self.__fe_payload['tender']['criteria'][q_0]['title']

                    # BR-1.0.1.16.2
                    expected_criteria_array[q_0]['source'] = "tenderer"

                    expected_criteria_array[q_0]['relatesTo'] = \
                        self.__fe_payload['tender']['criteria'][q_0]['relatesTo']

                    # BR-1.0.1.16.3
                    expected_criteria_array[q_0]['classification']['id'] = \
                        self.__fe_payload['tender']['criteria'][q_0]['classification']['id']

                    expected_criteria_array[q_0]['classification']['scheme'] = \
                        self.__fe_payload['tender']['criteria'][q_0]['classification']['scheme']

                    if "description" in self.__fe_payload['tender']['criteria'][q_0]:

                        expected_criteria_array[q_0]['description'] = \
                            self.__fe_payload['tender']['criteria'][q_0]['description']
                    else:
                        del expected_criteria_array[q_0]['description']

                    expected_requirementGroups_array = list()
                    for q_1 in range(len(self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'])):

                        expected_requirementGroups_array.append(copy.deepcopy(
                            self.__expected_fe_release['releases'][0]['tender']['criteria'][0]['requirementGroups'][0]
                        ))

                        # BR-1.0.1.17.1
                        try:
                            """Set permanent id."""

                            is_permanent_id_correct = is_it_uuid(
                                self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                    'requirementGroups'][q_1]['id']
                            )

                            if is_permanent_id_correct is True:

                                expected_requirementGroups_array[q_1]['id'] = \
                                    self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                        'requirementGroups'][q_1]['id']
                            else:
                                raise ValueError(f"The 'releases[0].tender.criteria[{q_0}].requirementGroups[{q_1}]."
                                                 f"id' must be uuid.")
                        except KeyError:
                            raise KeyError(f"Mismatch key into path 'releases[0].tender.criteria[{q_0}]."
                                           f"requirementGroups[{q_1}].id'")

                        if "description" in self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1]:

                            expected_requirementGroups_array[q_1]['description'] = \
                                self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1]['description']
                        else:
                            del expected_requirementGroups_array[q_1]['description']

                        expected_requirements_array = list()
                        for q_2 in range(len(
                                self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1]['requirements']
                        )):
                            expected_requirements_array.append(copy.deepcopy(
                                self.__expected_fe_release['releases'][0]['tender']['criteria'][0][
                                    'requirementGroups'][0]['requirements'][0]
                            ))

                            # BR-1.0.1.18.1
                            try:
                                """Set permanent id."""

                                is_permanent_id_correct = is_it_uuid(
                                    self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                        'requirementGroups'][q_1]['requirements'][q_2]['id']
                                )

                                if is_permanent_id_correct is True:

                                    expected_requirements_array[q_2]['id'] = \
                                        self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                            'requirementGroups'][q_1]['requirements'][q_2]['id']
                                else:
                                    raise ValueError(
                                        f"The 'releases[0].tender.criteria[{q_0}].requirementGroups[{q_1}]."
                                        f"requirements[{q_2}].id' must be uuid.")
                            except KeyError:
                                raise KeyError(f"Mismatch key into path 'releases[0].tender.criteria[{q_0}]."
                                               f"requirementGroups[{q_1}].requirements[{q_2}].id'")

                            expected_requirements_array[q_2]['title'] = \
                                self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                    'requirements'][q_2]['title']

                            if "description" in self.__fe_payload['tender']['criteria'][q_0][
                                    'requirementGroups'][q_1]['requirements'][q_2]:

                                expected_requirements_array[q_2]['description'] = \
                                    self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                        'requirements'][q_2]['description']
                            else:
                                del expected_requirements_array[q_2]['description']

                            if "period" in self.__fe_payload['tender']['criteria'][q_0][
                                    'requirementGroups'][q_1]['requirements'][q_2]:

                                expected_requirements_array[q_2]['period']['startDate'] = \
                                    self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                        'requirements'][q_2]['period']['startDate']

                                expected_requirements_array[q_2]['period']['endDate'] = \
                                    self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                        'requirements'][q_2]['period']['endDate']
                            else:
                                del expected_requirements_array[q_2]['period']

                            if "expectedValue" not in self.__fe_payload['tender']['criteria'][q_0][
                                    'requirementGroups'][q_1]['requirements'][q_2]:

                                del expected_requirements_array[q_2]['expectedValue']
                            else:
                                expected_requirements_array[q_2]['expectedValue'] = \
                                    self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                        'requirements'][q_2]['expectedValue']

                                expected_requirements_array[q_2]['dataType'] = \
                                    self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                    'requirements'][q_2]['dataType']

                            if "minValue" not in self.__fe_payload['tender']['criteria'][q_0][
                                    'requirementGroups'][q_1]['requirements'][q_2]:

                                del expected_requirements_array[q_2]['minValue']
                            else:
                                expected_requirements_array[q_2]['minValue'] = \
                                    self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                        'requirements'][q_2]['minValue']

                                expected_requirements_array[q_2]['dataType'] = \
                                    self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                        'requirements'][q_2]['dataType']

                            if "maxValue" not in self.__fe_payload['tender']['criteria'][q_0][
                                    'requirementGroups'][q_1]['requirements'][q_2]:

                                del expected_requirements_array[q_2]['maxValue']
                            else:
                                expected_requirements_array[q_2]['maxValue'] = \
                                    self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                        'requirements'][q_2]['maxValue']

                                expected_requirements_array[q_2]['dataType'] = \
                                    self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                        'requirements'][q_2]['dataType']

                            # BR-1.0.1.18.2
                            expected_requirements_array[q_2]['status'] = "active"

                            # BR-1.0.1.18.3
                            expected_requirements_array[q_2]['datePublished'] = \
                                self.__fe_message['data']['operationDate']

                            # BR-1.0.1.18.4
                            if "eligibleEvidences" in self.__fe_payload['tender']['criteria'][q_0][
                                    'requirementGroups'][q_1]['requirements'][q_2]:

                                expected_eligibleEvidences_array = list()
                                for q_3 in range(len(self.__fe_payload['tender']['criteria'][q_0][
                                        'requirementGroups'][q_1]['requirements'][q_2]['eligibleEvidences'])):

                                    expected_eligibleEvidences_array.append(copy.deepcopy(
                                        self.__expected_fe_release['releases'][0]['tender']['criteria'][0][
                                            'requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]
                                    ))

                                    try:
                                        """Set permanent id."""

                                        is_permanent_id_correct = is_it_uuid(
                                            self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                                'requirementGroups'][q_1]['requirements'][q_2][
                                                'eligibleEvidences'][q_3]['id']
                                        )

                                        if is_permanent_id_correct is True:

                                            expected_eligibleEvidences_array[q_3]['id'] = \
                                                self.__actual_fe_release['releases'][0]['tender']['criteria'][q_0][
                                                    'requirementGroups'][q_1]['requirements'][q_2][
                                                    'eligibleEvidences'][q_3]['id']
                                        else:
                                            raise ValueError(
                                                f"The 'releases[0].tender.criteria[{q_0}].requirementGroups[{q_1}]."
                                                f"requirements[{q_2}].eligibleEvidences[{q_3}].id' must be uuid.")
                                    except KeyError:
                                        raise KeyError(f"Mismatch key into path 'releases[0].tender.criteria[{q_0}]."
                                                       f"requirementGroups[{q_1}].requirements[{q_2}]."
                                                       f"eligibleEvidences[{q_3}].id'")

                                    expected_eligibleEvidences_array[q_3]['title'] = \
                                        self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                            'requirements'][q_2]['eligibleEvidences'][q_3]['title']

                                    if "description" in self.__fe_payload['tender']['criteria'][q_0][
                                            'requirementGroups'][q_1]['requirements'][q_2]['eligibleEvidences'][q_3]:

                                        expected_eligibleEvidences_array[q_3]['description'] = \
                                            self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                                'requirements'][q_2]['eligibleEvidences'][q_3]['description']
                                    else:
                                        del expected_eligibleEvidences_array[q_3]['description']

                                    expected_eligibleEvidences_array[q_3]['type'] = \
                                        self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                            'requirements'][q_2]['eligibleEvidences'][q_3]['type']

                                    if "relatedDocument" in self.__fe_payload['tender']['criteria'][q_0][
                                            'requirementGroups'][q_1]['requirements'][q_2]['eligibleEvidences'][q_3]:

                                        expected_eligibleEvidences_array[q_3]['relatedDocument']['id'] = \
                                            self.__fe_payload['tender']['criteria'][q_0]['requirementGroups'][q_1][
                                                'requirements'][q_2]['eligibleEvidences'][q_3]['relatedDocument']['id']
                                    else:
                                        del expected_eligibleEvidences_array[q_3]['relatedDocument']

                                expected_requirements_array[q_2]['eligibleEvidences'] = expected_eligibleEvidences_array
                            else:
                                del expected_requirementGroups_array[q_1]['requirements'][q_2]['eligibleEvidences']

                        expected_requirementGroups_array[q_1]['requirements'] = expected_requirements_array
                    expected_criteria_array[q_0]['requirementGroups'] = expected_requirementGroups_array

            except AttributeError:
                raise AttributeError("Mismatch the attribute for expected criteria array.")

            self.__expected_fe_release['releases'][0]['tender']['criteria'] = expected_criteria_array
        else:
            del self.__expected_fe_release['releases'][0]['tender']['criteria']

        # FR.COM-1.28.1
        self.__expected_fe_release['releases'][0]['tender']['otherCriteria']['reductionCriteria'] = \
            self.__fe_payload['tender']['otherCriteria']['reductionCriteria']

        self.__expected_fe_release['releases'][0]['tender']['otherCriteria']['qualificationSystemMethods'] = \
            self.__fe_payload['tender']['otherCriteria']['qualificationSystemMethods']

        # FR.COM-3.2.8, FR.COM-8.1.1, FR.COM-8.1.2
        self.__expected_fe_release['releases'][0]['tender']['enquiryPeriod']['startDate'] = \
            self.__fe_message['data']['operationDate']

        date = Date()
        expected_enquiryPeriod_endDate = date.selectiveProcedure_enquiryPeriod_endDate(
            preQualification_period_endDate=self.__fe_payload['preQualification']['period']['endDate'],
            interval_seconds=int(self.__period_shift)
        )

        self.__expected_fe_release['releases'][0]['tender']['enquiryPeriod']['endDate'] = \
            expected_enquiryPeriod_endDate

        # FR.COM-3.2.7
        self.__expected_fe_release['releases'][0]['tender']['hasEnquiries'] = False

        # FR.COM-1.28.1
        if "documents" in self.__fe_payload['tender']:
            expected_documents_array = list()

            try:
                """Prepare documents array for expected FE release."""
                for q_0 in range(len(self.__fe_payload['tender']['documents'])):

                    expected_documents_array.append(copy.deepcopy(
                        self.__expected_fe_release['releases'][0]['tender']['documents'][0]
                    ))

                    expected_documents_array[q_0]['id'] = self.__fe_payload['tender']['documents'][q_0]['id']

                    expected_documents_array[q_0]['documentType'] = \
                        self.__fe_payload['tender']['documents'][q_0]['documentType']

                    expected_documents_array[q_0]['title'] = \
                        self.__fe_payload['tender']['documents'][q_0]['title']

                    if "description" in expected_documents_array[q_0]:

                        expected_documents_array[q_0]['description'] = \
                            self.__fe_payload['tender']['documents'][q_0]['description']
                    else:
                        del expected_documents_array[q_0]['description']

                    expected_documents_array[q_0]['url'] = \
                        f"{self.__metadata_document_url}/{self.__fe_payload['tender']['documents'][q_0]['id']}"

                    expected_documents_array[q_0]['datePublished'] = self.__fe_message['data']['operationDate']

            except AttributeError:
                raise AttributeError("Mismatch the attribute for expected documents array.")

            self.__expected_fe_release['releases'][0]['tender']['documents'] = expected_documents_array
        else:
            del self.__expected_fe_release['releases'][0]['tender']['documents']

        # FR.COM-1.28.1
        self.__expected_fe_release['releases'][0]['tender']['submissionMethod'] = \
            self.__actual_ap_release['releases'][0]['tender']['submissionMethod']

        # FR.COM-1.28.1
        self.__expected_fe_release['releases'][0]['tender']['submissionMethodDetails'] = \
            self.__actual_ap_release['releases'][0]['tender']['submissionMethodDetails']

        # FR.COM-1.28.1
        self.__expected_fe_release['releases'][0]['tender']['submissionMethodRationale'] = \
            self.__actual_ap_release['releases'][0]['tender']['submissionMethodRationale']

        # FR.COM-1.28.1
        self.__expected_fe_release['releases'][0]['tender']['requiresElectronicCatalogue'] = \
            self.__actual_ap_release['releases'][0]['tender']['requiresElectronicCatalogue']

        # FR.COM-1.28.1
        if "procurementMethodModalities" in self.__fe_payload['tender']:
            self.__expected_fe_release['releases'][0]['tender']['procurementMethodModalities'] = \
                self.__fe_payload['tender']['procurementMethodModalities']
        else:
            del self.__expected_fe_release['releases'][0]['tender']['procurementMethodModalities']

        # FR.COM-1.28.1
        if "secondStage" in self.__fe_payload['tender']:
            self.__expected_fe_release['releases'][0]['tender']['secondStage'] = \
                self.__fe_payload['tender']['secondStage']
        else:
            del self.__expected_fe_release['releases'][0]['tender']['secondStage']

        # FR.COM-3.2.9
        self.__expected_fe_release['releases'][0]['preQualification']['period']['startDate'] = \
            self.__fe_message['data']['operationDate']

        self.__expected_fe_release['releases'][0]['preQualification']['period']['endDate'] = \
            self.__fe_payload['preQualification']['period']['endDate']

        # FR.COM-3.2.1
        self.__expected_fe_release['releases'][0]['hasPreviousNotice'] = True

        # FR.COM-3.2.3
        self.__expected_fe_release['releases'][0]['purposeOfNotice']['isACallForCompetition'] = True

        # Enrich 'releases[0].['parties']' section:
        # FR.COM-3.2.10, FR.COM-1.28.1
        expected_parties_array = list()

        for q_0 in range(len(self.__actual_ap_release['releases'][0]['parties'])):
            if self.__actual_ap_release['releases'][0]['parties'][q_0]['roles'] == ["centralPurchasingBody"]:
                expected_parties_array.append(self.__actual_ap_release['releases'][0]['parties'][q_0])
                expected_parties_array[q_0]['roles'] = ["procuringEntity"]

                # BR-1.0.1.15.2
                if "procuringEntity" in self.__fe_payload['tender']:
                    expected_persones_array = list()
                    for q_1 in range(len(self.__fe_payload['tender']['procuringEntity']['persones'])):

                        expected_persones_array.append(copy.deepcopy(
                            self.__expected_fe_release['releases'][0]['parties'][0]['persones'][0]
                        ))

                        persones_scheme = \
                            self.__fe_payload['tender']['procuringEntity']['persones'][q_1]['identifier']['scheme']

                        persones_id = \
                            self.__fe_payload['tender']['procuringEntity']['persones'][q_1]['identifier']['id']

                        expected_persones_array[q_1]['id'] = f"{persones_scheme}-{persones_id}"

                        expected_persones_array[q_1]['title'] = \
                            self.__fe_payload['tender']['procuringEntity']['persones'][q_1]['title']

                        expected_persones_array[q_1]['name'] = \
                            self.__fe_payload['tender']['procuringEntity']['persones'][q_1]['name']

                        expected_persones_array[q_1]['identifier']['scheme'] = \
                            self.__fe_payload['tender']['procuringEntity']['persones'][q_1]['identifier']['scheme']

                        expected_persones_array[q_1]['identifier']['id'] = \
                            self.__fe_payload['tender']['procuringEntity']['persones'][q_1]['identifier']['id']

                        if "uri" in expected_persones_array[q_1]['identifier']:

                            expected_persones_array[q_1]['identifier']['uri'] = \
                                self.__fe_payload['tender']['procuringEntity']['persones'][q_1]['identifier']['uri']
                        else:
                            del expected_persones_array[q_1]['identifier']['uri']

                        expected_businessFunctions_array = list()
                        for q_2 in range(len(
                                self.__fe_payload['tender']['procuringEntity']['persones'][q_1]['businessFunctions'])):

                            expected_businessFunctions_array.append(copy.deepcopy(
                                self.__expected_fe_release['releases'][0]['parties'][0]['persones'][0][
                                    'businessFunctions'][0]
                            ))

                            try:
                                """Set permanent id."""

                                is_permanent_id_correct = is_it_uuid(
                                    self.__actual_fe_release['releases'][0]['parties'][q_0]['persones'][q_1][
                                        'businessFunctions'][q_2]['id']
                                )

                                if is_permanent_id_correct is True:

                                    expected_businessFunctions_array[q_2]['id'] = \
                                        self.__actual_fe_release['releases'][0]['parties'][q_0]['persones'][q_1][
                                            'businessFunctions'][q_2]['id']
                                else:
                                    raise ValueError(
                                        f"The 'releases[0].parties[{q_0}].persones[{q_1}]."
                                        f"businessFunctions[{q_2}].id' must be uuid.")
                            except KeyError:
                                raise KeyError(f"Mismatch key into path 'releases[0].parties[{q_0}].persones[{q_1}]."
                                               f"businessFunctions[{q_2}].id'")

                            expected_businessFunctions_array[q_2]['type'] = \
                                self.__fe_payload['tender']['procuringEntity']['persones'][q_1][
                                    'businessFunctions'][q_2]['type']

                            expected_businessFunctions_array[q_2]['jobTitle'] = \
                                self.__fe_payload['tender']['procuringEntity']['persones'][q_1][
                                    'businessFunctions'][q_2]['jobTitle']

                            expected_businessFunctions_array[q_2]['period']['startDate'] = \
                                self.__fe_payload['tender']['procuringEntity']['persones'][q_1][
                                    'businessFunctions'][q_2]['period']['startDate']

                            expected_businessFunctions_documents_array = list()
                            if "documents" in self.__fe_payload['tender']['procuringEntity']['persones'][q_1][
                                    'businessFunctions'][q_2]:

                                for q_3 in range(len(self.__fe_payload['tender']['procuringEntity']['persones'][q_1][
                                        'businessFunctions'][q_2]['documents'])):

                                    expected_businessFunctions_documents_array.append(copy.deepcopy(
                                        self.__expected_fe_release['releases'][0]['parties'][0]['persones'][0][
                                            'businessFunctions'][0]['documents'][0]
                                    ))

                                    expected_businessFunctions_documents_array[q_3]['id'] = \
                                        self.__fe_payload['tender']['procuringEntity']['persones'][q_1][
                                            'businessFunctions'][q_2]['documents'][q_3]['id']

                                    expected_businessFunctions_documents_array[q_3]['documentType'] = \
                                        self.__fe_payload['tender']['procuringEntity']['persones'][q_1][
                                            'businessFunctions'][q_2]['documents'][q_3]['documentType']

                                    expected_businessFunctions_documents_array[q_3]['title'] = \
                                        self.__fe_payload['tender']['procuringEntity']['persones'][q_1][
                                            'businessFunctions'][q_2]['documents'][q_3]['title']

                                    if "description" in self.__fe_payload['tender']['procuringEntity'][
                                            'persones'][q_1]['businessFunctions'][q_2]['documents'][q_3]:

                                        expected_businessFunctions_documents_array[q_3]['description'] = \
                                            self.__fe_payload['tender']['procuringEntity']['persones'][q_1][
                                                'businessFunctions'][q_2]['documents'][q_3]['description']
                                    else:
                                        del expected_businessFunctions_documents_array[q_3]['description']

                                    expected_businessFunctions_documents_array[q_3]['url'] = \
                                        f"{self.__metadata_document_url}/" \
                                        f"{expected_businessFunctions_documents_array[q_3]['id']}"

                                    expected_businessFunctions_documents_array[q_3]['datePublished'] = \
                                        self.__fe_message['data']['operationDate']

                                expected_businessFunctions_array[q_2]['documents'] = \
                                    expected_businessFunctions_documents_array
                            else:
                                del expected_businessFunctions_array[q_2]['documents']

                        expected_persones_array[q_1]['businessFunctions'] = expected_businessFunctions_array
                    expected_parties_array[q_0]['persones'] = expected_persones_array

            if self.__actual_ap_release['releases'][0]['parties'][q_0]['roles'] == ["client"]:
                expected_parties_array.append(self.__actual_ap_release['releases'][0]['parties'][q_0])
                expected_parties_array[q_0]['roles'] = ["buyer"]

        final_expected_persones_array = list()
        if len(self.__actual_fe_release['releases'][0]['parties']) == len(expected_parties_array):
            for act in range(len(self.__actual_fe_release['releases'][0]['parties'])):
                for exp in range(len(expected_parties_array)):

                    if self.__actual_fe_release['releases'][0]['parties'][act]['id'] == \
                            expected_parties_array[exp]['id']:

                        final_expected_persones_array.append(expected_parties_array[exp])
        else:
            raise ValueError("The quantity of actual parties array != "
                             "quantity of expected parties array")
        self.__expected_fe_release['releases'][0]['parties'] = final_expected_persones_array

        # Enrich 'releases[0].['relatedProcesses']' section:
        # FR.COM-1.28.1
        expected_relatedProcesses_array = list()

        # Prepare object, where 'relationship' = 'aggregatePlanning'.
        expected_relatedProcesses_array.append(copy.deepcopy(
            self.__expected_fe_release['releases'][0]['relatedProcesses'][0]
        ))

        try:
            """Set permanent id."""

            is_permanent_id_correct = is_it_uuid(
                self.__actual_fe_release['releases'][0]['relatedProcesses'][0]['id']
            )

            if is_permanent_id_correct is True:

                expected_relatedProcesses_array[0]['id'] = \
                    self.__expected_fe_release['releases'][0]['relatedProcesses'][0]
            else:
                raise ValueError(
                    f"The 'releases[0].relatedProcesses[{0}].id' must be uuid.")
        except KeyError:
            raise KeyError(f"Mismatch key into path 'releases[0].relatedProcesses[{0}].id'.")

        expected_relatedProcesses_array[0]['relationship'] = ["aggregatePlanning"]
        expected_relatedProcesses_array[0]['scheme'] = "ocid"
        expected_relatedProcesses_array[0]['identifier'] = self.__ap_ocid
        expected_relatedProcesses_array[0]['uri'] = \
            f"{self.__metadata_tender_url}/{self.__ap_cpid}/{self.__ap_ocid}"

        # Prepare object, where 'relationship' = 'parent'.
        expected_relatedProcesses_array.append(copy.deepcopy(
            self.__expected_fe_release['releases'][0]['relatedProcesses'][0]
        ))

        expected_relatedProcesses_array[1]['relationship'] = ["parent"]
        expected_relatedProcesses_array[1]['scheme'] = "ocid"
        expected_relatedProcesses_array[1]['identifier'] = self.__ap_cpid
        expected_relatedProcesses_array[1]['uri'] = \
            f"{self.__metadata_tender_url}/{self.__ap_cpid}/{self.__ap_cpid}"

        final_expected_relatedProcesses_array = list()
        if len(self.__actual_fe_release['releases'][0]['relatedProcesses']) == len(expected_relatedProcesses_array):
            for act in range(len(self.__actual_fe_release['releases'][0]['relatedProcesses'])):
                for exp in range(len(expected_relatedProcesses_array)):

                    if self.__actual_fe_release['releases'][0]['relatedProcesses'][act]['relationship'] == \
                            expected_relatedProcesses_array[exp]['relationship']:

                        try:
                            """Set permanent id."""

                            is_permanent_id_correct = is_it_uuid(
                                self.__actual_fe_release['releases'][0]['relatedProcesses'][act]['id'])

                            if is_permanent_id_correct is True:

                                expected_relatedProcesses_array[exp]['id'] = \
                                    self.__actual_fe_release['releases'][0]['relatedProcesses'][act]['id']
                            else:
                                raise ValueError(f"The 'releases[0].relatedProcesses[{act}].id' must be uuid.")
                        except KeyError:
                            raise KeyError("Mismatch key into path 'releases[0].relatedProcesses[*].id'")

                        final_expected_relatedProcesses_array.append(expected_relatedProcesses_array[exp])
        else:
            raise ValueError("The quantity of actual relatedProcesses array != "
                             "quantity of expected relatedProcesses array")
        self.__expected_fe_release['releases'][0]['relatedProcesses'] = final_expected_relatedProcesses_array
        return self.__expected_fe_release
