import copy
import random
from tests.utils.PayloadModel.SubmitBid.bid_payload_library import PayloadLibrary
from tests.utils.data_of_enum import scale, documentType_for_bid, person_title, type_of_supplier
from tests.utils.date_class import Date
from tests.utils.functions import generate_requirement_response_array
from tests.utils.iStorage import Document


class BidPreparePayload:
    def __init__(self):
        self.constructor = copy.deepcopy(PayloadLibrary())
        document_one = Document("API.pdf")
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
        # document_one = Document("API.pdf")
        # self.document_one_was_uploaded = document_one.uploading_document()
        # self.document_two_was_uploaded = document_one.uploading_document()
        # self.standard_criteria = MdmService.get_standard_criteria(
        #     country=GlobalClassMetadata.country,
        #     language=GlobalClassMetadata.language)
        # self.contact_period = Date().contact_period()
        # self.duration_period = Date().duration_period()

    def create_bid_full_data_model(
            self, based_stage_release):
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
            payload['bid']['requirementResponses'] = [
                {}
            ]
            payload['bid']['requirementResponses'][0].update(
                self.constructor.requirement_response()
            )
            payload['bid']['requirementResponses'][0]['evidences'] = [
                {}, {}
            ]
            payload['bid']['requirementResponses'][0]['evidences'][0].update(
                self.constructor.evidence_object()
            )
            payload['bid']['requirementResponses'][0]['evidences'][1].update(
                self.constructor.evidence_object()
            )

            payload['bid']['tenderers'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0].update(
                self.constructor.tenderers_object()
            )
            payload['bid']['tenderers'][0]['additionalIdentifiers'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['additionalIdentifiers'][0].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][0]['additionalIdentifiers'][1].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][0]['persones'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['persones'][0].update(
                self.constructor.person_object()
            )
            payload['bid']['tenderers'][0]['persones'][1].update(
                self.constructor.person_object()
            )

            payload['bid']['tenderers'][0]['details']['mainEconomicActivities'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][0].update(
                self.constructor.main_economic_activities_object()
            )
            payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][1].update(
                self.constructor.main_economic_activities_object()
            )
            payload['bid']['tenderers'][0]['details']['mainEconomicActivities'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][0].update(
                self.constructor.main_economic_activities_object()
            )
            payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][1].update(
                self.constructor.main_economic_activities_object()
            )
            payload['bid']['tenderers'][0]['details']['permits'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['details']['permits'][0].update(
                self.constructor.permit_object()
            )
            payload['bid']['tenderers'][0]['details']['permits'][1].update(
                self.constructor.permit_object()
            )
            payload['bid']['tenderers'][0]['details']['bankAccounts'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['details']['bankAccounts'][0].update(
                self.constructor.bank_account_object()
            )
            payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][0]['details']['bankAccounts'][1].update(
                self.constructor.bank_account_object()
            )
            payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0].update(
                self.constructor.business_function_object()
            )
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][1].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1].update(
                self.constructor.business_function_object()
            )
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][1].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0].update(
                self.constructor.business_function_object()
            )
            payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][1].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1].update(
                self.constructor.business_function_object()
            )
            payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][1].update(
                self.constructor.document_object()
            )
            # =========
            payload['bid']['tenderers'][1].update(
                self.constructor.tenderers_object()
            )
            payload['bid']['tenderers'][1]['additionalIdentifiers'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['additionalIdentifiers'][0].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][1]['additionalIdentifiers'][1].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][1]['persones'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['persones'][0].update(
                self.constructor.person_object()
            )
            payload['bid']['tenderers'][1]['persones'][1].update(
                self.constructor.person_object()
            )

            payload['bid']['tenderers'][1]['details']['mainEconomicActivities'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][0].update(
                self.constructor.main_economic_activities_object()
            )
            payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][1].update(
                self.constructor.main_economic_activities_object()
            )
            payload['bid']['tenderers'][1]['details']['mainEconomicActivities'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][0].update(
                self.constructor.main_economic_activities_object()
            )
            payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][1].update(
                self.constructor.main_economic_activities_object()
            )
            payload['bid']['tenderers'][1]['details']['permits'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['details']['permits'][0].update(
                self.constructor.permit_object()
            )
            payload['bid']['tenderers'][1]['details']['permits'][1].update(
                self.constructor.permit_object()
            )
            payload['bid']['tenderers'][1]['details']['bankAccounts'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['details']['bankAccounts'][0].update(
                self.constructor.bank_account_object()
            )
            payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][1]['details']['bankAccounts'][1].update(
                self.constructor.bank_account_object()
            )
            payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0].update(
                self.constructor.business_function_object()
            )
            payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][1].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1].update(
                self.constructor.business_function_object()
            )
            payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][1].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0].update(
                self.constructor.business_function_object()
            )
            payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][1].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1].update(
                self.constructor.business_function_object()
            )
            payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'] = [
                {}, {}
            ]
            payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][1].update(
                self.constructor.document_object()
            )
            # =========
            payload['bid']['relatedLots'] = [
                {}
            ]
            payload['bid']['documents'] = [
                {}, {}
            ]
            payload['bid']['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['documents'][1].update(
                self.constructor.document_object()
            )

            del payload['bid']['items']
            # payload['bid']['items'] = [
            #     {}
            # ]
            # payload['bid']['items'][0].update(
            #     self.constructor.item_object()
            # )

        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

        payload['bid']['value']['amount'] = \
            based_stage_release['releases'][0]['tender']['lots'][0]['value']['amount'] + \
            based_stage_release['releases'][0]['tender']['lots'][1]['value']['amount']
        payload['bid']['value']['currency'] = \
            based_stage_release['releases'][0]['tender']['lots'][0]['value']['currency']
        payload['bid']['relatedLots'][0] = based_stage_release['releases'][0]['tender']['lots'][0]['id']
        payload['bid']['tenderers'][0]['name'] = "tenderers.name: 0"
        payload['bid']['tenderers'][0]['identifier']['id'] = "tenderers.identifier.id: 0"
        payload['bid']['tenderers'][0]['identifier']['legalName'] = "tenderers.identifier.legalName: 0"
        payload['bid']['tenderers'][0]['identifier']['scheme'] = "MD-IDNO"
        payload['bid']['tenderers'][0]['identifier']['uri'] = "tenderers.identifier.uri: 0"
        payload['bid']['tenderers'][0]['additionalIdentifiers'][0]['id'] = "tenderers.additionalIdentifiers.id: 0.0"
        payload['bid']['tenderers'][0]['additionalIdentifiers'][0]['legalName'] = \
            "tenderers.additionalIdentifiers.legalName: 0.0"
        payload['bid']['tenderers'][0]['additionalIdentifiers'][0]['scheme'] = \
            "tenderers.additionalIdentifiers.scheme: 0.0"
        payload['bid']['tenderers'][0]['additionalIdentifiers'][0]['uri'] = \
            "tenderers.additionalIdentifiers.uri: 0.0"
        payload['bid']['tenderers'][0]['additionalIdentifiers'][1]['id'] = "tenderers.additionalIdentifiers.id: 0.1"
        payload['bid']['tenderers'][0]['additionalIdentifiers'][1]['legalName'] = \
            "tenderers.additionalIdentifiers.legalName: 0.1"
        payload['bid']['tenderers'][0]['additionalIdentifiers'][1]['scheme'] = \
            "tenderers.additionalIdentifiers.scheme: 0.1"
        payload['bid']['tenderers'][0]['additionalIdentifiers'][1]['uri'] = \
            "tenderers.additionalIdentifiers.uri: 0.1"
        payload['bid']['tenderers'][0]['address']['streetAddress'] = "tenderers.address.streetAddress: 0"
        payload['bid']['tenderers'][0]['address']['postalCode'] = "tenderers.address.postalCode: 0"
        payload['bid']['tenderers'][0]['address']['addressDetails']['country']['id'] = "MD"
        payload['bid']['tenderers'][0]['address']['addressDetails']['country']['description'] = \
            "tenderers.address.addressDetails.country.description: 0"
        payload['bid']['tenderers'][0]['address']['addressDetails']['country']['scheme'] = \
            "tenderers.address.addressDetails.country.scheme: 0"
        payload['bid']['tenderers'][0]['address']['addressDetails']['region']['id'] = "1700000"
        payload['bid']['tenderers'][0]['address']['addressDetails']['region']['description'] = \
            "tenderers.address.addressDetails.region.description: 0"
        payload['bid']['tenderers'][0]['address']['addressDetails']['region']['scheme'] = \
            "tenderers.address.addressDetails.region.scheme: 0"
        payload['bid']['tenderers'][0]['address']['addressDetails']['locality']['id'] = "1701000"
        payload['bid']['tenderers'][0]['address']['addressDetails']['locality']['description'] = \
            "tenderers.address.addressDetails.locality.description: 0"
        payload['bid']['tenderers'][0]['address']['addressDetails']['locality']['scheme'] = \
            "tenderers.address.addressDetails.locality.scheme: 0"
        payload['bid']['tenderers'][0]['contactPoint']['name'] = "tenderers.contactPoint.name: 0"
        payload['bid']['tenderers'][0]['contactPoint']['email'] = "tenderers.contactPoint.email: 0"
        payload['bid']['tenderers'][0]['contactPoint']['telephone'] = "tenderers.contactPoint.telephone: 0"
        payload['bid']['tenderers'][0]['contactPoint']['faxNumber'] = "tenderers.contactPoint.faxNumber: 0"
        payload['bid']['tenderers'][0]['contactPoint']['url'] = "tenderers.contactPoint.url: 0"
        payload['bid']['tenderers'][0]['persones'][0]['title'] = f"{random.choice(person_title)}"
        payload['bid']['tenderers'][0]['persones'][0]['name'] = "tenderers.persones.name: 0.0"
        payload['bid']['tenderers'][0]['persones'][0]['identifier']['scheme'] = \
            "MD-IDNO"
        payload['bid']['tenderers'][0]['persones'][0]['identifier']['id'] = \
            "tenderers.persones.identifier.id: 0.0"
        payload['bid']['tenderers'][0]['persones'][0]['identifier']['uri'] = \
            "tenderers.persones.identifier.uri: 0.0"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['id'] = \
            "tenderers.persones.businessFunctions.id: 0.0.0"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['type'] = "authority"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['jobTitle'] = \
            "tenderers.persones.businessFunctions.jobTitle.id: 0.0.0"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['period']['startDate'] = \
            self.date.time_at_now()[0]
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][0]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][0]['id'] = \
            self.document_one_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][0]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 0.0.0.0"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][0]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 0.0.0.0"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][1]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][1]['id'] = \
            self.document_two_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][1]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 0.0.0.1"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][1]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 0.0.0.1"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['id'] = \
            "tenderers.persones.businessFunctions.id: 0.0.1"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['type'] = "contactPoint"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['jobTitle'] = \
            "tenderers.persones.businessFunctions.jobTitle.id: 0.0.1"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['period']['startDate'] = \
            self.date.time_at_now()[0]
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][0]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][0]['id'] = \
            self.document_three_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][0]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 0.0.1.0"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][0]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 0.0.1.0"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][1]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][1]['id'] = \
            self.document_four_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][1]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 0.0.1.1"
        payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][1]['documents'][1]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 0.0.1.1"

        payload['bid']['tenderers'][0]['persones'][1]['title'] = f"{random.choice(person_title)}"
        payload['bid']['tenderers'][0]['persones'][1]['name'] = "tenderers.persones.name: 0.1"
        payload['bid']['tenderers'][0]['persones'][1]['identifier']['scheme'] = \
            "MD-IDNO"
        payload['bid']['tenderers'][0]['persones'][1]['identifier']['id'] = \
            "tenderers.persones.identifier.id: 0.1"
        payload['bid']['tenderers'][0]['persones'][1]['identifier']['uri'] = \
            "tenderers.persones.identifier.uri: 0.1"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['id'] = \
            "tenderers.persones.businessFunctions.id: 0.1.0"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['type'] = "contactPoint"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['jobTitle'] = \
            "tenderers.persones.businessFunctions.jobTitle.id: 0.1.0"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['period']['startDate'] = \
            self.date.time_at_now()[0]
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][0]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][0]['id'] = \
            self.document_five_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][0]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 0.1.0.0"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][0]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 0.1.0.0"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][1]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][1]['id'] = \
            self.document_six_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][1]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 0.1.0.1"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][0]['documents'][1]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 0.1.0.1"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['id'] = \
            "tenderers.persones.businessFunctions.id: 0.1.1"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['type'] = "contactPoint"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['jobTitle'] = \
            "tenderers.persones.businessFunctions.jobTitle.id: 0.1.1"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['period']['startDate'] = \
            self.date.time_at_now()[0]
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][0]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][0]['id'] = \
            self.document_seven_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][0]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 0.1.1.0"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][0]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 0.1.1.0"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][1]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][1]['id'] = \
            self.document_eight_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][1]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 0.1.1.1"
        payload['bid']['tenderers'][0]['persones'][1]['businessFunctions'][1]['documents'][1]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 0.1.1.1"
        payload['bid']['tenderers'][0]['details']['typeOfSupplier'] = f"{random.choice(type_of_supplier)}"
        payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][0]['id'] = \
            "tenderers.details.mainEconomicActivities.id': 0.0"
        payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][0]['scheme'] = \
            "tenderers.details.mainEconomicActivities.scheme': 0.0"
        payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][0]['description'] = \
            "tenderers.details.mainEconomicActivities.description': 0.0"
        payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][0]['uri'] = \
            "tenderers.details.mainEconomicActivities.uri': 0.0"
        payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][1]['id'] = \
            "tenderers.details.mainEconomicActivities.id': 0.1"
        payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][1]['scheme'] = \
            "tenderers.details.mainEconomicActivities.scheme': 0.1"
        payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][1]['description'] = \
            "tenderers.details.mainEconomicActivities.description': 0.1"
        payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][1]['uri'] = \
            "tenderers.details.mainEconomicActivities.uri': 0.1"
        payload['bid']['tenderers'][0]['details']['scale'] = f"{random.choice(scale)}"
        payload['bid']['tenderers'][0]['details']['permits'][0]['id'] = \
            "tenderers.details.permits.id': 0.0"
        payload['bid']['tenderers'][0]['details']['permits'][0]['scheme'] = \
            "tenderers.details.permits.scheme': 0.0"
        payload['bid']['tenderers'][0]['details']['permits'][0]['url'] = \
            "tenderers.details.permits.url': 0.0"
        payload['bid']['tenderers'][0]['details']['permits'][0]['permitDetails']['issuedBy']['id'] = \
            "tenderers.details.permits.permitDetails.issueBy.id': 0.0"
        payload['bid']['tenderers'][0]['details']['permits'][0]['permitDetails']['issuedBy']['name'] = \
            "tenderers.details.permits.permitDetails.issueBy.id': 0.0"
        payload['bid']['tenderers'][0]['details']['permits'][0]['permitDetails']['issuedThought']['id'] = \
            "tenderers.details.permits.permitDetails.issuedThought.id': 0.0"
        payload['bid']['tenderers'][0]['details']['permits'][0]['permitDetails']['issuedThought']['name'] = \
            "tenderers.details.permits.permitDetails.issuedThought.id': 0.0"
        payload['bid']['tenderers'][0]['details']['permits'][0]['permitDetails']['validityPeriod']['startDate'] = \
            self.date.contact_period()[0]
        payload['bid']['tenderers'][0]['details']['permits'][0]['permitDetails']['validityPeriod']['endDate'] = \
            self.date.contact_period()[1]
        payload['bid']['tenderers'][0]['details']['permits'][1]['id'] = \
            "tenderers.details.permits.id': 0.1"
        payload['bid']['tenderers'][0]['details']['permits'][1]['scheme'] = \
            "tenderers.details.permits.scheme': 0.1"
        payload['bid']['tenderers'][0]['details']['permits'][1]['url'] = \
            "tenderers.details.permits.url': 0.1"
        payload['bid']['tenderers'][0]['details']['permits'][1]['permitDetails']['issuedBy']['id'] = \
            "tenderers.details.permits.permitDetails.issueBy.id': 0.1"
        payload['bid']['tenderers'][0]['details']['permits'][1]['permitDetails']['issuedBy']['name'] = \
            "tenderers.details.permits.permitDetails.issueBy.id': 0.1"
        payload['bid']['tenderers'][0]['details']['permits'][1]['permitDetails']['issuedThought']['id'] = \
            "tenderers.details.permits.permitDetails.issuedThought.id': 0.1"
        payload['bid']['tenderers'][0]['details']['permits'][1]['permitDetails']['issuedThought']['name'] = \
            "tenderers.details.permits.permitDetails.issuedThought.id': 0.1"
        payload['bid']['tenderers'][0]['details']['permits'][1]['permitDetails']['validityPeriod']['startDate'] = \
            self.date.contact_period()[0]
        payload['bid']['tenderers'][0]['details']['permits'][1]['permitDetails']['validityPeriod']['endDate'] = \
            self.date.contact_period()[1]
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['description'] = \
            "tenderers.details.bankAccounts.description.: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['bankName'] = \
            "tenderers.details.bankAccounts.bankName.: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['streetAddress'] = \
            "tenderers.details.bankAccounts.address.streetAddress.: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['postalCode'] = \
            "tenderers.details.bankAccounts.address.postalCode.: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['addressDetails']['country']['id'] = \
            "MD"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['addressDetails']['country'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.country.description.: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['addressDetails']['country'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.country.scheme.: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['addressDetails']['region']['id'] = \
            "1700000"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['addressDetails']['region'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.region.description.: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['addressDetails']['region'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.region.scheme.: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['addressDetails']['locality']['id'] = \
            "1701000"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['addressDetails']['locality'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.locality.description.: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['address']['addressDetails']['locality'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.locality.scheme.: 0.0"

        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['identifier']['scheme'] = \
            "UA-MFO"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['identifier']['id'] = \
            "tenderers.details.bankAccounts.address.identifier.id: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['accountIdentification']['scheme'] = \
            "IBAN"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['accountIdentification']['id'] = \
            "tenderers.details.bankAccounts.address.accountIdentification.id: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0]['scheme'] = \
            "fiscal"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0]['id'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 0.0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0]['legalName'] = \
            "tenderers.details.bankAccounts.additionalAccountIdentifiers.legalName: 0.0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0]['uri'] = \
            "tenderers.details.bankAccounts.additionalAccountIdentifiers.uri: 0.0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1]['scheme'] = \
            "fiscal"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1]['id'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 0.0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1]['legalName'] = \
            "tenderers.details.bankAccounts.additionalAccountIdentifiers.legalName: 0.0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1]['uri'] = \
            "tenderers.details.bankAccounts.additionalAccountIdentifiers.uri: 0.0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['description'] = \
            "tenderers.details.bankAccounts.description.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['bankName'] = \
            "tenderers.details.bankAccounts.bankName.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['streetAddress'] = \
            "tenderers.details.bankAccounts.address.streetAddress.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['postalCode'] = \
            "tenderers.details.bankAccounts.address.postalCode.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['addressDetails']['country']['id'] = \
            "MD"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['addressDetails']['country'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.country.description.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['addressDetails']['country'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.country.scheme.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['addressDetails']['region']['id'] = \
            "1700000"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['addressDetails']['region'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.region.description.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['addressDetails']['region'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.region.scheme.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['addressDetails']['locality']['id'] = \
            "1701000"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['addressDetails']['locality'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.locality.description.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['address']['addressDetails']['locality'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.locality.scheme.: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['identifier']['scheme'] = \
            "UA-MFO"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['identifier']['id'] = \
            "tenderers.details.bankAccounts.address.identifier.id: 0.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['accountIdentification']['scheme'] = \
            "IBAN"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['accountIdentification']['id'] = \
            "tenderers.details.bankAccounts.address.accountIdentification.id: 0.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0]['scheme'] = \
            "fiscal"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0]['id'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 0.1.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0]['legalName'] = \
            "tenderers.details.bankAccounts.additionalAccountIdentifiers.legalName: 0.1.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0]['uri'] = \
            "tenderers.details.bankAccounts.additionalAccountIdentifiers.uri: 0.1.0"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1]['scheme'] = \
            "fiscal"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1]['id'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 0.1.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1]['legalName'] = \
            "tenderers.details.bankAccounts.additionalAccountIdentifiers.legalName: 0.1.1"
        payload['bid']['tenderers'][0]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1]['uri'] = \
            "tenderers.details.bankAccounts.additionalAccountIdentifiers.uri: 0.1.0"
        payload['bid']['tenderers'][0]['details']['legalForm']['scheme'] = \
            "MD-CFOJ"
        payload['bid']['tenderers'][0]['details']['legalForm']['description'] = \
            "tenderers.details.details.legalForm.scheme: 0."
        payload['bid']['tenderers'][0]['details']['legalForm']['id'] = \
            "tenderers.details.details.legalForm.id: 0."
        payload['bid']['tenderers'][0]['details']['legalForm']['uri'] = \
            "tenderers.details.details.legalForm.uri: 0."

        payload['bid']['tenderers'][1]['name'] = "tenderers.name: 1"
        payload['bid']['tenderers'][1]['identifier']['id'] = "tenderers.identifier.id: 1"
        payload['bid']['tenderers'][1]['identifier']['legalName'] = "tenderers.identifier.legalName: 1"
        payload['bid']['tenderers'][1]['identifier']['scheme'] = "MD-IDNO"
        payload['bid']['tenderers'][1]['identifier']['uri'] = "tenderers.identifier.uri: 1"
        payload['bid']['tenderers'][1]['additionalIdentifiers'][0]['id'] = "tenderers.additionalIdentifiers.id: 1.0"
        payload['bid']['tenderers'][1]['additionalIdentifiers'][0]['legalName'] = \
            "tenderers.additionalIdentifiers.legalName: 0.0"
        payload['bid']['tenderers'][1]['additionalIdentifiers'][0]['scheme'] = \
            "tenderers.additionalIdentifiers.scheme: 0.0"
        payload['bid']['tenderers'][1]['additionalIdentifiers'][0]['uri'] = \
            "tenderers.additionalIdentifiers.uri: 0.0"
        payload['bid']['tenderers'][1]['additionalIdentifiers'][1]['id'] = "tenderers.additionalIdentifiers.id: 1.1"
        payload['bid']['tenderers'][1]['additionalIdentifiers'][1]['legalName'] = \
            "tenderers.additionalIdentifiers.legalName: 1.1"
        payload['bid']['tenderers'][1]['additionalIdentifiers'][1]['scheme'] = \
            "tenderers.additionalIdentifiers.scheme: 1.1"
        payload['bid']['tenderers'][1]['additionalIdentifiers'][1]['uri'] = \
            "tenderers.additionalIdentifiers.uri: 1.1"
        payload['bid']['tenderers'][1]['address']['streetAddress'] = "tenderers.address.streetAddress: 1"
        payload['bid']['tenderers'][1]['address']['postalCode'] = "tenderers.address.postalCode: 1"
        payload['bid']['tenderers'][1]['address']['addressDetails']['country']['id'] = "MD"
        payload['bid']['tenderers'][1]['address']['addressDetails']['country']['description'] = \
            "tenderers.address.addressDetails.country.description: 1"
        payload['bid']['tenderers'][1]['address']['addressDetails']['country']['scheme'] = \
            "tenderers.address.addressDetails.country.scheme: 1"
        payload['bid']['tenderers'][1]['address']['addressDetails']['region']['id'] = "1700000"
        payload['bid']['tenderers'][1]['address']['addressDetails']['region']['description'] = \
            "tenderers.address.addressDetails.region.description: 1"
        payload['bid']['tenderers'][1]['address']['addressDetails']['region']['scheme'] = \
            "tenderers.address.addressDetails.region.scheme: 1"
        payload['bid']['tenderers'][1]['address']['addressDetails']['locality']['id'] = "1701000"
        payload['bid']['tenderers'][1]['address']['addressDetails']['locality']['description'] = \
            "tenderers.address.addressDetails.locality.description: 1"
        payload['bid']['tenderers'][1]['address']['addressDetails']['locality']['scheme'] = \
            "tenderers.address.addressDetails.locality.scheme: 1"
        payload['bid']['tenderers'][1]['contactPoint']['name'] = "tenderers.contactPoint.name: 1"
        payload['bid']['tenderers'][1]['contactPoint']['email'] = "tenderers.contactPoint.email: 1"
        payload['bid']['tenderers'][1]['contactPoint']['telephone'] = "tenderers.contactPoint.telephone: 1"
        payload['bid']['tenderers'][1]['contactPoint']['faxNumber'] = "tenderers.contactPoint.faxNumber: 1"
        payload['bid']['tenderers'][1]['contactPoint']['url'] = "tenderers.contactPoint.url: 1"
        payload['bid']['tenderers'][1]['persones'][0]['title'] = f"{random.choice(person_title)}"
        payload['bid']['tenderers'][1]['persones'][0]['name'] = "tenderers.persones.name: 1.0"
        payload['bid']['tenderers'][1]['persones'][0]['identifier']['scheme'] = \
            "MD-IDNO"
        payload['bid']['tenderers'][1]['persones'][0]['identifier']['id'] = \
            "tenderers.persones.identifier.id: 1.0"
        payload['bid']['tenderers'][1]['persones'][0]['identifier']['uri'] = \
            "tenderers.persones.identifier.uri: 1.0"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['id'] = \
            "tenderers.persones.businessFunctions.id: 1.0.0"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['type'] = "authority"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['jobTitle'] = \
            "tenderers.persones.businessFunctions.jobTitle.id: 1.0.0"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['period']['startDate'] = \
            self.date.time_at_now()[0]
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][0]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][0]['id'] = \
            self.document_one_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][0]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 1.0.0.0"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][0]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 1.0.0.0"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][1]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][1]['id'] = \
            self.document_two_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][1]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 1.0.0.1"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][0]['documents'][1]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 1.0.0.1"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['id'] = \
            "tenderers.persones.businessFunctions.id: 1.0.1"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['type'] = "contactPoint"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['jobTitle'] = \
            "tenderers.persones.businessFunctions.jobTitle.id: 1.0.1"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['period']['startDate'] = \
            self.date.time_at_now()[0]
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][0]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][0]['id'] = \
            self.document_three_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][0]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 1.0.1.0"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][0]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 1.0.1.0"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][1]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][1]['id'] = \
            self.document_four_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][1]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 1.0.1.1"
        payload['bid']['tenderers'][1]['persones'][0]['businessFunctions'][1]['documents'][1]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 1.0.1.1"

        payload['bid']['tenderers'][1]['persones'][1]['title'] = f"{random.choice(person_title)}"
        payload['bid']['tenderers'][1]['persones'][1]['name'] = "tenderers.persones.name: 1.1"
        payload['bid']['tenderers'][1]['persones'][1]['identifier']['scheme'] = \
            "MD-IDNO"
        payload['bid']['tenderers'][1]['persones'][1]['identifier']['id'] = \
            "tenderers.persones.identifier.id: 1.1"
        payload['bid']['tenderers'][1]['persones'][1]['identifier']['uri'] = \
            "tenderers.persones.identifier.uri: 1.1"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['id'] = \
            "tenderers.persones.businessFunctions.id: 1.1.0"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['type'] = "contactPoint"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['jobTitle'] = \
            "tenderers.persones.businessFunctions.jobTitle.id: 1.1.0"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['period']['startDate'] = \
            self.date.time_at_now()[0]
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][0]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][0]['id'] = \
            self.document_five_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][0]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 1.1.0.0"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][0]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 1.1.0.0"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][1]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][1]['id'] = \
            self.document_six_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][1]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 1.1.0.1"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][0]['documents'][1]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 1.1.0.1"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['id'] = \
            "tenderers.persones.businessFunctions.id: 1.1.1"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['type'] = "contactPoint"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['jobTitle'] = \
            "tenderers.persones.businessFunctions.jobTitle.id: 1.1.1"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['period']['startDate'] = \
            self.date.time_at_now()[0]
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][0]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][0]['id'] = \
            self.document_seven_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][0]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 1.1.1.0"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][0]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 1.1.1.0"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][1]['documentType'] = \
            "regulatoryDocument"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][1]['id'] = \
            self.document_eight_was_uploaded[0]["data"]["id"]
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][1]['title'] = \
            "tenderers.persones.businessFunctions.documents.title: 1.1.1.1"
        payload['bid']['tenderers'][1]['persones'][1]['businessFunctions'][1]['documents'][1]['description'] = \
            "tenderers.persones.businessFunctions.documents.description: 1.1.1.1"
        payload['bid']['tenderers'][1]['details']['typeOfSupplier'] = f"{random.choice(type_of_supplier)}"
        payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][0]['id'] = \
            "tenderers.details.mainEconomicActivities.id': 1.0"
        payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][0]['scheme'] = \
            "tenderers.details.mainEconomicActivities.scheme': 1.0"
        payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][0]['description'] = \
            "tenderers.details.mainEconomicActivities.description': 1.0"
        payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][0]['uri'] = \
            "tenderers.details.mainEconomicActivities.uri': 1.0"
        payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][1]['id'] = \
            "tenderers.details.mainEconomicActivities.id': 1.1"
        payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][1]['scheme'] = \
            "tenderers.details.mainEconomicActivities.scheme': 1.1"
        payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][1]['description'] = \
            "tenderers.details.mainEconomicActivities.description': 1.1"
        payload['bid']['tenderers'][1]['details']['mainEconomicActivities'][1]['uri'] = \
            "tenderers.details.mainEconomicActivities.uri': 1.1"
        payload['bid']['tenderers'][1]['details']['scale'] = f"{random.choice(scale)}"
        payload['bid']['tenderers'][1]['details']['permits'][0]['id'] = \
            "tenderers.details.permits.id': 1.0"
        payload['bid']['tenderers'][1]['details']['permits'][0]['scheme'] = \
            "tenderers.details.permits.scheme': 1.0"
        payload['bid']['tenderers'][1]['details']['permits'][0]['url'] = \
            "tenderers.details.permits.url': 1.0"
        payload['bid']['tenderers'][1]['details']['permits'][0]['permitDetails']['issuedBy']['id'] = \
            "tenderers.details.permits.permitDetails.issueBy.id': 1.0"
        payload['bid']['tenderers'][1]['details']['permits'][0]['permitDetails']['issuedBy']['name'] = \
            "tenderers.details.permits.permitDetails.issueBy.id': 1.0"
        payload['bid']['tenderers'][1]['details']['permits'][0]['permitDetails']['issuedThought']['id'] = \
            "tenderers.details.permits.permitDetails.issuedThought.id': 1.0"
        payload['bid']['tenderers'][1]['details']['permits'][0]['permitDetails']['issuedThought']['name'] = \
            "tenderers.details.permits.permitDetails.issuedThought.id': 1.0"
        payload['bid']['tenderers'][1]['details']['permits'][0]['permitDetails']['validityPeriod']['startDate'] = \
            self.date.contact_period()[0]
        payload['bid']['tenderers'][1]['details']['permits'][0]['permitDetails']['validityPeriod']['endDate'] = \
            self.date.contact_period()[1]
        payload['bid']['tenderers'][1]['details']['permits'][1]['id'] = \
            "tenderers.details.permits.id': 1.1"
        payload['bid']['tenderers'][1]['details']['permits'][1]['scheme'] = \
            "tenderers.details.permits.scheme': 1.1"
        payload['bid']['tenderers'][1]['details']['permits'][1]['url'] = \
            "tenderers.details.permits.url': 1.1"
        payload['bid']['tenderers'][1]['details']['permits'][1]['permitDetails']['issuedBy']['id'] = \
            "tenderers.details.permits.permitDetails.issueBy.id': 1.1"
        payload['bid']['tenderers'][1]['details']['permits'][1]['permitDetails']['issuedBy']['name'] = \
            "tenderers.details.permits.permitDetails.issueBy.id': 1.1"
        payload['bid']['tenderers'][1]['details']['permits'][1]['permitDetails']['issuedThought']['id'] = \
            "tenderers.details.permits.permitDetails.issuedThought.id': 1.1"
        payload['bid']['tenderers'][1]['details']['permits'][1]['permitDetails']['issuedThought']['name'] = \
            "tenderers.details.permits.permitDetails.issuedThought.id': 1.1"
        payload['bid']['tenderers'][1]['details']['permits'][1]['permitDetails']['validityPeriod']['startDate'] = \
            self.date.contact_period()[0]
        payload['bid']['tenderers'][1]['details']['permits'][1]['permitDetails']['validityPeriod']['endDate'] = \
            self.date.contact_period()[1]
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['description'] = \
            "tenderers.details.bankAccounts.description.: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['bankName'] = \
            "tenderers.details.bankAccounts.bankName.: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['streetAddress'] = \
            "tenderers.details.bankAccounts.address.streetAddress.: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['postalCode'] = \
            "tenderers.details.bankAccounts.address.postalCode.: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['addressDetails']['country']['id'] = \
            "MD"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['addressDetails']['country'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.country.description.: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['addressDetails']['country'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.country.scheme.: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['addressDetails']['region']['id'] = \
            "1700000"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['addressDetails']['region'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.region.description.: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['addressDetails']['region'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.region.scheme.: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['addressDetails']['locality']['id'] = \
            "1701000"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['addressDetails']['locality'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.locality.description.: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['address']['addressDetails']['locality'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.locality.scheme.: 1.0"

        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['identifier']['scheme'] = \
            "UA-MFO"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['identifier']['id'] = \
            "tenderers.details.bankAccounts.address.identifier.id: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['accountIdentification']['scheme'] = \
            "IBAN"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['accountIdentification']['id'] = \
            "tenderers.details.bankAccounts.address.accountIdentification.id: 1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0]['scheme'] = \
            "fiscal"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0]['id'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 1.0.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0]['legalName'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.legalName: 1.0.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0]['uri'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.uri: 1.0.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1]['scheme'] = \
            "fiscal"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1]['id'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 1.0.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1]['legalName'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.legalName: 1.0.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][1]['uri'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.uri: 1.0.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['description'] = \
            "tenderers.details.bankAccounts.description.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['bankName'] = \
            "tenderers.details.bankAccounts.bankName.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['streetAddress'] = \
            "tenderers.details.bankAccounts.address.streetAddress.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['postalCode'] = \
            "tenderers.details.bankAccounts.address.postalCode.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['addressDetails']['country']['id'] = \
            "MD"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['addressDetails']['country'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.country.description.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['addressDetails']['country'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.country.scheme.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['addressDetails']['region']['id'] = \
            "1700000"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['addressDetails']['region'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.region.description.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['addressDetails']['region'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.region.scheme.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['addressDetails']['locality']['id'] = \
            "1701000"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['addressDetails']['locality'][
            'description'] = \
            "tenderers.details.bankAccounts.address.addressDetails.locality.description.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['address']['addressDetails']['locality'][
            'scheme'] = \
            "tenderers.details.bankAccounts.address.addressDetails.locality.scheme.: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['identifier']['scheme'] = \
            "UA-MFO"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['identifier']['id'] = \
            "tenderers.details.bankAccounts.address.identifier.id: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['accountIdentification']['scheme'] = \
            "IBAN"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['accountIdentification']['id'] = \
            "tenderers.details.bankAccounts.address.accountIdentification.id: 1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0]['scheme'] = \
            "fiscal"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0]['id'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 1.1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0]['legalName'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.legalName: 1.1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][0]['uri'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.uri: 1.1.0"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1]['scheme'] = \
            "fiscal"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1]['id'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.id: 1.1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1]['legalName'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.legalName: 1.1.1"
        payload['bid']['tenderers'][1]['details']['bankAccounts'][1]['additionalAccountIdentifiers'][1]['uri'] = \
            "tenderers.details.bankAccounts.address.additionalAccountIdentifiers.uri: 1.1.1"
        payload['bid']['tenderers'][1]['details']['legalForm']['scheme'] = \
            "MD-CFOJ"
        payload['bid']['tenderers'][1]['details']['legalForm']['description'] = \
            "tenderers.details.details.legalForm.scheme: 1."
        payload['bid']['tenderers'][1]['details']['legalForm']['id'] = \
            "tenderers.details.details.legalForm.id: 1."
        payload['bid']['tenderers'][1]['details']['legalForm']['uri'] = \
            "tenderers.details.details.legalForm.uri: 1."

        payload['bid']['documents'][0]['documentType'] = f"{random.choice(documentType_for_bid)}"
        payload['bid']['documents'][0]['id'] = self.document_nine_was_uploaded[0]['data']['id']
        payload['bid']['documents'][0]['title'] = "tenderers.documents.title: 0."
        payload['bid']['documents'][0]['description'] = "tenderers.documents.description: 0."
        payload['bid']['documents'][0]['relatedLots'] = [based_stage_release['releases'][0]['tender']['lots'][0]['id']]
        payload['bid']['documents'][1]['documentType'] = f"{random.choice(documentType_for_bid)}"
        payload['bid']['documents'][1]['id'] = self.document_ten_was_uploaded[0]['data']['id']
        payload['bid']['documents'][1]['title'] = "tenderers.documents.title: 0."
        payload['bid']['documents'][1]['description'] = "tenderers.documents.description: 0."
        payload['bid']['documents'][1]['relatedLots'] = [based_stage_release['releases'][0]['tender']['lots'][0]['id']]

        # payload['bid']['items'][0]['id'] = based_stage_release['releases'][0]['tender']['items'][0]['id']
        # payload['bid']['items'][0]['unit']['value']['amount'] = \
        #     based_stage_release['releases'][0]['tender']['lots'][0]['value']['amount']
        # payload['bid']['items'][0]['unit']['value']['currency'] = \
        #     based_stage_release['releases'][0]['tender']['lots'][0]['value']['currency']
        # payload['bid']['items'][0]['unit']['id'] = \
        #     based_stage_release['releases'][0]['tender']['items'][0]['unit']['id']

        payload['bid']['requirementResponses'] = generate_requirement_response_array(
            ev_release_criteria_array=based_stage_release['releases'][0]['tender']['criteria'],
            payload=payload
        )

        return payload
