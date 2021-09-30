import copy
import random

from tests.utils.PayloadModel.EnquiryPeriod.enquiry_payload_library import PayloadLibrary
from tests.utils.data_of_enum import locality_scheme, scale


class EnquiryPreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())

    def create_enquiry_full_data_model(self, based_stage_release):
        payload = {}

        try:
            """
            Update payload dictionary.
            """
            payload.update(self.constructor.enquiry_object())
            payload['enquiry']['author']['additionalIdentifiers'] = [{}, {}]
            payload['enquiry']['author']['additionalIdentifiers'][0].update(
                self.constructor.enquiry_author_additional_identifiers_object())

            payload['enquiry']['author']['additionalIdentifiers'][1].update(
                self.constructor.enquiry_author_additional_identifiers_object())
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

        payload['enquiry']['author']['name'] = "create enquiry: enquiry.author.name"
        payload['enquiry']['author']['identifier']['scheme'] = "MD-IDNO"
        payload['enquiry']['author']['identifier']['id'] = "create enquiry: enquiry.author.identifier.id"
        payload['enquiry']['author']['identifier']['legalName'] = "create enquiry: enquiry.author.identifier.legalName"
        payload['enquiry']['author']['identifier']['uri'] = "create enquiry: enquiry.author.identifier.uri"
        payload['enquiry']['author']['additionalIdentifiers'][0]['scheme'] = \
            "create enquiry: enquiry.author.additionalIdentifiers.scheme"
        payload['enquiry']['author']['additionalIdentifiers'][0]['id'] = \
            "create enquiry: enquiry.author.additionalIdentifiers.id"
        payload['enquiry']['author']['additionalIdentifiers'][0]["legalName"] = \
            "create enquiry: enquiry.author.additionalIdentifiers.legalName"
        payload['enquiry']['author']['additionalIdentifiers'][0]["uri"] = \
            "create enquiry: enquiry.author.additionalIdentifiers.uri"
        payload['enquiry']['author']['additionalIdentifiers'][1]['scheme'] = \
            "create enquiry: enquiry.author.additionalIdentifiers.scheme"
        payload['enquiry']['author']['additionalIdentifiers'][1]['id'] = \
            "create enquiry: enquiry.author.additionalIdentifiers.id"
        payload['enquiry']['author']['additionalIdentifiers'][1]["legalName"] = \
            "create enquiry: enquiry.author.additionalIdentifiers.legalName"
        payload['enquiry']['author']['additionalIdentifiers'][1]["uri"] = \
            "create enquiry: enquiry.author.additionalIdentifiers.uri"
        payload['enquiry']['author']['address']['streetAddress'] = \
            "create enquiry: enquiry.author.address.streetAddress"
        payload['enquiry']['author']['address']['postalCode'] = \
            "create enquiry: enquiry.author.address.postalCode"
        payload['enquiry']['author']['address']['addressDetails']['country']['id'] = "MD"
        payload['enquiry']['author']['address']['addressDetails']['region']['id'] = "1700000"
        payload['enquiry']['author']['address']['addressDetails']['locality']['scheme'] = \
            random.choice(locality_scheme)
        payload['enquiry']['author']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['enquiry']['author']['address']['addressDetails']['locality']['description'] = \
            "create enquiry: enquiry.author.address.addressDetails.locality.description"
        payload['enquiry']['author']['details']['scale'] = random.choice(scale)
        payload['enquiry']['author']['contactPoint']['name'] = "create enquiry: enquiry.author.contactPoint.name"
        payload['enquiry']['author']['contactPoint']['email'] = "create enquiry: enquiry.author.contactPoint.email"
        payload['enquiry']['author']['contactPoint']['telephone'] = \
            "create enquiry: enquiry.author.contactPoint.telephone"
        payload['enquiry']['author']['contactPoint']['faxNumber'] = \
            "create enquiry: enquiry.author.contactPoint.faxNumber"
        payload['enquiry']['author']['contactPoint']['url'] = "create enquiry: enquiry.author.contactPoint.url"
        payload['enquiry']['title'] = "create enquiry: enquiry.author.title"
        payload['enquiry']["description"] = "create enquiry: enquiry.author.description"
        payload['enquiry']["relatedLot"] = based_stage_release['releases'][0]['tender']['lots'][0]['id']

        return payload

    def create_enquiry_obligatory_data_model(self):
        payload = {}

        try:
            """
            Update payload dictionary.
            """
            payload.update(self.constructor.enquiry_object())
            payload['enquiry']['author']['additionalIdentifiers'] = [{}, {}]
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

        del payload['enquiry']['author']['additionalIdentifiers']
        del payload['enquiry']['author']['address']['postalCode']
        del payload['enquiry']['author']['contactPoint']['faxNumber']
        del payload['enquiry']['author']['contactPoint']['url']
        del payload['enquiry']["relatedLot"]

        payload['enquiry']['author']['name'] = "create enquiry: enquiry.author.name"
        payload['enquiry']['author']['identifier']['scheme'] = "MD-IDNO"
        payload['enquiry']['author']['identifier']['id'] = "create enquiry: enquiry.author.identifier.id"
        payload['enquiry']['author']['identifier']['legalName'] = "create enquiry: enquiry.author.identifier.legalName"
        payload['enquiry']['author']['identifier']['uri'] = "create enquiry: enquiry.author.identifier.uri"
        payload['enquiry']['author']['address']['streetAddress'] = \
            "create enquiry: enquiry.author.address.streetAddress"
        payload['enquiry']['author']['address']['addressDetails']['country']['id'] = "MD"
        payload['enquiry']['author']['address']['addressDetails']['region']['id'] = "1700000"
        payload['enquiry']['author']['address']['addressDetails']['locality']['scheme'] = \
            random.choice(locality_scheme)
        payload['enquiry']['author']['address']['addressDetails']['locality']['id'] = "1701000"
        payload['enquiry']['author']['address']['addressDetails']['locality']['description'] = \
            "create enquiry: enquiry.author.address.addressDetails.locality.description"
        payload['enquiry']['author']['details']['scale'] = random.choice(scale)
        payload['enquiry']['author']['contactPoint']['name'] = "create enquiry: enquiry.author.contactPoint.name"
        payload['enquiry']['author']['contactPoint']['email'] = "create enquiry: enquiry.author.contactPoint.email"
        payload['enquiry']['author']['contactPoint']['telephone'] = \
            "create enquiry: enquiry.author.contactPoint.telephone"
        payload['enquiry']['title'] = "create enquiry: enquiry.author.title"
        payload['enquiry']["description"] = "create enquiry: enquiry.author.description"
        return payload