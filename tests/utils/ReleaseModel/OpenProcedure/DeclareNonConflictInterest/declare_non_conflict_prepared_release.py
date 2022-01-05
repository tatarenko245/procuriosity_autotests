import copy
import datetime

from tests.utils.ReleaseModel.OpenProcedure.DeclareNonConflictInterest.declare_non_conflict_release_library import ReleaseLibrary
from tests.utils.functions import is_it_uuid, get_project_root


class DeclareExpectedRelease:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.metadata_tender_url = None
        self.metadata_document_url = None
        self.metadata_auction_url = None

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

    def awards_requirement_responses_array(
            self, actual_awards_array, declare_payload):
        actual_awards_requirement_responses_id = list()
        try:
            """
            Calculate how many quantity of object into actual_awards_requirement_responses_array
            """
            for a in actual_awards_array:
                if a['status'] == "pending":
                    if a['statusDetails'] == "awaiting":
                        for a_1 in a:
                            if a_1 == "requirementResponses":
                                for a_2 in a['requirementResponses']:
                                    actual_awards_requirement_responses_id.append(a_2['id'])
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_prepared_release.py -> \n" \
                          f"Class = DeclareExpectedRelease -> \n" \
                          f"Method = awards_requirement_responses_array -> \n" \
                          f"Message: Impossible to calculate how many quantity of object into " \
                          f"actual_awards_requirement_responses_array.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to calculate how many quantity of object into "
                            f"actual_awards_requirement_responses_array.")
        try:
            """
            Prepare final expected awards.requirementResponses.
            """

            for x in range(len(actual_awards_requirement_responses_id)):
                try:
                    """
                    Check that id into actual_awards_requirement_responses_array is uuid v.4
                    """
                    check = is_it_uuid(
                        uuid_to_test=actual_awards_requirement_responses_id[x],
                        version=4
                    )
                    if check is True:
                        pass
                    else:
                        raise ValueError("The id into actual_awards_requirement_responses_array is uuid v.4 "
                                         "must be uuid version 4")
                except Exception:
                    log_msg_one = f"\n{datetime.datetime.now()}\n" \
                                  f"File = declare_non_conflict_interest_prepared_release.py -> \n" \
                                  f"Class = DeclareExpectedRelease -> \n" \
                                  f"Method = awards_requirement_responses_array -> \n" \
                                  f"Message: Check your awards.requirementResponses array in actual ev release.\n"
                    with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                        logfile.write(log_msg_one)
                    raise Exception("Check your awards.requirementResponses array in actual ev release.")
            expected_requirement_responses_object = {}
            expected_requirement_responses_object.update(
                self.constructor.awards_requirement_responses_object())
            expected_requirement_responses_object['value'] = declare_payload['requirementResponse']['value']
            expected_requirement_responses_object['requirement']['id'] = \
                declare_payload['requirementResponse']['requirement']['id']
            expected_requirement_responses_object['responder']['id'] = \
                f"{declare_payload['requirementResponse']['responder']['identifier']['scheme']}-" \
                f"{declare_payload['requirementResponse']['responder']['identifier']['id']}"
            expected_requirement_responses_object['responder']['name'] = \
                declare_payload['requirementResponse']['responder']['name']
            expected_requirement_responses_object['relatedTenderer']['id'] = \
                declare_payload['requirementResponse']['relatedTenderer']['id']

            for a in actual_awards_array:
                if a['status'] == "pending":
                    if a['statusDetails'] == "awaiting":
                        for a_1 in a:
                            if a_1 == "requirementResponses":
                                for a_2 in a['requirementResponses']:
                                    if a_2['requirement']['id'] == \
                                            declare_payload['requirementResponse']['requirement']['id']:
                                        if a_2['responder']['id'] == \
                                                expected_requirement_responses_object['responder']['id']:
                                            if a_2['relatedTenderer']['id'] == \
                                                    declare_payload['requirementResponse']['relatedTenderer']['id']:
                                                expected_requirement_responses_object['id'] = a_2['id']
        except Exception:
            log_msg_one = f"\n{datetime.datetime.now()}\n" \
                          f"File = declare_non_conflict_interest_prepared_release.py -> \n" \
                          f"Class = DeclareExpectedRelease -> \n" \
                          f"Method = awards_requirement_responses_array -> \n" \
                          f"Message: Impossible to prepare final expected awards.requirementResponses.\n"
            with open(f'{get_project_root()}/logfile.txt', 'a') as logfile:
                logfile.write(log_msg_one)
            raise Exception("Impossible to prepare final expected awards.requirementResponses.")
        return expected_requirement_responses_object
