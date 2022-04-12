import copy
import random

from tests.utils.data_of_enum import locality_scheme_tuple, legalBasis_tuple, documentType_tuple, cpv_category_tuple, \
    cpv_goods_high_level_tuple, cpv_works_high_level_tuple, cpv_services_high_level_tuple, currency_tuple
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class AggregatedPlan:
    def __init__(self, centralPurchasingBody_id, host_to_service, maxDurationOfFA, tenderClassificationId=None,
                 currency=None):

        __pn_period = Date().planningNotice_period()
        __contact_period = Date().contactPeriod(maxDurationOfFA)

        __document_one = Document(host=host_to_service, file_name="API.pdf")
        self.__document_one_was_uploaded = __document_one.uploading_document()
        self.__host = host_to_service

        __tenderClassificationId = tenderClassificationId
        if __tenderClassificationId is None:
            __category = random.choice(cpv_category_tuple)
            if __category == "goods":
                __tenderClassificationId = random.choice(cpv_goods_high_level_tuple)
            elif __category == "works":
                __tenderClassificationId = random.choice(cpv_works_high_level_tuple)
            elif __category == "services":
                __tenderClassificationId = random.choice(cpv_services_high_level_tuple)

        if currency is None:
            currency = f"{random.choice(currency_tuple)}"

        self.__payload = {
            "tender": {
                "title": "create ap: tender.title",
                "description": "create ap: tender.description",
                "legalBasis": f"{random.choice(legalBasis_tuple)}",
                "procurementMethodRationale": "create ap: tender.procurementMethodRationale",
                "classification": {
                    "id": __tenderClassificationId
                },
                "tenderPeriod": {
                    "startDate": __pn_period
                },
                "procuringEntity": {
                    "name": "create ap: procuringEntity.name",
                    "identifier": {
                        "id": f"{centralPurchasingBody_id}",
                        "scheme": "MD-IDNO",
                        "legalName": "create ap: procuringEntity.identifier.legalName",
                        "uri": "create ap: procuringEntity.identifier.uri"
                    },
                    "address": {
                        "streetAddress": "create ap: procuringEntity.address.streetAddress",
                        "postalCode": "create ap: procuringEntity.address.postalCode",
                        "addressDetails": {
                            "country": {
                                "id": "MD"
                            },
                            "region": {
                                "id": "1700000"
                            },
                            "locality": {
                                "scheme": f"{random.choice(locality_scheme_tuple)}",
                                "id": "1701000",
                                "description":
                                    "create ap: tender.procuringEntity.address.addressDetails.locality.description"
                            }
                        }
                    },
                    "additionalIdentifiers": [{
                        "id": "create ap: tender.procuringEntity.additionalIdentifiers.id",
                        "scheme": "create ap: tender.procuringEntity.additionalIdentifiers.scheme",
                        "legalName": "create ap: tender.procuringEntity.additionalIdentifiers.legalName",
                        "uri": "create ap: tender.procuringEntity.additionalIdentifiers.uri"
                    }],
                    "contactPoint": {
                        "name": "create ap: tender.procuringEntity.contactPoint.name",
                        "email": "create ap: tender.procuringEntity.contactPoint.email",
                        "telephone": "create ap: tender.procuringEntity.contactPoint.telephone",
                        "faxNumber": "create ap: tender.procuringEntity.contactPoint.faxNumber",
                        "url": "create ap: tender.procuringEntity.contactPoint.url"
                    }
                },
                "documents": [
                    {
                        "documentType": f"{random.choice(documentType_tuple)}",
                        "id": self.__document_one_was_uploaded[0]["data"]["id"],
                        "title": "create ap: tender.documents.title",
                        "description": "create ap: tender.documents.description"
                    }],
                "contractPeriod": {
                    "startDate": __contact_period[0],
                    "endDate": __contact_period[1]
                },
                "value": {
                    "currency": currency
                }

            }
        }

    def build_aggregatedPlan_payload(self):
        return self.__payload

    def delete_optional_fields(
            self, *args, procuringEntity_additionalIdentifiers_position=0, document_position=0):
        for a in args:
            if a == "tender.procurementMethodRationale":
                del self.__payload['tender']['procurementMethodRationale']

            elif a == "tender.procuringEntity.additionalIdentifiers":
                del self.__payload['tender']['procuringEntity'][
                    'additionalIdentifiers']

            elif a == "tender.procuringEntity.additionalIdentifiers.uri":
                del self.__payload['tender']['procuringEntity'][
                    'additionalIdentifiers'][procuringEntity_additionalIdentifiers_position]['uri']

            elif a == "tender.procuringEntity.address.postalCode":
                del self.__payload['tender']['procuringEntity']['address']['postalCode']
            elif a == "tender.procuringEntity.contactPoint.faxNumber":
                del self.__payload['tender']['procuringEntity'][
                    'contactPoint']['faxNumber']
            elif a == "tender.procuringEntity.contactPoint.url":
                del self.__payload['tender']['procuringEntity'][
                    'contactPoint']['url']

            elif a == "tender.documents":
                del self.__payload['tender']['documents']
            elif a == "tender.documents.description":
                del self.__payload['tender']['documents'][document_position]['description']

            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def customize_tender_procuringEntity_additionalIdentifiers(
            self, quantity_of_tender_procuringEntity_additionalIdentifiers):

        new_additionalIdentifiers_array = list()
        for q in range(quantity_of_tender_procuringEntity_additionalIdentifiers):
            new_additionalIdentifiers_array.append(
                copy.deepcopy(self.__payload['tender']['procuringEntity']['additionalIdentifiers'][0])
            )

            new_additionalIdentifiers_array[q]['id'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.id"

            new_additionalIdentifiers_array[q]['scheme'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.scheme"

            new_additionalIdentifiers_array[q]['legalName'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.legalName"

            new_additionalIdentifiers_array[q]['uri'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.uri"

        self.__payload['tender']['procuringEntity']['additionalIdentifiers'] = new_additionalIdentifiers_array

    def customize_tender_documents(self, quantity_of_documents):

        new_documents_array = list()
        for q_0 in range(quantity_of_documents):
            new_documents_array.append(copy.deepcopy(self.__payload['tender']['documents'][0]))

            document_two = Document(host=self.__host, file_name="API.pdf")
            document_two_was_uploaded = document_two.uploading_document()

            new_documents_array[q_0]['id'] = document_two_was_uploaded[0]["data"]["id"]
            new_documents_array[q_0]['documentType'] = f"{random.choice(documentType_tuple)}"
            new_documents_array[q_0]['title'] = f"create pn: tender.documents{q_0}.title"
            new_documents_array[q_0]['description'] = f"create pn: tender.documents{q_0}.description"

        self.__payload['tender']['documents'] = new_documents_array

    def __del__(self):
        print(f"The instance of AggregatedPlan class: {__name__} was deleted.")
