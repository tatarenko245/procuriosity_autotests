class PayloadLibrary:
    @staticmethod
    def qualification_object():
        qualification = {
            "statusDetails": None,
            "internalId": None,
            "description": None,
            "documents": []
        }

        return qualification

    @staticmethod
    def qualification_documents_object():
        documents = {
                    "id": "9004ab09-ca9b-4cb7-95f4-525a3bf64734-1574862409148",
                    "documentType": "regulatoryDocument",
                    "title": "string",
                    "description": "string"
                }
        return documents
