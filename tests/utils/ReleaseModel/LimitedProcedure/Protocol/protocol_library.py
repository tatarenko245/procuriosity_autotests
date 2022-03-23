class ReleaseLibrary:
    @staticmethod
    def np_release_contracts_object():
        contracts = {
                "id": str,
                "date": str,
                "awardId": str,
                "relatedLots": list,
                "status": str,
                "statusDetails": str
            }
        return contracts
