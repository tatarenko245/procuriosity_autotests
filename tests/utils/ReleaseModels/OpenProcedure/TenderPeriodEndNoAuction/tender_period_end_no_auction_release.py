import copy

from tests.conftest import GlobalClassMetadata, GlobalClassTenderPeriodEndNoAuction, \
    GlobalClassCreateCnOnPn
from tests.utils.ReleaseModels.OpenProcedure.TenderPeriodEndNoAuction.tender_period_end_no_auction_release_library import \
    ReleaseLibrary
from tests.utils.functions_collection import check_uuid_version
from tests.utils.services.e_mdm_service import MdmService


class TenderPeriodExpectedChanges:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.metadata_tender_url = None
        self.metadata_document_url = None
        self.metadata_auction_url = None
        self.mdm = MdmService(host_for_service=GlobalClassMetadata.host_for_services)
        self.mdm = MdmService(host_for_service=GlobalClassMetadata.host_for_services)

        try:
            if environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
                self.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
                self.metadata_auction_url = "http://auction.eprocurement.systems/auctions/"

            elif environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
                self.metadata_document_url = "http://storage.eprocurement.systems/get"
                self.metadata_auction_url = "https://eauction.eprocurement.systems/auctions/"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")
        GlobalClassMetadata.metadata_budget_url = self.metadata_budget_url
        GlobalClassMetadata.metadata_tender_url = self.metadata_tender_url

    def prepare_unsuccessful_awards_array(self):
        try:
            """
            Check how many quantity of object into payload['tender']['lots'].
            """
            list_of_payload_lot_id = list()
            for ob in GlobalClassCreateCnOnPn.payload['tender']['lots']:
                for i in ob:
                    if i == "id":
                        list_of_payload_lot_id.append(i)
            quantity_of_lots_object_into_payload = len(list_of_payload_lot_id)
        except Exception:
            raise Exception("Impossible to check how many quantity of object into payload['tender']['lots']")
        try:
            """
            Check how many quantity of object into actual_ev_release['releases'][0]['tender']['lots'].
            """
            list_of_release_lot_id = list()
            for i in GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']['lots']:
                for i_1 in i:
                    if i_1 == "id":
                        list_of_release_lot_id.append(i_1)
            quantity_of_lots_object_into_release = len(list_of_release_lot_id)
        except Exception:
            raise Exception("Impossible to check how many quantity of object into "
                            "actual_ev_release['releases'][0]['tender']['lots']")
        try:
            """
            Compare quantity of object into payload['tender']['lots'] and 
            object into actual_ev_release['releases'][0]['tender']['lots'].
            """
            if quantity_of_lots_object_into_payload == \
                    quantity_of_lots_object_into_release:
                pass
            else:
                raise Exception("ERROR: quantity of object into payload['tender']['lots'] != quantity of"
                                "object into actual_ev_release['releases'][0]['tender']['lots']")
        except Exception:
            raise Exception("Impossible to compare quantity of object into payload['tender']['lots'] and "
                            "object into actual_ev_release['releases'][0]['tender']['lots']")
        expected_awards_array = []
        for q in range(quantity_of_lots_object_into_release):
            expected_awards_array.append(self.constructor.ev_release_unsuccessful_award_object())
            expected_awards_array[q]['title'] = "The contract/lot is not awarded"
            expected_awards_array[q]['description'] = "Other reasons (discontinuation of procedure)"
            expected_awards_array[q]['status'] = "unsuccessful"
            expected_awards_array[q]['statusDetails'] = "noOffersReceived"
            expected_awards_array[q]['date'] = \
                GlobalClassTenderPeriodEndNoAuction.feed_point_message['data']['operationDate']
            expected_awards_array[q]['relatedLots'] = \
                [GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']['lots'][q]['id']]

            if GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['awards'][q]['relatedLots'][0] == \
                    expected_awards_array[q]['relatedLots'][0]:
                expected_awards_array[q]['id'] = \
                    GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['awards'][q]['id']
            else:
                pass
        return expected_awards_array

    def prepare_bid_details_mapper(self, bid_payload, bid_feed_point_message):
        expected_bid_object = {}
        expected_bid_object.update(self.constructor.ev_release_bid_object())
        expected_bid_object['details'].append(self.constructor.ev_release_bid_details_object())
        try:
            """
            Check how many quantity of object into payload['bid']['tenderers'].
            """
            list_of_payload_tenderer_id = list()
            for tenderer_object in bid_payload['bid']['tenderers']:
                for i in tenderer_object['identifier']:
                    if i == "id":
                        list_of_payload_tenderer_id.append(i)
            quantity_of_tender_object_into_payload = len(list_of_payload_tenderer_id)
        except Exception:
            raise Exception("Check payload['bid']['tenderers']['identifier']['id']")
        try:
            check = check_uuid_version(
                uuid_to_test=GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids']['details'][0][
                    'id'],
                version=4
            )
            if check is True:
                expected_bid_object['details'][0]['id'] = \
                    GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids']['details'][0]['id']
            else:
                raise ValueError("businessFunctions.id in release must be uuid version 4")
        except Exception:
            raise Exception("Check your businessFunctions array in release")
        expected_bid_object['details'][0]['status'] = "pending"
        expected_bid_object['details'][0]['date'] = bid_feed_point_message['data']['operationDate']
        for q in range(quantity_of_tender_object_into_payload):
            expected_bid_object['details'][0]['tenderers'].append(
                self.constructor.ev_release_bid_details_tenderer_object())
            expected_bid_object['details'][0]['tenderers'][q]['id'] = \
                f"{bid_payload['bid']['tenderers'][q]['identifier']['scheme']}-" \
                f"{bid_payload['bid']['tenderers'][q]['identifier']['id']}"
            expected_bid_object['details'][0]['tenderers'][q]['name'] = bid_payload['bid']['tenderers'][q]['name']
        expected_bid_object['details'][0]['value']['amount'] = bid_payload['bid']['value']['amount']
        expected_bid_object['details'][0]['value']['currency'] = bid_payload['bid']['value']['currency']
        try:
            """
            Check how many quantity of object into payload['bid']['documents'].
            """
            list_of_payload_bid_documents_id = list()
            for i in bid_payload['bid']['documents']:
                for i_1 in i:
                    if i_1 == "id":
                        list_of_payload_bid_documents_id.append(i_1)
            quantity_of_bid_documents_into_payload = len(list_of_payload_bid_documents_id)
        except Exception:
            raise Exception("Check payload['bid']['documents']['id']")
        for q_one in range(quantity_of_bid_documents_into_payload):
            if GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender'][
                'awardCriteriaDetails'] == "automated" and \
                    bid_payload['bid']['documents'][q_one]['documentType'] == "submissionDocuments" or \
                    GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender'][
                        'awardCriteriaDetails'] == "automated" and \
                    bid_payload['bid']['documents'][q_one]['documentType'] == "x_eligibilityDocuments" or \
                    GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender'][
                        'awardCriteriaDetails'] == "manual":
                some_document = list()
                some_document.append(self.constructor.ev_release_bid_details_document_object())
                some_document[0]['id'] = bid_payload['bid']['documents'][q_one]['id']
                some_document[0]['documentType'] = bid_payload['bid']['documents'][q_one]['documentType']
                some_document[0]['title'] = bid_payload['bid']['documents'][q_one]['title']
                some_document[0]['description'] = bid_payload['bid']['documents'][q_one]['description']
                some_document[0]['url'] = f"{self.metadata_document_url}/" + bid_payload['bid'][
                    'documents'][q_one]['id']
                some_document[0]['datePublished'] = \
                    GlobalClassTenderPeriodEndNoAuction.feed_point_message['data']['operationDate']
                some_document[0]['relatedLots'] = bid_payload['bid']['documents'][q_one]['relatedLots']
                expected_bid_object['details'][0]['documents'].append(some_document[0])

        expected_bid_object['details'][0]['relatedLots'] = bid_payload['bid']['relatedLots']

        if "requirementResponses" in bid_payload['bid']:
            try:
                """
                Check how many quantity of object into payload['bid']['requirementResponses'].
                """
                list_of_payload_requirement_responses_id = list()
                for ob in bid_payload['bid']['requirementResponses']:
                    for i in ob:
                        if i == "id":
                            list_of_payload_requirement_responses_id.append(i)
                quantity_of_requirement_responses_object_into_payload = len(list_of_payload_requirement_responses_id)
            except Exception:
                raise Exception("Check payload['bid']['requirementResponses']['id']")
            try:
                """
                Check how many quantity of object into actual_ev_release['releases'][0]['bids']['details']
                ['requirementResponses'].
                """
                list_of_release_requirement_responses_id = list()
                for i in \
                        GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids']['details'][0][
                            'requirementResponses']:
                    for i_1 in i:
                        if i_1 == "id":
                            list_of_release_requirement_responses_id.append(i_1)
                quantity_of_requirement_responses_object_into_release = len(list_of_release_requirement_responses_id)
            except Exception:
                raise Exception("Check object into actual_ev_release['releases'][0]['bids']['details']"
                                "['requirementResponses']['id']")
            try:
                """
                Compare quantity of quantity of object into payload['bid']['requirementResponses'] and 
                object into actual_ev_release['releases'][0]['bids']['details']['requirementResponses'].
                """
                if quantity_of_requirement_responses_object_into_payload == \
                        quantity_of_requirement_responses_object_into_release:
                    pass
                else:
                    raise Exception("Quantity of of payload['bid']['requirementResponses'] != "
                                    "quantity of object into "
                                    "actual_ev_release['releases'][0]['bids']['details']['requirementResponses']")
            except Exception:
                raise Exception("Impossible to Compare quantity of quantity of object into "
                                "payload['bid']['requirementResponses'] and object into "
                                "actual_ev_release['releases'][0]['bids']['details']['requirementResponses']")
            for q_two in range(quantity_of_requirement_responses_object_into_payload):
                expected_bid_object['details'][0]['requirementResponses'].append(
                    self.constructor.ev_release_bid_details_requirement_response_object()
                )
                try:
                    check = check_uuid_version(
                        uuid_to_test=GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids'][
                            'details'][0]['requirementResponses'][q_two]['id'],
                        version=4
                    )
                    if check is True:
                        expected_bid_object['details'][0]['requirementResponses'][q_two]['id'] = \
                            GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids']['details'][0][
                                'requirementResponses'][q_two]['id']
                    else:
                        raise ValueError("requirementResponses.id in release must be uuid version 4")
                except Exception:
                    raise Exception("Check your requirementResponses array in release")

                expected_bid_object['details'][0]['requirementResponses'][q_two]['value'] = \
                    bid_payload['bid']['requirementResponses'][q_two]['value']
                expected_bid_object['details'][0]['requirementResponses'][q_two]['period']['startDate'] = \
                    bid_payload['bid']['requirementResponses'][q_two]['period']['startDate']
                expected_bid_object['details'][0]['requirementResponses'][q_two]['period']['endDate'] = \
                    bid_payload['bid']['requirementResponses'][q_two]['period']['endDate']
                expected_bid_object['details'][0]['requirementResponses'][q_two]['requirement']['id'] = \
                    bid_payload['bid']['requirementResponses'][q_two]['requirement']['id']

                related_tenderer_identifier = \
                    f"{bid_payload['bid']['requirementResponses'][q_two]['relatedTenderer']['identifier']['scheme']}-" \
                    f"{bid_payload['bid']['requirementResponses'][q_two]['relatedTenderer']['identifier']['id']}"
                for q in range(quantity_of_tender_object_into_payload):
                    expected_bid_object['details'][0]['requirementResponses'][q_two]['relatedTenderer']['id'] = \
                        related_tenderer_identifier
                    expected_bid_object['details'][0]['requirementResponses'][q_two]['relatedTenderer']['name'] = \
                        bid_payload['bid']['requirementResponses'][q_two]['relatedTenderer']['name']

                try:
                    """
                    Check how many quantity of object into payload['bid']['requirementResponses']['evidences'].
                    """
                    list_of_payload_requirement_responses_evidences_id = list()
                    for i in bid_payload['bid']['requirementResponses'][q_two]['evidences']:
                        for i_1 in i:
                            if i_1 == "id":
                                list_of_payload_requirement_responses_evidences_id.append(i_1)
                    quantity_of_evidences_object_into_payload = len(list_of_payload_requirement_responses_evidences_id)
                except Exception:
                    raise Exception("Check payload['bid']['requirementResponses']['evidences']['id']")
                try:
                    """
                    Check how many quantity of object into actual_ev_release['releases'][0]['bids']['details']
                    ['requirementResponses']['evidences'].
                    """
                    list_of_release_requirement_responses_evidences_id = list()
                    for i in \
                            GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids']['details'][0][
                                'requirementResponses'][q_two]['evidences']:
                        for i_1 in i:
                            if i_1 == "id":
                                list_of_release_requirement_responses_evidences_id.append(i_1)
                    quantity_of_evidences_into_release = len(list_of_release_requirement_responses_evidences_id)
                except Exception:
                    raise Exception("Check object into actual_ev_release['releases'][0]['bids']['details']"
                                    "['requirementResponses']['evidences']['id']")
                try:
                    """
                    Compare quantity of object into payload['bid']['requirementResponses']['evidences'] and 
                    object into actual_ev_release['releases'][0]['bids']['details']['requirementResponses']
                    ['evidences'].
                    """
                    if quantity_of_evidences_object_into_payload == quantity_of_evidences_into_release:
                        pass
                    else:
                        raise Exception("Quantity of object into payload['bid']['requirementResponses']['evidences'] "
                                        "!= object into actual_ev_release['releases'][0]['bids']['details']"
                                        "['requirementResponses']['evidences']")
                except Exception:
                    raise Exception("Impossible to compare quantity of object into "
                                    "payload['bid']['requirementResponses']['evidences'] and "
                                    "object into actual_ev_release['releases'][0]['bids']['details']"
                                    "['requirementResponses']['evidences']")
                for q_three in range(quantity_of_evidences_object_into_payload):
                    expected_bid_object['details'][0]['requirementResponses'][q_two]['evidences'].append(
                        self.constructor.ev_release_bid_details_requirement_response_evidences_object()
                    )
                    try:
                        check = check_uuid_version(
                            uuid_to_test=GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids'][
                                'details'][0]['requirementResponses'][q_two]['evidences'][q_three]['id'],
                            version=4
                        )
                        if check is True:
                            expected_bid_object['details'][0]['requirementResponses'][q_two][
                                'evidences'][q_three]['id'] = \
                                GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids'][
                                    'details'][0]['requirementResponses'][q_two]['evidences'][q_three]['id']
                        else:
                            raise ValueError("requirementResponses.id in release must be uuid version 4")
                    except Exception:
                        raise Exception("Check your requirementResponses array in release")
                    expected_bid_object['details'][0]['requirementResponses'][q_two]['evidences'][q_three]['title'] = \
                        bid_payload['bid']['requirementResponses'][q_two]['evidences'][q_three]['title']
                    expected_bid_object['details'][0]['requirementResponses'][q_two]['evidences'][q_three][
                        'description'] = bid_payload['bid']['requirementResponses'][q_two][
                        'evidences'][q_three]['description']
                    expected_bid_object['details'][0]['requirementResponses'][q_two]['evidences'][q_three][
                        'relatedDocument']['id'] = \
                        bid_payload['bid']['requirementResponses'][q_two]['evidences'][q_three]['relatedDocument']['id']
        else:
            del expected_bid_object['details'][0]['requirementResponses']

        if str(expected_bid_object['details'][0]['documents']) == str([]):
            del expected_bid_object['details'][0]['documents']

        expected_bid_object_mapper = {
            "tenderers": expected_bid_object['details'][0]['tenderers'],
            "value": expected_bid_object['details'][0]
        }
        return expected_bid_object_mapper

    @staticmethod
    def prepare_criteria_array_source_procuring_entity():
        quantity_of_criteria_object_into_release = 0
        if "criteria" in GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']:
            try:
                """
                Check how many quantity of object into GlobalClassCreateCnOnPn.actual_ev_release[
                'releases'][0]['tender']['criteria'].
                """
                list_of_release_render_criteria_id = list()
                for criteria_object in GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['criteria']:
                    for i in criteria_object:
                        if i == "id":
                            list_of_release_render_criteria_id.append(i)
                quantity_of_criteria_object_into_release = len(list_of_release_render_criteria_id)
            except Exception:
                raise Exception("Impossible to check how many quantity of object into "
                                "GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['criteria']")

        try:
            """
            Check 'id', 'requirementGroups.id', 'requirements.id' into 
            GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']['criteria'][*].
            """
            check_criteria_id = check_uuid_version(
                uuid_to_test=GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender'][
                    'criteria'][quantity_of_criteria_object_into_release]['id'],
                version=4
            )
            if check_criteria_id is True:
                pass
            else:
                raise ValueError("The 'id' into GlobalClassTenderPeriodEndNoAuction.actual_ev_release["
                                 "'releases'][0]['tender']['criteria'][*] must be uuid version 4")
            check_criteria_requirement_groups_id = check_uuid_version(
                uuid_to_test=GlobalClassTenderPeriodEndNoAuction.actual_ev_release[
                    'releases'][0]['tender']['criteria'][quantity_of_criteria_object_into_release][
                    'requirementGroups'][0]['id'],
                version=4
            )
            if check_criteria_requirement_groups_id is True:
                pass
            else:
                raise ValueError("The 'requirementGroups.id' into "
                                 "GlobalClassTenderPeriodEndNoAuction.actual_ev_release["
                                 "'releases'][0]['tender']['criteria'][*] must be uuid version 4")
            check_criteria_requirement_groups_requirements_id = check_uuid_version(
                uuid_to_test=GlobalClassTenderPeriodEndNoAuction.actual_ev_release[
                    'releases'][0]['tender']['criteria'][quantity_of_criteria_object_into_release][
                    'requirementGroups'][0]['requirements'][0]['id'],
                version=4
            )
            if check_criteria_requirement_groups_requirements_id is True:
                pass
            else:
                raise ValueError("The 'requirements.id' into "
                                 "GlobalClassTenderPeriodEndNoAuction.actual_ev_release["
                                 "'releases'][0]['tender']['criteria'][*]['requirementGroups'][*] "
                                 "must be uuid version 4")
        except Exception:
            raise Exception("The 'id' and 'requirementGroups.id' and 'requirements.id' into "
                            "GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]["
                            "'tender']['criteria'][*] must be uuid version 4")

        expected_criteria_array_source_procuring_entity = {
            "id": GlobalClassTenderPeriodEndNoAuction.actual_ev_release[
                'releases'][0]['tender']['criteria'][quantity_of_criteria_object_into_release]['id'],
            "title": "QualificationDeclaration of absence of conflict of interest and confidentiality",
            "source": "procuringEntity",
            "description": "Conflict of interest",
            "requirementGroups": [
                {
                    "id": GlobalClassTenderPeriodEndNoAuction.actual_ev_release[
                        'releases'][0]['tender']['criteria'][quantity_of_criteria_object_into_release][
                        'requirementGroups'][0]['id'],
                    "requirements": [
                        {
                            "id": GlobalClassTenderPeriodEndNoAuction.actual_ev_release[
                                'releases'][0]['tender']['criteria'][quantity_of_criteria_object_into_release][
                                'requirementGroups'][0]['requirements'][0]['id'],
                            "title": "I am aware of Article 24 of Directive 2014/24/EU on "
                                     "public procurement, which states that: \"The concept of "
                                     "conflicts of interest shall at least cover any situation "
                                     "where staff members of the contracting authority or of "
                                     "a procurement service provider acting on behalf of "
                                     "the contracting authority who are involved in the conduct of "
                                     "the procurement procedure or may influence the outcome of "
                                     "that procedure have, directly or indirectly, a financial, "
                                     "economic or other personal interest which might be perceived "
                                     "to compromise their impartiality and independence in the "
                                     "context of the procurement procedure.\"\nto the best of my "
                                     "knowledge and belief I have no conflict of interest with the "
                                     "operators who have submitted a tender for this procurement, "
                                     "including persons or members of a consortium, or with "
                                     "the subcontractors proposed;\nthere are no facts or "
                                     "circumstances, past or present, or that could arise in the "
                                     "foreseeable future, which might call into question my "
                                     "independence in the eyes of any party;\nif I discover during "
                                     "the course of the [project/evaluation] that such a conflict "
                                     "exists or could arise, I will inform the contracting "
                                     "authority without delay;\nI am encouraged to report "
                                     "a situation or risk of conflict of interest as well as any "
                                     "type of wrongdoing or fraud (i.e. whistleblowing), and if I "
                                     "do so, I should not be treated unfairly or be sanctioned;\nI "
                                     "understand that the contracting authority reserves the right "
                                     "to verify this information.",
                            "dataType": "boolean",
                            "status": "active",
                            "datePublished": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data'][
                                'operationDate'],
                            "expectedValue": True
                        },
                        {
                            "id": GlobalClassTenderPeriodEndNoAuction.actual_ev_release[
                                'releases'][0]['tender']['criteria'][quantity_of_criteria_object_into_release][
                                'requirementGroups'][0]['requirements'][1]['id'],
                            "title": "I confirm that I will keep all matters entrusted to me confidential. "
                                     "I will not communicate outside the [project team/evaluation committee] "
                                     "any confidential information that is revealed to me or that I have discovered. "
                                     "I will not make any adverse use of information given to me.",
                            "dataType": "boolean",
                            "status": "active",
                            "datePublished": GlobalClassTenderPeriodEndNoAuction.feed_point_message['data'][
                                'operationDate'],
                            "expectedValue": True
                        }]
                }],
            "relatesTo": "award",
            "classification": {
                "scheme": "ESPD-2.2.1",
                "id": "CRITERION.EXCLUSION.CONFLICT_OF_INTEREST.PROCEDURE_PARTICIPATION"
            }
        }
        return expected_criteria_array_source_procuring_entity, quantity_of_criteria_object_into_release

    def prepare_array_of_parties_mapper_for_successful_tender(self, bid_payload):
        expected_array_of_parties_mapper = []
        try:
            """
            Check how many quantity of object into payload['bid']['tenderers'].
            """
            list_of_payload_tenderer_id = list()
            for tenderer_object in bid_payload['bid']['tenderers']:
                for i in tenderer_object['identifier']:
                    if i == "id":
                        list_of_payload_tenderer_id.append(i)
            quantity_of_tender_object_into_payload = len(list_of_payload_tenderer_id)
        except Exception:
            raise Exception("Impossible to check how many quantity of object into payload['bid']['tenderers']")

        for t in range(quantity_of_tender_object_into_payload):
            try:
                """
                Prepare party object framework.
                """
                party_object = {}
                party_object.update(self.constructor.ev_release_parties_object())
            except Exception:
                raise Exception("Impossible to build expected party object framework.")
            try:
                """
                Enrich party object framework by value: 'id', 'name', 'identifier', 'address', 'additionalIdentifiers', 
                'contactPoint', 'details.typeOfSupplier', 'details.mainEconomicActivities', 
                'details.permits from payload' from payload and MDM.
                """
                party_object['id'] = f"{bid_payload['bid']['tenderers'][t]['identifier']['scheme']}-" \
                                     f"{bid_payload['bid']['tenderers'][t]['identifier']['id']}"
                party_object['name'] = bid_payload['bid']['tenderers'][t]['name']
                party_object['identifier'] = bid_payload['bid']['tenderers'][t]['identifier']
                party_object['address']['streetAddress'] = \
                    bid_payload['bid']['tenderers'][t]['address']['streetAddress']
                party_object['address']['postalCode'] = \
                    bid_payload['bid']['tenderers'][t]['address']['postalCode']
                try:
                    """
                    Enrich party object framework by value: 'address.addressDetails.country', 
                     'address.addressDetails.region', 'address.addressDetails.locality' from MDM.
                    """
                    tenderer_country_data = self.mdm.get_country(
                        country=bid_payload['bid']['tenderers'][t]['address']['addressDetails']['country']['id'],
                        language=self.language
                    )
                    tenderer_country_object = {
                        "scheme": tenderer_country_data['data']['scheme'],
                        "id": tenderer_country_data['data']['id'],
                        "description": tenderer_country_data['data']['description'],
                        "uri": tenderer_country_data['data']['uri']
                    }
                    tenderer_region_data = self.mdm.get_region(
                        country=bid_payload['bid']['tenderers'][t]['address']['addressDetails']['country']['id'],
                        region=bid_payload['bid']['tenderers'][t]['address']['addressDetails']['region']['id'],
                        language=self.language
                    )
                    tenderer_region_object = {
                        "scheme": tenderer_region_data['data']['scheme'],
                        "id": tenderer_region_data['data']['id'],
                        "description": tenderer_region_data['data']['description'],
                        "uri": tenderer_region_data['data']['uri']
                    }
                    if bid_payload['bid']['tenderers'][t]['address']['addressDetails']['locality']['scheme'] == "CUATM":
                        tenderer_locality_data = self.mdm.get_locality(
                            country=bid_payload['bid']['tenderers'][t]['address']['addressDetails']['country']['id'],
                            region=bid_payload['bid']['tenderers'][t]['address']['addressDetails']['region']['id'],
                            locality=bid_payload['bid']['tenderers'][t]['address']['addressDetails']['locality']['id'],
                            language=self.language
                        )
                        tenderer_locality_object = {
                            "scheme": tenderer_locality_data['data']['scheme'],
                            "id": tenderer_locality_data['data']['id'],
                            "description": tenderer_locality_data['data']['description'],
                            "uri": tenderer_locality_data['data']['uri']
                        }
                    else:
                        tenderer_locality_object = {
                            "scheme":
                                bid_payload['bid']['tenderers'][t]['address']['addressDetails'][
                                    'locality']['scheme'],
                            "id": bid_payload['bid']['tenderers'][t]['address']['addressDetails'][
                                'locality']['id'],
                            "description":
                                bid_payload['bid']['tenderers'][t]['address']['addressDetails'][
                                    'locality']['description']
                        }
                except Exception:
                    raise Exception("Impossible to enrich party object framework by value: "
                                    "'address.addressDetails.country', 'address.addressDetails.region', "
                                    "'address.addressDetails.locality' from MDM.")
                party_object['address']['addressDetails']['country'] = tenderer_country_object
                party_object['address']['addressDetails']['region'] = tenderer_region_object
                party_object['address']['addressDetails']['locality'] = tenderer_locality_object
                party_object['additionalIdentifiers'] = bid_payload['bid']['tenderers'][t]['additionalIdentifiers']
                party_object['contactPoint'] = bid_payload['bid']['tenderers'][t]['contactPoint']
                party_object['details']['typeOfSupplier'] = \
                    bid_payload['bid']['tenderers'][t]['details']['typeOfSupplier']
                party_object['details']['mainEconomicActivities'] = \
                    bid_payload['bid']['tenderers'][t]['details']['mainEconomicActivities']
                party_object['details']['permits'] = \
                    bid_payload['bid']['tenderers'][t]['details']['permits']
            except Exception:
                raise Exception("Impossible to enrich party object framework by value: 'id', 'name', "
                                "'identifier', 'address', 'additionalIdentifiers', "
                                "'contactPoint', 'details.typeOfSupplier', 'details.mainEconomicActivities', "
                                "'details.permits from payload and MDM'.")
            try:
                """
                Enrich party object framework by value: 'details.bankAccounts' from payload and MDM.
                """
                try:
                    """
                    Check how many quantity of object into payload['bid']['tenderers'][´details']['bankAccounts'].
                    """
                    list_of_payload_tenderer_details_bank_accounts_name = list()
                    for i in bid_payload['bid']['tenderers'][t]['details']['bankAccounts']:
                        for i_1 in i:
                            if i_1 == "bankName":
                                list_of_payload_tenderer_details_bank_accounts_name.append(i_1)
                    quantity_of_tender_details_bank_accounts_objects_into_payload = \
                        len(list_of_payload_tenderer_details_bank_accounts_name)
                except Exception:
                    raise Exception("Impossible to check how many quantity of object into "
                                    "payload['bid']['tenderers'][´details']['bankAccounts']")
                for b in range(quantity_of_tender_details_bank_accounts_objects_into_payload):
                    party_object['details']['bankAccounts'].append(
                        self.constructor.ev_release_parties_details_bank_account_object())
                    party_object['details']['bankAccounts'][b]['description'] = \
                        bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['description']
                    party_object['details']['bankAccounts'][b]['bankName'] = \
                        bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['bankName']
                    party_object['details']['bankAccounts'][b]['address']['streetAddress'] = \
                        bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address']['streetAddress']
                    party_object['details']['bankAccounts'][b]['address']['postalCode'] = \
                        bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address']['postalCode']

                    try:
                        """
                        Enrich party object framework by value: 
                        'bid.tenderers.details.bankAccounts.address.addressDetails.country', 
                        'bid.tenderers.details.bankAccounts.address.addressDetails.region',
                        'bid.tenderers.details.bankAccounts.address.addressDetails.locality'
                        from MDM.
                        """
                        bank_country_data = self.mdm.get_country(
                            country=bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                'addressDetails']['country']['id'],
                            language=self.language
                        )
                        bank_country_object = {
                            "scheme": bank_country_data['data']['scheme'],
                            "id": bank_country_data['data']['id'],
                            "description": bank_country_data['data']['description'],
                            "uri": bank_country_data['data']['uri']
                        }
                        bank_region_data = self.mdm.get_region(
                            country=bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                'addressDetails']['country']['id'],
                            region=bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                'addressDetails']['region']['id'],
                            language=self.language
                        )
                        bank_region_object = {
                            "scheme": bank_region_data['data']['scheme'],
                            "id": bank_region_data['data']['id'],
                            "description": bank_region_data['data']['description'],
                            "uri": bank_region_data['data']['uri']
                        }
                        if \
                                bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                    'addressDetails']['locality']['scheme'] == "CUATM":
                            bank_locality_data = self.mdm.get_locality(
                                country=bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                    'addressDetails']['country']['id'],
                                region=bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                    'addressDetails']['region']['id'],
                                locality=bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                    'addressDetails']['locality']['id'],
                                language=self.language
                            )
                            bank_locality_object = {
                                "scheme": bank_locality_data['data']['scheme'],
                                "id": bank_locality_data['data']['id'],
                                "description": bank_locality_data['data']['description'],
                                "uri": bank_locality_data['data']['uri']
                            }
                        else:
                            bank_locality_object = {
                                "scheme":
                                    bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                        'addressDetails']['locality']['scheme'],
                                "id": bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                    'addressDetails']['locality']['id'],
                                "description":
                                    bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['address'][
                                        'addressDetails']['locality']['description']
                            }
                    except Exception:
                        raise Exception("Impossible to enrich party object framework by value: "
                                        "'bid.tenderers.details.bankAccounts.address.addressDetails.country', "
                                        "'bid.tenderers.details.bankAccounts.address.addressDetails.region',"
                                        "'bid.tenderers.details.bankAccounts.address.addressDetails.locality'"
                                        "from MDM.")
                    party_object['details']['bankAccounts'][b]['address']['addressDetails']['country'] = \
                        bank_country_object
                    party_object['details']['bankAccounts'][b]['address']['addressDetails']['region'] = \
                        bank_region_object
                    party_object['details']['bankAccounts'][b]['address']['addressDetails']['locality'] = \
                        bank_locality_object
                    party_object['details']['bankAccounts'][b]['identifier'] = \
                        bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['identifier']
                    party_object['details']['bankAccounts'][b]['accountIdentification'] = \
                        bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['accountIdentification']
                    party_object['details']['bankAccounts'][b]['additionalAccountIdentifiers'] = \
                        bid_payload['bid']['tenderers'][t]['details']['bankAccounts'][b]['additionalAccountIdentifiers']
            except Exception:
                raise Exception("Impossible to enrich party object framework by value: 'details.bankAccounts' "
                                "from payload and MDM.")
            try:
                """
                Enrich party object framework by value: 'details.legalForm' from payload.
                """
                party_object['details']['legalForm'] = bid_payload['bid']['tenderers'][t]['details']['legalForm']
            except Exception:
                raise Exception("Impossible to enrich party object framework by value: 'details.legalForm' "
                                "from payload")
            try:
                """
                Enrich party object framework by value: 'details.legalForm', 'details.scale' from payload.
                """
                party_object['details']['legalForm'] = bid_payload['bid']['tenderers'][t]['details']['legalForm']
                party_object['details']['scale'] = bid_payload['bid']['tenderers'][t]['details']['scale']
            except Exception:
                raise Exception("Impossible to enrich party object framework by value: 'details.legalForm', "
                                "'details.scale' from payload")
            try:
                """
                Check how many quantity of object into payload['bid']['tenderers']['persones'].
                """
                list_of_payload_party_persones_id = list()
                for i in bid_payload['bid']['tenderers'][t]['persones']:
                    for i_1 in i:
                        if i_1 == "identifier":
                            for i_2 in i['identifier']:
                                if i_2 == "id":
                                    list_of_payload_party_persones_id.append(i_2)
                quantity_of_persones_into_payload = \
                    len(list_of_payload_party_persones_id)
            except Exception:
                raise Exception("Impossible to check how many quantity of object into "
                                "payload['bid']['tenderers']['persones'].")
            for p in range(quantity_of_persones_into_payload):
                party_object['persones'].append(self.constructor.ev_release_parties_person_object())
                party_object['persones'][p]['id'] = \
                    f"{bid_payload['bid']['tenderers'][t]['persones'][p]['identifier']['scheme']}-" \
                    f"{bid_payload['bid']['tenderers'][t]['persones'][p]['identifier']['id']}"
                party_object['persones'][p]['title'] = \
                    bid_payload['bid']['tenderers'][t]['persones'][p]['title']
                party_object['persones'][p]['name'] = \
                    bid_payload['bid']['tenderers'][t]['persones'][p]['name']
                party_object['persones'][p]['identifier'] = \
                    bid_payload['bid']['tenderers'][t]['persones'][p]['identifier']
                try:
                    """
                    Check how many quantity of object into payload['bid']['tenderers']['persones']['businessFunctions'].
                    """
                    list_of_payload_party_persones_business_functions_id = list()
                    for i in \
                            bid_payload['bid']['tenderers'][t]['persones'][p]['businessFunctions']:
                        for i_1 in i:
                            if i_1 == "id":
                                list_of_payload_party_persones_business_functions_id.append(i_1)
                    quantity_of_business_functions_into_payload = \
                        len(list_of_payload_party_persones_business_functions_id)
                except Exception:
                    raise Exception("Impossible to check how many quantity of object into "
                                    "payload['bid']['tenderers']['persones']['businessFunctions'].")
                for bf in range(quantity_of_business_functions_into_payload):
                    party_object['persones'][p]['businessFunctions'].append(
                        self.constructor.ev_release_parties_person_business_function_object()
                    )
                    party_object['persones'][p]['businessFunctions'][bf]['id'] = \
                        bid_payload['bid']['tenderers'][t]['persones'][p]['businessFunctions'][bf]['id']
                    party_object['persones'][p]['businessFunctions'][bf]['type'] = \
                        bid_payload['bid']['tenderers'][t]['persones'][p]['businessFunctions'][bf]['type']
                    party_object['persones'][p]['businessFunctions'][bf]['jobTitle'] = \
                        bid_payload['bid']['tenderers'][t]['persones'][p]['businessFunctions'][bf]['jobTitle']
                    party_object['persones'][p]['businessFunctions'][bf]['period']['startDate'] = \
                        bid_payload['bid']['tenderers'][t]['persones'][p]['businessFunctions'][bf]['period'][
                            'startDate']
                    try:
                        """
                        Check how many quantity of object into payload['bid']['tenderers']['persones']
                        ['businessFunctions']['documents'].
                        """
                        list_of_payload_party_persones_business_functions_documents_id = list()
                        for i in \
                                bid_payload['bid']['tenderers'][t]['persones'][p][
                                    'businessFunctions'][bf]['documents']:
                            for i_1 in i:
                                if i_1 == "id":
                                    list_of_payload_party_persones_business_functions_documents_id.append(i_1)
                        quantity_of_business_functions_documents_into_payload = \
                            len(list_of_payload_party_persones_business_functions_documents_id)
                    except Exception:
                        raise Exception("Impossible to check how many quantity of object into "
                                        "payload['bid']['tenderers']['persones']['businessFunctions']['documents'].")
                    for bfd in range(quantity_of_business_functions_documents_into_payload):
                        party_object['persones'][p]['businessFunctions'][bf]['documents'].append(
                            self.constructor.ev_release_parties_person_business_function_document_object()
                        )
                        party_object['persones'][p]['businessFunctions'][bf]['documents'][bfd][
                            'documentType'] = bid_payload['bid']['tenderers'][t]['persones'][p][
                            'businessFunctions'][bf]['documents'][bfd]['documentType']
                        party_object['persones'][p]['businessFunctions'][bf]['documents'][bfd][
                            'id'] = bid_payload['bid']['tenderers'][t]['persones'][p]['businessFunctions'][bf][
                            'documents'][bfd]['id']
                        party_object['persones'][p]['businessFunctions'][bf]['documents'][bfd][
                            'title'] = bid_payload['bid']['tenderers'][t]['persones'][p]['businessFunctions'][bf][
                            'documents'][bfd]['title']
                        party_object['persones'][p]['businessFunctions'][bf]['documents'][bfd][
                            'description'] = bid_payload['bid']['tenderers'][t]['persones'][p]['businessFunctions'][bf][
                            'documents'][bfd]['description']
                        party_object['persones'][p]['businessFunctions'][bf]['documents'][bfd]['url'] = \
                            f"{self.metadata_document_url}/" + \
                            bid_payload['bid']['tenderers'][t]['persones'][p][
                                'businessFunctions'][bf]['documents'][bfd]['id']
                        party_object['persones'][p]['businessFunctions'][bf]['documents'][bfd][
                            'datePublished'] = GlobalClassTenderPeriodEndNoAuction.feed_point_message['data'][
                            'operationDate']
            party_object['roles'] = ["tenderer", "supplier"]
            mapper = {
                "id": party_object['id'],
                "value": party_object
            }
            expected_array_of_parties_mapper.append(mapper)
        return expected_array_of_parties_mapper

    def prepare_array_of_awards_mapper(self, bid_payload):
        expected_array_of_awards_mapper = list()
        try:
            """
            Get 'relatedLots' from bid_payload.
            """
            related_lots_array = bid_payload['bid']['relatedLots']
        except Exception:
            raise Exception("Impossible to get 'relatedLots' from bid_payload.")

        try:
            """
            Check status of lot from bid_payload['bid']['relatedLots'].
            """
            lots_have_active_status = list()
            lots_have_unsuccessful_or_cancelled_status = list()
            for bl in related_lots_array:
                for li in GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']['lots']:
                    if li['id'] == bl:
                        if li['status'] == "active":
                            lots_have_active_status.append(li['id'])
                        elif li['status'] == "unsuccessful":
                            lots_have_unsuccessful_or_cancelled_status.append(li['id'])
                        elif li['status'] == "cancelled":
                            lots_have_unsuccessful_or_cancelled_status.append(li['id'])
                        else:
                            raise Exception("ERROR: status of lot was not found into "
                                            "'tender_period_end_actual_ev_release['releases'][0]['lots']'.")
        except Exception:
            raise Exception("Impossible to check status of lot from bid_payload['bid']['relatedLots'].")

        try:
            """
            Prepare successful award object framework.
            """
            quantity_of_lots_have_active_status = len(lots_have_active_status)

            for al in range(quantity_of_lots_have_active_status):
                successful_award_object = {}
                successful_award_object.update(self.constructor.ev_release_successful_award_object())
                successful_award_object['status'] = "pending"
                successful_award_object['statusDetails'] = "awaiting"
                successful_award_object['date'] = \
                    GlobalClassTenderPeriodEndNoAuction.feed_point_message['data']['operationDate']
                successful_award_object['value'] = bid_payload['bid']['value']

                try:
                    """
                    Check how many quantity of object into payload['bid']['tenderers'].
                    """
                    list_of_payload_tenderer_id = list()
                    for tenderer_object in bid_payload['bid']['tenderers']:
                        for i in tenderer_object['identifier']:
                            if i == "id":
                                list_of_payload_tenderer_id.append(i)
                    quantity_of_tender_object_into_payload = len(list_of_payload_tenderer_id)
                except Exception:
                    raise Exception("Impossible to check how many quantity of object into payload['bid']['tenderers']")
                for t in range(quantity_of_tender_object_into_payload):
                    successful_award_object['suppliers'].append(
                        self.constructor.ev_release_successful_award_supplier_object())
                    successful_award_object['suppliers'][t]['id'] = \
                        f"{bid_payload['bid']['tenderers'][t]['identifier']['scheme']}-" \
                        f"{bid_payload['bid']['tenderers'][t]['identifier']['id']}"
                    successful_award_object['suppliers'][t]['name'] = bid_payload['bid']['tenderers'][t]['name']
                successful_award_object['relatedLots'] = bid_payload['bid']['relatedLots']

                try:
                    """
                    Set 'relatedBid' into successful_award_array[al]['relatedLots'].
                    """
                    for detail in \
                            GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['bids']['details']:
                        if detail['tenderers'] == successful_award_object['suppliers']:
                            successful_award_object['relatedBid'] = detail['id']
                except Exception:
                    raise Exception("Impossible to set 'relatedBid' into successful_award_array[al]['relatedLots'].")

                if "criteria" in GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']:
                    try:
                        """
                        Check 'awardCriteria' & 'awardCriteriaDetails' into 
                        GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']['awardCriteria'].
                        """
                        award_criteria = GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender'][
                            'awardCriteria']
                        award_criteria_details = GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0][
                            'tender']['awardCriteriaDetails']

                        if award_criteria == "priceOnly" and award_criteria_details == "automated":
                            del successful_award_object['weightedValue']
                        elif award_criteria == "costOnly" or award_criteria == "qualityOnly" or \
                                award_criteria == "ratedCriteria":

                            try:
                                """
                                Check how many quantity of object into bid_payload['bid']['requirementResponses'].
                                Get requirement from bid_payload['bid']['requirementResponses'].
                                """
                                list_of_payload_requirement_id = list()
                                for tenderer_object in bid_payload['bid']['requirementResponses']:
                                    list_of_payload_requirement_id.append(tenderer_object['requirement']['id'])
                            except Exception:
                                raise Exception(
                                    "Impossible to check how many quantity of object into "
                                    "payload['bid']['requirementResponses'],"
                                    "Impossible to get requirement from bid_payload['bid']['requirementResponses'].")

                            coefficients_array_from_release = list()
                            try:
                                """
                                Get criteria, where relatesTo = 'tenderer', 'item', 'lot', 'tender' 
                                into criterion 'CRITERION.SELECTION' and 'CRITERION.OTHER'.
                                """
                                for rs in list_of_payload_requirement_id:
                                    for cr in \
                                            GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0][
                                                'tender']['criteria']:
                                        if cr['classification']['id'][:20] == "CRITERION.SELECTION." and \
                                                cr['relatesTo'] == "tenderer" or \
                                                cr['classification']['id'][:20] == "CRITERION.SELECTION." and \
                                                cr['relatesTo'] == "item" or \
                                                cr['classification']['id'][:20] == "CRITERION.SELECTION." and \
                                                cr['relatesTo'] == "lot" or \
                                                cr['classification']['id'][:20] == "CRITERION.SELECTION." and \
                                                cr['relatesTo'] == "tender":
                                            for cr_1 in cr['requirementGroups']:
                                                for cr_2 in cr_1['requirements']:
                                                    if rs == cr_2['id']:
                                                        for con in \
                                                                GlobalClassTenderPeriodEndNoAuction.actual_ev_release[
                                                                    'releases'][0]['tender']['conversions']:
                                                            if con['relatedItem'] == rs:
                                                                coefficient_mapper = {
                                                                    "id": rs,
                                                                    "coefficients": con['coefficients']
                                                                }
                                                                coefficients_array_from_release.append(
                                                                    coefficient_mapper)
                                        elif cr['classification']['id'][:16] == "CRITERION.OTHER." and \
                                                cr['relatesTo'] == "tenderer" or \
                                                cr['classification']['id'][:16] == "CRITERION.OTHER." and \
                                                cr['relatesTo'] == "item" or \
                                                cr['classification']['id'][:16] == "CRITERION.OTHER." and \
                                                cr['relatesTo'] == "lot" or \
                                                cr['classification']['id'][:16] == "CRITERION.OTHER." and \
                                                cr['relatesTo'] == "tender":
                                            for cr_1 in cr['requirementGroups']:
                                                for cr_2 in cr_1['requirements']:
                                                    if rs == cr_2['id']:
                                                        for con in \
                                                                GlobalClassTenderPeriodEndNoAuction.actual_ev_release[
                                                                    'releases'][0]['tender']['conversions']:
                                                            if con['relatedItem'] == rs:
                                                                coefficient_mapper = {
                                                                    "id": rs,
                                                                    "coefficients": con['coefficients']
                                                                }
                                                                coefficients_array_from_release.append(
                                                                    coefficient_mapper)
                            except Exception:
                                raise Exception(
                                    "Impossible to get criteria, where relatesTo = 'tenderer', 'item', 'lot', "
                                    "'tender' into criterion 'CRITERION.SELECTION' and 'CRITERION.OTHER'.")

                            if str(coefficients_array_from_release) != str([]):
                                try:
                                    """
                                    Prepare 'weightedValue' object.
                                    """
                                    for y in coefficients_array_from_release:
                                        for x in bid_payload['bid']['requirementResponses']:
                                            if x['requirement']['id'] == y['id']:
                                                for z in coefficients_array_from_release:

                                                    for z_1 in z['coefficients']:
                                                        """ z_1 is dict """
                                                        """# z_1['value'] is float """
                                                        if z_1['value'] == x['value']:
                                                            successful_award_object['weightedValue']['amount'] = \
                                                                round(successful_award_object['value']['amount'] *
                                                                      z_1['coefficient'], 2)
                                                            successful_award_object['weightedValue']['currency'] = \
                                                                successful_award_object['value']['currency']
                                except Exception:
                                    raise Exception("Impossible to prepare 'weightedValue' object.")
                            elif str(coefficients_array_from_release) == str([]):
                                successful_award_object['weightedValue'] = successful_award_object['value']
                    except Exception:
                        raise Exception("Impossible to check 'awardCriteria' & 'awardCriteriaDetails'.")
                try:
                    """
                    Set permanent id for successful_award_array[al]['id'].
                    """
                    successful_award_object['id'] = \
                        GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['awards'][al]['id']
                except Exception:
                    raise Exception("Impossible to check how many quantity of object into "
                                    "GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['awards'].")
                mapper = {
                    "suppliers": successful_award_object['suppliers'],
                    "value": successful_award_object
                }
                expected_array_of_awards_mapper.append(mapper)
        except Exception:
            raise Exception("Impossible to prepare successful award object framework.")
        return expected_array_of_awards_mapper
