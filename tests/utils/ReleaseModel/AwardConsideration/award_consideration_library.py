class ReleaseLibrary:
    @staticmethod
    def iterable_item_added_document_object(n):
        document_object = {
            f"root['releases'][0]['bids']['details'][0]['documents'][{n}]": {
                "id": None,
                "documentType": None,
                "title": None,
                "description": None,
                "url": None,
                "datePublished": None,
                "relatedLots": []
            }
        }
        return document_object
