import random

from tests.utils.data_of_enum import cpv_goods_low_level_03, cpv_goods_low_level_1, cpv_goods_low_level_2, \
    cpv_goods_low_level_3, cpv_goods_low_level_44, cpv_goods_low_level_48, cpv_works_low_level_45, \
    cpv_services_low_level_5, cpv_services_low_level_6, cpv_services_low_level_7, cpv_services_low_level_8, \
    cpv_services_low_level_92, cpv_services_low_level_98, documentType
from tests.utils.date_class import Date
from tests.utils.functions import set_permanent_id, generate_items_array, generate_lots_array
from tests.utils.iStorage import Document


class CnOnPnPreparePayload:
    def __init__(self, host_for_services):
        document_one = Document(host_for_services=host_for_services, file_name="API.pdf")
        self.document_one_was_uploaded = document_one.uploading_document()

        self.contact_period = Date().contact_period()
        self.duration_period = Date().duration_period()

    def create_cnonpn_obligatory_data_model(self, actual_ei_release, pn_payload):
        try:
            item_classification_id = None
            tender_classification_id = \
                actual_ei_release['releases'][0]['tender']['classification']['id']

            if tender_classification_id[0:3] == "031":
                item_classification_id = random.choice(cpv_goods_low_level_03)
            elif tender_classification_id[0:3] == "146":
                item_classification_id = random.choice(cpv_goods_low_level_1)
            elif tender_classification_id[0:3] == "221":
                item_classification_id = random.choice(cpv_goods_low_level_2)
            elif tender_classification_id[0:3] == "301":
                item_classification_id = random.choice(cpv_goods_low_level_3)
            elif tender_classification_id[0:3] == "444":
                item_classification_id = random.choice(cpv_goods_low_level_44)
            elif tender_classification_id[0:3] == "482":
                item_classification_id = random.choice(cpv_goods_low_level_48)
            elif tender_classification_id[0:3] == "451":
                item_classification_id = random.choice(cpv_works_low_level_45)
            elif tender_classification_id[0:3] == "515":
                item_classification_id = random.choice(cpv_services_low_level_5)
            elif tender_classification_id[0:3] == "637":
                item_classification_id = random.choice(cpv_services_low_level_6)
            elif tender_classification_id[0:3] == "713":
                item_classification_id = random.choice(cpv_services_low_level_7)
            elif tender_classification_id[0:3] == "851":
                item_classification_id = random.choice(cpv_services_low_level_8)
            elif tender_classification_id[0:3] == "923":
                item_classification_id = random.choice(cpv_services_low_level_92)
            elif tender_classification_id[0:3] == "983":
                item_classification_id = random.choice(cpv_services_low_level_98)
        except KeyError:
            raise KeyError("Check tender_classification_id")

        payload = {
            "tender": {
                "lots": [{
                    "id": "0",
                    "title": "create cnonpn: tender.lots.title",
                    "description": "create cnonpn: tender.lots.description",
                    "value": {
                        "amount": pn_payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount'],
                        "currency": pn_payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
                    },
                    "contractPeriod": {
                        "startDate": self.contact_period[0],
                        "endDate": self.contact_period[1]
                    },
                    "placeOfPerformance": {
                        "address": {
                            "streetAddress": "create cnonpn: tender.lots.placeOfPerformance.address.streetAddress",
                            "addressDetails": {
                                "country": {
                                    "id": "MD"
                                },
                                "region": {
                                    "id": "1700000"
                                },
                                "locality": {
                                    "scheme": "CUATM",
                                    "id": "1701000",
                                    "description": "create cnonpn: tender.lots.placeOfPerformance.address."
                                                   "addressDetails.locality.description"
                                }
                            }
                        }
                    }
                }],
                "items": [{
                    "id": "0",
                    "classification": {
                        "id": item_classification_id,
                        "scheme": "CPV",
                        "description": "create cnonpn: tender.items.classification.description"
                    },
                    "quantity": 60.0,
                    "unit": {
                        "id": "20",
                        "name": "create cnonpn: tender.items.unit.name"
                    },
                    "description": "create CNonPN: tender.items.description",
                    "relatedLot": "0"
                }],
                "documents": [{
                    "documentType": f"{random.choice(documentType)}",
                    "id": self.document_one_was_uploaded[0]["data"]["id"],
                    "title": "create cnonpn: tender.documents.title",
                    "description": "create cnonpn: tender.documents.description",
                    "relatedLots": ["0"]
                }],
                "awardCriteria": "priceOnly"
            }
        }
        return payload

    def update_cnonpn_obligatory_data_model(self, actual_ei_release, pre_qualification_period_end,
                                            actual_tp_release, need_to_set_permanent_id_for_lots_array=False,
                                            quantity_of_items_object=1, quantity_of_lots_object=1,
                                            need_to_set_permanent_id_for_documents_array=False,
                                            need_to_set_permanent_id_for_items_array=False):

        try:
            item_classification_id = None
            tender_classification_id = actual_ei_release['releases'][0]['tender']['classification']['id']

            if tender_classification_id[0:3] == "031":
                item_classification_id = random.choice(cpv_goods_low_level_03)
            elif tender_classification_id[0:3] == "146":
                item_classification_id = random.choice(cpv_goods_low_level_1)
            elif tender_classification_id[0:3] == "221":
                item_classification_id = random.choice(cpv_goods_low_level_2)
            elif tender_classification_id[0:3] == "301":
                item_classification_id = random.choice(cpv_goods_low_level_3)
            elif tender_classification_id[0:3] == "444":
                item_classification_id = random.choice(cpv_goods_low_level_44)
            elif tender_classification_id[0:3] == "482":
                item_classification_id = random.choice(cpv_goods_low_level_48)
            elif tender_classification_id[0:3] == "451":
                item_classification_id = random.choice(cpv_works_low_level_45)
            elif tender_classification_id[0:3] == "515":
                item_classification_id = random.choice(cpv_services_low_level_5)
            elif tender_classification_id[0:3] == "637":
                item_classification_id = random.choice(cpv_services_low_level_6)
            elif tender_classification_id[0:3] == "713":
                item_classification_id = random.choice(cpv_services_low_level_7)
            elif tender_classification_id[0:3] == "851":
                item_classification_id = random.choice(cpv_services_low_level_8)
            elif tender_classification_id[0:3] == "923":
                item_classification_id = random.choice(cpv_services_low_level_92)
            elif tender_classification_id[0:3] == "983":
                item_classification_id = random.choice(cpv_services_low_level_98)
        except KeyError:
            raise KeyError("Check tender_classification_id")

        payload = {
            "tender": {
                "title": "update cnonpn: tender.title",
                "description": "update cnonpn: tender.desciption",
                "lots": [{
                    "id": "update cnonpn: tender.lots.id",
                    "title": "update cnonpn: tender.lots.title",
                    "description": "update cnonpn: tender.lots.description",
                    "value": {
                        "amount": actual_tp_release['releases'][0]['tender']['lots'][0]['value']['amount'] - 100,
                        "currency": actual_tp_release['releases'][0]['tender']['lots'][0]['value']['currency']
                    },
                    "contractPeriod": {
                        "startDate": self.contact_period[0],
                        "endDate": self.contact_period[1]
                    },
                    "placeOfPerformance": {
                        "address": {
                            "streetAddress": "update cnonpn: tender.lots.placeOfPerformance.address.streetAddress",
                            "addressDetails": {
                                "country": {
                                    "id": "MD"
                                },
                                "region": {
                                    "id": "3400000"
                                },
                                "locality": {
                                    "scheme": "other",
                                    "id": "3401000",
                                    "description": "update cnonpn: tender.lots.placeOfPerformance.address."
                                                   "addressDetails.locality.description"
                                }
                            }
                        }
                    }
                }],
                "items": [{
                    "id": "0",
                    "classification": {
                        "id": item_classification_id,
                        "scheme": "CPV",
                        "description": "update cnonpn: tender.items.classification.description"
                    },
                    "quantity": 80.0,
                    "unit": {
                        "id": "10",
                        "name": "update cnonpn: tender.items.unit.name"
                    },
                    "description": "update CNonPN: tender.items.description",
                    "relatedLot": "0"
                }],
                "documents": [{
                    "documentType": f"{random.choice(documentType)}",
                    "id": self.document_one_was_uploaded[0]["data"]["id"],
                    "title": "update cnonpn: tender.documents.title",
                    "description": "update cnonpn: tender.documents.description",
                    "relatedLots": ["0"]
                }]
            }
        }

        payload['tender']['lots'] = generate_lots_array(
            quantity_of_object=quantity_of_lots_object,
            lot_object=payload['tender']['lots'][0])

        try:
            """
            Set permanent id for lots array.
            """
            if need_to_set_permanent_id_for_lots_array is True:
                payload['tender']['lots'] = set_permanent_id(
                    release_array=actual_tp_release['releases'][0]['tender']['lots'],
                    payload_array=payload['tender']['lots'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for lots array. Key 'lots' was not found.")

        payload['tender']['items'] = generate_items_array(
            quantity_of_object=quantity_of_items_object,
            item_object=payload['tender']['items'][0],
            tender_classification_id=tender_classification_id,
            lots_array=payload['tender']['lots'])

        try:
            """
            Set permanent id for items array.
            """
            if need_to_set_permanent_id_for_items_array is True:
                payload['tender']['items'] = set_permanent_id(
                    release_array=actual_tp_release['releases'][0]['tender']['items'],
                    payload_array=payload['tender']['items'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'items' was not found.")

        try:
            """
            Set permanent id for documents array.
            """
            if need_to_set_permanent_id_for_documents_array is True:
                payload['tender']['documents'] = set_permanent_id(
                    release_array=actual_tp_release['releases'][0]['tender']['documents'],
                    payload_array=payload['tender']['documents'])
            else:
                pass
        except KeyError:
            raise KeyError("Could not to set permanent id for items array. Key 'documents' was not found.")

        payload['tender']['documents'][0]['relatedLots'] = [payload['tender']['lots'][0]['id']]

        return payload
