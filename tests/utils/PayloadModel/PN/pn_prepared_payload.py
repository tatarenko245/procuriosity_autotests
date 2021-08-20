import copy
import json
import os
import random

from tests.conftest import GlobalClassCreateEi, GlobalClassCreateFs
from tests.utils.PayloadModel.PN.pn_payload_library import PayloadLibrary

from tests.utils.data_of_enum import legalBasis, cpv_goods_low_level_03, cpv_goods_low_level_1, cpv_goods_low_level_2, \
    cpv_goods_low_level_3, cpv_goods_low_level_44, cpv_goods_low_level_48, cpv_works_low_level_45, \
    cpv_services_low_level_5, cpv_services_low_level_6, cpv_services_low_level_7, cpv_services_low_level_8, \
    cpv_services_low_level_92, cpv_services_low_level_98, documentType
from tests.utils.date_class import Date
from tests.utils.functions import generate_items_array, generate_lots_array
from tests.utils.iStorage import Document


class PnPreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())
        self.pn_period = Date().planning_notice_period()
        document_one = Document("API.pdf")
        self.document_one_was_uploaded = document_one.uploading_document()

    def create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs(self):
        payload = {
            "tender": {},
            "planning": {}
        }

        payload['tender'].update(self.constructor.tender_object())
        payload['planning'].update(self.constructor.planning_object())
        payload['planning']['budget']['budgetBreakdown'] = [{}]
        payload['planning']['budget']['budgetBreakdown'][0].update(
            self.constructor.planning_budget_budget_breakdown_object())

        del payload['tender']['lots']
        del payload['tender']['items']
        del payload['tender']['procuringEntity']['identifier']['uri']
        del payload['tender']['procuringEntity']['additionalIdentifiers']
        del payload['tender']['procuringEntity']['address']['postalCode']
        del payload['tender']['procuringEntity']['contactPoint']['faxNumber']
        del payload['tender']['procuringEntity']['contactPoint']['url']
        del payload['planning']['rationale']
        del payload['planning']['budget']['description']

        payload['tender']['title'] = "create pn: tender.title"
        payload['tender']['description'] = "create pn: tender.description"
        payload['tender']['legalBasis'] = f"{random.choice(legalBasis)}"
        payload['tender']['tenderPeriod']['startDate'] = self.pn_period
        payload['tender']['procuringEntity']['name'] = "create pn: tender.procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "create pn: tender.procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "create pn: tender.procuringEntity.identifier.legalName"
        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "create pn: tender.procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "create pn: tender.procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "create pn: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "create pn: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "create pn: tender.procuringEntity.contactPoint.telephone"
        payload['planning']['budget']['budgetBreakdown'][0]['id'] = GlobalClassCreateFs.fs_id
        payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
        payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']

        return payload

    def create_pn_obligatory_data_model_with_lots_and_items_obligatory_based_on_one_fs(self):
        payload = {
            "tender": {},
            "planning": {}
        }

        payload['tender'].update(self.constructor.tender_object())
        payload['planning'].update(self.constructor.planning_object())
        payload['planning']['budget']['budgetBreakdown'] = [{}]
        payload['planning']['budget']['budgetBreakdown'][0].update(
            self.constructor.planning_budget_budget_breakdown_object())

        del payload['tender']['items'][0]['internalId']
        del payload['tender']['items'][0]['additionalClassifications']
        del payload['tender']['lots'][0]['internalId']
        del payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode']
        del payload['tender']['lots'][0]['placeOfPerformance']['description']
        del payload['tender']['procuringEntity']['identifier']['uri']
        del payload['tender']['procuringEntity']['additionalIdentifiers']
        del payload['tender']['procuringEntity']['address']['postalCode']
        del payload['tender']['procuringEntity']['contactPoint']['faxNumber']
        del payload['tender']['procuringEntity']['contactPoint']['url']

        contact_period = Date().contact_period()
        try:
            item_classification_id = None
            tender_classification_id = \
                GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['classification']['id']

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
        except KeyError:
            raise KeyError("Check tender_classification_id")

        payload['tender']['title'] = "create pn: tender.title"
        payload['tender']['description'] = "create pn: tender.description"
        payload['tender']['legalBasis'] = f"{random.choice(legalBasis)}"
        payload['tender']['tenderPeriod']['startDate'] = self.pn_period
        payload['tender']['lots'][0]['id'] = "0"
        payload['tender']['lots'][0]['title'] = "create pn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "create pn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 2000.01
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "create pn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "create pn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"
        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['quantity'] = 50
        payload['tender']['items'][0]['unit']['id'] = "10"
        payload['tender']['items'][0]['description'] = "create pn: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['procuringEntity']['name'] = "create pn: tender.procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "create pn: tender.procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "create pn: tender.procuringEntity.identifier.legalName"
        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "create pn: tender.procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "create pn: tender.procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "create pn: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "create pn: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "create pn: tender.procuringEntity.contactPoint.telephone"
        payload['planning']['budget']['description'] = "create pn: planning.description.description"
        payload['planning']['budget']['budgetBreakdown'][0]['id'] = GlobalClassCreateFs.fs_id
        payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
        payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['planning']['rationale'] = "create pn: planning.rationale"
        return payload

    def create_pn_full_data_model_with_lots_and_items_full_based_on_one_fs(self, quantity_of_lot_object=1,
                                                                           quantity_of_item_object=1):
        payload = {
            "tender": {},
            "planning": {}
        }

        payload['tender'].update(self.constructor.tender_object())
        payload['tender']['procuringEntity']['additionalIdentifiers'] = [{}]
        payload['tender']['procuringEntity']['additionalIdentifiers'][0].update(
            self.constructor.buyer_additional_identifiers_object())
        payload['tender']['lots'] = [{}]
        payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
        payload['tender']['items'] = [{}]
        payload['tender']['items'][0].update(self.constructor.tender_item_object())
        payload['tender']['items'][0]['additionalClassifications'] = [{}]
        payload['tender']['items'][0]['additionalClassifications'][0].update(
            self.constructor.tender_item_additional_classifications_object())
        payload['tender']['documents'] = [{}]
        payload['tender']['documents'][0].update(self.constructor.tender_document_object())
        payload['planning'].update(self.constructor.planning_object())
        payload['planning']['budget']['budgetBreakdown'] = [{}]
        payload['planning']['budget']['budgetBreakdown'][0].update(
            self.constructor.planning_budget_budget_breakdown_object())

        contact_period = Date().contact_period()
        try:
            item_classification_id = None
            tender_classification_id = \
                GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['classification']['id']

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
        except KeyError:
            raise KeyError("Check tender_classification_id")

        payload['tender']['title'] = "create pn: tender.title"
        payload['tender']['description'] = "create pn: tender.description"
        payload['tender']['legalBasis'] = f"{random.choice(legalBasis)}"
        payload['tender']['procurementMethodRationale'] = "create pn: tender.procurementMethodRationale"
        payload['tender']['procurementMethodAdditionalInfo'] = "create pn: tender.procurementMethodAdditionalInfo"
        payload['tender']['tenderPeriod']['startDate'] = self.pn_period
        payload['tender']['lots'][0]['id'] = "0"
        payload['tender']['lots'][0]['internalId'] = "create pn: tender.lots.internalId"
        payload['tender']['lots'][0]['title'] = "create pn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "create pn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 2000.01
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "create pn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode'] = \
            "create pn: tender.lots.placeOfPerformance.address.postalCode"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "create pn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"
        payload['tender']['lots'][0]['placeOfPerformance']['description'] = \
            "create pn: tender.lots.placeOfPerformance.description"
        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lot_object,
            lot_object=payload['tender']['lots'][0])
        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['internalId'] = "create pn: tender.items.internalId"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['additionalClassifications'][0]['id'] = "AA12-4"
        payload['tender']['items'][0]['quantity'] = 50
        payload['tender']['items'][0]['unit']['id'] = "10"
        payload['tender']['items'][0]['description'] = "create pn: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_item_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])
        payload['tender']['procuringEntity']['name'] = "create pn: tender.procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "create pn: tender.procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "create pn: tender.procuringEntity.identifier.legalName"
        payload['tender']['procuringEntity']['identifier']['uri'] = \
            "create pn: tender.procuringEntity.identifier.uri"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['id'] = \
            "create pn: tender.procuringEntity.additionalIdentifiers.id"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['scheme'] = \
            "create pn: tender.procuringEntity.additionalIdentifiers.scheme"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['legalName'] = \
            "create pn: tender.procuringEntity.additionalIdentifiers.legalName"
        payload['tender']['procuringEntity']['additionalIdentifiers'][0]['uri'] = \
            "create pn: tender.procuringEntity.additionalIdentifiers.uri"
        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "create pn: tender.procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['postalCode'] = \
            "create pn: tender.procuringEntity.address.postalCode"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "create pn: tender.procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "create pn: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "create pn: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "create pn: tender.procuringEntity.contactPoint.telephone"
        payload['tender']['procuringEntity']['contactPoint']['faxNumber'] = \
            "create pn: tender.procuringEntity.contactPoint.faxNumber"
        payload['tender']['procuringEntity']['contactPoint']['url'] = \
            "create pn: tender.procuringEntity.contactPoint.url"
        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "create pn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "create pn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]
        payload['planning']['budget']['description'] = "create pn: planning.description.description"
        payload['planning']['budget']['budgetBreakdown'][0]['id'] = GlobalClassCreateFs.fs_id
        payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
        payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['planning']['rationale'] = "create pn: planning.rationale"

        return payload

    def create_pn_obligatory_data_model_with_one_lots_and_items_based_on_one_fs(self, quantity_of_lot_object=1,
                                                                                quantity_of_item_object=1):
        payload = {
            "tender": {},
            "planning": {}
        }

        payload['tender'].update(self.constructor.tender_object())
        payload['tender']['lots'] = [{}]
        payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
        payload['tender']['items'] = [{}]
        payload['tender']['items'][0].update(self.constructor.tender_item_object())
        payload['tender']['documents'] = [{}]
        payload['tender']['documents'][0].update(self.constructor.tender_document_object())
        payload['planning'].update(self.constructor.planning_object())
        payload['planning']['budget']['budgetBreakdown'] = [{}]
        payload['planning']['budget']['budgetBreakdown'][0].update(
            self.constructor.planning_budget_budget_breakdown_object())

        del payload['planning']['rationale']
        del payload['planning']['budget']['description']
        del payload['tender']['procurementMethodRationale']
        del payload['tender']['procurementMethodAdditionalInfo']
        del payload['tender']['procuringEntity']['additionalIdentifiers']
        del payload['tender']['procuringEntity']['address']['postalCode']
        del payload['tender']['procuringEntity']['contactPoint']['faxNumber']
        del payload['tender']['procuringEntity']['contactPoint']['url']
        del payload['tender']['lots'][0]['internalId']
        del payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode']
        del payload['tender']['lots'][0]['placeOfPerformance']['description']
        del payload['tender']['items'][0]['internalId']
        del payload['tender']['items'][0]['additionalClassifications']
        del payload['tender']['documents']

        contact_period = Date().contact_period()
        try:
            item_classification_id = None
            tender_classification_id = \
                GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['classification']['id']

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
        except KeyError:
            raise KeyError("Check tender_classification_id")

        payload['tender']['title'] = "create pn: tender.title"
        payload['tender']['description'] = "create pn: tender.description"
        payload['tender']['legalBasis'] = f"{random.choice(legalBasis)}"
        payload['tender']['tenderPeriod']['startDate'] = self.pn_period
        payload['tender']['lots'][0]['id'] = "0"
        payload['tender']['lots'][0]['title'] = "create pn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "create pn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 2000.01
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "create pn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "create pn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"
        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lot_object,
            lot_object=payload['tender']['lots'][0])
        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['quantity'] = 50
        payload['tender']['items'][0]['unit']['id'] = "10"
        payload['tender']['items'][0]['description'] = "create pn: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_item_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])
        payload['tender']['procuringEntity']['name'] = "create pn: tender.procuringEntity.name"
        payload['tender']['procuringEntity']['identifier']['id'] = "create pn: tender.procuringEntity.identifier.id"
        payload['tender']['procuringEntity']['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['identifier']['legalName'] = \
            "create pn: tender.procuringEntity.identifier.legalName"
        payload['tender']['procuringEntity']['identifier']['uri'] = \
            "create pn: tender.procuringEntity.identifier.uri"
        payload['tender']['procuringEntity']['address']['streetAddress'] = \
            "create pn: tender.procuringEntity.address.streetAddress"
        payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'] = "CUATM"
        payload['tender']['procuringEntity']['address']['addressDetails']['locality']['description'] = \
            "create pn: tender.procuringEntity.address.addressDetails.locality.description"
        payload['tender']['procuringEntity']['contactPoint']['name'] = \
            "create pn: tender.procuringEntity.contactPoint.name"
        payload['tender']['procuringEntity']['contactPoint']['email'] = \
            "create pn: tender.procuringEntity.contactPoint.email"
        payload['tender']['procuringEntity']['contactPoint']['telephone'] = \
            "create pn: tender.procuringEntity.contactPoint.telephone"
        payload['planning']['budget']['budgetBreakdown'][0]['id'] = GlobalClassCreateFs.fs_id
        payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
        payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']

        return payload
