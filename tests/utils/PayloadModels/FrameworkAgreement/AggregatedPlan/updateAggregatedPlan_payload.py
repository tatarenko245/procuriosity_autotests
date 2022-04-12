import copy
import random

from tests.utils.data_of_enum import locality_scheme_tuple, documentType_tuple, unit_id_tuple, cpvs_tuple, \
    region_id_tuple
from tests.utils.date_class import Date
from tests.utils.functions_collection.functions import generate_items_array, generate_lots_array, \
    get_locality_id_according_with_region_id
from tests.utils.iStorage import Document


class UpdateAggregatedPlan:
    def __init__(self, host_to_service, currency, createAp_payload,  tenderClassificationId,
                 maxDurationOfFA):

        __pn_period = Date().planningNotice_period()
        __contractPeriod = Date().contactPeriod(maxDurationOfFA)

        __document_one = Document(host=host_to_service, file_name="API.pdf")
        self.__document_one_was_uploaded = __document_one.uploading_document()
        self.__host = host_to_service
        self.__currency = currency
        self.__createAp_payload = createAp_payload
        self.__tenderClassificationId = tenderClassificationId

        self.__payload = {
            "tender": {
                "title": "update ap: tender.title",
                "description": "update ap: tender.description",
                "procurementMethodRationale": "create ap: tender.procurementMethodRationale",
                "tenderPeriod": {
                    "startDate": __pn_period
                },
                "lots": [
                    {
                        "id": "0",
                        "internalId": "update ap: tender.lots[0].internalId",
                        "title": "update ap: tender.lots[0].title",
                        "description": "create ap: tender.lots[0].description",
                        "placeOfPerformance": {
                            "address": {
                                "streetAddress": "update ap: tender.lots[0].deliveryAddress.streetAddress",
                                "postalCode": "update ap: tender.lots[0].deliveryAddress.postalCode",
                                "addressDetails": {
                                    "country": {
                                        "id": "MD"
                                    },
                                    "region": {
                                        "id": "3400000"
                                    },
                                    "locality": {
                                        "id": "3401000",
                                        "description":
                                            "update ap: tender.lots[0].deliveryAddress.addressDetails.locality.uri",
                                        "scheme": f"{random.choice(locality_scheme_tuple)}",
                                        "uri": "update ap: tender.lots[0].deliveryAddress.addressDetails.locality.uri"
                                    }
                                }
                            },
                            "description": "update ap: tender.lots[0].placeOfPerformance.description"
                        }
                    }
                ],
                "items": [
                    {
                        "id": "0",
                        "internalId": "update ap: tender.items[0].internalId",
                        "description": "update ap: tender.items[0].description",
                        "classification": {
                            "id": self.__tenderClassificationId
                        },
                        "additionalClassifications": [
                            {
                                "id": "AA12-4"
                            }
                        ],
                        "deliveryAddress": {
                            "streetAddress": "update ap: tender.items[0].deliveryAddress.streetAddress",
                            "postalCode": "update ap: tender.items[0].deliveryAddress.postalCode",
                            "addressDetails": {
                                "country": {
                                    "id": "MD"
                                },
                                "region": {
                                    "id": "3400000"
                                },
                                "locality": {
                                    "id": "3401000",
                                    "description":
                                        "update ap: tender.items[0].deliveryAddress.addressDetails.locality.uri",
                                    "scheme": f"{random.choice(locality_scheme_tuple)}",
                                    "uri": "update ap: tender.items[0].deliveryAddress.addressDetails.locality.uri"
                                }
                            }
                        },
                        "quantity": "10",
                        "unit": {
                            "id": "10"
                        },
                        "relatedLot": "0"
                    }
                ],
                "documents": [
                    {
                        "documentType": f"{random.choice(documentType_tuple)}",
                        "id": self.__createAp_payload['tender']['documents'][0]['id'],
                        "title": "update ap: tender.documents[0].title",
                        "description": "update ap: tender.documents[0].description",
                        "relatedLots": ["0"]
                    }],
                "value": {
                    "currency": self.__currency
                }

            }
        }

    def build_updateAggregatedPlan_payload(self):
        return self.__payload

    def delete_optional_fields(
            self, *args, lot_position=0, item_position=0, additionalClassification_position=0, document_position=0):
        for a in args:
            if a == "tender.procurementMethodRationale":
                del self.__payload['tender']['procurementMethodRationale']

            elif a == "tender.lots.internalId":
                del self.__payload['tender']['lots'][lot_position]['internalId']
            elif a == "tender.lots.placeOfPerformance":
                del self.__payload['tender']['lots'][lot_position]['placeOfPerformance']
            elif a == "tender.lots.placeOfPerformance.address.streetAddress":
                del self.__payload['tender']['lots'][lot_position]['placeOfPerformance']['address']['streetAddress']
            elif a == "tender.lots.placeOfPerformance.address.postalCode":
                del self.__payload['tender']['lots'][lot_position]['placeOfPerformance']['address']['postalCode']
            elif a == "tender.lots.placeOfPerformance.address.addressDetails.locality":
                del self.__payload['tender']['lots'][lot_position]['placeOfPerformance']['address'][
                    'addressDetails']['locality']

            elif a == "tender.items.internalId":
                del self.__payload['tender']['items'][item_position]['internalId']
            elif a == "tender.items.additionalClassifications":
                del self.__payload['tender']['items'][item_position]['additionalClassifications']
            elif a == f"tender.items.additionalClassifications[{additionalClassification_position}]":

                del self.__payload['tender']['items'][item_position][
                    'additionalClassifications'][additionalClassification_position]

            elif a == "tender.items.deliveryAddress":
                del self.__payload['tender']['items'][item_position]['deliveryAddress']
            elif a == "tender.items.deliveryAddress.streetAddress":
                del self.__payload['tender']['items'][item_position]['deliveryAddress']['streetAddress']
            elif a == "tender.items.deliveryAddress.postalCode":
                del self.__payload['tender']['items'][item_position]['deliveryAddress']['postalCode']
            elif a == "tender.items.deliveryAddress.addressDetails.locality":
                del self.__payload['tender']['items'][item_position]['deliveryAddress']['addressDetails']['locality']

            elif a == "tender.documents":
                del self.__payload['tender']['documents']
            elif a == "tender.documents.description":
                del self.__payload['tender']['documents'][document_position]['description']
            elif a == "tender.documents.relatedLots":
                del self.__payload['tender']['documents'][document_position]['relatedLots']

            elif a == "tender.value":
                del self.__payload['tender']['value']
            else:
                raise KeyError(f"Impossible to delete attribute by path {a}.")

    def customize_tender_items(self, lot_id_list, quantity_of_items, quantity_of_items_additionalClassifications):
        """
        The max quantity of items must be 5, because it depends on cpvs_tuple from data_of_enum.
        The quantity of lot_id_list must be equal the quantity_of_items.
        """
        new_items_array = generate_items_array(
            quantity_of_object=quantity_of_items,
            item_object=copy.deepcopy(self.__payload['tender']['items'][0]),
            tender_classification_id=self.__tenderClassificationId
        )

        for q_0 in range(quantity_of_items):

            new_items_array[q_0]['internalId'] = f"update ap: tender.items{q_0}.internalId"
            new_items_array[q_0]['description'] = f"update ap: tender.items{q_0}.description"
            new_items_array[q_0]['unit']['id'] = f"{random.choice(unit_id_tuple)}"

            list_of_additionalClassification_id = list()
            for q_1 in range(quantity_of_items_additionalClassifications):
                new_items_array[q_0]['additionalClassifications'].append(
                    copy.deepcopy(self.__payload['tender']['items'][0]['additionalClassifications'][0]))

                while len(list_of_additionalClassification_id) < quantity_of_items_additionalClassifications:
                    additionalClassification_id = f"{random.choice(cpvs_tuple)}"
                    if additionalClassification_id not in list_of_additionalClassification_id:
                        list_of_additionalClassification_id.append(additionalClassification_id)

            for q_1 in range(quantity_of_items_additionalClassifications):

                new_items_array[q_0]['additionalClassifications'][q_1]['id'] = \
                    list_of_additionalClassification_id[q_1]

            new_items_array[q_0]['relatedLot'] = lot_id_list[q_0]

        self.__payload['tender']['items'] = new_items_array

    def customize_tender_lots(self, quantity_of_lots):
        new_lots_array = generate_lots_array(
            quantity_of_object=quantity_of_lots,
            lot_object=copy.deepcopy(self.__payload['tender']['lots'][0])
        )
        for q_0 in range(quantity_of_lots):

            new_lots_array[q_0]['internalId'] = f"update ap: tender.lots{q_0}.internalId"
            new_lots_array[q_0]['title'] = f"update ap: tender.lotss{q_0}.title"
            new_lots_array[q_0]['description'] = f"update ap: tender.lots{q_0}.description"

            new_lots_array[q_0]['placeOfPerformance']['streetAddress'] = \
                f"update ap: tender.lots{q_0}.placeOfPerformance.streetAddress"

            new_lots_array[q_0]['placeOfPerformance']['postalCode'] = \
                f"update ap: tender.lots{q_0}.placeOfPerformance.postalCode"

            new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['region']['id'] = \
                f"{random.choice(region_id_tuple)}"

            new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['locality']['id'] = \
                get_locality_id_according_with_region_id(
                    new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['region']['id'])

            new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['locality']['scheme'] = \
                f"{random.choice(locality_scheme_tuple)}"

            new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['locality']['description'] = \
                f"update ap: tender.lots{q_0}.placeOfPerformance.address.addressDetails.locality.description"

            new_lots_array[q_0]['placeOfPerformance']['address']['addressDetails']['locality']['uri'] = \
                f"update ap: tender.lots{q_0}.placeOfPerformance.address.addressDetails.locality.uri"

            new_lots_array[q_0]['placeOfPerformance']['description'] = \
                f"update ap: tender.lots{q_0}.placeOfPerformance.description"

        self.__payload['tender']['lots'] = new_lots_array

    def customize_tender_documents(self, lot_id_list, quantity_of_documents):
        """
        The quantity of lot_id_list must be equal the quantity_of_documents.
        """
        new_documents_array = list()
        for q_0 in range(quantity_of_documents):
            new_documents_array.append(copy.deepcopy(self.__payload['tender']['documents'][0]))

            document_two = Document(host=self.__host, file_name="API.pdf")
            document_two_was_uploaded = document_two.uploading_document()

            new_documents_array[q_0]['id'] = document_two_was_uploaded[0]["data"]["id"]
            new_documents_array[q_0]['documentType'] = f"{random.choice(documentType_tuple)}"
            new_documents_array[q_0]['title'] = f"update ap: tender.documents{q_0}.title"
            new_documents_array[q_0]['description'] = f"update ap: tender.documents{q_0}.description"

            new_documents_array[q_0]['relatedLots'] = [lot_id_list[q_0]]

        for q_1 in range(len(self.__createAp_payload['tender']['documents'])):
            new_documents_array.append(copy.deepcopy(self.__payload['tender']['documents'][0]))

            new_documents_array[q_1]['id'] = self.__createAp_payload['tender']['documents'][q_1]['id']
            new_documents_array[q_1]['documentType'] = f"{random.choice(documentType_tuple)}"
            new_documents_array[q_1]['title'] = f"update ap: tender.documents{q_1}.title"
            new_documents_array[q_1]['description'] = f"update up: tender.documents{q_1}.description"

            if "relatedLots" in self.__createAp_payload['tender']['documents'][q_1]:

                new_documents_array[q_1]['relatedLots'] = \
                    self.__createAp_payload['tender']['documents'][q_1]['relatedLots']
            else:
                del self.__createAp_payload['tender']['documents'][q_1]['relatedLots']

        self.__payload['tender']['documents'] = new_documents_array

    def __del__(self):
        print(f"The instance of UpdateAggregatedPlan class: {__name__} was deleted.")
