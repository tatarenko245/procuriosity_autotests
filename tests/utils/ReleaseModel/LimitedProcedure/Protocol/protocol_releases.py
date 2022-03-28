import copy

from tests.utils.ReleaseModel.LimitedProcedure.Protocol.protocol_library import ReleaseLibrary
from tests.utils.functions_collection import is_it_uuid


class ProtocolReleases:
    def __init__(self, language, protocol_feedPointMessage):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.protocol_feedPointMessage = protocol_feedPointMessage

    def create_contracts_array(self, lot_id, award_id, actual_contacts_array):
        expected_array_of_contracts_mapper = list()

        for actual_contract in range(len(actual_contacts_array)):
            try:
                """
                Prepare contracts object framework.
                """
                contract_object = dict()
                contract_object.update(self.constructor.np_release_contracts_object())
            except Exception:
                raise Exception("Impossible to build expected contacts object framework.")

            try:
                """
                Enrich contracts object framework by required value.
                """
                check_contracts_id = is_it_uuid(actual_contacts_array[actual_contract]['id'])

                if check_contracts_id is False:
                    raise Exception("Error: releases.contracts.id must be uuid")

                contract_object['id'] = actual_contacts_array[actual_contract]['id']
                contract_object['date'] = self.protocol_feedPointMessage['data']['operationDate']
                contract_object['awardId'] = award_id
                contract_object['relatedLots'] = [lot_id]
                contract_object['status'] = "pending"
                contract_object['statusDetails'] = "contractProject"
            except Exception:
                raise Exception("Impossible to enrich contracts object framework by required value.")

            mapper = {
                "id": contract_object['id'],
                "value": contract_object
            }
            expected_array_of_contracts_mapper.append(mapper)

        final_expected_contracts_array = list()
        for actual in range(len(actual_contacts_array)):
            for expected in range(len(expected_array_of_contracts_mapper)):
                if expected_array_of_contracts_mapper[expected]['id'] == actual_contacts_array[actual]['id']:
                    final_expected_contracts_array.append(expected_array_of_contracts_mapper[expected]['value'])
        return final_expected_contracts_array
