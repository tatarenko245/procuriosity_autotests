class MessageLibrary:
    @staticmethod
    def ei_message_model():
        message = {
            "X-OPERATION-ID": str,
            "X-RESPONSE-ID": str,
            "initiator": str,
            "data": {
                "ocid": str,
                "url": str,
                "operationDate": str,
                "outcomes": {
                    "ei": list
                }
            }
        }
        return message

    @staticmethod
    def ei_message_model_outcomes_ei_object():
        outcomes_ei = {
            "id": str,
            "X-TOKEN": str
        }
        return outcomes_ei