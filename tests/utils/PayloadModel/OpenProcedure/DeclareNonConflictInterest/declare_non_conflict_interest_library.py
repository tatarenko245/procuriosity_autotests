class PayloadLibrary:
    @staticmethod
    def requirement_response_object():
        requirement_response_object = {
            "id": None,
            "value": None,
            "relatedTenderer": {
                "id": None
            },
            "responder": {
                "title": None,
                "name": None,
                "identifier": {
                    "scheme": None,
                    "id": None,
                    "uri": None
                },
                "businessFunctions": []
            },
            "requirement": {
                "id": None
            }
        }
        return requirement_response_object

    @staticmethod
    def requirement_response_business_functions_object():
        business_functions_object = {
            "id": None,
            "type": None,
            "jobTitle": None,
            "period": {
                "startDate": None
            },
            "documents": []
        }
        return business_functions_object

    @staticmethod
    def business_functions_documents_object():
        documents = {
                    "id": "9004ab09-ca9b-4cb7-95f4-525a3bf64734-1574862409148",
                    "documentType": "regulatoryDocument",
                    "title": "string",
                    "description": "string"
                }
        return documents
