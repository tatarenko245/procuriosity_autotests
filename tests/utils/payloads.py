# тут лежать json
import copy
import random
from allure_commons._allure import step

from tests.conftest import GlobalClassCreateEi
from tests.utils.date_class import Date
from tests.utils.data_of_enum import locality_scheme, typeOfBuyer, mainGeneralActivity, mainSectoralActivity, \
    cpv_goods_high_level, cpv_works_high_level, cpv_services_high_level, cpv_category
from tests.utils.functions import generate_items_array, \
    get_value_from_classification_cpv_dictionary_xls, generate_tender_classification_id


class EiPayload:
    def __init__(self):
        ei_period = Date().expenditure_item_period()
        category = random.choice(cpv_category)
        self.tender_classification_id = None
        if category == "goods":
            self.tender_classification_id = random.choice(cpv_goods_high_level)
        elif category == "works":
            self.tender_classification_id = random.choice(cpv_works_high_level)
        elif category == "services":
            self.tender_classification_id = random.choice(cpv_services_high_level)
        self.payload = {
            "tender": {
                "title": "ei: tender.title",
                "description": "ei: tender.description",
                "classification": {
                    "id": self.tender_classification_id
                },
                "items": [{
                    "id": "1",
                    "description": "ei: tender.items[0].description",
                    "classification": {
                        "id": self.tender_classification_id
                    },
                    "additionalClassifications": [
                        {
                            "id": "AA12-4"
                        }
                    ],
                    "deliveryAddress": {
                        "streetAddress": "ei: tender.items[0].deliveryAddress.streetAddress",
                        "postalCode": "ei: tender.items[0].deliveryAddress.postalCode",
                        "addressDetails": {
                            "country": {
                                "id": "MD"

                            },
                            "region": {
                                "id": "1700000"

                            },
                            "locality": {
                                "id": "1701000",
                                "description": "ei: tender.items[0].deliveryAddress.addressDetails."
                                               "locality.description",
                                "scheme": f'{random.choice(locality_scheme)}'
                            }

                        }
                    },
                    "quantity": 1,
                    "unit": {
                        "id": "10"

                    }
                }]
            },
            "planning": {
                "budget": {
                    "period": {
                        "startDate": ei_period[0],
                        "endDate": ei_period[1]
                    }
                },
                "rationale": "ei: tender.items[0].deliveryAddress.postalCode"
            },
            "buyer": {
                "name": "ei: buyer.name",
                "identifier": {
                    "id": "ei: buyer.identifier.id",
                    "scheme": "MD-IDNO",
                    "legalName": "ei: buyer.identifier.legalName",
                    "uri": "ei: buyer.identifier.uri"
                },
                "address": {
                    "streetAddress": "ei: buyer.address.streetAddress",
                    "postalCode": "ei: buyer.address.postalCode",
                    "addressDetails": {
                        "country": {
                            "id": "MD"
                        },
                        "region": {
                            "id": "1700000"
                        },
                        "locality": {
                            "scheme": "CUATM",
                            "id": "1701000",
                            "description": "ei: buyer.address.addressDetails.locality.description"
                        }
                    }
                },
                "additionalIdentifiers": [{
                    "id": "ei buyer.additionalIdentifiers.id",
                    "scheme": "ei buyer.additionalIdentifiers.scheme",
                    "legalName": "ei buyer.additionalIdentifiers.description",
                    "uri": "ei buyer.additionalIdentifiers.uri"
                }],
                "contactPoint": {
                    "name": "ei: buyer.contactPoint.name",
                    "email": "ei: buyer.contactPoint.email",
                    "telephone": "ei: buyer.contactPoint.telephone",
                    "faxNumber": "ei: buyer.contactPoint.faxNUmber",
                    "url": "ei: buyer.contactPoint.url"
                },
                "details": {
                    "typeOfBuyer": f'{random.choice(typeOfBuyer)}',
                    "mainGeneralActivity": f'{random.choice(mainGeneralActivity)}',
                    "mainSectoralActivity": f'{random.choice(mainSectoralActivity)}'

                }
            }
        }

    def create_ei_obligatory_model_of_payload(self):
        del self.payload['tender']['description']
        del self.payload['tender']['items']
        del self.payload['planning']['rationale']
        del self.payload['buyer']['identifier']['uri']
        del self.payload['buyer']['address']['postalCode']
        del self.payload['buyer']['additionalIdentifiers']
        del self.payload['buyer']['contactPoint']['faxNumber']
        del self.payload['buyer']['contactPoint']['url']
        del self.payload['buyer']['details']
        return self.payload

    def create_ei_full_data_model_with_one_item_object(self):
        return self.payload

    def add_tender_items(self, quantity=2):
        item_object = {
            "id": "1",
            "description": "ei: tender.items[0].description",
            "classification": {
                "id": self.tender_classification_id
            },
            "additionalClassifications": [
                {
                    "id": "AA12-4"
                }
            ],
            "deliveryAddress": {
                "streetAddress": "ei: tender.items[0].deliveryAddress.streetAddress",
                "postalCode": "ei: tender.items[0].deliveryAddress.postalCode",
                "addressDetails": {
                    "country": {
                        "id": "MD"

                    },
                    "region": {
                        "id": "1700000"

                    },
                    "locality": {
                        "id": "1701000",
                        "description": "ei: tender.items[0].deliveryAddress.addressDetails."
                                       "locality.description",
                        "scheme": f'{random.choice(locality_scheme)}'
                    }

                }
            },
            "quantity": 1,
            "unit": {
                "id": "10"

            }
        }
        items_array = generate_items_array(
            quantity_of_object=quantity,
            item_object=item_object,
            tender_classification_id=self.tender_classification_id
        )
        temp_tender_classification_id = generate_tender_classification_id(items_array)
        new_tender_classification = get_value_from_classification_cpv_dictionary_xls(
            cpv=temp_tender_classification_id,
            language=GlobalClassCreateEi.language
        )
        self.payload['tender']['items'] = items_array
        self.payload['tender']['classification']['id'] = new_tender_classification[0]
        return self.payload

    def update_ei_obligatory_model_of_payload(self):
        del self.payload['tender']['description']
        del self.payload['tender']['items']
        del self.payload['planning']
        # Временно так как не пофиксили баг -> нужно раскомментировать del self.payload['tender']['classification']
        # и # del self.payload['buyer']
        # del self.payload['tender']['classification']
        # del self.payload['buyer']
        return self.payload

    def update_ei_full_data_model_with_one_item_object(self):
        # Временно так как не пофиксили баг -> нужно раскомментировать del self.payload['tender']['classification']
        # и # del self.payload['buyer']
        # del self.payload['tender']['classification']
        # del self.payload['buyer']
        return self.payload
