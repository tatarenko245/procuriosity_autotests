import copy
import random

from tests.utils.data_of_enum import cpv_category, cpv_goods_high_level, cpv_works_high_level, \
    cpv_services_high_level, locality_scheme, typeOfBuyer, mainGeneralActivity, mainSectoralActivity
from tests.utils.date_class import Date
from tests.utils.functions import generate_items_array
from tests.utils.payload_library import PayloadLibrary


class PreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())

    def create_ei_full_data_model(self, quantity_of_tender_item_object=1):
        payload = {
            "tender": {},
            "planning": {},
            "buyer": {}
        }

        payload['tender'].update(self.constructor.ei_tender_object())
        payload['planning'].update(self.constructor.ei_planning_obj())
        payload['buyer'].update(self.constructor.ei_buyer_obj())

        tender_classification_id = None
        category = random.choice(cpv_category)
        if category == "goods":
            tender_classification_id = random.choice(cpv_goods_high_level)
        elif category == "works":
            tender_classification_id = random.choice(cpv_works_high_level)
        elif category == "services":
            tender_classification_id = random.choice(cpv_services_high_level)

        payload['tender']['title'] = "create ei: tender.title"
        payload['tender']['description'] = "create ei: tender.description"
        payload['tender']['classification']['id'] = tender_classification_id
        payload['tender']['items'][0]['description'] = "create ei: tender.items.description"
        payload['tender']['items'][0]['classification']['id'] = tender_classification_id
        payload['tender']['items'][0]['additionalClassifications'][0]['id'] = "AA12-4"
        payload['tender']['items'][0]['deliveryAddress']['streetAddress'] = \
            "create ei: tender.items.deliveryAddress.streetAddress"
        payload['tender']['items'][0]['deliveryAddress']['postalCode'] = \
            "create ei: tender.items.deliveryAddress.postalCode"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['country']['id'] = "MD"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['locality']['description'] = \
            "create ei: tender.items[0].deliveryAddress.addressDetails.locality.description"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['items'][0]['quantity'] = 10
        payload['tender']['items'][0]['unit']['id'] = "10"
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_tender_item_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id)

        ei_period = Date().expenditure_item_period()
        payload['planning']['budget']['period']['startDate'] = ei_period[0]
        payload['planning']['budget']['period']['endDate'] = ei_period[1]
        payload['planning']['rationale'] = "create ei: planning.ratioanle"

        payload['buyer']['name'] = "create ei: buyer.name"
        payload['buyer']['identifier']['id'] = "create ei: buyer.identifier.id"
        payload['buyer']['identifier']['scheme'] = "MD-IDNO"
        payload['buyer']['identifier']['legalName'] = "create ei: buyer.identifier.legalName"
        payload['buyer']['identifier']['uri'] = "create ei: buyer.identifier.uri"
        payload['buyer']['address']['streetAddress'] = "create ei: buyer.address.streetAddress"
        payload['buyer']['address']['postalCode'] = "create ei: buyer.address.postalCode"
        payload['buyer']['address']['addressDetails']['country']['id'] = "MD"
        payload['buyer']['address']['addressDetails']['region']['id'] = "1700000"
        payload['buyer']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['buyer']['address']['addressDetails']['locality']['description'] = \
            "create ei: buyer.address.addressDetails.locality.description"
        payload['buyer']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['buyer']['additionalIdentifiers'][0]['id'] = "create ei buyer.additionalIdentifiers.id"
        payload['buyer']['additionalIdentifiers'][0]['scheme'] = "create ei buyer.additionalIdentifiers.scheme"
        payload['buyer']['additionalIdentifiers'][0]['legalName'] = "create ei buyer.additionalIdentifiers.legalName"
        payload['buyer']['additionalIdentifiers'][0]['uri'] = "create ei buyer.additionalIdentifiers.uri"
        payload['buyer']['contactPoint']['name'] = "create ei: buyer.contactPoint.name"
        payload['buyer']['contactPoint']['email'] = "create ei: buyer.contactPoint.email"
        payload['buyer']['contactPoint']['telephone'] = "create ei: buyer.contactPoint.telephone"
        payload['buyer']['contactPoint']['faxNumber'] = "create ei: buyer.contactPoint.faxNumber"
        payload['buyer']['contactPoint']['url'] = "create ei: buyer.contactPoint.url"
        payload['buyer']['details']['typeOfBuyer'] = f"{random.choice(typeOfBuyer)}"
        payload['buyer']['details']['mainGeneralActivity'] = f"{random.choice(mainGeneralActivity)}"
        payload['buyer']['details']['mainSectoralActivity'] = f"{random.choice(mainSectoralActivity)}"
        return payload

    def create_ei_obligatory_data_model(self):
        payload = {
            "tender": {},
            "planning": {},
            "buyer": {}
        }

        payload['tender'].update(self.constructor.ei_tender_object())
        payload['planning'].update(self.constructor.ei_planning_obj())
        payload['buyer'].update(self.constructor.ei_buyer_obj())

        tender_classification_id = None
        category = random.choice(cpv_category)
        if category == "goods":
            tender_classification_id = random.choice(cpv_goods_high_level)
        elif category == "works":
            tender_classification_id = random.choice(cpv_works_high_level)
        elif category == "services":
            tender_classification_id = random.choice(cpv_services_high_level)

        del payload['tender']['description']
        del payload['tender']['items']
        del payload['planning']['rationale']
        del payload['buyer']['identifier']['uri']
        del payload['buyer']['address']['postalCode']
        del payload['buyer']['additionalIdentifiers']
        del payload['buyer']['contactPoint']['faxNumber']
        del payload['buyer']['contactPoint']['url']
        del payload['buyer']['details']

        payload['tender']['title'] = "create ei: tender.title"
        payload['tender']['classification']['id'] = tender_classification_id
        ei_period = Date().expenditure_item_period()
        payload['planning']['budget']['period']['startDate'] = ei_period[0]
        payload['planning']['budget']['period']['endDate'] = ei_period[1]
        payload['buyer']['name'] = "create ei: buyer.name"
        payload['buyer']['identifier']['id'] = "create ei: buyer.identifier.id"
        payload['buyer']['identifier']['scheme'] = "MD-IDNO"
        payload['buyer']['identifier']['legalName'] = "create ei: buyer.identifier.legalName"
        payload['buyer']['address']['streetAddress'] = "create ei: buyer.address.streetAddress"
        payload['buyer']['address']['addressDetails']['country']['id'] = "MD"
        payload['buyer']['address']['addressDetails']['region']['id'] = "1700000"
        payload['buyer']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['buyer']['address']['addressDetails']['locality']['description'] = \
            "create ei: buyer.address.addressDetails.locality.description"
        payload['buyer']['address']['addressDetails']['locality']['scheme'] = "other"
        payload['buyer']['contactPoint']['name'] = "create ei: buyer.contactPoint.name"
        payload['buyer']['contactPoint']['email'] = "create ei: buyer.contactPoint.email"
        payload['buyer']['contactPoint']['telephone'] = "create ei: buyer.contactPoint.telephone"
        return payload

    def update_ei_full_data_model(self, tender_classification_id, quantity_of_tender_item_object=1):
        # Временно так как не пофиксили баг -> нужно раскомментировать del self.payload['tender']['classification']
        # и # del payload['buyer']
        # del payload['tender']['classification']
        # del payload['buyer']
        payload = {
            "tender": {},
            "planning": {},
            "buyer": {}
        }

        payload['tender'].update(self.constructor.ei_tender_object())
        payload['planning'].update(self.constructor.ei_planning_obj())
        payload['buyer'].update(self.constructor.ei_buyer_obj())
        payload['tender']['title'] = "update ei: tender.title"
        payload['tender']['description'] = "update ei: tender.description"
        payload['tender']['classification']['id'] = tender_classification_id
        payload['tender']['items'][0]['description'] = "update ei: tender.items.description"
        payload['tender']['items'][0]['classification']['id'] = tender_classification_id
        payload['tender']['items'][0]['additionalClassifications'][0]['id'] = "AA08-2"
        payload['tender']['items'][0]['deliveryAddress']['streetAddress'] = \
            "update ei: tender.items.deliveryAddress.streetAddress"
        payload['tender']['items'][0]['deliveryAddress']['postalCode'] = \
            "update ei: tender.items.deliveryAddress.postalCode"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['country']['id'] = "MD"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['region']['id'] = "3400000"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['locality']['id'] = "3401000"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['locality']['description'] = \
            "update ei: tender.items[0].deliveryAddress.addressDetails.locality.description"
        payload['tender']['items'][0]['deliveryAddress']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['items'][0]['quantity'] = 20
        payload['tender']['items'][0]['unit']['id'] = "20"
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_tender_item_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id)

        ei_period = Date().expenditure_item_period()
        payload['planning']['budget']['period']['startDate'] = ei_period[0]
        payload['planning']['budget']['period']['endDate'] = ei_period[1]
        payload['planning']['rationale'] = "update ei: planning.ratioanle"

        payload['buyer']['name'] = "update ei: buyer.name"
        payload['buyer']['identifier']['id'] = "update ei: buyer.identifier.id"
        payload['buyer']['identifier']['scheme'] = "MD-IDNO"
        payload['buyer']['identifier']['legalName'] = "update ei: buyer.identifier.legalName"
        payload['buyer']['identifier']['uri'] = "update ei: buyer.identifier.uri"
        payload['buyer']['address']['streetAddress'] = "update ei: buyer.address.streetAddress"
        payload['buyer']['address']['postalCode'] = "update ei: buyer.address.postalCode"
        payload['buyer']['address']['addressDetails']['country']['id'] = "MD"
        payload['buyer']['address']['addressDetails']['region']['id'] = "3400000"
        payload['buyer']['address']['addressDetails']['locality']['id'] = "3401000"
        payload['buyer']['address']['addressDetails']['locality']['description'] = \
            "update ei: buyer.address.addressDetails.locality.description"
        payload['buyer']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['buyer']['additionalIdentifiers'][0]['id'] = "update ei buyer.additionalIdentifiers.id"
        payload['buyer']['additionalIdentifiers'][0]['scheme'] = "update ei buyer.additionalIdentifiers.scheme"
        payload['buyer']['additionalIdentifiers'][0]['legalName'] = "update ei buyer.additionalIdentifiers.legalName"
        payload['buyer']['additionalIdentifiers'][0]['uri'] = "update ei buyer.additionalIdentifiers.uri"
        payload['buyer']['contactPoint']['name'] = "update ei: buyer.contactPoint.name"
        payload['buyer']['contactPoint']['email'] = "update ei: buyer.contactPoint.email"
        payload['buyer']['contactPoint']['telephone'] = "update ei: buyer.contactPoint.telephone"
        payload['buyer']['contactPoint']['faxNumber'] = "update ei: buyer.contactPoint.faxNumber"
        payload['buyer']['contactPoint']['url'] = "update ei: buyer.contactPoint.url"
        payload['buyer']['details']['typeOfBuyer'] = f"{random.choice(typeOfBuyer)}"
        payload['buyer']['details']['mainGeneralActivity'] = f"{random.choice(mainGeneralActivity)}"
        payload['buyer']['details']['mainSectoralActivity'] = f"{random.choice(mainSectoralActivity)}"
        return payload

    def update_ei_obligatory_data_model(self, tender_classification_id):
        # Временно так как не пофиксили баг -> нужно раскомментировать del self.payload['tender']['classification']
        # и # del payload['buyer']
        # del payload['tender']['classification']
        # del payload['buyer']
        payload = {
            "tender": {},
            "planning": {},
            "buyer": {}
        }

        payload['tender'].update(self.constructor.ei_tender_object())
        payload['planning'].update(self.constructor.ei_planning_obj())
        payload['buyer'].update(self.constructor.ei_buyer_obj())

        tender_classification_id = None
        category = random.choice(cpv_category)
        if category == "goods":
            tender_classification_id = random.choice(cpv_goods_high_level)
        elif category == "works":
            tender_classification_id = random.choice(cpv_works_high_level)
        elif category == "services":
            tender_classification_id = random.choice(cpv_services_high_level)

        del payload['tender']['description']
        del payload['tender']['items']
        del payload['planning']['rationale']
        del payload['buyer']['identifier']['uri']
        del payload['buyer']['address']['postalCode']
        del payload['buyer']['additionalIdentifiers']
        del payload['buyer']['contactPoint']['faxNumber']
        del payload['buyer']['contactPoint']['url']
        del payload['buyer']['details']

        payload['tender']['title'] = "update ei: tender.title"
        payload['tender']['classification']['id'] = tender_classification_id
        ei_period = Date().expenditure_item_period()
        payload['planning']['budget']['period']['startDate'] = ei_period[0]
        payload['planning']['budget']['period']['endDate'] = ei_period[1]
        payload['buyer']['name'] = "update ei: buyer.name"
        payload['buyer']['identifier']['id'] = "update ei: buyer.identifier.id"
        payload['buyer']['identifier']['scheme'] = "MD-IDNO"
        payload['buyer']['identifier']['legalName'] = "update ei: buyer.identifier.legalName"
        payload['buyer']['address']['streetAddress'] = "update ei: buyer.address.streetAddress"
        payload['buyer']['address']['addressDetails']['country']['id'] = "MD"
        payload['buyer']['address']['addressDetails']['region']['id'] = "3400000"
        payload['buyer']['address']['addressDetails']['locality']['id'] = "3401000"
        payload['buyer']['address']['addressDetails']['locality']['description'] = \
            "update ei: buyer.address.addressDetails.locality.description"
        payload['buyer']['address']['addressDetails']['locality']['scheme'] = "other"
        payload['buyer']['contactPoint']['name'] = "update ei: buyer.contactPoint.name"
        payload['buyer']['contactPoint']['email'] = "update ei: buyer.contactPoint.email"
        payload['buyer']['contactPoint']['telephone'] = "update ei: buyer.contactPoint.telephone"
        return payload

