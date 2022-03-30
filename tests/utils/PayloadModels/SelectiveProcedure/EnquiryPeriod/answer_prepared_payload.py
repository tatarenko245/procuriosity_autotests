

class AnswerPreparePayload:
    @staticmethod
    def create_answer_obligatory_data_model():
        payload = {
            "enquiry": {
                "answer": "create answer: answer"
            }
        }
        return payload
