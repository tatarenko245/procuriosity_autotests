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