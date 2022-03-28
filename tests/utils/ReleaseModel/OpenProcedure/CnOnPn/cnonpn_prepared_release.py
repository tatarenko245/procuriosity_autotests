import copy
import fnmatch

from tests.conftest import GlobalClassMetadata, GlobalClassCreatePn, GlobalClassCreateCnOnPn
from tests.utils.ReleaseModel.OpenProcedure.CnOnPn.cnonpn_release_library import ReleaseLibrary
from tests.utils.functions_collection import check_uuid_version, get_value_from_country_csv, get_value_from_region_csv, \
    get_value_from_locality_csv, get_value_from_classification_cpv_dictionary_xls, get_value_from_cpvs_dictionary_csv, \
    get_value_from_classification_unit_dictionary_csv, get_temporary_requirements_id_and_permanent_requirements_id, \
    get_temporary_lots_id_and_permanent_lots_id


class CnOnPnExpectedRelease:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.metadata_tender_url = None
        self.metadata_document_url = None
        self.metadata_auction_url = None

        try:
            if environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
                self.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
                self.metadata_auction_url = "http://auction.eprocurement.systems/auctions/"
                self.publisher_name = "M-Tender"
                self.publisher_uri = "https://www.mtender.gov.md"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"]

            elif environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
                self.metadata_document_url = "http://storage.eprocurement.systems/get"
                self.metadata_auction_url = "https://eauction.eprocurement.systems/auctions/"
                self.publisher_name = "Viešųjų pirkimų tarnyba"
                self.publisher_uri = "https://vpt.lrv.lt"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.json"]
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")
        GlobalClassMetadata.metadata_budget_url = self.metadata_budget_url
        GlobalClassMetadata.metadata_tender_url = self.metadata_tender_url

    def prepare_expected_lots_array(self, payload_lots_array, release_lots_array):
        expected_lots_array = []
        try:
            """
            Check how many quantity of object into payload_lots_array.
            """
            list_of_payload_lot_id = list()
            for lot_object in payload_lots_array:
                for i in lot_object:
                    if i == "id":
                        list_of_payload_lot_id.append(i)
            quantity_of_lot_object_into_payload = len(list_of_payload_lot_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['lots'][*]['id']")

        try:
            """
            Check how many quantity of object into release_lots_array.
            Check release_lots_array[*]['id'] -> is it uuid.
            """
            list_of_release_lot_id = list()
            for lot_object in release_lots_array:
                for i in lot_object:
                    if i == "id":
                        list_of_release_lot_id.append(i)
                        try:
                            check_uuid_version(
                                uuid_to_test=lot_object['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your lots array in release: "
                                             "release_lots_array.id in release must be uuid version 4")
            quantity_of_lot_object_into_release = len(list_of_release_lot_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['lots'][*]['id']")

        try:
            """
            Compare quantity of lot objects into payload_lots_array and release_lots_array.
            """
            if quantity_of_lot_object_into_payload == quantity_of_lot_object_into_release:
                pass
        except KeyError:
            raise KeyError("Quantity of lot objects into payload_lots_array != "
                           "quantity of lot objects into and release_lots_array")

        try:
            """
            Prepare lots array framework.
            """
            quantity_one = quantity_of_lot_object_into_release
            while quantity_one > 0:
                lot_object = {}
                lot_object.update(self.constructor.release_tender_lot_object())
                expected_lots_array.append(lot_object)
                quantity_one -= 1
        except ValueError:
            raise ValueError("Impossible to build expected lots array framework.")

        try:
            """
            Enrich lots array by value.
            """
            quantity_two = quantity_of_lot_object_into_release - 1
            while quantity_two >= 0:
                expected_lots_array[quantity_two]['id'] = release_lots_array[quantity_two]['id']
                """
                Enrich or delete optional fields: 
                - "internalId";
                - "postalCode;
                - "description";
                """
                if "internalId" in payload_lots_array[quantity_two]:
                    expected_lots_array[quantity_two]['internalId'] = payload_lots_array[quantity_two]['internalId']
                else:
                    del expected_lots_array[quantity_two]['internalId']

                if "postalCode" in payload_lots_array[quantity_two]['placeOfPerformance']['address']:
                    expected_lots_array[quantity_two]['placeOfPerformance']['address']['postalCode'] = \
                        payload_lots_array[quantity_two]['placeOfPerformance']['address']['postalCode']
                else:
                    del expected_lots_array[quantity_two]['placeOfPerformance']['address']['postalCode']

                if "description" in payload_lots_array[quantity_two]['placeOfPerformance']:
                    expected_lots_array[quantity_two]['placeOfPerformance']['description'] = \
                        payload_lots_array[quantity_two]['placeOfPerformance']['description']
                else:
                    del expected_lots_array[quantity_two]['placeOfPerformance']['description']

                """
                Enrich obligatory fields:
                - "title";
                - "description";
                - value";
                - "contactPeriod";
                - "placeOfPerformance";
                - "status";
                - "statusDetails";
                - "hasOptions";
                - "hasRecurrence";
                - "hasRenewal";
                
                """
                expected_lots_array[quantity_two]['title'] = payload_lots_array[quantity_two]['title']
                expected_lots_array[quantity_two]['description'] = payload_lots_array[quantity_two]['description']
                expected_lots_array[quantity_two]['value'] = payload_lots_array[quantity_two]['value']
                expected_lots_array[quantity_two]['contractPeriod'] = payload_lots_array[quantity_two]['contractPeriod']
                expected_lots_array[quantity_two]['placeOfPerformance']['address'] = \
                    payload_lots_array[quantity_two]['placeOfPerformance']['address']

                lot_country_data = get_value_from_country_csv(
                    country=payload_lots_array[quantity_two]['placeOfPerformance'][
                        'address']['addressDetails']['country']['id'],
                    language=self.language
                )
                lot_country_object = {
                    "scheme": lot_country_data[2],
                    "id": payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                        'country']['id'],
                    "description": lot_country_data[1],
                    "uri": lot_country_data[3]
                }

                lot_region_data = get_value_from_region_csv(
                    region=payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                        'region']['id'],
                    country=payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                        'country']['id'],
                    language=self.language
                )
                lot_region_object = {
                    "scheme": lot_region_data[2],
                    "id": payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                        'region']['id'],
                    "description": lot_region_data[1],
                    "uri": lot_region_data[3]
                }

                if \
                        payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                            'locality']['scheme'] == "CUATM":
                    lot_locality_data = get_value_from_locality_csv(
                        locality=payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                            'locality']['id'],
                        region=payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                            'region']['id'],
                        country=payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                            'country']['id'],
                        language=self.language
                    )
                    lot_locality_object = {
                        "scheme": lot_locality_data[2],
                        "id": payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                            'locality']['id'],
                        "description": lot_locality_data[1],
                        "uri": lot_locality_data[3]
                    }
                else:
                    lot_locality_object = {
                        "scheme": payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                            'locality']['scheme'],
                        "id": payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
                            'locality']['id'],
                        "description": payload_lots_array[quantity_two]['placeOfPerformance']['address'][
                            'addressDetails']['locality']['description']
                    }

                expected_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails']['country'] = \
                    lot_country_object
                expected_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails']['region'] = \
                    lot_region_object
                expected_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails']['locality'] = \
                    lot_locality_object

                expected_lots_array[quantity_two]['status'] = 'active'
                expected_lots_array[quantity_two]['statusDetails'] = 'empty'
                expected_lots_array[quantity_two]['hasOptions'] = False
                expected_lots_array[quantity_two]['hasRecurrence'] = False
                expected_lots_array[quantity_two]['hasRenewal'] = False

                quantity_two -= 1
        except ValueError:
            raise ValueError("Impossible to enrich expected lots array framework.")
        return expected_lots_array

    def prepare_expected_items_array(self, payload_items_array, release_items_array, release_lots_array=None):
        expected_items_array = []
        try:
            """
            Check how many quantity of object into payload_items_array.
            """
            list_of_payload_item_id = list()
            for item_object in payload_items_array:
                for i in item_object:
                    if i == "id":
                        list_of_payload_item_id.append(i)
            quantity_of_item_object_into_payload = len(list_of_payload_item_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['items'][*]['id']")

        try:
            """
            Check how many quantity of object into release_items_array.
            Check release_items_array[*]['id'] -> is it uuid.
            """
            list_of_release_item_id = list()
            for item_object in release_items_array:
                for i in item_object:
                    if i == "id":
                        list_of_release_item_id.append(i)
                        try:
                            check_uuid_version(
                                uuid_to_test=item_object['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your items array in release: "
                                             "release_items_array.id in release must be uuid version 4")
            quantity_of_item_object_into_release = len(list_of_release_item_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['items'][*]['id']")

        try:
            """
            Compare quantity of item objects into payload_items_array and release_items_array.
            """
            if quantity_of_item_object_into_payload == quantity_of_item_object_into_release:
                pass
        except KeyError:
            raise KeyError("Quantity of item objects into payload_items_array != "
                           "quantity of item objects into and release_items_array")

        try:
            """
            Prepare items array framework.
            """
            quantity_one = quantity_of_item_object_into_release
            while quantity_one > 0:
                item_object = {}
                item_object.update(self.constructor.release_tender_item_object())
                item_object['additionalClassifications'] = [{}]
                item_object['additionalClassifications'][0].update(
                    self.constructor.release_tender_items_additional_classifications())
                expected_items_array.append(item_object)
                quantity_one -= 1
        except ValueError:
            raise ValueError("Impossible to build expected items array framework.")

        try:
            """
            Enrich items array by value.
            """
            quantity_two = quantity_of_item_object_into_release - 1
            while quantity_two >= 0:
                expected_items_array[quantity_two]['id'] = release_items_array[quantity_two]['id']
                """
                Enrich or delete optional fields: 
                - "internalId";
                - "additionalClassifications";
                - "relatedLot";
                """
                if "internalId" in payload_items_array[quantity_two]:
                    expected_items_array[quantity_two]['internalId'] = payload_items_array[quantity_two]['internalId']
                else:
                    del expected_items_array[quantity_two]['internalId']

                if "additionalClassifications" in payload_items_array[quantity_two]:
                    cpvs_data = get_value_from_cpvs_dictionary_csv(
                        cpvs=payload_items_array[quantity_two]['additionalClassifications'][0]['id'],
                        language=self.language
                    )

                    expected_items_array[quantity_two]['additionalClassifications'][0]['id'] = cpvs_data[0]
                    expected_items_array[quantity_two]['additionalClassifications'][0]['scheme'] = "CPVS"
                    expected_items_array[quantity_two]['additionalClassifications'][0]['description'] = cpvs_data[2]
                else:
                    del expected_items_array[quantity_two]['additionalClassifications']

                if "relatedLot" in payload_items_array[quantity_two]:
                    expected_items_array[quantity_two]['relatedLot'] = release_lots_array[quantity_two]['id']
                else:
                    del expected_items_array[quantity_two]['relatedLot']

                """
                Enrich obligatory fields:
                - "description";
                - "classification";
                - "unit";
                - "quantity"
                """
                expected_items_array[quantity_two]['description'] = payload_items_array[quantity_two]['description']
                cpv_data = get_value_from_classification_cpv_dictionary_xls(
                    cpv=payload_items_array[quantity_two]['classification']['id'],
                    language=self.language
                )
                expected_items_array[quantity_two]['classification']['id'] = cpv_data[0]
                expected_items_array[quantity_two]['classification']['scheme'] = "CPV"
                expected_items_array[quantity_two]['classification']['description'] = cpv_data[1]

                unit_data = get_value_from_classification_unit_dictionary_csv(
                    unit_id=payload_items_array[quantity_two]['unit']['id'],
                    language=self.language
                )
                expected_items_array[quantity_two]['unit']['id'] = unit_data[0]
                expected_items_array[quantity_two]['unit']['name'] = unit_data[1]

                expected_items_array[quantity_two]['quantity'] = float(payload_items_array[quantity_two]['quantity'])
                quantity_two -= 1
        except ValueError:
            raise ValueError("Impossible to enrich expected items array framework.")
        return expected_items_array

    def prepare_expected_documents_array(self, payload, release):
        payload_documents_array = payload['tender']['documents']
        release_documents_array = release['releases'][0]['tender']['documents']
        payload_lots_array = payload['tender']['lots']
        release_lots_array = release['releases'][0]['tender']['lots']
        dictionary_of_lots_id = get_temporary_lots_id_and_permanent_lots_id(
            temporary_lots_array=payload_lots_array,
            permanent_lots_array=release_lots_array)

        expected_documents_array = []
        try:
            """
            Check how many quantity of object into payload_documents_array.
            """
            list_of_payload_document_id = list()
            for document_object in payload_documents_array:
                for i in document_object:
                    if i == "id":
                        list_of_payload_document_id.append(i)
            quantity_of_document_object_into_payload = len(list_of_payload_document_id)

        except KeyError:
            raise KeyError("Check ['releases']['tender']['documents'][*]['id']")

        try:
            """
            Check how many quantity of object into release_documents_array.
            Check release_documents_array[*]['id'] -> is it uuid.
            """
            list_of_release_document_id = list()
            for document_object in release_documents_array:
                for i in document_object:
                    if i == "id":
                        list_of_release_document_id.append(i)
                        try:
                            check_uuid_version(
                                uuid_to_test=document_object['id'][0:36],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your documents array in release: "
                                             "release_documents_array.id in release must be uuid version 4")
            quantity_of_document_object_into_release = len(list_of_release_document_id)

        except KeyError:
            raise KeyError("Check ['releases']['tender']['documents'][*]['id']")

        try:
            """
            Compare quantity of document objects into payload_documents_array and release_documents_array.
            """
            if quantity_of_document_object_into_payload == quantity_of_document_object_into_release:
                pass
        except KeyError:
            raise KeyError("Quantity of document objects into payload_documents_array != "
                           "quantity of document objects into and release_documents_array")

        try:
            """
            Prepare lots array framework.
            """
            quantity_one = quantity_of_document_object_into_release
            while quantity_one > 0:
                lot_object = {}
                lot_object.update(self.constructor.release_tender_document_object())
                expected_documents_array.append(lot_object)
                quantity_one -= 1
        except ValueError:
            raise ValueError("Impossible to build expected documents array framework.")

        try:
            """
            Enrich lots array by value.
            """
            quantity_two = quantity_of_document_object_into_release - 1
            while quantity_two >= 0:
                """
                Enrich or delete optional fields: 
                - "title";
                - "description";
                - "relatedLots";
                """

                if "title" in payload_documents_array[quantity_two]:
                    expected_documents_array[quantity_two]['title'] = payload_documents_array[quantity_two]['title']
                else:
                    del expected_documents_array[quantity_two]['title']

                if "description" in payload_documents_array[quantity_two]:
                    expected_documents_array[quantity_two]['description'] = \
                        payload_documents_array[quantity_two]['description']
                else:
                    del expected_documents_array[quantity_two]['description']

                """
                Enrich obligatory fields:
                - "documentType";
                - "id";
                """
                expected_documents_array[quantity_two]['id'] = payload_documents_array[quantity_two]['id']
                expected_documents_array[quantity_two]['documentType'] = \
                    payload_documents_array[quantity_two]['documentType']
                expected_documents_array[quantity_two]['url'] = \
                    f"{self.metadata_document_url}/{payload_documents_array[quantity_two]['id']}"
                expected_documents_array[quantity_two]['relatedLots'] = \
                    [dictionary_of_lots_id[payload['tender']['documents'][quantity_two][
                        'relatedLots'][0]]]
                expected_documents_array[quantity_two]['datePublished'] = \
                    GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']

                for document_object in release_documents_array:
                    for i in document_object:
                        if i == "id":
                            if document_object[i] == payload_documents_array[quantity_two]['id']:
                                expected_documents_array[quantity_two]['id'] = \
                                    document_object['id']
                                expected_documents_array[quantity_two]['documentType'] = \
                                    document_object['documentType']
                                expected_documents_array[quantity_two]['datePublished'] = \
                                    document_object['datePublished']
                quantity_two -= 1
        except ValueError:
            raise ValueError("Impossible to enrich expected lots array framework.")

        return expected_documents_array

    def prepare_expected_criteria_array(self, payload_criteria_array, release_criteria_array):
        payload_criteria_array = copy.deepcopy(payload_criteria_array)
        release_criteria_array = copy.deepcopy(release_criteria_array)
        expected_criteria_array = []
        try:
            """
            Check how many quantity of object into payload_criteria array.
            """
            list_of_payload_criteria_id = list()
            for criteria_object in copy.deepcopy(payload_criteria_array):
                for i in criteria_object:
                    if i == "id":
                        list_of_payload_criteria_id.append(i)
            quantity_of_criteria_object_into_payload = len(list_of_payload_criteria_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['criteria'][*]['id']")

        try:
            """
            Check how many quantity of object into release_criteria_array.
            Check release_criteria_array[*]['id'] -> is it uuid.
            """
            list_of_release_criteria_id = list()
            for criteria_object in release_criteria_array:
                for i in criteria_object:
                    if i == "id":
                        list_of_release_criteria_id.append(i)
                        try:
                            check_uuid_version(
                                uuid_to_test=criteria_object['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your criteria array in release: "
                                             "release_criteria_array.id in release must be uuid version 4")
            quantity_of_criteria_object_into_release = len(list_of_release_criteria_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['criteria'][*]['id']")

        try:
            """
            Compare quantity of criteria objects into payload_criteria_array and release_criteria_array.
            """
            if quantity_of_criteria_object_into_payload == quantity_of_criteria_object_into_release:
                pass
        except KeyError:
            raise KeyError("Quantity of criteria objects into payload_criteria_array != "
                           "quantity of criteria objects into and release_criteria_array")

        try:
            """
            Prepare criteria array framework.
            """
            quantity_one = quantity_of_criteria_object_into_release
            while quantity_one > 0:
                criteria_object = {}
                criteria_object.update(self.constructor.ev_release_tender_criteria_section())
                expected_criteria_array.append(criteria_object)
                quantity_one -= 1
        except ValueError:
            raise ValueError("Impossible to build expected criteria array framework.")

        try:
            """
            Enrich criteria array by value.
            """
            quantity_two = quantity_of_criteria_object_into_release - 1
            while quantity_two >= 0:
                expected_criteria_array[quantity_two]['id'] = release_criteria_array[quantity_two]['id']
                """
                Enrich obligatory fields:
                - "requirementGroups";
                """
                expected_criteria_array[quantity_two]['title'] = \
                    payload_criteria_array[quantity_two]['title']
                expected_criteria_array[quantity_two]['description'] = \
                    payload_criteria_array[quantity_two]['description']
                expected_criteria_array[quantity_two]['relatesTo'] = \
                    payload_criteria_array[quantity_two]['relatesTo']
                expected_criteria_array[quantity_two]['classification'] = \
                    payload_criteria_array[quantity_two]['classification']
                expected_criteria_array[quantity_two]['requirementGroups'] = \
                    payload_criteria_array[quantity_two]['requirementGroups']
                expected_criteria_array[quantity_two]['source'] = "tenderer"
                if "relatedItem" in payload_criteria_array[quantity_two]:
                    expected_criteria_array[quantity_two]['relatedItem'] = \
                        payload_criteria_array[quantity_two]['relatedItem']

                try:
                    """
                    Check how many quantity of object into payload_criteria_requirement_groups array.
                    """
                    list_of_payload_criteria_requirement_groups_id = list()
                    for requirement_group_object in payload_criteria_array[quantity_two]['requirementGroups']:
                        for i in requirement_group_object:
                            if i == "id":
                                list_of_payload_criteria_requirement_groups_id.append(i)
                    quantity_of_criteria_requirement_groups_object_into_payload = \
                        len(list_of_payload_criteria_requirement_groups_id)
                except KeyError:
                    raise KeyError("Check ['releases']['tender']['criteria'][*]['requirementGroups'][*]['id']")

                try:
                    """
                    Check how many quantity of object into release_criteria_requirement_groups array.
                    Check release_criteria_requirement_groups array[*]['id'] -> is it uuid.
                    """
                    list_of_release_criteria_requirement_groups_id = list()
                    for requirement_group_object in release_criteria_array[quantity_two]['requirementGroups']:
                        for i in requirement_group_object:
                            if i == "id":
                                list_of_release_criteria_requirement_groups_id.append(i)
                                try:
                                    check_uuid_version(
                                        uuid_to_test=requirement_group_object['id'],
                                        version=4
                                    )
                                except ValueError:
                                    raise ValueError("Check your criteria.requirementGroups array in release: "
                                                     "release_criteria_requirementGroups_array.id in release "
                                                     "must be uuid version 4")
                    quantity_of_criteria_requirement_groups_object_into_release = \
                        len(list_of_release_criteria_requirement_groups_id)
                except KeyError:
                    raise KeyError("Check ['releases']['tender']['criteria'][*]['requirementGroups'][*]['id']")

                try:
                    """
                    Compare quantity of requirementGroups objects into payload and release.
                    """
                    if quantity_of_criteria_requirement_groups_object_into_payload == \
                            quantity_of_criteria_requirement_groups_object_into_release:
                        pass
                except KeyError:
                    raise KeyError("Quantity of requirementGroups objects into payload_criteria_array != "
                                   "quantity of requirementGroups objects into and release_criteria_array")
                quantity_three = quantity_of_criteria_requirement_groups_object_into_release - 1

                while quantity_three >= 0:
                    expected_criteria_array[quantity_two]['requirementGroups'][quantity_three]['id'] = \
                        release_criteria_array[quantity_two]['requirementGroups'][quantity_three]['id']

                    try:
                        """
                        Check how many quantity of object into payload_criteria_requirement_groups_requirements array.
                        """
                        list_of_payload_criteria_requirement_groups_requirements_id = list()
                        for requirement_object in payload_criteria_array[quantity_two][
                                'requirementGroups'][quantity_three]['requirements']:
                            for i in requirement_object:
                                if i == "id":
                                    list_of_payload_criteria_requirement_groups_requirements_id.append(i)
                        quantity_of_criteria_requirement_groups_requirements_object_into_payload = \
                            len(list_of_payload_criteria_requirement_groups_requirements_id)
                    except KeyError:
                        raise KeyError("Check ['releases']['tender']['criteria'][*]['requirementGroups'][*]"
                                       "['requirements'][*]['id']")

                    try:
                        """
                        Check how many quantity of object into release_criteria_requirement_groups_requirements array.
                        Check release_criteria_requirement_groups_requirements array[*]['id'] -> is it uuid.
                        """
                        list_of_release_criteria_requirement_groups_requirements_id = list()
                        for requirement_object in release_criteria_array[quantity_two][
                                'requirementGroups'][quantity_three]['requirements']:
                            for i in requirement_object:
                                if i == "id":
                                    list_of_release_criteria_requirement_groups_requirements_id.append(i)
                                    try:
                                        check_uuid_version(
                                            uuid_to_test=requirement_object['id'],
                                            version=4
                                        )
                                    except ValueError:
                                        raise ValueError("Check your criteria.requirementGroups array in release: "
                                                         "release_criteria_requirementGroups_requirements_array.id "
                                                         "in release must be uuid version 4")
                        quantity_of_criteria_requirement_groups_requirements_object_into_release = \
                            len(list_of_release_criteria_requirement_groups_requirements_id)
                    except KeyError:
                        raise KeyError("Check ['releases']['tender']['criteria'][*]['requirementGroups'][*]"
                                       "['requirements']['id']")

                    try:
                        """
                        Compare quantity of requirements objects into payload and release.
                        """
                        if quantity_of_criteria_requirement_groups_requirements_object_into_payload == \
                                quantity_of_criteria_requirement_groups_requirements_object_into_release:
                            pass
                    except KeyError:
                        raise KeyError("Quantity of requirements objects into payload_criteria_array != "
                                       "quantity of requirements objects into and release_criteria_array")
                    quantity_four = quantity_of_criteria_requirement_groups_requirements_object_into_release - 1
                    while quantity_four >= 0:
                        expected_criteria_array[quantity_two]['requirementGroups'][quantity_three][
                            'requirements'][quantity_four]['id'] = \
                            release_criteria_array[quantity_two]['requirementGroups'][quantity_three][
                                'requirements'][quantity_four]['id']

                        expected_criteria_array[quantity_two]['requirementGroups'][quantity_three][
                            'requirements'][quantity_four]['status'] = "active"
                        expected_criteria_array[quantity_two]['requirementGroups'][quantity_three][
                            'requirements'][quantity_four]['datePublished'] = \
                            GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
                        quantity_four -= 1
                    quantity_three -= 1
                quantity_two -= 1
        except ValueError:
            raise ValueError("Impossible to enrich expected criteria array framework.")

        return expected_criteria_array

    def prepare_expected_conversions_array(self, payload, actual_release):

        payload_conversions_array = payload['tender']['conversions']
        release_conversions_array = actual_release['releases'][0]['tender']['conversions']

        payload_criteria_array = payload['tender']['criteria']
        release_criteria_array = actual_release['releases'][0]['tender']['criteria']

        dictionary_of_requirement_id = get_temporary_requirements_id_and_permanent_requirements_id(
            temporary_criteria_array=payload_criteria_array,
            permanent_criteria_array=release_criteria_array)

        expected_conversions_array = []
        try:
            """
            Check how many quantity of conversion object into payload_conversions array.
            """
            list_of_payload_conversions_id = list()
            list_of_payload_conversions_coefficients_id = list()
            quantity_of_conversions_coefficients_object_into_payload = 0
            for conversions_object in payload_conversions_array:
                for i in conversions_object:
                    if i == "id":
                        list_of_payload_conversions_id.append(i)
                    try:
                        """
                        Check how many quantity of coefficients object into payload_conversions['coefficients'] array.
                        """
                        if i == "coefficients":
                            for coefficient_object in conversions_object['coefficients']:
                                for o in coefficient_object:
                                    if o == "id":
                                        list_of_payload_conversions_coefficients_id.append(o)

                        quantity_of_conversions_coefficients_object_into_payload = \
                            len(list_of_payload_conversions_coefficients_id)
                    except KeyError:
                        raise KeyError("Check ['releases']['tender']['conversions'][*]['coefficients'][*]['id']")
            quantity_of_conversions_object_into_payload = len(list_of_payload_conversions_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['conversions'][*]['id']")

        try:
            """
            Check how many quantity of object into release_conversions_array.
            Check release_conversions_array[*]['id'] -> is it uuid.
            """
            list_of_release_conversions_id = list()
            list_of_release_conversions_coefficients_id = list()
            quantity_of_conversion_coefficients_object_into_release = None
            for conversion_object in release_conversions_array:
                for i in conversion_object:
                    if i == "id":
                        list_of_release_conversions_id.append(conversion_object['id'])
                        try:
                            check_uuid_version(
                                uuid_to_test=conversion_object['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your criteria array in release: "
                                             "criteria.id in release must be uuid version 4")
                    try:
                        """
                        Check how many quantity of coefficients object into release_conversions['coefficients'] array.
                        """
                        if i == "coefficients":
                            for coefficient_object in conversion_object['coefficients']:
                                for o in coefficient_object:
                                    if o == "id":
                                        list_of_release_conversions_coefficients_id.append(coefficient_object[o])
                                        try:
                                            check_uuid_version(
                                                uuid_to_test=coefficient_object[o],
                                                version=4
                                            )
                                        except ValueError:
                                            raise ValueError("Check your conversions.coefficients array in release: "
                                                             "conversions.coefficients.id in release must be "
                                                             "uuid version 4")
                        quantity_of_conversion_coefficients_object_into_release = \
                            len(list_of_release_conversions_coefficients_id)
                    except KeyError:
                        raise KeyError("Check ['releases']['tender']['conversions'][*]['coefficients'][*]['id']")
            quantity_of_conversion_object_into_release = len(list_of_release_conversions_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['conversions'][*]['id']")

        try:
            """
            Compare quantity of conversions objects into payload_conversions_array and release_conversions_array.
            """
            if quantity_of_conversions_object_into_payload == quantity_of_conversion_object_into_release:
                pass
        except KeyError:
            raise KeyError("Quantity of conversions objects into payload_conversions_array != "
                           "quantity of conversions objects into and release_conversions_array")

        try:
            """
            Compare quantity of conversions.coefficients objects into 
            quantity_of_conversions_coefficients_object_into_payload and 
            quantity_of_conversion_coefficients_object_into_release.
            """
            if quantity_of_conversions_coefficients_object_into_payload == \
                    quantity_of_conversion_coefficients_object_into_release:
                pass
        except KeyError:
            raise KeyError("Quantity of conversions.coefficients objects into "
                           "quantity_of_conversions_coefficients_object_into_payload != "
                           "quantity_of_conversion_coefficients_object_into_release")

        try:
            """
            Prepare conversions array framework.
            """
            quantity_one = quantity_of_conversion_object_into_release
            while quantity_one > 0:
                conversion_object = {}
                conversion_object.update(self.constructor.ev_release_tender_conversions_section())
                expected_conversions_array.append(conversion_object)
                quantity_one -= 1
        except ValueError:
            raise ValueError("Impossible to build expected conversions array framework.")

        try:
            """
            Enrich conversions array by value.
            """
            quantity_two = quantity_of_conversion_object_into_release - 1

            while quantity_two >= 0:
                expected_conversions_array[quantity_two]['id'] = release_conversions_array[quantity_two]['id']
                """
                Enrich obligatory fields:
                - "coefficients";
                - "relatedItem";

                """
                expected_conversions_array[quantity_two]['relatesTo'] = \
                    payload_conversions_array[quantity_two]['relatesTo']

                expected_conversions_array[quantity_two]['rationale'] = \
                    payload_conversions_array[quantity_two]['rationale']
                expected_conversions_array[quantity_two]['description'] = \
                    payload_conversions_array[quantity_two]['description']
                expected_conversions_array[quantity_two]['coefficients'] = \
                    payload_conversions_array[quantity_two]['coefficients']

                expected_conversions_array[quantity_two]['relatedItem'] = \
                    dictionary_of_requirement_id[payload_conversions_array[quantity_two]['relatedItem']]

                coefficient_id = list()
                for coefficient_object in release_conversions_array[quantity_two]['coefficients']:
                    for o in coefficient_object:
                        if o == "id":
                            coefficient_id.append(coefficient_object[o])
                quantity_three = len(coefficient_id) - 1
                for expected_conversions_object in expected_conversions_array[quantity_two]['coefficients']:
                    for i in expected_conversions_object:
                        if i == "id":
                            while quantity_three >= 0:
                                expected_conversions_array[quantity_two]['coefficients'][quantity_three]['id'] = \
                                    coefficient_id[quantity_three]
                                quantity_three -= 1
                quantity_two -= 1

        except ValueError:
            raise ValueError("Impossible to enrich expected conversions array framework.")

        return expected_conversions_array

    def prepare_expected_electronic_auction_details_array(self, payload_electronic_auction_details_array,
                                                          release_electronic_auction_details_array):
        expected_electronic_auction_details_array = []
        try:
            """
            Check how many quantity of object into payload_electronic_auction_details_array.
            """
            list_of_payload_electronic_auction_details_id = list()
            for electronic_auction_details_object in payload_electronic_auction_details_array:
                for i in electronic_auction_details_object:
                    if i == "id":
                        list_of_payload_electronic_auction_details_id.append(i)
            quantity_of_electronic_auction_details_object_into_payload = \
                len(list_of_payload_electronic_auction_details_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['electronicAuction']['details'][*]['id']")

        try:
            """
            Check how many quantity of object into release_electronic_auction_details_array.
            Check release_electronic_auction_details_array[*]['id'] -> is it uuid.
            """
            list_of_release_electronic_auction_details_id = list()
            for electronic_auction_details_object in release_electronic_auction_details_array:
                for i in electronic_auction_details_object:
                    if i == "id":
                        list_of_release_electronic_auction_details_id.append(i)
                        try:
                            check_uuid_version(
                                uuid_to_test=electronic_auction_details_object['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your electronic_auction_details array in release: "
                                             "release_electronic_auction_details_array.id in release must be "
                                             "uuid version 4")
            quantity_of_electronic_auction_details_object_into_release = \
                len(list_of_release_electronic_auction_details_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['electronicAuction']['details'][*]['id']")

        try:
            """
            Compare quantity of electronic_auction_details objects into payload_electronic_auction_details_array 
            and release_electronic_auction_details_array.
            """
            if quantity_of_electronic_auction_details_object_into_payload == \
                    quantity_of_electronic_auction_details_object_into_release:
                pass
        except KeyError:
            raise KeyError("Quantity of lot objects into payload_electronic_auction_details_array != "
                           "quantity of lot objects into and release_electronic_auction_details_array")

        try:
            """
            Prepare electronic_auction_details array framework.
            """
            quantity_one = quantity_of_electronic_auction_details_object_into_release
            while quantity_one > 0:
                electronic_auction_details_object = {}
                electronic_auction_details_object.update(
                    self.constructor.ev_release_tender_electronic_auctions_details())
                expected_electronic_auction_details_array.append(electronic_auction_details_object)
                electronic_auction_details_object['electronicAuctionModalities'] = [{}]
                electronic_auction_details_object['electronicAuctionModalities'][0].update(
                    self.constructor.ev_release_tender_electronic_auctions_details_electronic_auction_modalities())
                quantity_one -= 1
        except ValueError:
            raise ValueError("Impossible to build expected electronic_auction_details array framework.")

        try:
            """
            Enrich electronic_auction_details array by value.
            """
            quantity_two = quantity_of_electronic_auction_details_object_into_release - 1
            while quantity_two >= 0:
                expected_electronic_auction_details_array[quantity_two]['id'] = \
                    release_electronic_auction_details_array[quantity_two]['id']

                """
                Enrich obligatory fields:
                - "relatedLot";
                - "auctionPeriod.startDate";
                - "electronicAuctionModalities";
                """

                expected_electronic_auction_details_array[quantity_two]['relatedLot'] = \
                    GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['lots'][quantity_two]['id']

                try:
                    check_date = fnmatch.fnmatch(
                        GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['electronicAuctions'][
                            'details'][quantity_two]['auctionPeriod']['startDate'],
                        "202*-*-*T*:*:*Z")
                    if check_date is True:
                        pass
                except ValueError:
                    raise ValueError("Check your electronicAuctions.details.auctionPeriod.startDate in EV release.")

                expected_electronic_auction_details_array[quantity_two]['auctionPeriod']['startDate'] = \
                    release_electronic_auction_details_array[quantity_two]['auctionPeriod']['startDate']
                expected_electronic_auction_details_array[quantity_two]['electronicAuctionModalities'][0][
                    'url'] = \
                    f"{self.metadata_auction_url}{GlobalClassCreateCnOnPn.ev_id}/" \
                    f"{GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['lots'][quantity_two]['id']}"
                expected_electronic_auction_details_array[quantity_two]['electronicAuctionModalities'][0][
                    'eligibleMinimumDifference'] = \
                    payload_electronic_auction_details_array[quantity_two]['electronicAuctionModalities'][0][
                        'eligibleMinimumDifference']
                quantity_two -= 1
        except ValueError:
            raise ValueError("Impossible to enrich expected electronicAuction.details array framework.")
        return expected_electronic_auction_details_array

    def ev_release_full_data_model_with_auction_criteria_conversions(self, payload, actual_release):
        release_id = GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id']
        tender_id = GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['id']
        related_processes_id_first = \
            GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['relatedProcesses'][0]['id']
        related_processes_id_second = \
            GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['relatedProcesses'][1]['id']

        release = {
            "releases": [{
                "tender": {},
                "relatedProcesses": [{}, {}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.ev_release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.ev_release_tender_section())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][1].update(self.constructor.release_related_processes_section())

        try:
            check_uuid_version(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in EV release: tender_id in EV release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in EV release: release_id in EV release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=related_processes_id_first,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in EV release: "
                             "tender_id in EV release must be uuid version 1")

        try:
            check_uuid_version(
                uuid_to_test=related_processes_id_second,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in EV release: "
                             "tender_id in EV release must be uuid version 1")

        try:
            check_operation_date = fnmatch.fnmatch(
                GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['auctionPeriod']['startDate'],
                "202*-*-*T*:*:*Z")
            if check_operation_date is True:
                pass
        except ValueError:
            raise ValueError("Check your auctionPeriod.startDate in EV release.")

        release['uri'] = f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreateCnOnPn.ev_id}"
        release['version'] = "1.1"
        release['extensions'] = self.extensions
        release['publisher']['name'] = self.publisher_name
        release['publisher']['uri'] = self.publisher_uri
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreateCnOnPn.ev_id
        release['releases'][0]['id'] = f"{GlobalClassCreateCnOnPn.ev_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "tender"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['hasPreviousNotice'] = True
        release['releases'][0]['purposeOfNotice']['isACallForCompetition'] = True

        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "active"
        release['releases'][0]['tender']['statusDetails'] = "clarification"
        release['releases'][0]['tender']['lots'] = self.prepare_expected_lots_array(
            payload_lots_array=payload['tender']['lots'],
            release_lots_array=actual_release['releases'][0]['tender']['lots'])
        release['releases'][0]['tender']['items'] = self.prepare_expected_items_array(
            payload_items_array=payload['tender']['items'],
            release_items_array=actual_release['releases'][0]['tender']['items'],
            release_lots_array=actual_release['releases'][0]['tender']['lots']
        )

        release['releases'][0]['tender']['criteria'] = self.prepare_expected_criteria_array(
            payload_criteria_array=GlobalClassCreateCnOnPn.payload['tender']['criteria'],
            release_criteria_array=GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['criteria']
        )

        release['releases'][0]['tender']['conversions'] = self.prepare_expected_conversions_array(
            payload=GlobalClassCreateCnOnPn.payload,
            actual_release=GlobalClassCreateCnOnPn.actual_ev_release
        )

        release['releases'][0]['tender']['lotGroups'][0]['optionToCombine'] = False
        release['releases'][0]['tender']['enquiryPeriod']['startDate'] = \
            GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
        release['releases'][0]['tender']['enquiryPeriod']['endDate'] = \
            GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
        release['releases'][0]['tender']['tenderPeriod']['startDate'] = \
            GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
        release['releases'][0]['tender']['tenderPeriod']['endDate'] = \
            GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate']

        release['releases'][0]['tender']['auctionPeriod']['startDate'] = \
            GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['auctionPeriod']['startDate']
        release['releases'][0]['tender']['hasEnquiries'] = False
        release['releases'][0]['tender']['awardCriteria'] = GlobalClassCreateCnOnPn.payload['tender']['awardCriteria']
        release['releases'][0]['tender']['awardCriteriaDetails'] = \
            GlobalClassCreateCnOnPn.payload['tender']['awardCriteriaDetails']
        release['releases'][0]['tender']['submissionMethod'] = ["electronicSubmission"]
        release['releases'][0]['tender']['submissionMethodDetails'] = \
            "Lista platformelor: achizitii, ebs, licitatie, yptender"
        release['releases'][0]['tender']['submissionMethodRationale'] = \
            ["Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"]
        release['releases'][0]['tender']['requiresElectronicCatalogue'] = False
        release['releases'][0]['tender']['procurementMethodModalities'] = \
            GlobalClassCreateCnOnPn.payload['tender']['procurementMethodModalities']
        release['releases'][0]['tender']['electronicAuctions']['details'] = \
            self.prepare_expected_electronic_auction_details_array(
                payload_electronic_auction_details_array=GlobalClassCreateCnOnPn.payload['tender'][
                    'electronicAuctions']['details'],
                release_electronic_auction_details_array=GlobalClassCreateCnOnPn.actual_ev_release[
                    'releases'][0]['tender']['electronicAuctions']['details']
            )

        release['releases'][0]['tender']['documents'] = self.prepare_expected_documents_array(
            payload=GlobalClassCreateCnOnPn.payload,
            release=GlobalClassCreateCnOnPn.actual_ev_release
        )

        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id_first
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_ocid}"
        release['releases'][0]['relatedProcesses'][1]['id'] = related_processes_id_second
        release['releases'][0]['relatedProcesses'][1]['relationship'][0] = "planning"
        release['releases'][0]['relatedProcesses'][1]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][1]['identifier'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['relatedProcesses'][1]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_id}"

        return release

    def ev_release_obligatory_data_model_without_auction_criteria_conversions(self, payload, actual_release):
        release_id = GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['id']
        tender_id = GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['tender']['id']
        related_processes_id_first = \
            GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['relatedProcesses'][0]['id']
        related_processes_id_second = \
            GlobalClassCreateCnOnPn.actual_ev_release['releases'][0]['relatedProcesses'][1]['id']

        release = {
            "releases": [{
                "tender": {},
                "relatedProcesses": [{}, {}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.ev_release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.ev_release_tender_section())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][1].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['tender']['criteria']
        del release['releases'][0]['tender']['conversions']
        del release['releases'][0]['tender']['auctionPeriod']
        del release['releases'][0]['tender']['electronicAuctions']
        del release['releases'][0]['tender']['procurementMethodModalities']

        try:
            check_uuid_version(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in EV release: tender_id in EV release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in EV release: release_id in EV release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=related_processes_id_first,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in EV release: "
                             "tender_id in EV release must be uuid version 1")

        try:
            check_uuid_version(
                uuid_to_test=related_processes_id_second,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in EV release: "
                             "tender_id in EV release must be uuid version 1")

        release['uri'] = f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreateCnOnPn.ev_id}"
        release['version'] = "1.1"
        release['extensions'] = self.extensions
        release['publisher']['name'] = self.publisher_name
        release['publisher']['uri'] = self.publisher_uri
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreateCnOnPn.ev_id
        release['releases'][0]['id'] = f"{GlobalClassCreateCnOnPn.ev_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "tender"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['hasPreviousNotice'] = True
        release['releases'][0]['purposeOfNotice']['isACallForCompetition'] = True

        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "active"
        release['releases'][0]['tender']['statusDetails'] = "clarification"

        release['releases'][0]['tender']['lots'] = self.prepare_expected_lots_array(
            payload_lots_array=payload['tender']['lots'],
            release_lots_array=actual_release['releases'][0]['tender']['lots'])
        release['releases'][0]['tender']['items'] = self.prepare_expected_items_array(
            payload_items_array=payload['tender']['items'],
            release_items_array=actual_release['releases'][0]['tender']['items'],
            release_lots_array=actual_release['releases'][0]['tender']['lots']
        )

        release['releases'][0]['tender']['lotGroups'][0]['optionToCombine'] = False
        release['releases'][0]['tender']['enquiryPeriod']['startDate'] = \
            GlobalClassCreateCnOnPn.feed_point_message['data']['operationDate']
        release['releases'][0]['tender']['enquiryPeriod']['endDate'] = \
            GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
        release['releases'][0]['tender']['tenderPeriod']['startDate'] = \
            GlobalClassCreateCnOnPn.payload['tender']['enquiryPeriod']['endDate']
        release['releases'][0]['tender']['tenderPeriod']['endDate'] = \
            GlobalClassCreateCnOnPn.payload['tender']['tenderPeriod']['endDate']

        release['releases'][0]['tender']['hasEnquiries'] = False
        release['releases'][0]['tender']['awardCriteria'] = GlobalClassCreateCnOnPn.payload['tender']['awardCriteria']
        release['releases'][0]['tender']['awardCriteriaDetails'] = "automated"
        release['releases'][0]['tender']['submissionMethod'] = ["electronicSubmission"]
        release['releases'][0]['tender']['submissionMethodDetails'] = \
            "Lista platformelor: achizitii, ebs, licitatie, yptender"
        release['releases'][0]['tender']['submissionMethodRationale'] = \
            ["Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"]
        release['releases'][0]['tender']['requiresElectronicCatalogue'] = False

        release['releases'][0]['tender']['documents'] = self.prepare_expected_documents_array(
            payload=GlobalClassCreateCnOnPn.payload,
            release=GlobalClassCreateCnOnPn.actual_ev_release
        )

        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id_first
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_ocid}"
        release['releases'][0]['relatedProcesses'][1]['id'] = related_processes_id_second
        release['releases'][0]['relatedProcesses'][1]['relationship'][0] = "planning"
        release['releases'][0]['relatedProcesses'][1]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][1]['identifier'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['relatedProcesses'][1]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_id}"

        return release
