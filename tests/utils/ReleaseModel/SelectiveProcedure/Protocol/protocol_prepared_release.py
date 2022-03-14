import copy
from tests.utils.ReleaseModel.SelectiveProcedure.Protocol.protocol_library import ReleaseLibrary


class ProtocolRelease:
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

    def iterable_item_added_contracts_array_as_contract_project(self, actual_ev_release, protocol_feed_point_message,
                                                                award_id, lot_id):
        iterable_item_added = list()
        try:
            """
            Prepare iterable_item_added object
            """
            new_item = {}
            new_item.update(self.constructor.iterable_item_added_contract())
            new_item['id'] = actual_ev_release['releases'][0]['contracts'][0]['id']
            new_item['date'] = protocol_feed_point_message['data']['operationDate']
            new_item['awardId'] = award_id
            new_item['relatedLots'] = [lot_id]
            new_item['status'] = "pending"
            new_item['statusDetails'] = "contractProject"
            iterable_item_added.append(new_item)
        except Exception:
            raise Exception("Impossible to prepare iterable_item_added object")
        return iterable_item_added

    def iterable_item_added_contracts_array_as_unsuccessful(self, actual_ev_release, protocol_feed_point_message,
                                                            lot_id):
        iterable_item_added = list()
        try:
            """
            Prepare iterable_item_added object
            """
            new_item = {}
            new_item.update(self.constructor.iterable_item_added_contract())
            del new_item['awardId']
            new_item['id'] = actual_ev_release['releases'][0]['contracts'][0]['id']
            new_item['date'] = protocol_feed_point_message['data']['operationDate']
            new_item['relatedLots'] = [lot_id]
            new_item['status'] = "pending"
            new_item['statusDetails'] = "unsuccessful"
            iterable_item_added.append(new_item)
        except Exception:
            raise Exception("Impossible to prepare iterable_item_added object")
        return iterable_item_added
