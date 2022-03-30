class ReleaseLibrary:
    @staticmethod
    def invitation_object():
        invitation = {
            "id": None,
            "date": None,
            "status": None,
            "tenderers": [],
            "relatedQualification": None
        }
        return invitation

    @staticmethod
    def invitation_tenderers_object():
        tenderer = {
            "id": None,
            "name": None
        }
        return tenderer

    @staticmethod
    def award_object():
        award = {
            "id": None,
            "date": None,
            "title": None,
            "description": None,
            "status": None,
            "statusDetails": None,
            "relatedLots": []
        }
        return award
