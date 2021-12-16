class PayloadLibrary:
    @staticmethod
    def award_object():
        award = {
            "statusDetails": None,
            "description": None,
            "documents": []
        }
        return award

    @staticmethod
    def award_document_object():
        document = {
            "id": None,
            "documentType": None,
            "title": None,
            "description": None,
            "relatedLots": []
        }
        return document
