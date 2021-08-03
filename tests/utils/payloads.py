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
        self.ei_period = Date().expenditure_item_period()
        category = random.choice(cpv_category)
        self.tender_classification_id = None
        self.payload = None
        if category == "goods":
            self.tender_classification_id = random.choice(cpv_goods_high_level)
        elif category == "works":
            self.tender_classification_id = random.choice(cpv_works_high_level)
        elif category == "services":
            self.tender_classification_id = random.choice(cpv_services_high_level)


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
        self.payload = {
            "tender": {
                "title": "create ei: tender.title",
                "description": "create ei: tender.description",
                "classification": {
                    "id": self.tender_classification_id
                },
                "items": [{
                    "id": "1",
                    "description": "create ei: tender.items[0].description",
                    "classification": {
                        "id": self.tender_classification_id
                    },
                    "additionalClassifications": [
                        {
                            "id": "AA12-4"
                        }
                    ],
                    "deliveryAddress": {
                        "streetAddress": "create ei: tender.items[0].deliveryAddress.streetAddress",
                        "postalCode": "create ei: tender.items[0].deliveryAddress.postalCode",
                        "addressDetails": {
                            "country": {
                                "id": "MD"

                            },
                            "region": {
                                "id": "1700000"

                            },
                            "locality": {
                                "id": "1701000",
                                "description": "create ei: tender.items[0].deliveryAddress.addressDetails."
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
                        "startDate": self.ei_period[0],
                        "endDate": self.ei_period[1]
                    }
                },
                "rationale": "create ei: tender.items[0].deliveryAddress.postalCode"
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
                            "scheme": "CUATM",
                            "id": "1701000",
                            "description": "create ei: buyer.address.addressDetails.locality.description"
                        }
                    }
                },
                "additionalIdentifiers": [{
                    "id": "create ei buyer.additionalIdentifiers.id",
                    "scheme": "create ei buyer.additionalIdentifiers.scheme",
                    "legalName": "create ei buyer.additionalIdentifiers.description",
                    "uri": "create ei buyer.additionalIdentifiers.uri"
                }],
                "contactPoint": {
                    "name": "create ei: buyer.contactPoint.name",
                    "email": "create ei: buyer.contactPoint.email",
                    "telephone": "create ei: buyer.contactPoint.telephone",
                    "faxNumber": "create ei: buyer.contactPoint.faxNUmber",
                    "url": "create ei: buyer.contactPoint.url"
                },
                "details": {
                    "typeOfBuyer": f'{random.choice(typeOfBuyer)}',
                    "mainGeneralActivity": f'{random.choice(mainGeneralActivity)}',
                    "mainSectoralActivity": f'{random.choice(mainSectoralActivity)}'

                }
            }
        }
        return self.payload

    def add_tender_items(self, quantity=2):
        items_array = generate_items_array(
            quantity_of_object=quantity,
            item_object=self.payload['tender']['items'][0],
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
        return self.payload

    def update_ei_full_data_model_with_one_item_object(self):
        self.payload = {
            "tender": {
                "title": "update ei: tender.title",
                "description": "update ei: tender.description",
                "classification": {
                    "id": self.tender_classification_id
                },
                "items": [{
                    "id": "1",
                    "description": "update ei: tender.items[0].description",
                    "classification": {
                        "id": self.tender_classification_id
                    },
                    "additionalClassifications": [
                        {
                            "id": "AA08-2"
                        }
                    ],
                    "deliveryAddress": {
                        "streetAddress": "update ei: tender.items[0].deliveryAddress.streetAddress",
                        "postalCode": "update ei: tender.items[0].deliveryAddress.postalCode",
                        "addressDetails": {
                            "country": {
                                "id": "MD"

                            },
                            "region": {
                                "id": "3400000"

                            },
                            "locality": {
                                "id": "3401000",
                                "description": "update ei: tender.items[0].deliveryAddress.addressDetails."
                                               "locality.description",
                                "scheme": f'{random.choice(locality_scheme)}'
                            }

                        }
                    },
                    "quantity": 2,
                    "unit": {
                        "id": "20"

                    }
                }]
            },
            "planning": {
                "rationale": "update ei: tender.items[0].deliveryAddress.postalCode"
            },
            "buyer": {
                "name": "update ei: buyer.name",
                "identifier": {
                    "id": "update ei: buyer.identifier.id",
                    "scheme": "MD-IDNO",
                    "legalName": "update ei: buyer.identifier.legalName",
                    "uri": "update ei: buyer.identifier.uri"
                },
                "address": {
                    "streetAddress": "update ei: buyer.address.streetAddress",
                    "postalCode": "update ei: buyer.address.postalCode",
                    "addressDetails": {
                        "country": {
                            "id": "MD"
                        },
                        "region": {
                            "id": "3400000"
                        },
                        "locality": {
                            "scheme": "CUATM",
                            "id": "3401000",
                            "description": "update ei: buyer.address.addressDetails.locality.description"
                        }
                    }
                },
                "additionalIdentifiers": [{
                    "id": "update ei buyer.additionalIdentifiers.id",
                    "scheme": "update ei buyer.additionalIdentifiers.scheme",
                    "legalName": "update ei buyer.additionalIdentifiers.description",
                    "uri": "update ei buyer.additionalIdentifiers.uri"
                }],
                "contactPoint": {
                    "name": "update ei: buyer.contactPoint.name",
                    "email": "update ei: buyer.contactPoint.email",
                    "telephone": "update ei: buyer.contactPoint.telephone",
                    "faxNumber": "update ei: buyer.contactPoint.faxNUmber",
                    "url": "update ei: buyer.contactPoint.url"
                },
                "details": {
                    "typeOfBuyer": f'{random.choice(typeOfBuyer)}',
                    "mainGeneralActivity": f'{random.choice(mainGeneralActivity)}',
                    "mainSectoralActivity": f'{random.choice(mainSectoralActivity)}'

                }
            }
        }
        # Временно так как не пофиксили баг -> нужно раскомментировать del self.payload['tender']['classification']
        # и # del self.payload['buyer']
        # del self.payload['tender']['classification']
        # del self.payload['buyer']
        return self.payload
