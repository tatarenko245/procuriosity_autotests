import copy
import random

from tests.utils.data_of_enum import locality_scheme, legalBasis, cpv_goods_low_level_03, cpv_goods_low_level_1, \
    cpv_goods_low_level_2, cpv_goods_low_level_3, cpv_goods_low_level_44, cpv_goods_low_level_48, \
    cpv_works_low_level_45, cpv_services_low_level_5, cpv_services_low_level_6, cpv_services_low_level_7, \
    cpv_services_low_level_8, cpv_services_low_level_92, cpv_services_low_level_98, documentType
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class PlanPayload:
    def __init__(self, fs_id, amount, currency, tender_classification_id, host):
        pn_period = Date().planning_notice_period()
        contact_period = Date().contact_period()

        document_one = Document(host=host, file_name="API.pdf")
        self.document_one_was_uploaded = document_one.uploading_document()

        try:
            item_classification_id = None
            tender_classification_id = tender_classification_id

            if tender_classification_id[0:3] == "031":
                item_classification_id = random.choice(cpv_goods_low_level_03)
            elif tender_classification_id[0:3] == "146":
                item_classification_id = random.choice(cpv_goods_low_level_1)
            elif tender_classification_id[0:3] == "221":
                item_classification_id = random.choice(cpv_goods_low_level_2)
            elif tender_classification_id[0:3] == "301":
                item_classification_id = random.choice(cpv_goods_low_level_3)
            elif tender_classification_id[0:3] == "444":
                item_classification_id = random.choice(cpv_goods_low_level_44)
            elif tender_classification_id[0:3] == "482":
                item_classification_id = random.choice(cpv_goods_low_level_48)
            elif tender_classification_id[0:3] == "451":
                item_classification_id = random.choice(cpv_works_low_level_45)
            elif tender_classification_id[0:3] == "515":
                item_classification_id = random.choice(cpv_services_low_level_5)
            elif tender_classification_id[0:3] == "637":
                item_classification_id = random.choice(cpv_services_low_level_6)
            elif tender_classification_id[0:3] == "713":
                item_classification_id = random.choice(cpv_services_low_level_7)
            elif tender_classification_id[0:3] == "851":
                item_classification_id = random.choice(cpv_services_low_level_8)
            elif tender_classification_id[0:3] == "923":
                item_classification_id = random.choice(cpv_services_low_level_92)
            elif tender_classification_id[0:3] == "983":
                item_classification_id = random.choice(cpv_services_low_level_98)
        except ValueError:
            raise ValueError("Check tender_classification_id")

        self.__payload = {
            "planning": {
                "rationale": "create pn: planning.rationale",
                "budget": {
                    "description": "create pn: planning.description.description",
                    "budgetBreakdown": [
                        {
                            "id": fs_id,
                            "amount": {
                                "amount": amount,
                                "currency": currency
                            }
                        }
                    ]
                }
            },
            "tender": {
                "title": "create pn: tender.title",
                "description": "create pn: tender.description",
                "legalBasis": f"{random.choice(legalBasis)}",
                "procurementMethodRationale": "create pn: tender.procurementMethodRationale",
                "procurementMethodAdditionalInfo": "create pn: tender.procurementMethodAdditionalInfo",
                "tenderPeriod":
                    {
                        "startDate": pn_period
                    },
                "lots": [
                    {
                        "id": "0",
                        "internalId": "create pn: tender.lots0.internalId",
                        "title": "create pn: tender.lots0.title",
                        "description": "create pn: tender.lots0.description",
                        "value": {
                            "amount": amount,
                            "currency": currency
                        },
                        "contractPeriod": {
                            "startDate": contact_period[0],
                            "endDate": contact_period[1]
                        },
                        "placeOfPerformance": {
                            "address": {
                                "streetAddress": "create pn: tender.lots0.deliveryAddress.streetAddress",
                                "postalCode": "create ei: tender.lots0.deliveryAddress.postalCode",
                                "addressDetails": {
                                    "country": {
                                        "id": "MD"
                                    },
                                    "region": {
                                        "id": "3400000"
                                    },
                                    "locality": {
                                        "id": "3401000",
                                        "description":
                                            "create ei: tender.lots0.deliveryAddress.addressDetails.locality.uri",
                                        "scheme": f"{random.choice(locality_scheme)}",
                                        "uri": "create ei: tender.lots0.deliveryAddress.addressDetails.locality.uri"
                                    }
                                }
                            },
                            "description": "create pn: tender.lots0.placeOfPerformance.description"
                        }
                    }],
                "items": [
                    {
                        "id": "0",
                        "internalId": "create pn: tender.items0.internalId",
                        "classification": {
                            "id": item_classification_id
                        },
                        "additionalClassifications": [
                            {
                                "id": "AA12-4"
                            }
                        ],
                        "quantity": "10",
                        "unit": {
                            "id": "10"
                        },
                        "description": "create ei: tender.items0.description",
                        "relatedLot": ["0"]
                    }],
                "documents": [
                    {
                        "documentType": f"{random.choice(documentType)}",
                        "id": self.document_one_was_uploaded[0]["data"]["id"],
                        "title": "create pn: tender.documents.title",
                        "description": "create pn: tender.documents.description",
                        "relatedLots": ["0"]
                    }]
            }
        }

    def build_plan_payload(self):
        return self.__payload

    def delete_optional_fields(
            self, *args, procuringentity_additionalidentifiers_positionn=0,
            buyer_additionalidentifiers_position=0):
        for a in args:
            if a == "tender.procuringEntity.identifier.uri":
                del self.__payload['tender']['procuringEntity']['identifier']['uri']
            elif a == "tender.procuringEntity.address.postalCode":
                del self.__payload['tender']['procuringEntity']['address']['postalCode']
            elif a == "tender.procuringEntity.additionalIdentifiers":
                del self.__payload['tender']['procuringEntity']['additionalIdentifiers']
            elif a == "tender.procuringEntity.additionalIdentifiers.uri":

                del self.__payload['tender']['procuringEntity'][
                    'additionalIdentifiers'][procuringentity_additionalidentifiers_positionn]['uri']

            elif a == "tender.procuringEntity.contactPoint.faxNumber":
                del self.__payload['tender']['procuringEntity']['contactPoint']['faxNumber']
            elif a == "tender.procuringEntity.contactPoint.url":
                del self.__payload['tender']['procuringEntity']['contactPoint']['url']

            elif a == "planning.budget.id":
                del self.__payload['planning']['budget']['id']
            elif a == "planning.budget.description":
                del self.__payload['planning']['budget']['description']
            elif a == "planning.budget.europeanUnionFunding":
                self.__payload['planning']['budget']['isEuropeanUnionFunded'] = False
                del self.__payload['planning']['budget']['europeanUnionFunding']
            elif a == "planning.budget.europeanUnionFunding.uri":
                del self.__payload['planning']['budget']['europeanUnionFunding']['uri']
            elif a == "planning.budget.project":
                del self.__payload['planning']['budget']['project']
            elif a == "planning.budget.projectID":
                del self.__payload['planning']['budget']['projectID']
            elif a == "planning.budget.uri":
                del self.__payload['planning']['budget']['uri']
            elif a == "planning.rationale":
                del self.__payload['planning']['rationale']

            elif a == "buyer.identifier.uri":
                del self.__payload['buyer']['identifier']['uri']
            elif a == "buyer.address.postalCode":
                del self.__payload['buyer']['address']['postalCode']
            elif a == "buyer.additionalIdentifiers":
                del self.__payload['buyer']['additionalIdentifiers']
            elif a == "buyer.additionalIdentifiers.uri":
                del self.__payload['buyer']['additionalIdentifiers'][buyer_additionalidentifiers_position]['uri']
            elif a == "buyer.contactPoint.faxNumber":
                del self.__payload['buyer']['contactPoint']['faxNumber']
            elif a == "buyer.contactPoint.url":
                del self.__payload['buyer']['contactPoint']['url']

            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def customize_buyer_additionalidentifiers(self, quantity_of_buyer_additionalidentifiers):
        new_additionalidentifiers_array = list()
        for q in range(quantity_of_buyer_additionalidentifiers):
            new_additionalidentifiers_array.append(copy.deepcopy(self.__payload['buyer']['additionalIdentifiers'][0]))
            new_additionalidentifiers_array[q]['id'] = f"create fs: buyer.additionalIdentifiers{q}.id"
            new_additionalidentifiers_array[q]['scheme'] = f"create fs: buyer.additionalIdentifiers{q}.scheme"
            new_additionalidentifiers_array[q]['legalName'] = f"create fs: buyer.additionalIdentifiers{q}.legalName"
            new_additionalidentifiers_array[q]['uri'] = f"create fs: buyer.additionalIdentifiers{q}.uri"

        self.__payload['buyer']['additionalIdentifiers'] = new_additionalidentifiers_array

    def customize_tender_procuringentity_additionalidentifiers(
            self, quantity_of_tender_procuringentity_additionalidentifiers):
        new_additionalidentifiers_array = list()
        for q in range(quantity_of_tender_procuringentity_additionalidentifiers):
            new_additionalidentifiers_array.append(
                copy.deepcopy(self.__payload['tender']['procuringEntity']['additionalIdentifiers'][0])
            )

            new_additionalidentifiers_array[q]['id'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.id"

            new_additionalidentifiers_array[q]['scheme'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.scheme"

            new_additionalidentifiers_array[q]['legalName'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.legalName"

            new_additionalidentifiers_array[q]['uri'] = \
                f"create fs: tender.procuringEntity.additionalIdentifiers{q}.uri"

        self.__payload['tender']['procuringEntity']['additionalIdentifiers'] = new_additionalidentifiers_array

    def __del__(self):
        print(f"The instance of class {__name__} was deleted.")
