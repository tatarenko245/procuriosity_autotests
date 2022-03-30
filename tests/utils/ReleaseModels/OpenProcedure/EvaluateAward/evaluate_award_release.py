import copy

from tests.utils.ReleaseModels.OpenProcedure.EvaluateAward.evaluate_award_library import ReleaseLibrary


class AwardEvaluationRelease:
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

    def iterable_item_added_awards_documents_full_data_model(self, award_payload, award_evaluation_feed_point_message):
        try:
            """
            Calculate how many documents into award_payload['awards'].
            """
            award_documents_list = list()
            if "documents" in award_payload['award']:
                for d in award_payload['award']['documents']:
                    award_documents_list.append(d['id'])
        except Exception:
            raise Exception("Impossible to calculate how many documents into award_payload['award'].")

        try:
            """
            Prepare iterable_item_added object
            """
            iterable_item_added = list()

            for m in range(len(award_documents_list)):
                new_item = {}
                new_item.update(self.constructor.iterable_item_added_awards_document_object())
                new_item['id'] = award_payload['award']['documents'][m]['id']
                new_item['documentType'] = award_payload['award']['documents'][m]['documentType']
                new_item['title'] = award_payload['award']['documents'][m]['title']
                new_item['description'] = award_payload['award']['documents'][m]['description']
                new_item['relatedLots'] = award_payload['award']['documents'][m]['relatedLots']
                new_item['url'] = f"{self.metadata_document_url}/{award_payload['award']['documents'][m]['id']}"
                new_item['datePublished'] = award_evaluation_feed_point_message['data']['operationDate']

                iterable_item_added.append(new_item)
        except Exception:
            raise Exception("Impossible to prepare iterable_item_added object")
        return iterable_item_added

    def iterable_item_added_awards_documents_obligatory_data_model(self, award_payload,
                                                                   award_evaluation_feed_point_message):
        try:
            """
            Calculate how many documents into award_payload['awards'].
            """
            award_documents_list = list()
            if "documents" in award_payload['award']:
                for d in award_payload['award']['documents']:
                    award_documents_list.append(d['id'])
        except Exception:
            raise Exception("Impossible to calculate how many documents into award_payload['award'].")

        try:
            """
            Prepare iterable_item_added object
            """
            iterable_item_added = list()

            for m in range(len(award_documents_list)):
                new_item = {}
                new_item.update(self.constructor.iterable_item_added_awards_document_object())
                del new_item['description']
                del new_item['relatedLots']
                new_item['id'] = award_payload['award']['documents'][m]['id']
                new_item['documentType'] = award_payload['award']['documents'][m]['documentType']
                new_item['title'] = award_payload['award']['documents'][m]['title']
                new_item['url'] = f"{self.metadata_document_url}/{award_payload['award']['documents'][m]['id']}"
                new_item['datePublished'] = award_evaluation_feed_point_message['data']['operationDate']

                iterable_item_added.append(new_item)
        except Exception:
            raise Exception("Impossible to prepare iterable_item_added object")
        return iterable_item_added
