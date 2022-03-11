class ReleaseLibrary:
    @staticmethod
    def tp_release_bid_object():
        bid_object = {
            "details": []
        }
        return bid_object

    @staticmethod
    def tp_release_bid_details_object():
        details_object = {
            "id": None,
            "date": None,
            "status": None,
            "tenderers": [],
            "value": {
                "amount": None,
                "currency": None
            },
            "documents": [],
            "relatedLots": [],
            "requirementResponses": []
        }
        return details_object

    @staticmethod
    def tp_release_bid_details_tenderer_object():
        tenderer_object = {
            "id": None,
            "name": None
        }
        return tenderer_object

    @staticmethod
    def tp_release_bid_details_document_object():
        document_object = {
            "id": None,
            "documentType": None,
            "title": None,
            "description": None,
            "url": None,
            "datePublished": None,
            "relatedLots": []
        }
        return document_object

    @staticmethod
    def tp_release_bid_details_requirement_response_object():
        requirement_response_object = {
            "id": None,
            "value": None,
            "period": {
                "startDate": None,
                "endDate": None
            },
            "requirement": {
                "id": None
            },
            "relatedTenderer": {
                "id": None,
                "name": None
            },
            "evidences": []
        }
        return requirement_response_object

    @staticmethod
    def tp_release_bid_details_requirement_response_evidences_object():
        evidences_object = {
            "id": None,
            "title": None,
            "description": None,
            "relatedDocument": {
                "id": None
            }
        }
        return evidences_object

    @staticmethod
    def tp_release_unsuccessful_award_object():
        award_object = {
            "id": None,
            "title": None,
            "description": None,
            "status": None,
            "statusDetails": None,
            "date": None,
            "relatedLots": []
        }
        return award_object

    @staticmethod
    def tp_release_successful_award_object():
        award_object = {
            "id": None,
            "status": None,
            "statusDetails": None,
            "date": None,
            "value": {
                "amount": None,
                "currency": None
            },
            "suppliers": [],
            "relatedLots": [],
            "relatedBid": None,
            "weightedValue": {
                "amount": None,
                "currency": None
            }
        }
        return award_object

    @staticmethod
    def tp_release_successful_award_supplier_object():
        supplier_object = {
            "id": None,
            "name": None
        }
        return supplier_object
