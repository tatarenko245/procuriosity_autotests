import copy

from tests.conftest import GlobalClassMetadata
from tests.utils.PayloadModel.SubmitBid.bid_payload_library import PayloadLibrary
from tests.utils.date_class import Date
from tests.utils.functions import set_permanent_id
from tests.utils.iStorage import Document
from tests.utils.services.e_mdm_service import MdmService


class BidPreparePayload:
    def __init__(self, need_to_set_permanent_id_for_lots_array, based_stage_release):
        self.constructor = copy.deepcopy(PayloadLibrary())
        self.need_to_set_permanent_id_for_lots_array = need_to_set_permanent_id_for_lots_array
        self.based_stage_release = based_stage_release
        # document_one = Document("API.pdf")
        # self.document_one_was_uploaded = document_one.uploading_document()
        # self.document_two_was_uploaded = document_one.uploading_document()
        # self.standard_criteria = MdmService.get_standard_criteria(
        #     country=GlobalClassMetadata.country,
        #     language=GlobalClassMetadata.language)
        # self.contact_period = Date().contact_period()
        # self.duration_period = Date().duration_period()

    def create_bid_full_data_model(
            self, related_lot):
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
            payload['bid']['tenderers'] = [
                {}
            ]
            payload['bid']['relatedLots'] = [
                {}
            ]
            payload['bid']['documents'] = [
                {}
            ]
            payload['bid']['items'] = [
                {}
            ]
            payload['bid']['requirementResponses'][0].update(
                self.constructor.requirement_response()
            )
            payload['bid']['requirementResponses'][0]['evidences'] = [
                {}
            ]
            payload['bid']['requirementResponses'][0]['evidences'][0].update(
                self.constructor.evidence_object()
            )
            payload['bid']['tenderers'][0].update(
                self.constructor.tenderers_object()
            )
            payload['bid']['tenderers'][0]['additionalIdentifiers'] = [
                {}
            ]
            payload['bid']['tenderers'][0]['additionalIdentifiers'][0].update(
                self.constructor.additional_identifiers_object()
            )
            payload['bid']['tenderers'][0]['persones'] = [{}]
            payload['bid']['tenderers'][0]['persones'][0].update(
                self.constructor.person_object()
            )
            payload['bid']['tenderers'][0]['details']['mainEconomicActivities'] = [
                {}
            ]
            payload['bid']['tenderers'][0]['details']['mainEconomicActivities'][0].update(
                self.constructor.main_economic_activities_object()
            )
            payload['bid']['tenderers'][0]['details']['permits'] = [
                {}
            ]
            payload['bid']['tenderers'][0]['details']['permits'][0].update(
                self.constructor.permit_object()
            )
            payload['bid']['tenderers'][0]['details']['bankAccounts'] = [
                {}
            ]
            payload['bid']['tenderers'][0]['details']['bankAccounts'][0].update(
                self.constructor.bank_account_object()
            )
            payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'] = [
                {}
            ]
            payload['bid']['tenderers'][0]['details']['bankAccounts'][0]['additionalAccountIdentifiers'][0].update(
                self.constructor.additional_account_identifier_object()
            )
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'] = [
                {}
            ]
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0].update(
                self.constructor.business_function_object()
            )
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'] = [
                {}
            ]
            payload['bid']['tenderers'][0]['persones'][0]['businessFunctions'][0]['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['documents'] = [{}]
            payload['bid']['documents'][0].update(
                self.constructor.document_object()
            )
            payload['bid']['items'] = [
                {}
            ]
            payload['bid']['items'][0].update(
                self.constructor.item_object()
            )
        except KeyError:
            raise KeyError("Impossible to update payload dictionary, check 'self.constructor'.")

        try:
            """
            Set permanent id for lots array.
            """
            if self.need_to_set_permanent_id_for_lots_array is True:
                payload['bid']['relatedLots'] = set_permanent_id(
                    release_array=self.based_stage_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        return payload
