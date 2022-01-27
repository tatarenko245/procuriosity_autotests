class QualificationPreparePayload:
    @staticmethod
    def create_qualification_obligatory_data_model(status_details):
        payload = {
            "qualification": {
                "statusDetails": status_details
            }
        }
        return payload
