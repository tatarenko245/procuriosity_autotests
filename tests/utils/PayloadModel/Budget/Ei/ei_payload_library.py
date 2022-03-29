import random

import jmespath

from tests.utils.data_of_enum import cpv_category, cpv_goods_high_level, cpv_works_high_level, cpv_services_high_level, \
    locality_scheme, typeOfBuyer, mainGeneralActivity, mainSectoralActivity
from tests.utils.date_class import Date


class ExpenditureItemPayload:
    def __init__(self):

        category = random.choice(cpv_category)
        tender_classification_id = None
        if category == "goods":
            tender_classification_id = random.choice(cpv_goods_high_level)
        elif category == "works":
            tender_classification_id = random.choice(cpv_works_high_level)
        elif category == "services":
            tender_classification_id = random.choice(cpv_services_high_level)

        ei_period = Date().expenditure_item_period()

        self.__payload__ = {
            "tender": {
                "title": "create ei: tender.title",
                "description": "create ei: tender.description",
                "classification": {
                    "id": tender_classification_id
                },
                "items": [
                    {
                        "id": "0",
                        "description": f"create ei: tender.items0.description",
                        "classification": {
                            "id": tender_classification_id
                        },
                        "additionalClassifications": [
                            {
                                "id": "AA12-4"
                            }
                        ],
                        "deliveryAddress": {
                            "streetAddress": "create ei: tender.items0.deliveryAddress.streetAddress",
                            "postalCode": "create ei: tender.items0.deliveryAddress.postalCode",
                            "addressDetails": {
                                "country": {
                                    "id": "MD"
                                },
                                "region": {
                                    "id": "3400000"
                                },
                                "locality": {
                                    "id": "3401000",
                                    "description": "create ei: tender.items0.deliveryAddress.addressDetails.locality.uri",
                                    "scheme": f"{random.choice(locality_scheme)}",
                                    "uri": "create ei: tender.items0.deliveryAddress.addressDetails.locality.uri"
                                }
                            }
                        },
                        "quantity": "10",
                        "unit": {
                            "id": "10"
                        }
                    }
                ]
            },
            "planning": {
                "budget": {
                    "period": {
                        "startDate": ei_period[0],
                        "endDate": ei_period[1]
                    }
                },
                "rationale": "create ei: planning.rationale"
            },
            "buyer": {
                "name": "create ei: buyer.name",
                "identifier": {
                    "id": "create ei: buyer.identifier.id",
                    "scheme": "MD-IDNO",
                    "legalName": "create ei: buyer.identifier.legalName",
                    "uri": "create ei: buyer.identifier.uri"
                },
                "address": {
                    "streetAddress": "create ei: buyer.address.streetAddress",
                    "postalCode": "create ei: buyer.address.postalCode",
                    "addressDetails": {
                        "country": {
                            "id": "MD"
                        },
                        "region": {
                            "id": "1700000"
                        },
                        "locality": {
                            "scheme": f"{random.choice(locality_scheme)}",
                            "id": "1701000",
                            "description": "create ei: buyer.address.addressDetails.locality.description"
                        }
                    }
                },
                "additionalIdentifiers": [
                    {
                        "id": "create ei buyer.additionalIdentifiers0.id",
                        "scheme": "create ei buyer.additionalIdentifiers0.scheme",
                        "legalName": "create ei buyer.additionalIdentifiers0.legalName",
                        "uri": "create ei buyer.additionalIdentifiers0.uri"
                    }
                ],
                "contactPoint": {
                    "name": "create ei: buyer.contactPoint.name",
                    "email": "create ei: buyer.contactPoint.email",
                    "telephone": "create ei: buyer.contactPoint.telephone",
                    "faxNumber": "create ei: buyer.contactPoint.faxNumber",
                    "url": "create ei: buyer.contactPoint.url"
                },
                "details": {
                    "typeOfBuyer": f"{random.choice(typeOfBuyer)}",
                    "mainGeneralActivity": f"{random.choice(mainGeneralActivity)}",
                    "mainSectoralActivity": f"{random.choice(mainSectoralActivity)}"

                }
            }
        }

    def build_expenditure_item_payload(self):
        return self.__payload__

    def delete_optional_fields_into_tender_object(self, *args, item_position, buyer_additionalidentifiers_position):
        for a in args:
            if a == "tender.description":
                del self.__payload__['tender']['description']
            elif a == "tender.items":
                del self.__payload__['tender']['items']
            elif a == "tender.items.additionalClassifications":
                del self.__payload__['tender']['items'][item_position]['additionalClassifications']
            elif a == "tender.items.deliveryAddress.postalCode":
                del self.__payload__['tender']['items'][item_position]['deliveryAddress']['postalCode']
            elif a == "tender.items.deliveryAddress.addressDetails.locality.uri":
                del self.__payload__['tender']['items'][item_position]['deliveryAddress']['addressDetails']['locality'][
                    'uri']

            elif a == "planning.rationale":
                del self.__payload__['planning']['rationale']

            elif a == "buyer.identifier.uri":
                del self.__payload__['buyer']['identifier']['uri']
            elif a == "buyer.address.postalCode":
                del self.__payload__['buyer']['address']['postalCode']
            elif a == "buyer.additionalIdentifiers":
                del self.__payload__['buyer']['additionalIdentifiers']
            elif a == "buyer.additionalIdentifiers.uri":
                del self.__payload__['buyer']['additionalIdentifiers'][buyer_additionalidentifiers_position]['uri']
            elif a == "buyer.contactPoint.faxNumber":
                del self.__payload__['buyer']['contactPoint']['faxNumber']
            elif a == "buyer.contactPoint.url":
                del self.__payload__['buyer']['contactPoint']['url']
            elif a == "buyer.details":
                del self.__payload__['buyer']['details']
            elif a == "buyer.details.typeOfBuyer":
                del self.__payload__['buyer']['details']['typeOfBuyer']
            elif a == "buyer.details.mainGeneralActivity":
                del self.__payload__['buyer']['details']['mainGeneralActivity']
            elif a == "buyer.details.mainSectoralActivity":
                del self.__payload__['buyer']['details']['mainSectoralActivity']
            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def customize_tender_items(self, *args, quantity_of_items, quantity_of_items_additionalclassifications):
        item_object_model = self.__payload__['tender']['items'][0]

        self.__payload__['tender']['items'] = list()
        for q_0 in range(quantity_of_items):

            self.__payload__['tender']['items'][q_0]['additionalClassifications'] = list()
            for q_1 in range(quantity_of_items_additionalclassifications):
                self.__payload__['tender']['items'][q_0]['additionalClassifications'].append(
                    item_object_model['additionalClassifications'][0])

            self.__payload__['tender']['items'].append(item_object_model)

    def customize_buyer_additionalidentifiers(self, *args, quantity_of_buyer_additionalidentifiers):
        additionalidentifier_object_model = self.__payload__['buyer']['additionalIdentifiers'][0]

        self.__payload__['buyer']['additionalIdentifiers'] = list()
        for q in range(quantity_of_buyer_additionalidentifiers):
            self.__payload__['buyer']['additionalIdentifiers'].append(
                additionalidentifier_object_model
            )
