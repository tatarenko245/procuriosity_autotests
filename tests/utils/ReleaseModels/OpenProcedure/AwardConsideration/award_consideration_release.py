import copy

from tests.utils.ReleaseModels.OpenProcedure.AwardConsideration.award_consideration_library import ReleaseLibrary


class AwardConsiderationRelease:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.metadata_tender_url = None
        self.metadata_document_url = None
        self.metadata_auction_url = None

        try:
            if environment == "dev":
                self.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"

            elif environment == "sandbox":
                self.metadata_document_url = "http://storage.eprocurement.systems/get"

        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

    def iterable_item_added_new_bid_details_document(self, bid_payload, award_consideration_feed_point_message):
        try:
            """
            Calculate how many documents have documentType "x_qualificationDocuments" or "submissionDocuments".
            Calculate how many documents into bid_payload['bids'].
            """
            bid_documents_list_without = list()
            bid_documents_list_with = list()
            if "documents" in bid_payload['bid']:
                for d in bid_payload['bid']['documents']:
                    if d['documentType'] != "x_eligibilityDocuments" and \
                            d['documentType'] != "submissionDocuments":
                        bid_documents_list_with.append(d)

                    elif d['documentType'] == "x_eligibilityDocuments" or \
                            d['documentType'] == "submissionDocuments":
                        bid_documents_list_without.append(d)
        except Exception:
            raise Exception(
                "Impossible to calculate how many documents have documentType 'x_qualificationDocuments' or "
                "'submissionDocuments'."
                "Impossible to calculate how many documents into bid_payload['bid'].")

        try:
            """
            Prepare iterable_item_added object
            """
            iterable_item_added = dict()
            if len(bid_documents_list_with) > 0:
                for m in range(len(bid_documents_list_with)):
                    n = len(bid_documents_list_without) + m
                    new_item = {}
                    new_item.update(self.constructor.iterable_item_added_document_object(n=n))

                    new_item[f"root['releases'][0]['bids']['details'][0]['documents'][{n}]"]['id'] = \
                        bid_documents_list_with[m]['id']
                    new_item[f"root['releases'][0]['bids']['details'][0]['documents'][{n}]"]['documentType'] = \
                        bid_documents_list_with[m]['documentType']
                    new_item[f"root['releases'][0]['bids']['details'][0]['documents'][{n}]"]['title'] = \
                        bid_documents_list_with[m]['title']
                    new_item[f"root['releases'][0]['bids']['details'][0]['documents'][{n}]"]['description'] = \
                        bid_documents_list_with[m]['description']
                    new_item[f"root['releases'][0]['bids']['details'][0]['documents'][{n}]"]['url'] = \
                        f"{self.metadata_document_url}/{bid_documents_list_with[m]['id']}"
                    new_item[f"root['releases'][0]['bids']['details'][0]['documents'][{n}]"]['datePublished'] = \
                        award_consideration_feed_point_message['data']['operationDate']
                    new_item[f"root['releases'][0]['bids']['details'][0]['documents'][{n}]"]['relatedLots'] = \
                        bid_documents_list_with[m]['relatedLots']

                    iterable_item_added.update(new_item)

        except Exception:
            raise Exception("Impossible to prepare iterable_item_added object")

        # FReq-1.4.1.12:
        if str(bid_documents_list_without) == str([]):
            is_some_bid_document_was_opened_into_tender_period_end = False
        else:
            is_some_bid_document_was_opened_into_tender_period_end = True
        return iterable_item_added, is_some_bid_document_was_opened_into_tender_period_end

