import copy
import json
import random

from tests.utils.PayloadModel.Budget.Ei.ei_payload_library import ExpenditureItemConstructorPayload
from tests.utils.data_of_enum import cpv_category, cpv_goods_high_level, cpv_works_high_level, \
    cpv_services_high_level, typeOfBuyer, mainGeneralActivity, mainSectoralActivity, currency, locality_scheme
from tests.utils.date_class import Date


class ExpenditureItemPayload:
    def __init__(
            self, is_tender_description=False, is_tender_items_array=False, quantity_of_tender_items_objects=1,
            is_tender_items_additionalclassifications_array=False,
            quantity_of_tender_items_additionalclassifications_objects=1,
            is_tender_items_deliveryaddress_postalcode=False,
            is_tender_items_deliveryaddress_addressdetails_locality_uri=False,
            is_planning_rationale=False, is_buyer_identifier_uri=False, is_buyer_address_postalcode=False,
            is_buyer_address_addressdetails_locality_uri=False, is_buyer_additionalidentifiers_array=False,
            quantity_of_buyer_additionalidentifiers_array=1, is_buyer_contactpoint_faxnumber=False,
            is_buyer_contactpoint_url=False, is_buyer_details=False, is_buyer_details_typeofbuyer=False,
            is_buyer_details_maingeneralactivity=False, is_buyer_details_mainsectoralactivity=False):

        self.tender_description = is_tender_description
        self.is_tender_items_array = is_tender_items_array
        self.quantity_of_tender_items_objects = quantity_of_tender_items_objects
        self.is_tender_items_additionalclassifications_array = is_tender_items_additionalclassifications_array

        self.quantity_of_tender_items_additionalclassifications_objects = \
            quantity_of_tender_items_additionalclassifications_objects

        self.is_tender_items_deliveryaddress_postalcode = is_tender_items_deliveryaddress_postalcode
        self.is_tender_items_addressdetails_locality_uri = is_tender_items_deliveryaddress_addressdetails_locality_uri
        self.is_planning_rationale = is_planning_rationale
        self.is_buyer_identifier_uri = is_buyer_identifier_uri
        self.is_buyer_address_postalcode = is_buyer_address_postalcode
        self.is_buyer_address_addressdetails_locality_uri = is_buyer_address_addressdetails_locality_uri
        self.is_buyer_additionalidentifiers_array = is_buyer_additionalidentifiers_array
        self.quantity_of_buyer_additionalidentifiers_array = quantity_of_buyer_additionalidentifiers_array
        self.is_buyer_contactpoint_faxnumber = is_buyer_contactpoint_faxnumber
        self.is_buyer_contactpoint_url = is_buyer_contactpoint_url
        self.is_buyer_details = is_buyer_details
        self.is_buyer_details_typeofbuyer = is_buyer_details_typeofbuyer
        self.is_buyer_details_maingeneralactivity = is_buyer_details_maingeneralactivity
        self.is_buyer_details_mainsectoralactivity = is_buyer_details_mainsectoralactivity

        self.currency = f"{random.choice(currency)}"

    def create_expenditure_item(self):

        ei_period = Date().expenditure_item_period()



        try:
            """
            Prepare payload with optional value.
            """
            if self.tender_description is True:
                payload['tender']['description'] = "create ei: tender.description"
            else:
                del payload['tender']['description']

            if self.is_tender_items_array is True:
                payload['tender']['items'] = list()
                for item in range(self.quantity_of_tender_items_objects):
                    payload['tender']['items'].append(constructor.tender_items_object())

                    payload['tender']['items'][item]['id'] = f"{item}"
                    payload['tender']['items'][item]['description'] = f"create ei: tender.items{item}.description"
                    payload['tender']['items'][item]['classification']['id'] = tender_classification_id

                    payload['tender']['items'][item]['deliveryAddress']['streetAddress'] = \
                        f"create ei: tender.items{item}.deliveryAddress.streetAddress"

                    payload['tender']['items'][item]['deliveryAddress']['addressDetails']['country']['id'] = "MD"
                    payload['tender']['items'][item]['deliveryAddress']['addressDetails']['region']['id'] = "1700000"

                    payload['tender']['items'][item]['deliveryAddress']['addressDetails']['locality']['scheme'] = \
                        f"{random.choice(locality_scheme)}"

                    payload['tender']['items'][item]['deliveryAddress']['addressDetails']['locality']['id'] = \
                        "1701000"

                    payload['tender']['items'][item]['deliveryAddress']['addressDetails']['locality'][
                        'description'] = \
                        f"create ei: tender.items{item}.deliveryAddress.addressDetails.locality.description"

                    payload['tender']['items'][item]['deliveryAddress']['addressDetails']['locality']['uri'] = \
                        f"create ei: tender.items{item}.deliveryAddress.addressDetails.locality.uri"

                    payload['tender']['items'][item]['quantity'] = 10
                    payload['tender']['items'][item]['unit']['id'] = "10"

                    if self.is_tender_items_additionalclassifications_array is True:
                        payload['tender']['items'][item]['additionalClassifications'] = list()
                        for classification in range(self.quantity_of_tender_items_additionalclassifications_objects):
                            payload['tender']['items'][item]['additionalClassifications'].append(
                                constructor.tender_items_additionalclassifications_object())

                            payload['tender']['items'][item]['additionalClassifications'][classification]['id'] = \
                                "AA12-4"
                    else:
                        del payload['tender']['items'][item]['additionalClassifications']

                    if self.is_tender_items_deliveryaddress_postalcode is True:

                        payload['tender']['items'][item]['deliveryAddress']['postalCode'] = \
                            f"create ei: tender.items{item}.deliveryAddress.postalCode"
                    else:
                        del payload['tender']['items'][item]['deliveryAddress']['postalCode']

                    if self.is_buyer_address_addressdetails_locality_uri is True:

                        payload['tender']['items'][item]['deliveryAddress']['addressDetails'][
                            'locality']['uri'] = \
                            f"create ei: tender.items{item}.deliveryAddress.addressDetails.locality.uri"
                    else:
                        del payload['tender']['items'][item]['deliveryAddress']['addressDetails'][
                            'locality']['uri']
            else:
                del payload['tender']['items']

            if self.is_planning_rationale is True:
                payload['planning']['rationale'] = "create ei: planning.rationale"
            else:
                del payload['planning']['rationale']

            if self.is_buyer_identifier_uri is True:
                payload['buyer']['identifier']['uri'] = "create ei: buyer.identifier.uri"
            else:
                del payload['buyer']['identifier']['uri']

            if self.is_buyer_address_postalcode is True:
                payload['buyer']['address']['postalCode'] = "create ei: buyer.address.postalCode"
            else:
                del payload['buyer']['address']['postalCode']

            if self.is_buyer_additionalidentifiers_array is True:
                payload['buyer']['additionalIdentifiers'] = list()
                for identifier in range(self.quantity_of_buyer_additionalidentifiers_array):

                    payload['buyer']['additionalIdentifiers'].append(
                        constructor.buyer_additionalidentifiers_object())

                    payload['buyer']['additionalIdentifiers'][identifier]['id'] = \
                        f"create ei buyer.additionalIdentifiers{identifier}.id"

                    payload['buyer']['additionalIdentifiers'][identifier]['scheme'] = \
                        f"create ei: buyer.additionalIdentifiers{identifier}.scheme"

                    payload['buyer']['additionalIdentifiers'][identifier]['legalName'] = \
                        f"create ei: buyer.additionalIdentifiers{identifier}.legalName"

                    if self.is_tender_items_addressdetails_locality_uri is True:
                        payload['buyer']['additionalIdentifiers'][identifier]['uri'] = \
                            f"create ei: buyer.additionalIdentifiers{identifier}.uri"
                    else:
                        del payload['buyer']['additionalIdentifiers'][identifier]['uri']
            else:
                del payload['buyer']['additionalIdentifiers']

            if self.is_buyer_contactpoint_faxnumber is True:
                payload['buyer']['contactPoint']['faxNumber'] = "create ei: buyer.contactPoint.faxNumber"
            else:
                del payload['buyer']['contactPoint']['faxNumber']

            if self.is_buyer_contactpoint_url is True:
                payload['buyer']['contactPoint']['url'] = "create ei: buyer.contactPoint.url"
            else:
                del payload['buyer']['contactPoint']['url']

            if self.is_buyer_details is True:
                if self.is_buyer_details_typeofbuyer is True:
                    payload['buyer']['details']['typeOfBuyer'] = f"{random.choice(typeOfBuyer)}"
                else:
                    del payload['buyer']['details']['typeOfBuyer']

                if self.is_buyer_details_maingeneralactivity is True:
                    payload['buyer']['details']['mainGeneralActivity'] = f"{random.choice(mainGeneralActivity)}"
                else:
                    del payload['buyer']['details']['mainGeneralActivity']

                if self.is_buyer_details_mainsectoralactivity is True:

                    payload['buyer']['details']['mainSectoralActivity'] = f"{random.choice(mainSectoralActivity)}"
                else:
                    del payload['buyer']['details']['mainSectoralActivity']

                payload['buyer']['contactPoint']['url'] = "create ei: buyer.contactPoint.url"
            else:
                del payload['buyer']['details']
        except KeyError:
            raise KeyError("Impossible to prepare payload with optional value.")
        return payload
