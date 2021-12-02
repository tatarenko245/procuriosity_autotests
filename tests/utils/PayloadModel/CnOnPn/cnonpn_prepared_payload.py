import copy
import random

from tests.conftest import GlobalClassCreateEi, GlobalClassCreateFs, GlobalClassCreatePn, GlobalClassMetadata
from tests.utils.PayloadModel.CnOnPn.cnonpn_payload_library import PayloadLibrary

from tests.utils.data_of_enum import cpv_goods_low_level_03, cpv_goods_low_level_1, cpv_goods_low_level_2, \
    cpv_goods_low_level_3, cpv_goods_low_level_44, cpv_goods_low_level_48, cpv_works_low_level_45, \
    cpv_services_low_level_5, cpv_services_low_level_6, cpv_services_low_level_7, cpv_services_low_level_8, \
    cpv_services_low_level_92, cpv_services_low_level_98, documentType
from tests.utils.date_class import Date
from tests.utils.functions import generate_items_array, generate_lots_array, set_permanent_id, \
    generate_criteria_array, set_eligibility_evidences_unique_temporary_id, \
    set_criteria_array_unique_temporary_id, generate_conversions_array, set_conversions_unique_temporary_id
from tests.utils.iStorage import Document
from tests.utils.services.e_mdm_service import MdmService


class CnOnPnPreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())
        document_one = Document("API.pdf")
        self.document_one_was_uploaded = document_one.uploading_document()
        self.document_two_was_uploaded = document_one.uploading_document()
        self.standard_criteria = MdmService(host=GlobalClassMetadata.host_for_services).get_standard_criteria(
            country=GlobalClassMetadata.country,
            language=GlobalClassMetadata.language)
        self.contact_period = Date().contact_period()
        self.duration_period = Date().duration_period()
        self.business_function_date = Date().old_period()[0]

    def create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv_auction(
            self, enquiry_interval, tender_interval, quantity_of_lots_object, quantity_of_items_object,
            based_stage_release, need_to_set_permanent_id_for_lots_array=False,
            need_to_set_permanent_id_for_items_array=False, need_to_set_permanent_id_for_documents_array=False):

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

        payload = {
            "planning": {},
            "tender": {}
        }

        try:
            """
            Update payload dictionary.
            """
            payload['planning'].update(self.constructor.planning_object())
            payload['tender'].update(self.constructor.tender_object())
            payload['tender']['procuringEntity']['persones'].append(self.constructor.tender_procuring_entity_persones())
            payload['tender']['procuringEntity']['persones'][0]['businessFunctions'].append(
                self.constructor.tender_procuring_entity_persones_business_functions_object())
            payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]['documents'].append(
                self.constructor.tender_procuring_entity_persones_business_document_object()
            )
            for ql in range(quantity_of_lots_object):
                payload['tender']['lots'].append(self.constructor.tender_lots_object())
                payload['tender']['lots'][ql]['options'] = [{}, {}]
                payload['tender']['lots'][ql]['options'][0].update(self.constructor.tender_lots_option_object())
                payload['tender']['lots'][ql]['options'][1].update(self.constructor.tender_lots_option_object())
                payload['tender']['lots'][ql]['recurrence']['dates'] = [{}, {}]
                payload['tender']['lots'][ql]['recurrence']['dates'][0].update(
                    self.constructor.tender_lots_recurrence_dates_object())
                payload['tender']['lots'][ql]['recurrence']['dates'][1].update(
                    self.constructor.tender_lots_recurrence_dates_object())

                payload['tender']['lots'][ql]['id'] = "create cnonpn: tender.lots.id"
                payload['tender']['lots'][ql]['internalId'] = "create cnonpn: tender.lots.internalId"
                payload['tender']['lots'][ql]['title'] = "create cnonpn: tender.lots.title"
                payload['tender']['lots'][ql]['description'] = "create cnonpn: tender.lots.description"
                payload['tender']['lots'][ql]['value']['amount'] = 4000.05
                payload['tender']['lots'][ql]['value']['currency'] = \
                    GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
                payload['tender']['lots'][ql]['contractPeriod']['startDate'] = self.contact_period[0]
                payload['tender']['lots'][ql]['contractPeriod']['endDate'] = self.contact_period[1]
                payload['tender']['lots'][ql]['placeOfPerformance']['address']['streetAddress'] = \
                    "create cnonpn: tender.lots.placeOfPerformance.address.streetAddress"
                payload['tender']['lots'][ql]['placeOfPerformance']['address']['postalCode'] = \
                    "create cnonpn: tender.lots.placeOfPerformance.address.postalCode"
                payload['tender']['lots'][ql]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
                payload['tender']['lots'][ql]['placeOfPerformance']['address']['addressDetails']['region'][
                    'id'] = "1700000"
                payload['tender']['lots'][ql]['placeOfPerformance']['address']['addressDetails']['locality'][
                    'id'] = "1701000"
                payload['tender']['lots'][ql]['placeOfPerformance']['address']['addressDetails']['locality'][
                    'description'] = \
                    "create cnonpn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
                payload['tender']['lots'][ql]['placeOfPerformance']['address']['addressDetails']['locality'][
                    'scheme'] = "CUATM"
                payload['tender']['lots'][ql]['placeOfPerformance']['description'] = \
                    "create cnonpn: tender.lots.placeOfPerformance.description"
                payload['tender']['lots'][ql]['hasOptions'] = True
                payload['tender']['lots'][ql]['options'][0][
                    'description'] = "create CNonPN: tender.lots[0].options.description"
                payload['tender']['lots'][ql]['options'][0]['period']['durationInDays'] = 180
                payload['tender']['lots'][ql]['options'][0]['period']['startDate'] = self.duration_period[0]
                payload['tender']['lots'][ql]['options'][0]['period']['endDate'] = self.duration_period[1]
                payload['tender']['lots'][ql]['options'][0]['period']['maxExtentDate'] = self.duration_period[1]
                payload['tender']['lots'][ql]['options'][1][
                    'description'] = "create CNonPN: tender.lots[0].options.description"
                payload['tender']['lots'][ql]['options'][1]['period']['durationInDays'] = 180
                payload['tender']['lots'][ql]['options'][1]['period']['startDate'] = self.duration_period[0]
                payload['tender']['lots'][ql]['options'][1]['period']['endDate'] = self.duration_period[1]
                payload['tender']['lots'][ql]['options'][1]['period']['maxExtentDate'] = self.duration_period[1]
                payload['tender']['lots'][ql]['hasRecurrence'] = True
                payload['tender']['lots'][ql]['recurrence']['dates'][0]['startDate'] = self.duration_period[0]
                payload['tender']['lots'][ql]['recurrence']['dates'][1]['startDate'] = self.duration_period[0]
                payload['tender']['lots'][ql]['recurrence'][
                    'description'] = "create CNonPN: tender.lots.recurrence.description"
                payload['tender']['lots'][ql]['hasRenewal'] = True
                payload['tender']['lots'][ql]['renewal'][
                    'description'] = "create CNonPN: tender.lots.renewal.description"
                payload['tender']['lots'][ql]['renewal']['minimumRenewals'] = 2
                payload['tender']['lots'][ql]['renewal']['maximumRenewals'] = 5
                payload['tender']['lots'][ql]['renewal']['period']['durationInDays'] = 365
                payload['tender']['lots'][ql]['renewal']['period']['startDate'] = self.duration_period[0]
                payload['tender']['lots'][ql]['renewal']['period']['endDate'] = self.duration_period[1]
                payload['tender']['lots'][ql]['renewal']['period']['maxExtentDate'] = self.duration_period[1]

            for qi in range(quantity_of_items_object):
                payload['tender']['items'].append(self.constructor.tender_item_object())
                payload['tender']['items'][qi]['additionalClassifications'].append(
                    self.constructor.buyer_additional_identifiers_object())

                payload['tender']['items'][qi]['id'] = "0"
                payload['tender']['items'][qi]['internalId'] = "create cnonpn: tender.items.internalId"
                payload['tender']['items'][qi]['classification']['id'] = item_classification_id
                payload['tender']['items'][qi]['classification']['scheme'] = "CPV"
                payload['tender']['items'][qi]['classification']['description'] = \
                    "create cnonpn: tender.items.classification.description"
                payload['tender']['items'][qi]['quantity'] = 60.00
                payload['tender']['items'][qi]['unit']['id'] = "20"
                payload['tender']['items'][qi]['unit']['name'] = "create cnonpn: tender.items.unit.name"
                payload['tender']['items'][qi]['additionalClassifications'][0]['id'] = "AA08-2"
                payload['tender']['items'][qi]['additionalClassifications'][0]['scheme'] = "CPVS"
                payload['tender']['items'][qi]['additionalClassifications'][0]['description'] = \
                    "create cnonpn: tender.items.additionalClassifications.description"
                payload['tender']['items'][qi]['description'] = "create CNonPN: tender.items.description"
                payload['tender']['items'][qi]['relatedLot'] = payload['tender']['lots'][qi]['id']
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

        payload['planning']['rationale'] = "create cnonpn: planning.rationale"
        payload['planning']['budget']['description'] = "create cnonpn: planning.budget.description"
        payload['tender']['procurementMethodRationale'] = "create cnonpn: tender.procurementMethodRationale"
        payload['tender']['procurementMethodAdditionalInfo'] = "create cnonpn: tender.procurementMethodAdditionalInfo"
        payload['tender']['awardCriteria'] = "ratedCriteria"
        payload['tender']['awardCriteriaDetails'] = "automated"
        payload['tender']['enquiryPeriod']['endDate'] = Date().enquiry_period_end_date(interval=enquiry_interval)
        payload['tender']['tenderPeriod']['endDate'] = Date().tender_period_end_date(interval=tender_interval)
        payload['tender']['procuringEntity']['id'] = \
            GlobalClassCreatePn.actual_ms_release['releases'][0]['tender']['procuringEntity']['id']
        payload['tender']['procuringEntity']['persones'][0]['title'] =  \
            "create cnonpn: tender.procuringEntity.persones.title"
        payload['tender']['procuringEntity']['persones'][0]['name'] = \
            "create cnonpn: tender.procuringEntity.persones.name"
        payload['tender']['procuringEntity']['persones'][0]['identifier']['id'] = \
            "create cnonpn: tender.procuringEntity.persones.identifier.id"
        payload['tender']['procuringEntity']['persones'][0]['identifier']['scheme'] = "MD-IDNO"
        payload['tender']['procuringEntity']['persones'][0]['identifier']['uri'] = \
            "create cnonpn: tender.procuringEntity.persones.identifier.uri"
        payload['tender']['procuringEntity']['persones'][0]['identifier']['scheme'] = \
            "create cnonpn: tender.procuringEntity.persones.identifier.scheme"
        payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]['id'] = \
            "create cnonpn: tender.procuringEntity.persones.businessFunctions.id"
        payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]['type'] = "chairman"
        payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]['jobTitle'] = \
            "create cnonpn: tender.procuringEntity.persones.businessFunctions.jobTitle"
        payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]['period']['startDate'] = \
            self.business_function_date
        payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]['documents'][0]['documentType'] = \
            "regulatoryDocument"
        payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]['documents'][0]['id'] = \
            self.document_two_was_uploaded[0]["data"]["id"]
        payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]['documents'][0]['title'] = \
            "create cnonpn: tender.procuringEntity.persones.businessFunctions.documents.title"
        payload['tender']['procuringEntity']['persones'][0]['businessFunctions'][0]['documents'][0]['description'] = \
            "create cnonpn: tender.procuringEntity.persones.businessFunctions.documents.description"

        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        for ql in range(quantity_of_lots_object):
            payload['tender']['electronicAuctions']['details'].append(
                self.constructor.tender_electronic_auctions_details_object())
            payload['tender']['electronicAuctions']['details'][ql]['electronicAuctionModalities'].append(
                self.constructor.tender_electronic_auctions_details_electronic_auction_modalities_object())
            payload['tender']['electronicAuctions']['details'][ql]['id'] = str(ql)
            payload['tender']['electronicAuctions']['details'][ql]['relatedLot'] = \
                payload['tender']['lots'][ql]['id']
            payload['tender']['electronicAuctions']['details'][ql]['electronicAuctionModalities'][0][
                'eligibleMinimumDifference']['amount'] = 10.00
            payload['tender']['electronicAuctions']['details'][ql]['electronicAuctionModalities'][0][
                'eligibleMinimumDifference']['currency'] = \
                GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']

        payload['tender']['documents'] = [{}, {}]
        payload['tender']['documents'][0].update(self.constructor.tender_document_object())
        payload['tender']['documents'][1].update(self.constructor.tender_document_object())

        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        payload['tender']['documents'][1]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][1]['id'] = self.document_two_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][1]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][1]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][1]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")

        try:
            """
            Prepare criteria array with all exclusion_criteria_objects, all selection_criteria_objects, 
            all other_criteria_objects.
            """

            # exclusion_criteria_objects
            exclusion_criteria_object = {}
            exclusion_criteria_object.update((self.constructor.tender_criteria_object()))
            exclusion_criteria_object['requirementGroups'] = [{}]
            exclusion_criteria_object['requirementGroups'][0].update(
                self.constructor.tender_criteria_requirement_groups_object())
            exclusion_criteria_object['requirementGroups'][0]['requirements'] = [{}]
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_object())
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'] = [{}]
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_eligible_evidences_object())

            del exclusion_criteria_object['relatedItem']
            del exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['minValue']
            del exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['maxValue']

            exclusion_criteria_object['title'] = "create cnonpn: tender.criteria[*].title"
            exclusion_criteria_object['description'] = "create cnonpn: tender.criteria[*].description"
            exclusion_criteria_object['relatesTo'] = "tenderer"
            exclusion_criteria_object['requirementGroups'][0]['description'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].description"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['title'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].requirements[*].title"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['dataType'] = "boolean"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['expectedValue'] = True
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['period']['startDate'] = \
                Date().old_period()[0]
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['period']['endDate'] = \
                Date().old_period()[1]
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'description'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.description"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['type'] = \
                "document"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'relatedDocument']['id'] = self.document_two_was_uploaded[0]['data']['id']

            exclusion_criteria_array = generate_criteria_array(
                quantity_of_criteria_object=len(self.standard_criteria[1]),
                criteria_object=exclusion_criteria_object,
                quantity_of_groups_object=1,
                quantity_of_requirements_object=2,
                quantity_of_evidences_object=2,
                type_of_standard_criteria=1
            )

            # selection_criteria_objects
            selection_criteria_object = {}
            selection_criteria_object.update(self.constructor.tender_criteria_object())
            selection_criteria_object['requirementGroups'] = [{}]
            selection_criteria_object['requirementGroups'][0].update(
                self.constructor.tender_criteria_requirement_groups_object())
            selection_criteria_object['requirementGroups'][0]['requirements'] = [{}]
            selection_criteria_object['requirementGroups'][0]['requirements'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_object())
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'] = [{}]
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_eligible_evidences_object())

            del selection_criteria_object['relatedItem']
            del selection_criteria_object['requirementGroups'][0]['requirements'][0]['expectedValue']

            selection_criteria_object['title'] = "create cnonpn: tender.criteria[*].title"
            selection_criteria_object['description'] = "create cnonpn: tender.criteria[*].description"
            selection_criteria_object['relatesTo'] = "tenderer"
            selection_criteria_object['requirementGroups'][0]['description'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].description"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['title'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].requirements[*].title"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['dataType'] = "number"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['minValue'] = 0.99
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['maxValue'] = 99.99
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['period']['startDate'] = \
                Date().old_period()[0]
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['period']['endDate'] = \
                Date().old_period()[1]
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'description'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.description"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['type'] = \
                "document"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'relatedDocument']['id'] = self.document_two_was_uploaded[0]['data']['id']

            selection_criteria_array = generate_criteria_array(
                quantity_of_criteria_object=len(self.standard_criteria[2]),
                criteria_object=selection_criteria_object,
                quantity_of_groups_object=2,
                quantity_of_requirements_object=2,
                quantity_of_evidences_object=2,
                type_of_standard_criteria=2
            )

            # other_criteria_objects
            other_criteria_object = {}
            other_criteria_object.update(self.constructor.tender_criteria_object())
            other_criteria_object['requirementGroups'] = [{}]
            other_criteria_object['requirementGroups'][0].update(
                self.constructor.tender_criteria_requirement_groups_object())
            other_criteria_object['requirementGroups'][0]['requirements'] = [{}]
            other_criteria_object['requirementGroups'][0]['requirements'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_object())
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'] = [{}]
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_eligible_evidences_object())

            del other_criteria_object['requirementGroups'][0]['requirements'][0]['minValue']
            del other_criteria_object['requirementGroups'][0]['requirements'][0]['maxValue']

            other_criteria_object['title'] = "create cnonpn: tender.criteria[*].title"
            other_criteria_object['description'] = "create cnonpn: tender.criteria[*].description"
            other_criteria_object['relatesTo'] = "lot"
            other_criteria_object['relatedItem'] = payload['tender']['lots'][0]['id']
            other_criteria_object['requirementGroups'][0]['description'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].description"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['title'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].requirements[*].title"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['dataType'] = "boolean"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['expectedValue'] = True
            other_criteria_object['requirementGroups'][0]['requirements'][0]['period']['startDate'] = \
                Date().old_period()[0]
            other_criteria_object['requirementGroups'][0]['requirements'][0]['period']['endDate'] = \
                Date().old_period()[1]
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['description'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.description"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['type'] = \
                "document"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'relatedDocument']['id'] = self.document_two_was_uploaded[0]['data']['id']

            other_criteria_array = generate_criteria_array(
                quantity_of_criteria_object=len(self.standard_criteria[3]),
                criteria_object=other_criteria_object,
                quantity_of_groups_object=2,
                quantity_of_requirements_object=2,
                quantity_of_evidences_object=2,
                type_of_standard_criteria=3
            )

            payload['tender']['criteria'] = exclusion_criteria_array + selection_criteria_array + other_criteria_array
            payload['tender']['criteria'] = set_eligibility_evidences_unique_temporary_id(
                payload_criteria_array=payload['tender']['criteria'])

            payload['tender']['criteria'] = set_criteria_array_unique_temporary_id(
                payload_criteria_array=payload['tender']['criteria']
            )
        except ValueError:
            raise ValueError("Impossible to prepare criteria array.")

        try:
            """
            Prepare conversion array.
            """
            # Conversion array for exclusion_criteria_array -> FReq-1.1.1.36

            # Conversion array for selection_criteria_array
            requirements_objects = list()
            for o in selection_criteria_array:
                if "id" in o:
                    for o_1 in o['requirementGroups']:
                        if "id" in o_1:
                            for o_2 in o_1['requirements']:
                                if "id" in o_2:
                                    requirements_objects.append(o_2['id'])
            quantity_of_requirements_objects = len(requirements_objects)

            conversion_object = {}
            conversion_object.update(self.constructor.tender_conversion_object())
            conversion_object['id'] = "0"
            conversion_object['relatesTo'] = "requirement"
            conversion_object['rationale'] = "create cnonpn: tender.conversion.rationale"
            conversion_object['description'] = "create cnonpn: tender.conversion.description"
            conversion_object['coefficients'] = [{}, {}]
            conversion_object['coefficients'][0].update(self.constructor.tender_conversion_coefficient_object())
            conversion_object['coefficients'][1].update(self.constructor.tender_conversion_coefficient_object())
            conversion_object['coefficients'][0]['id'] = "create cnonpn: tender.conversion.coefficients.id"
            conversion_object['coefficients'][0]['value'] = 0.99
            conversion_object['coefficients'][0]['coefficient'] = 1
            conversion_object['coefficients'][1]['id'] = "create cnonpn: tender.conversion.coefficients.id"
            conversion_object['coefficients'][1]['value'] = 99.99
            conversion_object['coefficients'][1]['coefficient'] = 0.99
            payload['tender']['conversions'].append(conversion_object)

            # Limited by math -> 0.99 ^ 22 = 0.8
            if quantity_of_requirements_objects >= 22:
                quantity = 21
            else:
                quantity = quantity_of_requirements_objects
            conversion_array_for_selection_criteria = generate_conversions_array(
                quantity_of_conversion_object=quantity,
                conversion_object=conversion_object,
                requirements_array=requirements_objects
            )

            # Conversion array for other_criteria_array
            requirements_objects = list()
            for o in other_criteria_array:
                if "id" in o:
                    for o_1 in o['requirementGroups']:
                        if "id" in o_1:
                            for o_2 in o_1['requirements']:
                                if "id" in o_2:
                                    requirements_objects.append(o_2['id'])
            quantity_of_requirements_objects = len(requirements_objects)

            conversion_object = {}
            conversion_object.update(self.constructor.tender_conversion_object())
            conversion_object['id'] = "0"
            conversion_object['relatesTo'] = "requirement"
            conversion_object['rationale'] = "create cnonpn: tender.conversion.rationale"
            conversion_object['description'] = "create cnonpn: tender.conversion.description"
            conversion_object['coefficients'] = [{}, {}]
            conversion_object['coefficients'][0].update(self.constructor.tender_conversion_coefficient_object())
            conversion_object['coefficients'][0]['id'] = "0"
            conversion_object['coefficients'][0]['value'] = True
            conversion_object['coefficients'][0]['coefficient'] = 0.99
            conversion_object['coefficients'][1].update(self.constructor.tender_conversion_coefficient_object())
            conversion_object['coefficients'][1]['id'] = "1"
            conversion_object['coefficients'][1]['value'] = False
            conversion_object['coefficients'][1]['coefficient'] = 1
            payload['tender']['conversions'].append(conversion_object)

            if quantity_of_requirements_objects >= 1:
                quantity = 1
            else:
                quantity = quantity_of_requirements_objects
            conversion_array_for_other_criteria = generate_conversions_array(
                quantity_of_conversion_object=quantity,
                conversion_object=conversion_object,
                requirements_array=requirements_objects
            )

            payload['tender']['conversions'] = \
                conversion_array_for_selection_criteria + \
                conversion_array_for_other_criteria

            payload['tender']['conversions'] = set_conversions_unique_temporary_id(
                payload_conversions_array=payload['tender']['conversions'])
        except ValueError:
            raise ValueError("Impossible to prepare conversions array.")

        return payload

    def create_cnonpn_obligatory_data_model_with_lots_items_documents(
            self, enquiry_interval, tender_interval, quantity_of_lots_object, quantity_of_items_object,
            based_stage_release, need_to_set_permanent_id_for_lots_array=False,
            need_to_set_permanent_id_for_items_array=False, need_to_set_permanent_id_for_documents_array=False):
        payload = {
            "tender": {}
        }

        try:
            """
            Update payload dictionary.
            """
            payload['tender'].update(self.constructor.tender_object())
            payload['tender']['lots'] = [{}]
            payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
            payload['tender']['items'] = [{}]
            payload['tender']['items'][0].update(self.constructor.tender_item_object())
            payload['tender']['items'][0]['additionalClassifications'] = [{}]
            payload['tender']['items'][0]['additionalClassifications'][0].update(
                self.constructor.buyer_additional_identifiers_object())
            payload['tender']['documents'] = [{}]
            payload['tender']['documents'][0].update(self.constructor.tender_document_object())

            del payload['tender']['electronicAuctions']
            del payload['tender']['procurementMethodRationale']
            del payload['tender']['procurementMethodAdditionalInfo']
            del payload['tender']['procurementMethodModalities']
            del payload['tender']['criteria']
            del payload['tender']['conversions']
            del payload['tender']['lots'][0]['internalId']
            del payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode']
            del payload['tender']['lots'][0]['placeOfPerformance']['description']
            del payload['tender']['lots'][0]['hasOptions']
            del payload['tender']['lots'][0]['options']
            del payload['tender']['lots'][0]['hasRecurrence']
            del payload['tender']['lots'][0]['recurrence']
            del payload['tender']['lots'][0]['hasRenewal']
            del payload['tender']['lots'][0]['renewal']
            del payload['tender']['items'][0]['internalId']
            del payload['tender']['items'][0]['additionalClassifications']
            del payload['tender']['procuringEntity']

        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

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

        payload['tender']['awardCriteria'] = "priceOnly"
        payload['tender']['enquiryPeriod']['endDate'] = Date().enquiry_period_end_date(interval=enquiry_interval)
        payload['tender']['tenderPeriod']['endDate'] = Date().tender_period_end_date(interval=tender_interval)

        payload['tender']['lots'][0]['id'] = "create cnonpn: tender.lots.id"
        payload['tender']['lots'][0]['title'] = "create cnonpn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "create cnonpn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 4000.05
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = self.contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = self.contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"

        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['classification']['scheme'] = "CPV"
        payload['tender']['items'][0]['classification']['description'] = \
            "create cnonpn: tender.items.classification.description"
        payload['tender']['items'][0]['quantity'] = 60.00
        payload['tender']['items'][0]['unit']['id'] = "20"
        payload['tender']['items'][0]['unit']['name'] = "create cnonpn: tender.items.unit.name"
        payload['tender']['items'][0]['description'] = "create CNonPN: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")

        return payload

    def create_cnonpn_full_data_model_with_lots_items_documents_criteria_conv(
            self, enquiry_interval, tender_interval, quantity_of_lots_object, quantity_of_items_object,
            based_stage_release, need_to_set_permanent_id_for_lots_array=False,
            need_to_set_permanent_id_for_items_array=False, need_to_set_permanent_id_for_documents_array=False):
        payload = {
            "planning": {},
            "tender": {}
        }

        try:
            """
            Update payload dictionary.
            """
            payload['planning'].update(self.constructor.planning_object())
            payload['tender'].update(self.constructor.tender_object())
            payload['tender']['lots'] = [{}]
            payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
            payload['tender']['lots'][0]['options'] = [{}, {}]
            payload['tender']['lots'][0]['options'][0].update(self.constructor.tender_lots_option_object())
            payload['tender']['lots'][0]['options'][1].update(self.constructor.tender_lots_option_object())
            payload['tender']['lots'][0]['recurrence']['dates'] = [{}, {}]
            payload['tender']['lots'][0]['recurrence']['dates'][0].update(
                self.constructor.tender_lots_recurrence_dates_object())
            payload['tender']['lots'][0]['recurrence']['dates'][1].update(
                self.constructor.tender_lots_recurrence_dates_object())

            payload['tender']['items'] = [{}]
            payload['tender']['items'][0].update(self.constructor.tender_item_object())
            payload['tender']['items'][0]['additionalClassifications'] = [{}]
            payload['tender']['items'][0]['additionalClassifications'][0].update(
                self.constructor.buyer_additional_identifiers_object())

            payload['tender']['documents'] = [{}, {}]
            payload['tender']['documents'][0].update(self.constructor.tender_document_object())
            payload['tender']['documents'][1].update(self.constructor.tender_document_object())
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

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

        del payload['tender']['electronicAuctions']
        del payload['tender']['procurementMethodModalities']

        payload['planning']['rationale'] = "create cnonpn: planning.rationale"
        payload['planning']['budget']['description'] = "create cnonpn: planning.budget.description"
        payload['tender']['procurementMethodRationale'] = "create cnonpn: tender.procurementMethodRationale"
        payload['tender']['procurementMethodAdditionalInfo'] = "create cnonpn: tender.procurementMethodAdditionalInfo"
        payload['tender']['awardCriteria'] = "ratedCriteria"
        payload['tender']['awardCriteriaDetails'] = "automated"
        payload['tender']['enquiryPeriod']['endDate'] = Date().enquiry_period_end_date(interval=enquiry_interval)
        payload['tender']['tenderPeriod']['endDate'] = Date().tender_period_end_date(interval=tender_interval)
        payload['tender']['procuringEntity'] = \
            GlobalClassCreatePn.actual_ms_release['releases'][0]['tender']['procuringEntity']

        payload['tender']['lots'][0]['id'] = "create cnonpn: tender.lots.id"
        payload['tender']['lots'][0]['internalId'] = "create cnonpn: tender.lots.internalId"
        payload['tender']['lots'][0]['title'] = "create cnonpn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "create cnonpn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 4000.05
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = self.contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = self.contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.postalCode"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"
        payload['tender']['lots'][0]['placeOfPerformance']['description'] = \
            "create cnonpn: tender.lots.placeOfPerformance.description"
        payload['tender']['lots'][0]['hasOptions'] = True
        payload['tender']['lots'][0]['options'][0]['description'] = "create CNonPN: tender.lots[0].options.description"
        payload['tender']['lots'][0]['options'][0]['period']['durationInDays'] = 180
        payload['tender']['lots'][0]['options'][0]['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['options'][0]['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][0]['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][1]['description'] = "create CNonPN: tender.lots[0].options.description"
        payload['tender']['lots'][0]['options'][1]['period']['durationInDays'] = 180
        payload['tender']['lots'][0]['options'][1]['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['options'][1]['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][1]['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['hasRecurrence'] = True
        payload['tender']['lots'][0]['recurrence']['dates'][0]['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['recurrence']['dates'][1]['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['recurrence']['description'] = "create CNonPN: tender.lots.recurrence.description"
        payload['tender']['lots'][0]['hasRenewal'] = True
        payload['tender']['lots'][0]['renewal']['description'] = "create CNonPN: tender.lots.renewal.description"
        payload['tender']['lots'][0]['renewal']['minimumRenewals'] = 2
        payload['tender']['lots'][0]['renewal']['maximumRenewals'] = 5
        payload['tender']['lots'][0]['renewal']['period']['durationInDays'] = 365
        payload['tender']['lots'][0]['renewal']['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['renewal']['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['renewal']['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['internalId'] = "create cnonpn: tender.items.internalId"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['classification']['scheme'] = "CPV"
        payload['tender']['items'][0]['classification']['description'] = \
            "create cnonpn: tender.items.classification.description"
        payload['tender']['items'][0]['quantity'] = 60.00
        payload['tender']['items'][0]['unit']['id'] = "20"
        payload['tender']['items'][0]['unit']['name'] = "create cnonpn: tender.items.unit.name"
        payload['tender']['items'][0]['additionalClassifications'][0]['id'] = "AA08-2"
        payload['tender']['items'][0]['additionalClassifications'][0]['scheme'] = "CPVS"
        payload['tender']['items'][0]['additionalClassifications'][0]['description'] = \
            "create cnonpn: tender.items.additionalClassifications.description"
        payload['tender']['items'][0]['description'] = "create CNonPN: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        payload['tender']['documents'][1]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][1]['id'] = self.document_two_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][1]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][1]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][1]['relatedLots'] = [payload['tender']['lots'][0]['id']]
        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")

        try:
            """
            Prepare criteria array with all exclusion_criteria_objects, all selection_criteria_objects, 
            all other_criteria_objects.
            """

            # exclusion_criteria_objects
            exclusion_criteria_object = {}
            exclusion_criteria_object.update((self.constructor.tender_criteria_object()))
            exclusion_criteria_object['requirementGroups'] = [{}]
            exclusion_criteria_object['requirementGroups'][0].update(
                self.constructor.tender_criteria_requirement_groups_object())
            exclusion_criteria_object['requirementGroups'][0]['requirements'] = [{}]
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_object())
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'] = [{}]
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_eligible_evidences_object())

            del exclusion_criteria_object['relatedItem']
            del exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['minValue']
            del exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['maxValue']

            exclusion_criteria_object['title'] = "create cnonpn: tender.criteria[*].title"
            exclusion_criteria_object['description'] = "create cnonpn: tender.criteria[*].description"
            exclusion_criteria_object['relatesTo'] = "tenderer"
            exclusion_criteria_object['requirementGroups'][0]['description'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].description"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['title'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].requirements[*].title"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['dataType'] = "boolean"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['expectedValue'] = True
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['period']['startDate'] = \
                Date().old_period()[0]
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['period']['endDate'] = \
                Date().old_period()[1]
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'description'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.description"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['type'] = \
                "document"
            exclusion_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'relatedDocument']['id'] = self.document_two_was_uploaded[0]['data']['id']

            exclusion_criteria_array = generate_criteria_array(
                quantity_of_criteria_object=len(self.standard_criteria[1]),
                criteria_object=exclusion_criteria_object,
                quantity_of_groups_object=1,
                quantity_of_requirements_object=2,
                quantity_of_evidences_object=2,
                type_of_standard_criteria=1
            )

            # selection_criteria_objects
            selection_criteria_object = {}
            selection_criteria_object.update(self.constructor.tender_criteria_object())
            selection_criteria_object['requirementGroups'] = [{}]
            selection_criteria_object['requirementGroups'][0].update(
                self.constructor.tender_criteria_requirement_groups_object())
            selection_criteria_object['requirementGroups'][0]['requirements'] = [{}]
            selection_criteria_object['requirementGroups'][0]['requirements'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_object())
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'] = [{}]
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_eligible_evidences_object())

            del selection_criteria_object['relatedItem']
            del selection_criteria_object['requirementGroups'][0]['requirements'][0]['expectedValue']

            selection_criteria_object['title'] = "create cnonpn: tender.criteria[*].title"
            selection_criteria_object['description'] = "create cnonpn: tender.criteria[*].description"
            selection_criteria_object['relatesTo'] = "tenderer"
            selection_criteria_object['requirementGroups'][0]['description'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].description"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['title'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].requirements[*].title"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['dataType'] = "number"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['minValue'] = 0.99
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['maxValue'] = 99.99
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['period']['startDate'] = \
                Date().old_period()[0]
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['period']['endDate'] = \
                Date().old_period()[1]
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'description'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.description"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['type'] = \
                "document"
            selection_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'relatedDocument']['id'] = self.document_two_was_uploaded[0]['data']['id']

            selection_criteria_array = generate_criteria_array(
                quantity_of_criteria_object=len(self.standard_criteria[2]),
                criteria_object=selection_criteria_object,
                quantity_of_groups_object=2,
                quantity_of_requirements_object=2,
                quantity_of_evidences_object=2,
                type_of_standard_criteria=2
            )

            # other_criteria_objects
            other_criteria_object = {}
            other_criteria_object.update(self.constructor.tender_criteria_object())
            other_criteria_object['requirementGroups'] = [{}]
            other_criteria_object['requirementGroups'][0].update(
                self.constructor.tender_criteria_requirement_groups_object())
            other_criteria_object['requirementGroups'][0]['requirements'] = [{}]
            other_criteria_object['requirementGroups'][0]['requirements'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_object())
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'] = [{}]
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0].update(
                self.constructor.tender_criteria_requirement_groups_requirements_eligible_evidences_object())

            del other_criteria_object['requirementGroups'][0]['requirements'][0]['minValue']
            del other_criteria_object['requirementGroups'][0]['requirements'][0]['maxValue']

            other_criteria_object['title'] = "create cnonpn: tender.criteria[*].title"
            other_criteria_object['description'] = "create cnonpn: tender.criteria[*].description"
            other_criteria_object['relatesTo'] = "lot"
            other_criteria_object['relatedItem'] = payload['tender']['lots'][0]['id']
            other_criteria_object['requirementGroups'][0]['description'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].description"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['title'] = \
                "create cnonpn: tender.criteria[*].requirementGroups[*].requirements[*].title"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['dataType'] = "boolean"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['expectedValue'] = True
            other_criteria_object['requirementGroups'][0]['requirements'][0]['period']['startDate'] = \
                Date().old_period()[0]
            other_criteria_object['requirementGroups'][0]['requirements'][0]['period']['endDate'] = \
                Date().old_period()[1]
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['title'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.title"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['description'] = \
                "create cnonpn: tender.criteria.requirementGroups.requirements.eligibleEvidences.description"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0]['type'] = \
                "document"
            other_criteria_object['requirementGroups'][0]['requirements'][0]['eligibleEvidences'][0][
                'relatedDocument']['id'] = self.document_two_was_uploaded[0]['data']['id']

            other_criteria_array = generate_criteria_array(
                quantity_of_criteria_object=len(self.standard_criteria[3]),
                criteria_object=other_criteria_object,
                quantity_of_groups_object=2,
                quantity_of_requirements_object=2,
                quantity_of_evidences_object=2,
                type_of_standard_criteria=3
            )

            payload['tender']['criteria'] = exclusion_criteria_array + selection_criteria_array + other_criteria_array
            payload['tender']['criteria'] = set_eligibility_evidences_unique_temporary_id(
                payload_criteria_array=payload['tender']['criteria'])

            payload['tender']['criteria'] = set_criteria_array_unique_temporary_id(
                payload_criteria_array=payload['tender']['criteria']
            )
        except ValueError:
            raise ValueError("Impossible to prepare criteria array.")

        try:
            """
            Prepare conversion array.
            """
            # Conversion array for exclusion_criteria_array -> FReq-1.1.1.36

            # Conversion array for selection_criteria_array
            requirements_objects = list()
            for o in selection_criteria_array:
                if "id" in o:
                    for o_1 in o['requirementGroups']:
                        if "id" in o_1:
                            for o_2 in o_1['requirements']:
                                if "id" in o_2:
                                    requirements_objects.append(o_2['id'])
            quantity_of_requirements_objects = len(requirements_objects)

            conversion_object = {}
            conversion_object.update(self.constructor.tender_conversion_object())
            conversion_object['id'] = "0"
            conversion_object['relatesTo'] = "requirement"
            conversion_object['rationale'] = "create cnonpn: tender.conversion.rationale"
            conversion_object['description'] = "create cnonpn: tender.conversion.description"
            conversion_object['coefficients'] = [{}, {}]
            conversion_object['coefficients'][0].update(self.constructor.tender_conversion_coefficient_object())
            conversion_object['coefficients'][1].update(self.constructor.tender_conversion_coefficient_object())
            conversion_object['coefficients'][0]['id'] = "create cnonpn: tender.conversion.coefficients.id"
            conversion_object['coefficients'][0]['value'] = 0.99
            conversion_object['coefficients'][0]['coefficient'] = 1
            conversion_object['coefficients'][1]['id'] = "create cnonpn: tender.conversion.coefficients.id"
            conversion_object['coefficients'][1]['value'] = 99.99
            conversion_object['coefficients'][1]['coefficient'] = 0.99
            payload['tender']['conversions'].append(conversion_object)

            # Limited by math -> 0.99 ^ 22 = 0.8
            if quantity_of_requirements_objects >= 22:
                quantity = 21
            else:
                quantity = quantity_of_requirements_objects
            conversion_array_for_selection_criteria = generate_conversions_array(
                quantity_of_conversion_object=quantity,
                conversion_object=conversion_object,
                requirements_array=requirements_objects
            )

            # Conversion array for other_criteria_array
            requirements_objects = list()
            for o in other_criteria_array:
                if "id" in o:
                    for o_1 in o['requirementGroups']:
                        if "id" in o_1:
                            for o_2 in o_1['requirements']:
                                if "id" in o_2:
                                    requirements_objects.append(o_2['id'])
            quantity_of_requirements_objects = len(requirements_objects)

            conversion_object = {}
            conversion_object.update(self.constructor.tender_conversion_object())
            conversion_object['id'] = "0"
            conversion_object['relatesTo'] = "requirement"
            conversion_object['rationale'] = "create cnonpn: tender.conversion.rationale"
            conversion_object['description'] = "create cnonpn: tender.conversion.description"
            conversion_object['coefficients'] = [{}, {}]
            conversion_object['coefficients'][0].update(self.constructor.tender_conversion_coefficient_object())
            conversion_object['coefficients'][0]['id'] = "0"
            conversion_object['coefficients'][0]['value'] = True
            conversion_object['coefficients'][0]['coefficient'] = 0.99
            conversion_object['coefficients'][1].update(self.constructor.tender_conversion_coefficient_object())
            conversion_object['coefficients'][1]['id'] = "1"
            conversion_object['coefficients'][1]['value'] = False
            conversion_object['coefficients'][1]['coefficient'] = 1
            payload['tender']['conversions'].append(conversion_object)

            if quantity_of_requirements_objects >= 1:
                quantity = 1
            else:
                quantity = quantity_of_requirements_objects
            conversion_array_for_other_criteria = generate_conversions_array(
                quantity_of_conversion_object=quantity,
                conversion_object=conversion_object,
                requirements_array=requirements_objects
            )

            payload['tender']['conversions'] = \
                conversion_array_for_selection_criteria + \
                conversion_array_for_other_criteria

            payload['tender']['conversions'] = set_conversions_unique_temporary_id(
                payload_conversions_array=payload['tender']['conversions'])
        except ValueError:
            raise ValueError("Impossible to prepare conversions array.")

        return payload

    def create_cnonpn_full_data_model_with_lots_items_documents(
            self, enquiry_interval, tender_interval, quantity_of_lots_object, quantity_of_items_object,
            based_stage_release, need_to_set_permanent_id_for_lots_array=False,
            need_to_set_permanent_id_for_items_array=False, need_to_set_permanent_id_for_documents_array=False):
        payload = {
            "planning": {},
            "tender": {}
        }

        try:
            """
            Update payload dictionary.
            """
            payload['planning'].update(self.constructor.planning_object())
            payload['tender'].update(self.constructor.tender_object())
            del payload['tender']['criteria']
            del payload['tender']['conversions']
            payload['tender']['lots'] = [{}]
            payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
            payload['tender']['lots'][0]['options'] = [{}, {}]
            payload['tender']['lots'][0]['options'][0].update(self.constructor.tender_lots_option_object())
            payload['tender']['lots'][0]['options'][1].update(self.constructor.tender_lots_option_object())
            payload['tender']['lots'][0]['recurrence']['dates'] = [{}, {}]
            payload['tender']['lots'][0]['recurrence']['dates'][0].update(
                self.constructor.tender_lots_recurrence_dates_object())
            payload['tender']['lots'][0]['recurrence']['dates'][1].update(
                self.constructor.tender_lots_recurrence_dates_object())

            payload['tender']['items'] = [{}]
            payload['tender']['items'][0].update(self.constructor.tender_item_object())
            payload['tender']['items'][0]['additionalClassifications'] = [{}]
            payload['tender']['items'][0]['additionalClassifications'][0].update(
                self.constructor.buyer_additional_identifiers_object())

            payload['tender']['documents'] = [{}, {}]
            payload['tender']['documents'][0].update(self.constructor.tender_document_object())
            payload['tender']['documents'][1].update(self.constructor.tender_document_object())
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

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

        del payload['tender']['electronicAuctions']
        del payload['tender']['procurementMethodModalities']

        payload['planning']['rationale'] = "create cnonpn: planning.rationale"
        payload['planning']['budget']['description'] = "create cnonpn: planning.budget.description"
        payload['tender']['awardCriteria'] = "priceOnly"
        payload['tender']['procurementMethodRationale'] = "create cnonpn: tender.procurementMethodRationale"
        payload['tender']['procurementMethodAdditionalInfo'] = "create cnonpn: tender.procurementMethodAdditionalInfo"
        payload['tender']['enquiryPeriod']['endDate'] = Date().enquiry_period_end_date(interval=enquiry_interval)
        payload['tender']['tenderPeriod']['endDate'] = Date().tender_period_end_date(interval=tender_interval)
        payload['tender']['procuringEntity'] = \
            GlobalClassCreatePn.actual_ms_release['releases'][0]['tender']['procuringEntity']

        payload['tender']['lots'][0]['id'] = "create cnonpn: tender.lots.id"
        payload['tender']['lots'][0]['internalId'] = "create cnonpn: tender.lots.internalId"
        payload['tender']['lots'][0]['title'] = "create cnonpn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "create cnonpn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 4000.05
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = self.contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = self.contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.postalCode"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"
        payload['tender']['lots'][0]['placeOfPerformance']['description'] = \
            "create cnonpn: tender.lots.placeOfPerformance.description"
        payload['tender']['lots'][0]['hasOptions'] = True
        payload['tender']['lots'][0]['options'][0]['description'] = "create CNonPN: tender.lots[0].options.description"
        payload['tender']['lots'][0]['options'][0]['period']['durationInDays'] = 180
        payload['tender']['lots'][0]['options'][0]['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['options'][0]['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][0]['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][1]['description'] = "create CNonPN: tender.lots[0].options.description"
        payload['tender']['lots'][0]['options'][1]['period']['durationInDays'] = 180
        payload['tender']['lots'][0]['options'][1]['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['options'][1]['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][1]['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['hasRecurrence'] = True
        payload['tender']['lots'][0]['recurrence']['dates'][0]['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['recurrence']['dates'][1]['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['recurrence']['description'] = "create CNonPN: tender.lots.recurrence.description"
        payload['tender']['lots'][0]['hasRenewal'] = True
        payload['tender']['lots'][0]['renewal']['description'] = "create CNonPN: tender.lots.renewal.description"
        payload['tender']['lots'][0]['renewal']['minimumRenewals'] = 2
        payload['tender']['lots'][0]['renewal']['maximumRenewals'] = 5
        payload['tender']['lots'][0]['renewal']['period']['durationInDays'] = 365
        payload['tender']['lots'][0]['renewal']['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['renewal']['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['renewal']['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['internalId'] = "create cnonpn: tender.items.internalId"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['classification']['scheme'] = "CPV"
        payload['tender']['items'][0]['classification']['description'] = \
            "create cnonpn: tender.items.classification.description"
        payload['tender']['items'][0]['quantity'] = 60.00
        payload['tender']['items'][0]['unit']['id'] = "20"
        payload['tender']['items'][0]['unit']['name'] = "create cnonpn: tender.items.unit.name"
        payload['tender']['items'][0]['additionalClassifications'][0]['id'] = "AA08-2"
        payload['tender']['items'][0]['additionalClassifications'][0]['scheme'] = "CPVS"
        payload['tender']['items'][0]['additionalClassifications'][0]['description'] = \
            "create cnonpn: tender.items.additionalClassifications.description"
        payload['tender']['items'][0]['description'] = "create CNonPN: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        payload['tender']['documents'][1]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][1]['id'] = self.document_two_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][1]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][1]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][1]['relatedLots'] = [payload['tender']['lots'][0]['id']]
        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")

        return payload

    def update_cnonpn_full_data_model_with_lots_items_documents_auction(
            self, enquiry_interval, tender_interval, quantity_of_lots_object, quantity_of_items_object,
            based_stage_release, need_to_set_permanent_id_for_lots_array=False,
            need_to_set_permanent_id_for_items_array=False, need_to_set_permanent_id_for_documents_array=False,
            need_to_set_permanent_id_for_electronic_auction=False):
        payload = {
            "planning": {},
            "tender": {}
        }

        try:
            """
            Update payload dictionary.
            """
            payload['planning'].update(self.constructor.planning_object())
            payload['tender'].update(self.constructor.tender_object())
            payload['tender']['electronicAuctions']['details'] = [{}, {}]
            payload['tender']['electronicAuctions']['details'][0].update(
                self.constructor.tender_electronic_auctions_details_object())
            payload['tender']['electronicAuctions']['details'][0]['electronicAuctionModalities'] = [{}]
            payload['tender']['electronicAuctions']['details'][0]['electronicAuctionModalities'][0].update(
                self.constructor.tender_electronic_auctions_details_electronic_auction_modalities_object())
            payload['tender']['electronicAuctions']['details'][1].update(
                self.constructor.tender_electronic_auctions_details_object())
            payload['tender']['electronicAuctions']['details'][1]['electronicAuctionModalities'] = [{}]
            payload['tender']['electronicAuctions']['details'][1]['electronicAuctionModalities'][0].update(
                self.constructor.tender_electronic_auctions_details_electronic_auction_modalities_object())
            payload['tender']['lots'] = [{}]
            payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
            payload['tender']['lots'][0]['options'] = [{}, {}]
            payload['tender']['lots'][0]['options'][0].update(self.constructor.tender_lots_option_object())
            payload['tender']['lots'][0]['options'][1].update(self.constructor.tender_lots_option_object())
            payload['tender']['lots'][0]['recurrence']['dates'] = [{}, {}]
            payload['tender']['lots'][0]['recurrence']['dates'][0].update(
                self.constructor.tender_lots_recurrence_dates_object())
            payload['tender']['lots'][0]['recurrence']['dates'][1].update(
                self.constructor.tender_lots_recurrence_dates_object())

            payload['tender']['items'] = [{}]
            payload['tender']['items'][0].update(self.constructor.tender_item_object())
            payload['tender']['items'][0]['additionalClassifications'] = [{}]
            payload['tender']['items'][0]['additionalClassifications'][0].update(
                self.constructor.buyer_additional_identifiers_object())

            payload['tender']['documents'] = [{}, {}]
            payload['tender']['documents'][0].update(self.constructor.tender_document_object())
            payload['tender']['documents'][1].update(self.constructor.tender_document_object())
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

        del payload['tender']['criteria']
        del payload['tender']['conversions']

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

        payload['tender']['title'] = "This field is redundant"
        payload['tender']['description'] = "This field is redundant"

        payload['planning']['rationale'] = "update cnonpn: planning.rationale"
        payload['planning']['budget']['description'] = "update cnonpn: planning.budget.description"
        payload['tender']['procurementMethodRationale'] = "update cnonpn: tender.procurementMethodRationale"
        payload['tender']['procurementMethodAdditionalInfo'] = "update cnonpn: tender.procurementMethodAdditionalInfo"
        payload['tender']['enquiryPeriod']['endDate'] = Date().enquiry_period_end_date(interval=enquiry_interval)
        payload['tender']['tenderPeriod']['endDate'] = Date().tender_period_end_date(interval=tender_interval)
        payload['tender']['procuringEntity'] = \
            GlobalClassCreatePn.actual_ms_release['releases'][0]['tender']['procuringEntity']

        payload['tender']['lots'][0]['id'] = "update cnonpn: tender.lots.id"
        payload['tender']['lots'][0]['internalId'] = "update cnonpn: tender.lots.internalId"
        payload['tender']['lots'][0]['title'] = "update cnonpn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "create cnonpn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 4040.45
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = self.contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = self.contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "update cnonpn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode'] = \
            "update cnonpn: tender.lots.placeOfPerformance.address.postalCode"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "3400000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = "3401000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "update cnonpn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"
        payload['tender']['lots'][0]['placeOfPerformance']['description'] = \
            "update cnonpn: tender.lots.placeOfPerformance.description"
        payload['tender']['lots'][0]['hasOptions'] = True
        payload['tender']['lots'][0]['options'][0]['description'] = "update CNonPN: tender.lots[0].options.description"
        payload['tender']['lots'][0]['options'][0]['period']['durationInDays'] = 180
        payload['tender']['lots'][0]['options'][0]['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['options'][0]['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][0]['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][1]['description'] = "update CNonPN: tender.lots[0].options.description"
        payload['tender']['lots'][0]['options'][1]['period']['durationInDays'] = 180
        payload['tender']['lots'][0]['options'][1]['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['options'][1]['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][1]['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['hasRecurrence'] = True
        payload['tender']['lots'][0]['recurrence']['dates'][0]['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['recurrence']['dates'][1]['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['recurrence']['description'] = "update CNonPN: tender.lots.recurrence.description"
        payload['tender']['lots'][0]['hasRenewal'] = True
        payload['tender']['lots'][0]['renewal']['description'] = "update CNonPN: tender.lots.renewal.description"
        payload['tender']['lots'][0]['renewal']['minimumRenewals'] = 1
        payload['tender']['lots'][0]['renewal']['maximumRenewals'] = 4
        payload['tender']['lots'][0]['renewal']['period']['durationInDays'] = 364
        payload['tender']['lots'][0]['renewal']['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['renewal']['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['renewal']['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['internalId'] = "update cnonpn: tender.items.internalId"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['classification']['scheme'] = "CPV"
        payload['tender']['items'][0]['classification']['description'] = \
            "update cnonpn: tender.items.classification.description"
        payload['tender']['items'][0]['quantity'] = 70.00
        payload['tender']['items'][0]['unit']['id'] = "18"
        payload['tender']['items'][0]['unit']['name'] = "update cnonpn: tender.items.unit.name"
        payload['tender']['items'][0]['additionalClassifications'][0]['id'] = "AA06-6"
        payload['tender']['items'][0]['additionalClassifications'][0]['scheme'] = "CPVS"
        payload['tender']['items'][0]['additionalClassifications'][0]['description'] = \
            "update cnonpn: tender.items.additionalClassifications.description"
        payload['tender']['items'][0]['description'] = "update CNonPN: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "update cnonpn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "update cnonpn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        payload['tender']['documents'][1]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][1]['id'] = self.document_two_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][1]['title'] = "update cnonpn: tender.documents.title"
        payload['tender']['documents'][1]['description'] = "update cnonpn: tender.documents.description"
        payload['tender']['documents'][1]['relatedLots'] = [payload['tender']['lots'][1]['id']]
        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")

        payload['tender']['electronicAuctions']['details'][0]['id'] = "0"
        payload['tender']['electronicAuctions']['details'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['electronicAuctions']['details'][0]['electronicAuctionModalities'][0][
            'eligibleMinimumDifference']['amount'] = 40.00
        payload['tender']['electronicAuctions']['details'][0]['electronicAuctionModalities'][0][
            'eligibleMinimumDifference']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['electronicAuctions']['details'][1]['id'] = "1"
        payload['tender']['electronicAuctions']['details'][1]['relatedLot'] = payload['tender']['lots'][1]['id']
        payload['tender']['electronicAuctions']['details'][1]['electronicAuctionModalities'][0][
            'eligibleMinimumDifference']['amount'] = 40.00
        payload['tender']['electronicAuctions']['details'][1]['electronicAuctionModalities'][0][
            'eligibleMinimumDifference']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']

        try:
            """
            Set permanent id for electronicAuctions.details array.
            """
            if need_to_set_permanent_id_for_electronic_auction is True:
                payload['tender']['electronicAuctions']['details'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender'][
                        'electronicAuctions']['details'],
                    payload_array=payload['tender']['electronicAuctions']['details'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for electronicAuctions.details array."
                           "Key 'electronicAuctions.details' was not found.")

        return payload

    def update_cnonpn_obligatory_data_model_with_lots_items_documents_without_auction(
            self, enquiry_interval, tender_interval, quantity_of_lots_object, quantity_of_items_object,
            based_stage_release, need_to_set_permanent_id_for_lots_array=False,
            need_to_set_permanent_id_for_items_array=False, need_to_set_permanent_id_for_documents_array=False):

        payload = {
            "tender": {}
        }

        try:
            """
            Update payload dictionary.
            """
            payload['tender'].update(self.constructor.tender_object())
            payload['tender']['lots'] = [{}]
            payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
            payload['tender']['items'] = [{}]
            payload['tender']['items'][0].update(self.constructor.tender_item_object())
            payload['tender']['items'][0]['additionalClassifications'] = [{}]
            payload['tender']['items'][0]['additionalClassifications'][0].update(
                self.constructor.buyer_additional_identifiers_object())
            payload['tender']['documents'] = [{}]
            payload['tender']['documents'][0].update(self.constructor.tender_document_object())

            del payload['tender']['electronicAuctions']
            del payload['tender']['procurementMethodRationale']
            del payload['tender']['procurementMethodAdditionalInfo']
            del payload['tender']['procurementMethodModalities']
            del payload['tender']['criteria']
            del payload['tender']['conversions']
            del payload['tender']['lots'][0]['internalId']
            del payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode']
            del payload['tender']['lots'][0]['placeOfPerformance']['description']
            del payload['tender']['lots'][0]['hasOptions']
            del payload['tender']['lots'][0]['options']
            del payload['tender']['lots'][0]['hasRecurrence']
            del payload['tender']['lots'][0]['recurrence']
            del payload['tender']['lots'][0]['hasRenewal']
            del payload['tender']['lots'][0]['renewal']
            del payload['tender']['items'][0]['internalId']
            del payload['tender']['items'][0]['additionalClassifications']
            del payload['tender']['procuringEntity']

        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

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

        payload['tender']['title'] = "This field is redundant"
        payload['tender']['description'] = "This field is redundant"

        payload['tender']['awardCriteria'] = "priceOnly"
        payload['tender']['enquiryPeriod']['endDate'] = Date().enquiry_period_end_date(interval=enquiry_interval)
        payload['tender']['tenderPeriod']['endDate'] = Date().tender_period_end_date(interval=tender_interval)

        payload['tender']['lots'][0]['id'] = "update cnonpn: tender.lots.id"
        payload['tender']['lots'][0]['title'] = "update cnonpn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "update cnonpn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 4040.45
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = self.contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = self.contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "update cnonpn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "3400000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality'][
            'id'] = "3401000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"

        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['classification']['scheme'] = "CPV"
        payload['tender']['items'][0]['classification']['description'] = \
            "update cnonpn: tender.items.classification.description"
        payload['tender']['items'][0]['quantity'] = 70.00
        payload['tender']['items'][0]['unit']['id'] = "18"
        payload['tender']['items'][0]['unit']['name'] = "update cnonpn: tender.items.unit.name"
        payload['tender']['items'][0]['description'] = "update CNonPN: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "update cnonpn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "update cnonpn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")

        return payload

    def update_cnonpn_full_data_model_with_lots_items_documents_without_auction(
            self, enquiry_interval, tender_interval, quantity_of_lots_object, quantity_of_items_object,
            based_stage_release, need_to_set_permanent_id_for_lots_array=False,
            need_to_set_permanent_id_for_items_array=False, need_to_set_permanent_id_for_documents_array=False):
        payload = {
            "planning": {},
            "tender": {}
        }

        try:
            """
            Update payload dictionary.
            """
            payload['planning'].update(self.constructor.planning_object())
            payload['tender'].update(self.constructor.tender_object())
            payload['tender']['lots'] = [{}]
            payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
            payload['tender']['lots'][0]['options'] = [{}, {}]
            payload['tender']['lots'][0]['options'][0].update(self.constructor.tender_lots_option_object())
            payload['tender']['lots'][0]['options'][1].update(self.constructor.tender_lots_option_object())
            payload['tender']['lots'][0]['recurrence']['dates'] = [{}, {}]
            payload['tender']['lots'][0]['recurrence']['dates'][0].update(
                self.constructor.tender_lots_recurrence_dates_object())
            payload['tender']['lots'][0]['recurrence']['dates'][1].update(
                self.constructor.tender_lots_recurrence_dates_object())

            payload['tender']['items'] = [{}]
            payload['tender']['items'][0].update(self.constructor.tender_item_object())
            payload['tender']['items'][0]['additionalClassifications'] = [{}]
            payload['tender']['items'][0]['additionalClassifications'][0].update(
                self.constructor.buyer_additional_identifiers_object())

            payload['tender']['documents'] = [{}, {}]
            payload['tender']['documents'][0].update(self.constructor.tender_document_object())
            payload['tender']['documents'][1].update(self.constructor.tender_document_object())
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

        del payload['tender']['criteria']
        del payload['tender']['conversions']
        del payload['tender']['electronicAuctions']

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

        payload['tender']['title'] = "This field is redundant"
        payload['tender']['description'] = "This field is redundant"

        payload['planning']['rationale'] = "update cnonpn: planning.rationale"
        payload['planning']['budget']['description'] = "update cnonpn: planning.budget.description"
        payload['tender']['procurementMethodRationale'] = "update cnonpn: tender.procurementMethodRationale"
        payload['tender']['procurementMethodAdditionalInfo'] = "update cnonpn: tender.procurementMethodAdditionalInfo"
        payload['tender']['enquiryPeriod']['endDate'] = Date().enquiry_period_end_date(interval=enquiry_interval)
        payload['tender']['tenderPeriod']['endDate'] = Date().tender_period_end_date(interval=tender_interval)
        payload['tender']['procuringEntity'] = \
            GlobalClassCreatePn.actual_ms_release['releases'][0]['tender']['procuringEntity']

        payload['tender']['lots'][0]['id'] = "update cnonpn: tender.lots.id"
        payload['tender']['lots'][0]['internalId'] = "update cnonpn: tender.lots.internalId"
        payload['tender']['lots'][0]['title'] = "update cnonpn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "update cnonpn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 4040.45
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = self.contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = self.contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "update cnonpn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode'] = \
            "update cnonpn: tender.lots.placeOfPerformance.address.postalCode"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "3400000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = "3401000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "update cnonpn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"
        payload['tender']['lots'][0]['placeOfPerformance']['description'] = \
            "update cnonpn: tender.lots.placeOfPerformance.description"
        payload['tender']['lots'][0]['hasOptions'] = True
        payload['tender']['lots'][0]['options'][0]['description'] = "update CNonPN: tender.lots[0].options.description"
        payload['tender']['lots'][0]['options'][0]['period']['durationInDays'] = 180
        payload['tender']['lots'][0]['options'][0]['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['options'][0]['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][0]['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][1]['description'] = "update CNonPN: tender.lots[0].options.description"
        payload['tender']['lots'][0]['options'][1]['period']['durationInDays'] = 180
        payload['tender']['lots'][0]['options'][1]['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['options'][1]['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['options'][1]['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['hasRecurrence'] = True
        payload['tender']['lots'][0]['recurrence']['dates'][0]['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['recurrence']['dates'][1]['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['recurrence']['description'] = "update CNonPN: tender.lots.recurrence.description"
        payload['tender']['lots'][0]['hasRenewal'] = True
        payload['tender']['lots'][0]['renewal']['description'] = "update CNonPN: tender.lots.renewal.description"
        payload['tender']['lots'][0]['renewal']['minimumRenewals'] = 1
        payload['tender']['lots'][0]['renewal']['maximumRenewals'] = 4
        payload['tender']['lots'][0]['renewal']['period']['durationInDays'] = 364
        payload['tender']['lots'][0]['renewal']['period']['startDate'] = self.duration_period[0]
        payload['tender']['lots'][0]['renewal']['period']['endDate'] = self.duration_period[1]
        payload['tender']['lots'][0]['renewal']['period']['maxExtentDate'] = self.duration_period[1]
        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['internalId'] = "update cnonpn: tender.items.internalId"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['classification']['scheme'] = "CPV"
        payload['tender']['items'][0]['classification']['description'] = \
            "update cnonpn: tender.items.classification.description"
        payload['tender']['items'][0]['quantity'] = 70.00
        payload['tender']['items'][0]['unit']['id'] = "18"
        payload['tender']['items'][0]['unit']['name'] = "update cnonpn: tender.items.unit.name"
        payload['tender']['items'][0]['additionalClassifications'][0]['id'] = "AA06-6"
        payload['tender']['items'][0]['additionalClassifications'][0]['scheme'] = "CPVS"
        payload['tender']['items'][0]['additionalClassifications'][0]['description'] = \
            "update cnonpn: tender.items.additionalClassifications.description"
        payload['tender']['items'][0]['description'] = "update CNonPN: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "update cnonpn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "update cnonpn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        payload['tender']['documents'][1]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][1]['id'] = self.document_two_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][1]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][1]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][1]['relatedLots'] = [payload['tender']['lots'][1]['id']]
        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")

        return payload

    def update_cnonpn_obligatory_data_model_with_lots_items_documents_with_auction(
            self, enquiry_interval, tender_interval, quantity_of_lots_object, quantity_of_items_object,
            based_stage_release, need_to_set_permanent_id_for_lots_array=False,
            need_to_set_permanent_id_for_items_array=False, need_to_set_permanent_id_for_documents_array=False,
            need_to_set_permanent_id_for_electronic_auction=False):

        payload = {
            "tender": {}
        }

        try:
            """
            Update payload dictionary.
            """
            payload['tender'].update(self.constructor.tender_object())
            payload['tender']['electronicAuctions']['details'] = [{}, {}]
            payload['tender']['electronicAuctions']['details'][0].update(
                self.constructor.tender_electronic_auctions_details_object())
            payload['tender']['electronicAuctions']['details'][0]['electronicAuctionModalities'] = [{}]
            payload['tender']['electronicAuctions']['details'][0]['electronicAuctionModalities'][0].update(
                self.constructor.tender_electronic_auctions_details_electronic_auction_modalities_object())
            payload['tender']['electronicAuctions']['details'][1].update(
                self.constructor.tender_electronic_auctions_details_object())
            payload['tender']['electronicAuctions']['details'][1]['electronicAuctionModalities'] = [{}]
            payload['tender']['electronicAuctions']['details'][1]['electronicAuctionModalities'][0].update(
                self.constructor.tender_electronic_auctions_details_electronic_auction_modalities_object())
            payload['tender']['lots'] = [{}]
            payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
            payload['tender']['items'] = [{}]
            payload['tender']['items'][0].update(self.constructor.tender_item_object())
            payload['tender']['items'][0]['additionalClassifications'] = [{}]
            payload['tender']['items'][0]['additionalClassifications'][0].update(
                self.constructor.buyer_additional_identifiers_object())
            payload['tender']['documents'] = [{}, {}]
            payload['tender']['documents'][0].update(self.constructor.tender_document_object())
            payload['tender']['documents'][1].update(self.constructor.tender_document_object())

            del payload['tender']['procurementMethodRationale']
            del payload['tender']['procurementMethodAdditionalInfo']
            del payload['tender']['procurementMethodModalities']
            del payload['tender']['criteria']
            del payload['tender']['conversions']
            del payload['tender']['lots'][0]['internalId']
            del payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode']
            del payload['tender']['lots'][0]['placeOfPerformance']['description']
            del payload['tender']['lots'][0]['hasOptions']
            del payload['tender']['lots'][0]['options']
            del payload['tender']['lots'][0]['hasRecurrence']
            del payload['tender']['lots'][0]['recurrence']
            del payload['tender']['lots'][0]['hasRenewal']
            del payload['tender']['lots'][0]['renewal']
            del payload['tender']['items'][0]['internalId']
            del payload['tender']['items'][0]['additionalClassifications']
            del payload['tender']['procuringEntity']

        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

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

        payload['tender']['title'] = "This field is redundant"
        payload['tender']['description'] = "This field is redundant"

        payload['tender']['awardCriteria'] = "priceOnly"
        payload['tender']['enquiryPeriod']['endDate'] = Date().enquiry_period_end_date(interval=enquiry_interval)
        payload['tender']['tenderPeriod']['endDate'] = Date().tender_period_end_date(interval=tender_interval)

        payload['tender']['lots'][0]['id'] = "update cnonpn: tender.lots.id"
        payload['tender']['lots'][0]['title'] = "update cnonpn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "update cnonpn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 4040.45
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = self.contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = self.contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "update cnonpn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "3400000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality'][
            'id'] = "3401000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"

        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['classification']['scheme'] = "CPV"
        payload['tender']['items'][0]['classification']['description'] = \
            "update cnonpn: tender.items.classification.description"
        payload['tender']['items'][0]['quantity'] = 70.00
        payload['tender']['items'][0]['unit']['id'] = "18"
        payload['tender']['items'][0]['unit']['name'] = "update cnonpn: tender.items.unit.name"
        payload['tender']['items'][0]['description'] = "update CNonPN: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "update cnonpn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "update cnonpn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        payload['tender']['documents'][1]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][1]['id'] = self.document_two_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][1]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][1]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][1]['relatedLots'] = [payload['tender']['lots'][1]['id']]

        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")

        payload['tender']['electronicAuctions']['details'][0]['id'] = "0"
        payload['tender']['electronicAuctions']['details'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['electronicAuctions']['details'][0]['electronicAuctionModalities'][0][
            'eligibleMinimumDifference']['amount'] = 40.00
        payload['tender']['electronicAuctions']['details'][0]['electronicAuctionModalities'][0][
            'eligibleMinimumDifference']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['electronicAuctions']['details'][1]['id'] = "1"
        payload['tender']['electronicAuctions']['details'][1]['relatedLot'] = payload['tender']['lots'][1]['id']
        payload['tender']['electronicAuctions']['details'][1]['electronicAuctionModalities'][0][
            'eligibleMinimumDifference']['amount'] = 40.00
        payload['tender']['electronicAuctions']['details'][1]['electronicAuctionModalities'][0][
            'eligibleMinimumDifference']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']

        try:
            """
            Set permanent id for electronicAuctions.details array.
            """
            if need_to_set_permanent_id_for_electronic_auction is True:
                payload['tender']['electronicAuctions']['details'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender'][
                        'electronicAuctions']['details'],
                    payload_array=payload['tender']['electronicAuctions']['details'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for electronicAuctions.details array."
                           "Key 'electronicAuctions.details' was not found.")

        return payload

    def create_cnonpn_obligatory_data_model_with_lots_items_documents_auction(
            self, enquiry_interval, tender_interval, quantity_of_lots_object, quantity_of_items_object,
            based_stage_release, need_to_set_permanent_id_for_lots_array=False,
            need_to_set_permanent_id_for_items_array=False, need_to_set_permanent_id_for_documents_array=False):
        payload = {
            "tender": {}
        }

        try:
            """
            Update payload dictionary.
            """
            payload['tender'].update(self.constructor.tender_object())
            payload['tender']['lots'] = [{}]
            payload['tender']['lots'][0].update(self.constructor.tender_lots_object())
            payload['tender']['items'] = [{}]
            payload['tender']['items'][0].update(self.constructor.tender_item_object())
            payload['tender']['items'][0]['additionalClassifications'] = [{}]
            payload['tender']['items'][0]['additionalClassifications'][0].update(
                self.constructor.buyer_additional_identifiers_object())
            payload['tender']['documents'] = [{}]
            payload['tender']['documents'][0].update(self.constructor.tender_document_object())

            del payload['tender']['procurementMethodRationale']
            del payload['tender']['procurementMethodAdditionalInfo']
            del payload['tender']['criteria']
            del payload['tender']['conversions']
            del payload['tender']['lots'][0]['internalId']
            del payload['tender']['lots'][0]['placeOfPerformance']['address']['postalCode']
            del payload['tender']['lots'][0]['placeOfPerformance']['description']
            del payload['tender']['lots'][0]['hasOptions']
            del payload['tender']['lots'][0]['options']
            del payload['tender']['lots'][0]['hasRecurrence']
            del payload['tender']['lots'][0]['recurrence']
            del payload['tender']['lots'][0]['hasRenewal']
            del payload['tender']['lots'][0]['renewal']
            del payload['tender']['items'][0]['internalId']
            del payload['tender']['items'][0]['additionalClassifications']
            del payload['tender']['procuringEntity']

        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

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

        payload['tender']['awardCriteria'] = "priceOnly"
        payload['tender']['enquiryPeriod']['endDate'] = Date().enquiry_period_end_date(interval=enquiry_interval)
        payload['tender']['tenderPeriod']['endDate'] = Date().tender_period_end_date(interval=tender_interval)

        payload['tender']['lots'][0]['id'] = "create cnonpn: tender.lots.id"
        payload['tender']['lots'][0]['title'] = "create cnonpn: tender.lots.title"
        payload['tender']['lots'][0]['description'] = "create cnonpn: tender.lots.description"
        payload['tender']['lots'][0]['value']['amount'] = 4000.05
        payload['tender']['lots'][0]['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        payload['tender']['lots'][0]['contractPeriod']['startDate'] = self.contact_period[0]
        payload['tender']['lots'][0]['contractPeriod']['endDate'] = self.contact_period[1]
        payload['tender']['lots'][0]['placeOfPerformance']['address']['streetAddress'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.streetAddress"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['country']['id'] = "MD"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = "1700000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
            "create cnonpn: tender.lots.placeOfPerformance.address.addressDetails.locality.description"
        payload['tender']['lots'][0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
            "CUATM"

        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'][0]['id'] = "0"
        payload['tender']['items'][0]['classification']['id'] = item_classification_id
        payload['tender']['items'][0]['classification']['scheme'] = "CPV"
        payload['tender']['items'][0]['classification']['description'] = \
            "create cnonpn: tender.items.classification.description"
        payload['tender']['items'][0]['quantity'] = 60.00
        payload['tender']['items'][0]['unit']['id'] = "20"
        payload['tender']['items'][0]['unit']['name'] = "create cnonpn: tender.items.unit.name"
        payload['tender']['items'][0]['description'] = "create CNonPN: tender.items.description"
        payload['tender']['items'][0]['relatedLot'] = payload['tender']['lots'][0]['id']
        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        for ql in range(quantity_of_lots_object):
            payload['tender']['electronicAuctions']['details'].append(
                self.constructor.tender_electronic_auctions_details_object())
            payload['tender']['electronicAuctions']['details'][ql]['electronicAuctionModalities'].append(
                self.constructor.tender_electronic_auctions_details_electronic_auction_modalities_object())
            payload['tender']['electronicAuctions']['details'][ql]['id'] = str(ql)
            payload['tender']['electronicAuctions']['details'][ql]['relatedLot'] = \
                payload['tender']['lots'][ql]['id']
            payload['tender']['electronicAuctions']['details'][ql]['electronicAuctionModalities'][0][
                'eligibleMinimumDifference']['amount'] = 10.00
            payload['tender']['electronicAuctions']['details'][ql]['electronicAuctionModalities'][0][
                'eligibleMinimumDifference']['currency'] = \
                GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']

        payload['tender']['documents'][0]['documentType'] = f"{random.choice(documentType)}"
        payload['tender']['documents'][0]['id'] = self.document_one_was_uploaded[0]["data"]["id"]
        payload['tender']['documents'][0]['title'] = "create cnonpn: tender.documents.title"
        payload['tender']['documents'][0]['description'] = "create cnonpn: tender.documents.description"
        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=based_stage_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")
        return payload
