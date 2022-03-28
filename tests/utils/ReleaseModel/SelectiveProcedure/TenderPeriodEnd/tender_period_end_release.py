import copy

from tests.utils.ReleaseModel.SelectiveProcedure.TenderPeriodEnd.tender_period_end_release_library import ReleaseLibrary
from tests.utils.functions_collection import check_uuid_version
from tests.utils.services.e_mdm_service import MdmService


class TenderPeriodExpectedChanges:
    def __init__(self, environment, language, host_for_services):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.metadata_tender_url = None
        self.metadata_document_url = None
        self.metadata_auction_url = None
        self.mdm = MdmService(host_for_service=host_for_services)

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

    def prepare_unsuccessful_awards_array(
            self, cnonpn_payload, actual_tp_release_after_tender_period_end_expired,
            tender_period_end_feed_point_message):
        try:
            """
            Check how many quantity of object into payload['tender']['lots'].
            """
            list_of_payload_lot_id = list()
            for ob in cnonpn_payload['tender']['lots']:
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
            for i in actual_tp_release_after_tender_period_end_expired['releases'][0]['tender']['lots']:
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
            expected_awards_array.append(self.constructor.tp_release_unsuccessful_award_object())
            expected_awards_array[q]['title'] = "The contract/lot is not awarded"
            expected_awards_array[q]['description'] = "Other reasons (discontinuation of procedure)"
            expected_awards_array[q]['status'] = "unsuccessful"
            expected_awards_array[q]['statusDetails'] = "noOffersReceived"
            expected_awards_array[q]['date'] = \
                tender_period_end_feed_point_message['data']['operationDate']
            expected_awards_array[q]['relatedLots'] = \
                [actual_tp_release_after_tender_period_end_expired['releases'][0]['tender']['lots'][q]['id']]

            if actual_tp_release_after_tender_period_end_expired['releases'][0]['awards'][q]['relatedLots'][0] == \
                    expected_awards_array[q]['relatedLots'][0]:
                expected_awards_array[q]['id'] = \
                    actual_tp_release_after_tender_period_end_expired['releases'][0]['awards'][q]['id']
            else:
                pass
        return expected_awards_array

    def prepare_bid_details_mapper(
            self, bid_payload, bid_feed_point_message, actual_tp_release_after_tender_period_end,
            tender_period_end_feed_point_message):
        expected_bid_object = {}
        expected_bid_object.update(self.constructor.tp_release_bid_object())
        expected_bid_object['details'].append(self.constructor.tp_release_bid_details_object())
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
                uuid_to_test=actual_tp_release_after_tender_period_end['releases'][0]['bids']['details'][0][
                    'id'],
                version=4
            )
            if check is True:
                expected_bid_object['details'][0]['id'] = \
                    actual_tp_release_after_tender_period_end['releases'][0]['bids']['details'][0]['id']
            else:
                raise ValueError("businessFunctions.id in release must be uuid version 4")
        except Exception:
            raise Exception("Check your businessFunctions array in release")
        expected_bid_object['details'][0]['status'] = "pending"
        expected_bid_object['details'][0]['date'] = bid_feed_point_message['data']['operationDate']
        for q in range(quantity_of_tender_object_into_payload):
            expected_bid_object['details'][0]['tenderers'].append(
                self.constructor.tp_release_bid_details_tenderer_object())
            expected_bid_object['details'][0]['tenderers'][q]['id'] = \
                f"{bid_payload['bid']['tenderers'][q]['identifier']['scheme']}-" \
                f"{bid_payload['bid']['tenderers'][q]['identifier']['id']}"
            expected_bid_object['details'][0]['tenderers'][q]['name'] = bid_payload['bid']['tenderers'][q]['name']
        expected_bid_object['details'][0]['value']['amount'] = bid_payload['bid']['value']['amount']
        expected_bid_object['details'][0]['value']['currency'] = bid_payload['bid']['value']['currency']

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
                        actual_tp_release_after_tender_period_end['releases'][0]['bids']['details'][0][
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
                    self.constructor.tp_release_bid_details_requirement_response_object()
                )
                try:
                    check = check_uuid_version(
                        uuid_to_test=actual_tp_release_after_tender_period_end['releases'][0]['bids'][
                            'details'][0]['requirementResponses'][q_two]['id'],
                        version=4
                    )
                    if check is True:
                        expected_bid_object['details'][0]['requirementResponses'][q_two]['id'] = \
                            actual_tp_release_after_tender_period_end['releases'][0]['bids']['details'][0][
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
                            actual_tp_release_after_tender_period_end['releases'][0]['bids']['details'][0][
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
                        self.constructor.tp_release_bid_details_requirement_response_evidences_object()
                    )
                    try:
                        check = check_uuid_version(
                            uuid_to_test=actual_tp_release_after_tender_period_end['releases'][0]['bids'][
                                'details'][0]['requirementResponses'][q_two]['evidences'][q_three]['id'],
                            version=4
                        )
                        if check is True:
                            expected_bid_object['details'][0]['requirementResponses'][q_two][
                                'evidences'][q_three]['id'] = \
                                actual_tp_release_after_tender_period_end['releases'][0]['bids'][
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

    def prepare_array_of_awards_mapper(self, bid_payload, actual_tp_release_after_tender_period_end,
                                       tender_period_end_feed_point_message):
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
                for li in actual_tp_release_after_tender_period_end['releases'][0]['tender']['lots']:
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
                successful_award_object.update(self.constructor.tp_release_successful_award_object())
                successful_award_object['status'] = "pending"
                successful_award_object['statusDetails'] = "awaiting"
                successful_award_object['date'] = \
                    tender_period_end_feed_point_message['data']['operationDate']
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
                        self.constructor.tp_release_successful_award_supplier_object())
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
                            actual_tp_release_after_tender_period_end['releases'][0]['bids']['details']:
                        if detail['tenderers'] == successful_award_object['suppliers']:
                            successful_award_object['relatedBid'] = detail['id']
                except Exception:
                    raise Exception("Impossible to set 'relatedBid' into successful_award_array[al]['relatedLots'].")

                if "criteria" in actual_tp_release_after_tender_period_end['releases'][0]['tender']:
                    try:
                        """
                        Check 'awardCriteria' & 'awardCriteriaDetails' into 
                        GlobalClassTenderPeriodEndNoAuction.actual_ev_release['releases'][0]['tender']['awardCriteria'].
                        """
                        award_criteria = actual_tp_release_after_tender_period_end['releases'][0]['tender'][
                            'awardCriteria']
                        award_criteria_details = actual_tp_release_after_tender_period_end['releases'][0][
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
                                            actual_tp_release_after_tender_period_end['releases'][0][
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
                                                                actual_tp_release_after_tender_period_end[
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
                                                                actual_tp_release_after_tender_period_end[
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
                        actual_tp_release_after_tender_period_end['releases'][0]['awards'][al]['id']
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
