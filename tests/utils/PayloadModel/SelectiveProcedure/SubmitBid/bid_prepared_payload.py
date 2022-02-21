import copy
import json

from tests.utils.PayloadModel.SelectiveProcedure.SubmitBid.bid_payload_library import PayloadLibrary
from tests.utils.date_class import Date
from tests.utils.iStorage import Document


class BidPreparePayload:
    def __init__(self, host_for_services):
        self.constructor = copy.deepcopy(PayloadLibrary())
        document_one = Document(host_for_services, file_name="API.pdf")
        self.document_one_was_uploaded = document_one.uploading_document()
        self.document_two_was_uploaded = document_one.uploading_document()
        self.document_three_was_uploaded = document_one.uploading_document()
        self.document_four_was_uploaded = document_one.uploading_document()
        self.document_five_was_uploaded = document_one.uploading_document()
        self.document_six_was_uploaded = document_one.uploading_document()
        self.document_seven_was_uploaded = document_one.uploading_document()
        self.document_eight_was_uploaded = document_one.uploading_document()
        self.document_nine_was_uploaded = document_one.uploading_document()
        self.document_ten_was_uploaded = document_one.uploading_document()
        self.date = Date()

    def create_bid_obligatory_data_model(
            self, based_stage_release, submission_payload):
        payload = {
            "bid": {}
        }
        try:
            """
            Update payload dictionary.
            """
            payload['bid'].update(
                self.constructor.bid_object()
            )

            del payload['bid']['requirementResponses']
            del payload['bid']['documents']
            del payload['bid']['items']
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

        payload['bid']['value']['amount'] = \
            based_stage_release['releases'][0]['tender']['lots'][0]['value']['amount']
        payload['bid']['value']['currency'] = \
            based_stage_release['releases'][0]['tender']['lots'][0]['value']['currency']
        payload['bid']['relatedLots'].append(based_stage_release['releases'][0]['tender']['lots'][0]['id'])

        for i in range(len(submission_payload['submission']['candidates'])):
            tenderer_object = self.constructor.tenderers_object()

            del tenderer_object['identifier']['uri']
            del tenderer_object['additionalIdentifiers']
            del tenderer_object['address']['postalCode']
            del tenderer_object['contactPoint']['faxNumber']
            del tenderer_object['contactPoint']['url']
            del tenderer_object['persones']
            del tenderer_object['details']['mainEconomicActivities']
            del tenderer_object['details']['permits']
            del tenderer_object['details']['bankAccounts']
            del tenderer_object['details']['legalForm']
            del tenderer_object['details']['typeOfSupplier']

            tenderer_object['name'] = submission_payload['submission']['candidates'][i]['name']

            tenderer_object['identifier']['id'] = submission_payload['submission']['candidates'][i]['identifier']['id']

            tenderer_object['identifier']['legalName'] = \
                submission_payload['submission']['candidates'][i]['identifier']['legalName']

            tenderer_object['identifier']['scheme'] = \
                submission_payload['submission']['candidates'][i]['identifier']['scheme']

            tenderer_object['address']['streetAddress'] = \
                submission_payload['submission']['candidates'][i]['address']['streetAddress']

            tenderer_object['address']['addressDetails']['country']['id'] = \
                submission_payload['submission']['candidates'][i]['address']['addressDetails']['country']['id']

            tenderer_object['address']['addressDetails']['country']['description'] = \
                submission_payload['submission']['candidates'][i]['address']['addressDetails']['country']['description']

            tenderer_object['address']['addressDetails']['country']['scheme'] = \
                submission_payload['submission']['candidates'][i]['address']['addressDetails']['country']['scheme']

            tenderer_object['address']['addressDetails']['region']['id'] = \
                submission_payload['submission']['candidates'][i]['address']['addressDetails']['region']['id']

            tenderer_object['address']['addressDetails']['region']['description'] = \
                submission_payload['submission']['candidates'][i]['address']['addressDetails']['region']['description']

            tenderer_object['address']['addressDetails']['region']['scheme'] = \
                submission_payload['submission']['candidates'][i]['address']['addressDetails']['region']['scheme']

            tenderer_object['address']['addressDetails']['locality']['id'] = \
                submission_payload['submission']['candidates'][i]['address']['addressDetails']['locality']['id']

            tenderer_object['address']['addressDetails']['locality']['description'] = \
                submission_payload['submission']['candidates'][i]['address']['addressDetails']['locality'][
                    'description']

            tenderer_object['address']['addressDetails']['locality']['scheme'] = \
                submission_payload['submission']['candidates'][i]['address']['addressDetails']['locality']['scheme']

            tenderer_object['contactPoint']['name'] = \
                submission_payload['submission']['candidates'][i]['contactPoint']['name']

            tenderer_object['contactPoint']['email'] = \
                submission_payload['submission']['candidates'][i]['contactPoint']['email']

            tenderer_object['contactPoint']['telephone'] = \
                submission_payload['submission']['candidates'][i]['contactPoint']['telephone']

            tenderer_object['details']['scale'] = \
                submission_payload['submission']['candidates'][i]['details']['scale']

            payload['bid']['tenderers'].append(tenderer_object)

        return payload
