import copy
import random

from tests.utils.data_of_enum import cpv_category, cpv_goods_high_level, cpv_works_high_level, \
    cpv_services_high_level, typeOfBuyer, mainGeneralActivity, mainSectoralActivity, currency
from tests.utils.date_class import Date
from tests.utils.functions import generate_items_array
from tests.utils.payload_library import PayloadLibrary


class PreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())
        self.ei_period = Date().expenditure_item_period()
        self.currency = f"{random.choice(currency)}"

    def create_ei_full_data_model(self, quantity_of_tender_item_object=1):
        payload = {
            "tender": {},
            "planning": {},
            "buyer": {}
        }

        payload['tender'].update(self.constructor.tender_object())
        payload['planning'].update(self.constructor.planning_obj())
        payload['buyer'].update(self.constructor.buyer_obj())

        del payload['planning']['budget']['id']
        del payload['planning']['budget']['description']
        del payload['planning']['budget']['amount']
        del payload['planning']['budget']['isEuropeanUnionFunded']
        del payload['planning']['budget']['europeanUnionFunding']
        del payload['planning']['budget']['project']
        del payload['planning']['budget']['projectID']
        del payload['planning']['budget']['uri']

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

        payload['planning']['budget']['period']['startDate'] = self.ei_period[0]
        payload['planning']['budget']['period']['endDate'] = self.ei_period[1]
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

        payload['tender'].update(self.constructor.tender_object())
        payload['planning'].update(self.constructor.planning_obj())
        payload['buyer'].update(self.constructor.buyer_obj())

        del payload['planning']['budget']['id']
        del payload['planning']['budget']['description']
        del payload['planning']['budget']['amount']
        del payload['planning']['budget']['isEuropeanUnionFunded']
        del payload['planning']['budget']['europeanUnionFunding']
        del payload['planning']['budget']['project']
        del payload['planning']['budget']['projectID']
        del payload['planning']['budget']['uri']

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
        payload['planning']['budget']['period']['startDate'] = self.ei_period[0]
        payload['planning']['budget']['period']['endDate'] = self.ei_period[1]
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
        payload = {
            "tender": {},
            "planning": {}
        }

        payload['tender'].update(self.constructor.tender_object())
        payload['planning'].update(self.constructor.planning_obj())

        del payload['tender']['classification']
        del payload['planning']['budget']['id']
        del payload['planning']['budget']['description']
        del payload['planning']['budget']['amount']
        del payload['planning']['budget']['isEuropeanUnionFunded']
        del payload['planning']['budget']['europeanUnionFunding']
        del payload['planning']['budget']['project']
        del payload['planning']['budget']['projectID']
        del payload['planning']['budget']['uri']

        payload['tender']['title'] = "update ei: tender.title"
        payload['tender']['description'] = "update ei: tender.description"
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

        payload['planning']['budget']['period']['startDate'] = self.ei_period[0]
        payload['planning']['budget']['period']['endDate'] = self.ei_period[1]
        payload['planning']['rationale'] = "update ei: planning.ratioanle"
        return payload

    def update_ei_obligatory_data_model(self):
        payload = {
            "tender": {},
            "planning": {}
        }

        payload['tender'].update(self.constructor.tender_object())
        payload['planning'].update(self.constructor.planning_obj())

        del payload['tender']['classification']
        del payload['planning']['budget']['id']
        del payload['planning']['budget']['description']
        del payload['planning']['budget']['amount']
        del payload['planning']['budget']['isEuropeanUnionFunded']
        del payload['planning']['budget']['europeanUnionFunding']
        del payload['planning']['budget']['project']
        del payload['planning']['budget']['projectID']
        del payload['planning']['budget']['uri']
        del payload['tender']['description']
        del payload['tender']['items']
        del payload['planning']['rationale']

        payload['tender']['title'] = "update ei: tender.title"
        payload['planning']['budget']['period']['startDate'] = self.ei_period[0]
        payload['planning']['budget']['period']['endDate'] = self.ei_period[1]
        return payload

    def create_fs_full_data_model_own_money(self):
        payload = {
            "tender": {},
            "planning": {},
            "buyer": {}
        }

        payload['tender'].update(self.constructor.procuring_entity_obj())
        payload['planning'].update(self.constructor.planning_obj())
        payload['buyer'].update(self.constructor.buyer_obj())

        payload['buyer']['name'] = "create fs: buyer.name"
        payload['buyer']['identifier']['id'] = "create fs: buyer.identifier.id"
        payload['buyer']['identifier']['scheme'] = "MD-IDNO"
        payload['buyer']['identifier']['legalName'] = "create fs: buyer.identifier.legalName"
        payload['buyer']['identifier']['uri'] = "create fs: buyer.identifier.uri"
        payload['buyer']['address']['streetAddress'] = "create fs: buyer.address.streetAddress"
        payload['buyer']['address']['postalCode'] = "create fs: buyer.address.postalCode"
        payload['buyer']['address']['addressDetails']['country']['id'] = "MD"
        payload['buyer']['address']['addressDetails']['region']['id'] = "1700000"
        payload['buyer']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['buyer']['address']['addressDetails']['locality']['description'] = \
            "create fs: buyer.address.addressDetails.locality.description"
        payload['buyer']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['buyer']['additionalIdentifiers'][0]['id'] = "create fs: buyer.additionalIdentifiers.id"
        payload['buyer']['additionalIdentifiers'][0]['scheme'] = "create fs: buyer.additionalIdentifiers.scheme"
        payload['buyer']['additionalIdentifiers'][0]['legalName'] = "create fs: buyer.additionalIdentifiers.legalName"
        payload['buyer']['additionalIdentifiers'][0]['uri'] = "create fs: buyer.additionalIdentifiers.uri"
        payload['buyer']['contactPoint']['name'] = "create fs: buyer.contactPoint.name"
        payload['buyer']['contactPoint']['email'] = "create fs: buyer.contactPoint.email"
        payload['buyer']['contactPoint']['telephone'] = "create fs: buyer.contactPoint.telephone"
        payload['buyer']['contactPoint']['faxNumber'] = "create fs: buyer.contactPoint.faxNumber"
        payload['buyer']['contactPoint']['url'] = "create fs: buyer.contactPoint.url"
        payload['buyer']['details']['typeOfBuyer'] = f"{random.choice(typeOfBuyer)}"
        payload['buyer']['details']['mainGeneralActivity'] = f"{random.choice(mainGeneralActivity)}"
        payload['buyer']['details']['mainSectoralActivity'] = f"{random.choice(mainSectoralActivity)}"

        payload['tender']['procuringEntity']['name'] = "create fs: procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "create fs: procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "create fs: procuringEntity.identifier.legalName"
        payload['tender']['procuringEntity']['identifier']['uri'] = "create fs: procuringEntity.identifier.uri"
        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "create fs: procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['postalCode'] = "create fs: procuringEntity.address.postalCode"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "create fs: procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['id'] = \
            "create fs: tender.procuringEntity.additionalIdentifiers.id"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['scheme'] = \
            "create fs: tender.procuringEntity.additionalIdentifiers.scheme"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['legalName'] = \
            "create fs: tender.procuringEntity.additionalIdentifiers.legalName"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['uri'] = \
            "create fs: tender.procuringEntity.additionalIdentifiers.uri"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "create fs: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "create fs: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "create fs: tender.procuringEntity.contactPoint.telephone"
        payload['tender']['procuringEntity']['contactPoint']['faxNumber'] = \
            "create fs: tender.procuringEntity.contactPoint.faxNumber"
        payload['tender']['procuringEntity']['contactPoint']['url'] = \
            "create fs: tender.procuringEntity.contactPoint.url"

        payload['planning']['budget']['id'] = "create fs: planning.budget.id"
        payload['planning']['budget']['description'] = "create fs: planning.budget.description"
        payload['planning']['budget']['period']['startDate'] = self.ei_period[0]
        payload['planning']['budget']['period']['endDate'] = self.ei_period[1]
        payload['planning']['budget']['amount']['amount'] = 88889.89
        payload['planning']['budget']['amount']['currency'] = self.currency
        payload['planning']['budget']['isEuropeanUnionFunded'] = True
        payload['planning']['budget']['europeanUnionFunding']['projectName'] = \
            "create fs: planning.budget.europeanUnionFunding.projectName"
        payload['planning']['budget']['europeanUnionFunding']['projectIdentifier'] = \
            "create fs: planning.budget.europeanUnionFunding.projectIdentifier"
        payload['planning']['budget']['europeanUnionFunding']['uri'] = \
            "create fs: planning.budget.europeanUnionFunding.uri"
        payload['planning']['budget']['project'] = "create fs: planning.budget.project"
        payload['planning']['budget']['projectID'] = "create fs: planning.budget.projectID"
        payload['planning']['budget']['uri'] = "create fs: planning.budget.uri"
        payload['planning']['rationale'] = "create fs: planning.rationale"
        return payload

    def create_fs_obligatory_data_model_own_money(self):
        payload = {
            "tender": {},
            "planning": {},
            "buyer": {}
        }

        payload['tender'].update(self.constructor.procuring_entity_obj())
        payload['planning'].update(self.constructor.planning_obj())
        payload['buyer'].update(self.constructor.buyer_obj())

        del payload['buyer']['identifier']['uri']
        del payload['buyer']['address']['postalCode']
        del payload['buyer']['additionalIdentifiers']
        del payload['buyer']['contactPoint']['faxNumber']
        del payload['buyer']['contactPoint']['url']
        del payload['buyer']['details']
        del payload['tender']['procuringEntity']['identifier']['uri']
        del payload['tender']['procuringEntity']['additionalIdentifiers']
        del payload['tender']['procuringEntity']['address']['postalCode']
        del payload['tender']['procuringEntity']['contactPoint']['faxNumber']
        del payload['tender']['procuringEntity']['contactPoint']['url']
        del payload['planning']['budget']['id']
        del payload['planning']['budget']['description']
        del payload['planning']['budget']['europeanUnionFunding']
        del payload['planning']['budget']['project']
        del payload['planning']['budget']['projectID']
        del payload['planning']['budget']['uri']
        del payload['planning']['rationale']

        payload['buyer']['name'] = "create fs: buyer.name"
        payload['buyer']['identifier']['id'] = "create fs: buyer.identifier.id"
        payload['buyer']['identifier']['scheme'] = "MD-IDNO"
        payload['buyer']['identifier']['legalName'] = "create fs: buyer.identifier.legalName"
        payload['buyer']['address']['streetAddress'] = "create fs: buyer.address.streetAddress"
        payload['buyer']['address']['addressDetails']['country']['id'] = "MD"
        payload['buyer']['address']['addressDetails']['region']['id'] = "1700000"
        payload['buyer']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['buyer']['address']['addressDetails']['locality']['description'] = \
            "create fs: buyer.address.addressDetails.locality.description"
        payload['buyer']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['buyer']['contactPoint']['name'] = "create fs: buyer.contactPoint.name"
        payload['buyer']['contactPoint']['email'] = "create fs: buyer.contactPoint.email"
        payload['buyer']['contactPoint']['telephone'] = "create fs: buyer.contactPoint.telephone"

        payload['tender']['procuringEntity']['name'] = "create fs: procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "create fs: procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "create fs: procuringEntity.identifier.legalName"

        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "create fs: procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "create fs: procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "create fs: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "create fs: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "create fs: tender.procuringEntity.contactPoint.telephone"

        payload['planning']['budget']['period']['startDate'] = self.ei_period[0]
        payload['planning']['budget']['period']['endDate'] = self.ei_period[1]
        payload['planning']['budget']['amount']['amount'] = 88889.89
        payload['planning']['budget']['amount']['currency'] = self.currency
        payload['planning']['budget']['isEuropeanUnionFunded'] = False
        return payload

    def create_fs_full_data_model_treasury_money(self):
        payload = {
            "tender": {},
            "planning": {}
        }

        payload['tender'].update(self.constructor.procuring_entity_obj())
        payload['planning'].update(self.constructor.planning_obj())

        payload['tender']['procuringEntity']['name'] = "create fs: procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "create fs: procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "create fs: procuringEntity.identifier.legalName"
        payload['tender']['procuringEntity']['identifier']['uri'] = "create fs: procuringEntity.identifier.uri"
        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "create fs: procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['postalCode'] = "create fs: procuringEntity.address.postalCode"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "create fs: procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['id'] = \
            "create fs: tender.procuringEntity.additionalIdentifiers.id"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['scheme'] = \
            "create fs: tender.procuringEntity.additionalIdentifiers.scheme"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['legalName'] = \
            "create fs: tender.procuringEntity.additionalIdentifiers.legalName"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['uri'] = \
            "create fs: tender.procuringEntity.additionalIdentifiers.uri"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "create fs: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "create fs: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "create fs: tender.procuringEntity.contactPoint.telephone"
        payload['tender']['procuringEntity']['contactPoint']['faxNumber'] = \
            "create fs: tender.procuringEntity.contactPoint.faxNumber"
        payload['tender']['procuringEntity']['contactPoint']['url'] = \
            "create fs: tender.procuringEntity.contactPoint.url"

        payload['planning']['budget']['id'] = "create fs: planning.budget.id"
        payload['planning']['budget']['description'] = "create fs: planning.budget.description"
        payload['planning']['budget']['period']['startDate'] = self.ei_period[0]
        payload['planning']['budget']['period']['endDate'] = self.ei_period[1]
        payload['planning']['budget']['amount']['amount'] = 88889.89
        payload['planning']['budget']['amount']['currency'] = self.currency
        payload['planning']['budget']['isEuropeanUnionFunded'] = True
        payload['planning']['budget']['europeanUnionFunding']['projectName'] = \
            "create fs: planning.budget.europeanUnionFunding.projectName"
        payload['planning']['budget']['europeanUnionFunding']['projectIdentifier'] = \
            "create fs: planning.budget.europeanUnionFunding.projectIdentifier"
        payload['planning']['budget']['europeanUnionFunding']['uri'] = \
            "create fs: planning.budget.europeanUnionFunding.uri"
        payload['planning']['budget']['project'] = "create fs: planning.budget.project"
        payload['planning']['budget']['projectID'] = "create fs: planning.budget.projectID"
        payload['planning']['budget']['uri'] = "create fs: planning.budget.uri"
        payload['planning']['rationale'] = "create fs: planning.rationale"
        return payload

    def create_fs_obligatory_data_model_treasury_money(self):
        payload = {
            "tender": {},
            "planning": {}
        }

        payload['tender'].update(self.constructor.procuring_entity_obj())
        payload['planning'].update(self.constructor.planning_obj())

        del payload['tender']['procuringEntity']['identifier']['uri']
        del payload['tender']['procuringEntity']['address']['postalCode']
        del payload['tender']['procuringEntity']['additionalIdentifiers']
        del payload['tender']['procuringEntity']['contactPoint']['faxNumber']
        del payload['tender']['procuringEntity']['contactPoint']['url']
        del payload['planning']['budget']['id']
        del payload['planning']['budget']['description']
        del payload['planning']['budget']['europeanUnionFunding']
        del payload['planning']['budget']['project']
        del payload['planning']['budget']['projectID']
        del payload['planning']['budget']['uri']
        del payload['planning']['rationale']

        payload['tender']['procuringEntity']['name'] = "create fs: procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "create fs: procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "create fs: procuringEntity.identifier.legalName"
        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "create fs: procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "create fs: procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "create fs: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "create fs: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "create fs: tender.procuringEntity.contactPoint.telephone"
        payload['planning']['budget']['period']['startDate'] = self.ei_period[0]
        payload['planning']['budget']['period']['endDate'] = self.ei_period[1]
        payload['planning']['budget']['amount']['amount'] = 88889.89
        payload['planning']['budget']['amount']['currency'] = self.currency
        payload['planning']['budget']['isEuropeanUnionFunded'] = False
        return payload

    def update_fs_obligatory_data_model_treasury_money(self):
        payload = {
            "tender": {},
            "planning": {}
        }

        payload['tender'].update(self.constructor.tender_object())
        payload['planning'].update(self.constructor.planning_obj())

        del payload['planning']['budget']['id']
        del payload['planning']['budget']['description']
        del payload['planning']['budget']['europeanUnionFunding']
        del payload['planning']['budget']['project']
        del payload['planning']['budget']['projectID']
        del payload['planning']['budget']['uri']
        del payload['planning']['rationale']

        new_period = Date().expenditure_item_period(end=80)
        payload['planning']['budget']['period']['startDate'] = new_period[0]
        payload['planning']['budget']['period']['endDate'] = new_period[1]
        payload['planning']['budget']['amount']['amount'] = 11119.89
        payload['planning']['budget']['amount']['currency'] = self.currency
        payload['planning']['budget']['isEuropeanUnionFunded'] = False
        return payload

    def update_fs_full_data_model_treasury_money(self):
        payload = {
            "tender": {},
            "planning": {}
        }

        new_period = Date().expenditure_item_period(end=80)
        payload['tender'].update(self.constructor.procuring_entity_obj())
        payload['planning'].update(self.constructor.planning_obj())

        payload['tender']['procuringEntity']['name'] = "update fs: procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "update fs: procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "create fs: procuringEntity.identifier.legalName"
        payload['tender']['procuringEntity']['identifier']['uri'] = "update fs: procuringEntity.identifier.uri"
        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "create fs: procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['postalCode'] = "update fs: procuringEntity.address.postalCode"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "3400000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "3401000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "other"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "update fs: procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['id'] = \
            "update fs: tender.procuringEntity.additionalIdentifiers.id"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['scheme'] = \
            "update fs: tender.procuringEntity.additionalIdentifiers.scheme"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['legalName'] = \
            "update fs: tender.procuringEntity.additionalIdentifiers.legalName"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['uri'] = \
            "update fs: tender.procuringEntity.additionalIdentifiers.uri"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "update fs: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "update fs: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "update fs: tender.procuringEntity.contactPoint.telephone"
        payload['tender']['procuringEntity']['contactPoint']['faxNumber'] = \
            "update fs: tender.procuringEntity.contactPoint.faxNumber"
        payload['tender']['procuringEntity']['contactPoint']['url'] = \
            "update fs: tender.procuringEntity.contactPoint.url"

        payload['planning']['budget']['id'] = "update fs: planning.budget.id"
        payload['planning']['budget']['description'] = "update fs: planning.budget.description"
        payload['planning']['budget']['period']['startDate'] = new_period[0]
        payload['planning']['budget']['period']['endDate'] = new_period[1]
        payload['planning']['budget']['amount']['amount'] = 11119.89
        payload['planning']['budget']['amount']['currency'] = self.currency
        payload['planning']['budget']['isEuropeanUnionFunded'] = True
        payload['planning']['budget']['europeanUnionFunding']['projectName'] = \
            "update fs: planning.budget.europeanUnionFunding.projectName"
        payload['planning']['budget']['europeanUnionFunding']['projectIdentifier'] = \
            "update fs: planning.budget.europeanUnionFunding.projectIdentifier"
        payload['planning']['budget']['europeanUnionFunding']['uri'] = \
            "update fs: planning.budget.europeanUnionFunding.uri"
        payload['planning']['budget']['project'] = "update fs: planning.budget.project"
        payload['planning']['budget']['projectID'] = "update fs: planning.budget.projectID"
        payload['planning']['budget']['uri'] = "update fs: planning.budget.uri"
        payload['planning']['rationale'] = "update fs: planning.rationale"
        return payload

    def update_fs_obligatory_data_model_own_money(self):
        payload = {
            "planning": {},
            "buyer": {}
        }

        new_period = Date().expenditure_item_period(end=80)

        payload['planning'].update(self.constructor.planning_obj())
        payload['buyer'].update(self.constructor.buyer_obj())

        del payload['buyer']['identifier']['uri']
        del payload['buyer']['address']['postalCode']
        del payload['buyer']['additionalIdentifiers']
        del payload['buyer']['contactPoint']['faxNumber']
        del payload['buyer']['contactPoint']['url']
        del payload['buyer']['details']
        del payload['planning']['budget']['id']
        del payload['planning']['budget']['description']
        del payload['planning']['budget']['europeanUnionFunding']
        del payload['planning']['budget']['project']
        del payload['planning']['budget']['projectID']
        del payload['planning']['budget']['uri']
        del payload['planning']['rationale']

        payload['buyer']['name'] = "update fs: buyer.name"
        payload['buyer']['identifier']['id'] = "update fs: buyer.identifier.id"
        payload['buyer']['identifier']['scheme'] = "MD-IDNO"
        payload['buyer']['identifier']['legalName'] = "update fs: buyer.identifier.legalName"
        payload['buyer']['address']['streetAddress'] = "update fs: buyer.address.streetAddress"
        payload['buyer']['address']['addressDetails']['country']['id'] = "MD"
        payload['buyer']['address']['addressDetails']['region']['id'] = "3400000"
        payload['buyer']['address']['addressDetails']['locality']['id'] = "3401000"
        payload['buyer']['address']['addressDetails']['locality']['description'] = \
            "update fs: buyer.address.addressDetails.locality.description"
        payload['buyer']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['buyer']['contactPoint']['name'] = "update fs: buyer.contactPoint.name"
        payload['buyer']['contactPoint']['email'] = "update fs: buyer.contactPoint.email"
        payload['buyer']['contactPoint']['telephone'] = "update fs: buyer.contactPoint.telephone"

        payload['planning']['budget']['period']['startDate'] = new_period[0]
        payload['planning']['budget']['period']['endDate'] = new_period[1]
        payload['planning']['budget']['amount']['amount'] = 11119.89
        payload['planning']['budget']['amount']['currency'] = self.currency
        payload['planning']['budget']['isEuropeanUnionFunded'] = False
        return payload

    def update_fs_full_data_model_own_money(self):
        payload = {
            "tender": {},
            "planning": {},
            "buyer": {}
        }

        new_period = Date().expenditure_item_period(end=80)

        payload['tender'].update(self.constructor.procuring_entity_obj())
        payload['planning'].update(self.constructor.planning_obj())
        payload['buyer'].update(self.constructor.buyer_obj())

        payload['buyer']['name'] = "update fs: buyer.name"
        payload['buyer']['identifier']['id'] = "update fs: buyer.identifier.id"
        payload['buyer']['identifier']['scheme'] = "MD-IDNO"
        payload['buyer']['identifier']['legalName'] = "update fs: buyer.identifier.legalName"
        payload['buyer']['identifier']['uri'] = "update fs: buyer.identifier.uri"
        payload['buyer']['address']['streetAddress'] = "update fs: buyer.address.streetAddress"
        payload['buyer']['address']['postalCode'] = "update fs: buyer.address.postalCode"
        payload['buyer']['address']['addressDetails']['country']['id'] = "MD"
        payload['buyer']['address']['addressDetails']['region']['id'] = "3400000"
        payload['buyer']['address']['addressDetails']['locality']['id'] = "3401000"
        payload['buyer']['address']['addressDetails']['locality']['description'] = \
            "create fs: buyer.address.addressDetails.locality.description"
        payload['buyer']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['buyer']['additionalIdentifiers'][0]['id'] = "update fs: buyer.additionalIdentifiers.id"
        payload['buyer']['additionalIdentifiers'][0]['scheme'] = "update fs: buyer.additionalIdentifiers.scheme"
        payload['buyer']['additionalIdentifiers'][0]['legalName'] = "update fs: buyer.additionalIdentifiers.legalName"
        payload['buyer']['additionalIdentifiers'][0]['uri'] = "update fs: buyer.additionalIdentifiers.uri"
        payload['buyer']['contactPoint']['name'] = "update fs: buyer.contactPoint.name"
        payload['buyer']['contactPoint']['email'] = "updatefs: buyer.contactPoint.email"
        payload['buyer']['contactPoint']['telephone'] = "update fs: buyer.contactPoint.telephone"
        payload['buyer']['contactPoint']['faxNumber'] = "update fs: buyer.contactPoint.faxNumber"
        payload['buyer']['contactPoint']['url'] = "update fs: buyer.contactPoint.url"
        payload['buyer']['details']['typeOfBuyer'] = f"{random.choice(typeOfBuyer)}"
        payload['buyer']['details']['mainGeneralActivity'] = f"{random.choice(mainGeneralActivity)}"
        payload['buyer']['details']['mainSectoralActivity'] = f"{random.choice(mainSectoralActivity)}"

        payload['tender']['procuringEntity']['name'] = "update fs: procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "update fs: procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "update fs: procuringEntity.identifier.legalName"
        payload['tender']['procuringEntity']['identifier']['uri'] = "update fs: procuringEntity.identifier.uri"
        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "update fs: procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['postalCode'] = "update fs: procuringEntity.address.postalCode"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "3400000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "3401000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "update fs: procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['id'] = \
            "update fs: tender.procuringEntity.additionalIdentifiers.id"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['scheme'] = \
            "update fs: tender.procuringEntity.additionalIdentifiers.scheme"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['legalName'] = \
            "update fs: tender.procuringEntity.additionalIdentifiers.legalName"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['uri'] = \
            "create fs: tender.procuringEntity.additionalIdentifiers.uri"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "update fs: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "update fs: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "update fs: tender.procuringEntity.contactPoint.telephone"
        payload['tender']['procuringEntity']['contactPoint']['faxNumber'] = \
            "update fs: tender.procuringEntity.contactPoint.faxNumber"
        payload['tender']['procuringEntity']['contactPoint']['url'] = \
            "update fs: tender.procuringEntity.contactPoint.url"

        payload['planning']['budget']['id'] = "update fs: planning.budget.id"
        payload['planning']['budget']['description'] = "update fs: planning.budget.description"
        payload['planning']['budget']['period']['startDate'] = new_period[0]
        payload['planning']['budget']['period']['endDate'] = new_period[1]
        payload['planning']['budget']['amount']['amount'] = 11119.89
        payload['planning']['budget']['amount']['currency'] = self.currency
        payload['planning']['budget']['isEuropeanUnionFunded'] = True
        payload['planning']['budget']['europeanUnionFunding']['projectName'] = \
            "update fs: planning.budget.europeanUnionFunding.projectName"
        payload['planning']['budget']['europeanUnionFunding']['projectIdentifier'] = \
            "update fs: planning.budget.europeanUnionFunding.projectIdentifier"
        payload['planning']['budget']['europeanUnionFunding']['uri'] = \
            "update fs: planning.budget.europeanUnionFunding.uri"
        payload['planning']['budget']['project'] = "update fs: planning.budget.project"
        payload['planning']['budget']['projectID'] = "update fs: planning.budget.projectID"
        payload['planning']['budget']['uri'] = "update fs: planning.budget.uri"
        payload['planning']['rationale'] = "update fs: planning.rationale"
        return payload
