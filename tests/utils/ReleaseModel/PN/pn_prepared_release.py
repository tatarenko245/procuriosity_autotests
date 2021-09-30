import copy

from tests.conftest import GlobalClassMetadata, GlobalClassCreatePn, GlobalClassCreateEi, GlobalClassCreateFs
from tests.utils.ReleaseModel.PN.pn_release_library import ReleaseLibrary

from tests.utils.functions import is_it_uuid, get_value_from_country_csv, get_value_from_region_csv, \
    get_value_from_locality_csv, get_value_from_cpvs_dictionary_csv, get_value_from_classification_cpv_dictionary_xls, \
    get_value_from_classification_unit_dictionary_csv, get_contract_period_for_ms_release, \
    generate_tender_classification_id, get_sum_of_lot


class PnExpectedRelease:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.metadata_tender_url = None
        self.metadata_document_url = None
        self.main_procurement_category = None
        try:
            if environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
                self.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
            elif environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
                self.metadata_document_url = "http://storage.eprocurement.systems/get"
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
                            is_it_uuid(
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
                - "isRecurrent";
                - "hasRenewals";
                - "hasVariants";
                - "hasOptions";
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

                if payload_lots_array[quantity_two]['placeOfPerformance']['address']['addressDetails'][
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

                expected_lots_array[quantity_two]['status'] = 'planning'
                expected_lots_array[quantity_two]['statusDetails'] = 'empty'
                expected_lots_array[quantity_two]['recurrentProcurement'][0]['isRecurrent'] = False
                expected_lots_array[quantity_two]['renewals'][0]['hasRenewals'] = False
                expected_lots_array[quantity_two]['variants'][0]['hasVariants'] = False
                expected_lots_array[quantity_two]['options'][0]['hasOptions'] = False
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
                            is_it_uuid(
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

    def prepare_expected_documents_array(self, payload_documents_array, release_documents_array):
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
                            is_it_uuid(
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
                    [GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['lots'][0]['id']]
                expected_documents_array[quantity_two]['datePublished'] = \
                    GlobalClassCreatePn.feed_point_message['data']['operationDate']
                quantity_two -= 1
        except ValueError:
            raise ValueError("Impossible to enrich expected lots array framework.")

        return expected_documents_array

    def pn_release_full_data_model_with_lots_and_items_full_based_on_one_fs(self):
        release_id = GlobalClassCreatePn.actual_pn_release['releases'][0]['id']
        tender_id = GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['id']
        related_processes_id = GlobalClassCreatePn.actual_pn_release['releases'][0]['relatedProcesses'][0]['id']

        release = {
            "releases": [{
                "tender": {},
                "relatedProcesses": [{}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.pn_release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.pn_release_tender_section())
        release['releases'][0]['tender']['lotGroups'] = [{}]
        release['releases'][0]['tender']['lotGroups'][0].update(
            self.constructor.pn_release_tender_lot_group_option_to_combine())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())

        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in FS release: tender_id in FS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in FS release: release_id in FS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=related_processes_id,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in FS release: "
                             "tender_id in FS release must be uuid version 1")

        release['uri'] = f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_id}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['id'] = f"{GlobalClassCreatePn.pn_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = "Planning Notice"
        release['releases'][0]['tender']['description'] = "Contracting process is planned"
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "planning"
        release['releases'][0]['tender']['lots'] = self.prepare_expected_lots_array(
            payload_lots_array=GlobalClassCreatePn.payload['tender']['lots'],
            release_lots_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['lots'])
        release['releases'][0]['tender']['items'] = self.prepare_expected_items_array(
            payload_items_array=GlobalClassCreatePn.payload['tender']['items'],
            release_items_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['items'],
            release_lots_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['lots']
        )
        release['releases'][0]['tender']['lotGroups'][0]['optionToCombine'] = False
        release['releases'][0]['tender']['tenderPeriod']['startDate'] = \
            GlobalClassCreatePn.payload['tender']['tenderPeriod']['startDate']
        release['releases'][0]['tender']['hasEnquiries'] = False
        release['releases'][0]['tender']['submissionMethod'][0] = "electronicSubmission"
        release['releases'][0]['tender']['submissionMethodDetails'] = \
            "Lista platformelor: achizitii, ebs, licitatie, yptender"
        release['releases'][0]['tender']['submissionMethodRationale'][0] = \
            "Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"
        release['releases'][0]['tender']['requiresElectronicCatalogue'] = False
        release['releases'][0]['tender']['documents'] = self.prepare_expected_documents_array(
            payload_documents_array=GlobalClassCreatePn.payload['tender']['documents'],
            release_documents_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['documents']
        )
        release['releases'][0]['hasPreviousNotice'] = False
        release['releases'][0]['purposeOfNotice']['isACallForCompetition'] = False
        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_ocid}"

        return release

    def ms_release_full_data_model_with_four_parties_object_based_on_fs(self):
        release_id = GlobalClassCreatePn.actual_ms_release['releases'][0]['id']
        tender_id = GlobalClassCreatePn.actual_ms_release['releases'][0]['tender']['id']
        related_processes_id_first = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][0]['id']
        related_processes_id_second = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][1]['id']
        related_processes_id_third = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][2]['id']

        release = {
            "releases": [{
                "planning": {},
                "tender": {},
                "parties": [{}, {}, {}, {}],
                "relatedProcesses": [{}, {}, {}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.ms_release_general_attributes())
        release['releases'][0]['planning'].update(self.constructor.ms_release_planning_section())
        release['releases'][0]['planning']['budget']['budgetBreakdown'] = [{}]
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0].update(
            self.constructor.ms_release_planning_budget_budget_breakdown_obj())
        release['releases'][0]['tender'].update(self.constructor.ms_release_tender_section())
        release['releases'][0]['parties'][3].update(self.constructor.release_parties_section())
        release['releases'][0]['parties'][3]['additionalIdentifiers'] = [{}]
        release['releases'][0]['parties'][3]['additionalIdentifiers'][0].update(
            self.constructor.release_parties_additional_identifiers())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][1].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][2].update(self.constructor.release_related_processes_section())

        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in MS release: tender_id in MS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in MS release: release_id in MS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=related_processes_id_first,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id[0] in MS release: "
                             "tender_id in MS release must be uuid version 1")
        try:
            is_it_uuid(
                uuid_to_test=related_processes_id_second,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id[1] in MS release: "
                             "tender_id in MS release must be uuid version 1")

        try:
            is_it_uuid(
                uuid_to_test=related_processes_id_third,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id[2] in MS release: "
                             "tender_id in MS release must be uuid version 1")

        try:
            procuring_entity_country_data = get_value_from_country_csv(
                country=
                GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )
            procuring_entity_country_object = {
                "scheme": procuring_entity_country_data[2],
                "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": procuring_entity_country_data[1],
                "uri": procuring_entity_country_data[3]
            }

            procuring_entity_region_data = get_value_from_region_csv(
                region=GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                country=
                GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            procuring_entity_region_object = {
                "scheme": procuring_entity_region_data[2],
                "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                "description": procuring_entity_region_data[1],
                "uri": procuring_entity_region_data[3]
            }

            if GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                'scheme'] == "CUATM":
                procuring_entity_locality_data = get_value_from_locality_csv(
                    locality=
                    GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'id'],
                    region=
                    GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                        'id'],
                    country=
                    GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                        'id'],
                    language=self.language
                )
                procuring_entity_locality_object = {
                    "scheme": procuring_entity_locality_data[2],
                    "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description": procuring_entity_locality_data[1],
                    "uri": procuring_entity_locality_data[3]
                }
            else:
                procuring_entity_locality_object = {
                    "scheme":
                        GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'scheme'],
                    "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description":
                        GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        try:
            eligibility_criteria = None
            if self.language == "ro":
                eligibility_criteria = "Regulile generale privind naționalitatea și originea, precum și " \
                                       "alte criterii de eligibilitate sunt enumerate în Ghidul practic privind " \
                                       "procedurile de contractare a acțiunilor externe ale UE (PRAG)"
            elif self.language == "en":
                eligibility_criteria = "The general rules on nationality and origin, as well as other eligibility " \
                                       "criteria are listed in the Practical Guide to Contract Procedures for EU " \
                                       "External Actions (PRAG)"
        except ValueError:
            raise ValueError("Check language")

        cpv_data = get_value_from_classification_cpv_dictionary_xls(
            cpv=generate_tender_classification_id(items_array=GlobalClassCreatePn.payload['tender']['items']),
            language=self.language
        )

        release['uri'] = f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_ocid}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['id'] = f"{GlobalClassCreatePn.pn_ocid}-{release_id[29:42]}"
        release['releases'][0]['date'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = GlobalClassCreatePn.payload['tender']['title']
        release['releases'][0]['tender']['description'] = GlobalClassCreatePn.payload['tender']['description']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "planning notice"
        release['releases'][0]['tender']['value']['amount'] = \
            get_sum_of_lot(lots_array=GlobalClassCreatePn.payload['tender']['lots'])
        release['releases'][0]['tender']['value']['currency'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        release['releases'][0]['tender']['procurementMethod'] = "open"
        release['releases'][0]['tender']['procurementMethodDetails'] = "testOpenTender"
        release['releases'][0]['tender']['mainProcurementCategory'] = \
            GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['mainProcurementCategory']
        release['releases'][0]['tender']['procurementMethodRationale'] = \
            GlobalClassCreatePn.payload['tender']['procurementMethodRationale']
        release['releases'][0]['tender']['hasEnquiries'] = False
        release['releases'][0]['tender']['eligibilityCriteria'] = eligibility_criteria
        release['releases'][0]['tender']['contractPeriod']['startDate'] = \
            get_contract_period_for_ms_release(GlobalClassCreatePn.payload['tender']['lots'])[0]
        release['releases'][0]['tender']['contractPeriod']['endDate'] = \
            get_contract_period_for_ms_release(GlobalClassCreatePn.payload['tender']['lots'])[1]
        release['releases'][0]['tender']['procuringEntity']['id'] = \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['tender']['procuringEntity']['name'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['name']
        release['releases'][0]['tender']['acceleratedProcedure']['isAcceleratedProcedure'] = False
        release['releases'][0]['tender']['classification']['id'] = cpv_data[0]
        release['releases'][0]['tender']['classification']['description'] = cpv_data[1]
        release['releases'][0]['tender']['classification']['scheme'] = "CPV"
        release['releases'][0]['tender']['designContest']['serviceContractAward'] = False
        release['releases'][0]['tender']['electronicWorkflows']['useOrdering'] = False
        release['releases'][0]['tender']['electronicWorkflows']['usePayment'] = False
        release['releases'][0]['tender']['electronicWorkflows']['acceptInvoicing'] = False
        release['releases'][0]['tender']['jointProcurement']['isJointProcurement'] = False
        release['releases'][0]['tender']['legalBasis'] = GlobalClassCreatePn.payload['tender']['legalBasis']
        release['releases'][0]['tender']['procedureOutsourcing']['procedureOutsourced'] = False
        release['releases'][0]['tender']['dynamicPurchasingSystem']['hasDynamicPurchasingSystem'] = False
        release['releases'][0]['tender']['framework']['isAFramework'] = False
        release['releases'][0]['tender']['procurementMethodAdditionalInfo'] = \
            GlobalClassCreatePn.payload['tender']['procurementMethodAdditionalInfo']
        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id_first
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "planning"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_id}"
        release['releases'][0]['relatedProcesses'][1]['id'] = related_processes_id_second
        release['releases'][0]['relatedProcesses'][1]['relationship'][0] = "x_expenditureItem"
        release['releases'][0]['relatedProcesses'][1]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][1]['identifier'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['relatedProcesses'][1]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        release['releases'][0]['relatedProcesses'][2]['id'] = related_processes_id_third
        release['releases'][0]['relatedProcesses'][2]['relationship'][0] = "x_fundingSource"
        release['releases'][0]['relatedProcesses'][2]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][2]['identifier'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['relatedProcesses'][2]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateFs.fs_id}"
        release['releases'][0]['planning']['rationale'] = GlobalClassCreatePn.payload['planning']['rationale']
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = \
            GlobalClassCreateFs.actual_fs_release['releases'][0]['planning']['budget']['isEuropeanUnionFunded']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['sourceParty'] = \
            GlobalClassCreateFs.actual_fs_release['releases'][0]['planning']['budget']['sourceEntity']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['period'] = \
            GlobalClassCreateFs.actual_fs_release['releases'][0]['planning']['budget']['period']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['europeanUnionFunding'] = \
            GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding']

        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['description'] = \
            GlobalClassCreateFs.payload['planning']['budget']['description']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['amount']['amount'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['amount']['currency'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['id'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        release['releases'][0]['planning']['budget']['description'] = \
            GlobalClassCreatePn.payload['planning']['budget']['description']
        release['releases'][0]['parties'][0] = GlobalClassCreateEi.actual_ei_release['releases'][0]['parties'][0]
        release['releases'][0]['parties'][1] = GlobalClassCreateFs.actual_fs_release['releases'][0]['parties'][1]
        release['releases'][0]['parties'][2] = GlobalClassCreateFs.actual_fs_release['releases'][0]['parties'][0]
        release['releases'][0]['parties'][3]['id'] = \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][3]['name'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][3]['identifier'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']
        release['releases'][0]['parties'][3]['additionalIdentifiers'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['additionalIdentifiers']
        release['releases'][0]['parties'][3]['address']['streetAddress'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][3]['address']['postalCode'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['postalCode']
        release['releases'][0]['parties'][3]['address']['addressDetails']['country'] = procuring_entity_country_object
        release['releases'][0]['parties'][3]['address']['addressDetails']['region'] = procuring_entity_region_object
        release['releases'][0]['parties'][3]['address']['addressDetails']['locality'] = procuring_entity_locality_object
        release['releases'][0]['parties'][3]['contactPoint'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['contactPoint']
        release['releases'][0]['parties'][3]['roles'][0] = "procuringEntity"

        return release

    def pn_release_obligatory_data_model_with_lots_and_items_based_on_one_fs(self):
        release_id = GlobalClassCreatePn.actual_pn_release['releases'][0]['id']
        tender_id = GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['id']
        related_processes_id = GlobalClassCreatePn.actual_pn_release['releases'][0]['relatedProcesses'][0]['id']

        release = {
            "releases": [{
                "tender": {},
                "relatedProcesses": [{}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.pn_release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.pn_release_tender_section())
        release['releases'][0]['tender']['lotGroups'] = [{}]
        release['releases'][0]['tender']['lotGroups'][0].update(
            self.constructor.pn_release_tender_lot_group_option_to_combine())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['tender']['documents']

        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in FS release: tender_id in FS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in FS release: release_id in FS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=related_processes_id,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in FS release: "
                             "tender_id in FS release must be uuid version 1")

        release['uri'] = f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_id}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['id'] = f"{GlobalClassCreatePn.pn_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = "Planning Notice"
        release['releases'][0]['tender']['description'] = "Contracting process is planned"
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "planning"
        release['releases'][0]['tender']['lots'] = self.prepare_expected_lots_array(
            payload_lots_array=GlobalClassCreatePn.payload['tender']['lots'],
            release_lots_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['lots'])
        release['releases'][0]['tender']['items'] = self.prepare_expected_items_array(
            payload_items_array=GlobalClassCreatePn.payload['tender']['items'],
            release_items_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['items'],
            release_lots_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['lots']
        )
        release['releases'][0]['tender']['lotGroups'][0]['optionToCombine'] = False
        release['releases'][0]['tender']['tenderPeriod']['startDate'] = \
            GlobalClassCreatePn.payload['tender']['tenderPeriod']['startDate']
        release['releases'][0]['tender']['hasEnquiries'] = False
        release['releases'][0]['tender']['submissionMethod'][0] = "electronicSubmission"
        release['releases'][0]['tender']['submissionMethodDetails'] = \
            "Lista platformelor: achizitii, ebs, licitatie, yptender"
        release['releases'][0]['tender']['submissionMethodRationale'][0] = \
            "Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"
        release['releases'][0]['tender']['requiresElectronicCatalogue'] = False
        release['releases'][0]['hasPreviousNotice'] = False
        release['releases'][0]['purposeOfNotice']['isACallForCompetition'] = False
        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_ocid}"

        return release

    def ms_release_obligatory_data_model_with_four_parties_object_based_on_fs_full(self):
        release_id = GlobalClassCreatePn.actual_ms_release['releases'][0]['id']
        tender_id = GlobalClassCreatePn.actual_ms_release['releases'][0]['tender']['id']
        related_processes_id_first = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][0]['id']
        related_processes_id_second = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][1]['id']
        related_processes_id_third = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][2]['id']

        release = {
            "releases": [{
                "planning": {},
                "tender": {},
                "parties": [{}, {}, {}, {}],
                "relatedProcesses": [{}, {}, {}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.ms_release_general_attributes())
        release['releases'][0]['planning'].update(self.constructor.ms_release_planning_section())
        release['releases'][0]['planning']['budget']['budgetBreakdown'] = [{}]
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0].update(
            self.constructor.ms_release_planning_budget_budget_breakdown_obj())
        release['releases'][0]['tender'].update(self.constructor.ms_release_tender_section())
        release['releases'][0]['parties'][3].update(self.constructor.release_parties_section())
        release['releases'][0]['parties'][3]['additionalIdentifiers'] = [{}]
        release['releases'][0]['parties'][3]['additionalIdentifiers'][0].update(
            self.constructor.release_parties_additional_identifiers())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][1].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][2].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['tender']['procurementMethodRationale']
        del release['releases'][0]['tender']['procurementMethodAdditionalInfo']
        del release['releases'][0]['planning']['rationale']
        del release['releases'][0]['planning']['budget']['description']
        del release['releases'][0]['parties'][3]['additionalIdentifiers']
        del release['releases'][0]['parties'][3]['address']['postalCode']
        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in MS release: tender_id in MS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in MS release: release_id in MS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=related_processes_id_first,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id[0] in MS release: "
                             "tender_id in MS release must be uuid version 1")
        try:
            is_it_uuid(
                uuid_to_test=related_processes_id_second,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id[1] in MS release: "
                             "tender_id in MS release must be uuid version 1")

        try:
            is_it_uuid(
                uuid_to_test=related_processes_id_third,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id[2] in MS release: "
                             "tender_id in MS release must be uuid version 1")

        try:
            procuring_entity_country_data = get_value_from_country_csv(
                country=
                GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )
            procuring_entity_country_object = {
                "scheme": procuring_entity_country_data[2],
                "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": procuring_entity_country_data[1],
                "uri": procuring_entity_country_data[3]
            }

            procuring_entity_region_data = get_value_from_region_csv(
                region=GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                country=
                GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            procuring_entity_region_object = {
                "scheme": procuring_entity_region_data[2],
                "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                "description": procuring_entity_region_data[1],
                "uri": procuring_entity_region_data[3]
            }

            if GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                'scheme'] == "CUATM":
                procuring_entity_locality_data = get_value_from_locality_csv(
                    locality=
                    GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'id'],
                    region=
                    GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                        'id'],
                    country=
                    GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                        'id'],
                    language=self.language
                )
                procuring_entity_locality_object = {
                    "scheme": procuring_entity_locality_data[2],
                    "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description": procuring_entity_locality_data[1],
                    "uri": procuring_entity_locality_data[3]
                }
            else:
                procuring_entity_locality_object = {
                    "scheme":
                        GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'scheme'],
                    "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description":
                        GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        try:
            eligibility_criteria = None
            if self.language == "ro":
                eligibility_criteria = "Regulile generale privind naționalitatea și originea, precum și " \
                                       "alte criterii de eligibilitate sunt enumerate în Ghidul practic privind " \
                                       "procedurile de contractare a acțiunilor externe ale UE (PRAG)"
            elif self.language == "en":
                eligibility_criteria = "The general rules on nationality and origin, as well as other eligibility " \
                                       "criteria are listed in the Practical Guide to Contract Procedures for EU " \
                                       "External Actions (PRAG)"
        except ValueError:
            raise ValueError("Check language")

        cpv_data = get_value_from_classification_cpv_dictionary_xls(
            cpv=generate_tender_classification_id(items_array=GlobalClassCreatePn.payload['tender']['items']),
            language=self.language
        )

        release['uri'] = f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_ocid}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['id'] = f"{GlobalClassCreatePn.pn_ocid}-{release_id[29:42]}"
        release['releases'][0]['date'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = GlobalClassCreatePn.payload['tender']['title']
        release['releases'][0]['tender']['description'] = GlobalClassCreatePn.payload['tender']['description']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "planning notice"
        release['releases'][0]['tender']['value']['amount'] = \
            get_sum_of_lot(lots_array=GlobalClassCreatePn.payload['tender']['lots'])
        release['releases'][0]['tender']['value']['currency'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        release['releases'][0]['tender']['procurementMethod'] = "open"
        release['releases'][0]['tender']['procurementMethodDetails'] = "testOpenTender"
        release['releases'][0]['tender']['mainProcurementCategory'] = \
            GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['mainProcurementCategory']

        release['releases'][0]['tender']['hasEnquiries'] = False
        release['releases'][0]['tender']['eligibilityCriteria'] = eligibility_criteria
        release['releases'][0]['tender']['contractPeriod']['startDate'] = \
            get_contract_period_for_ms_release(GlobalClassCreatePn.payload['tender']['lots'])[0]
        release['releases'][0]['tender']['contractPeriod']['endDate'] = \
            get_contract_period_for_ms_release(GlobalClassCreatePn.payload['tender']['lots'])[1]
        release['releases'][0]['tender']['procuringEntity']['id'] = \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['tender']['procuringEntity']['name'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['name']
        release['releases'][0]['tender']['acceleratedProcedure']['isAcceleratedProcedure'] = False
        release['releases'][0]['tender']['classification']['id'] = cpv_data[0]
        release['releases'][0]['tender']['classification']['description'] = cpv_data[1]
        release['releases'][0]['tender']['classification']['scheme'] = "CPV"
        release['releases'][0]['tender']['designContest']['serviceContractAward'] = False
        release['releases'][0]['tender']['electronicWorkflows']['useOrdering'] = False
        release['releases'][0]['tender']['electronicWorkflows']['usePayment'] = False
        release['releases'][0]['tender']['electronicWorkflows']['acceptInvoicing'] = False
        release['releases'][0]['tender']['jointProcurement']['isJointProcurement'] = False
        release['releases'][0]['tender']['legalBasis'] = GlobalClassCreatePn.payload['tender']['legalBasis']
        release['releases'][0]['tender']['procedureOutsourcing']['procedureOutsourced'] = False
        release['releases'][0]['tender']['dynamicPurchasingSystem']['hasDynamicPurchasingSystem'] = False
        release['releases'][0]['tender']['framework']['isAFramework'] = False
        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id_first
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "planning"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_id}"
        release['releases'][0]['relatedProcesses'][1]['id'] = related_processes_id_second
        release['releases'][0]['relatedProcesses'][1]['relationship'][0] = "x_expenditureItem"
        release['releases'][0]['relatedProcesses'][1]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][1]['identifier'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['relatedProcesses'][1]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        release['releases'][0]['relatedProcesses'][2]['id'] = related_processes_id_third
        release['releases'][0]['relatedProcesses'][2]['relationship'][0] = "x_fundingSource"
        release['releases'][0]['relatedProcesses'][2]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][2]['identifier'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['relatedProcesses'][2]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateFs.fs_id}"
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = \
            GlobalClassCreateFs.actual_fs_release['releases'][0]['planning']['budget']['isEuropeanUnionFunded']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['sourceParty'] = \
            GlobalClassCreateFs.actual_fs_release['releases'][0]['planning']['budget']['sourceEntity']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['period'] = \
            GlobalClassCreateFs.actual_fs_release['releases'][0]['planning']['budget']['period']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['europeanUnionFunding'] = \
            GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding']

        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['description'] = \
            GlobalClassCreateFs.payload['planning']['budget']['description']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['amount']['amount'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['amount']['currency'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['id'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        release['releases'][0]['parties'][0] = GlobalClassCreateEi.actual_ei_release['releases'][0]['parties'][0]
        release['releases'][0]['parties'][1] = GlobalClassCreateFs.actual_fs_release['releases'][0]['parties'][1]
        release['releases'][0]['parties'][2] = GlobalClassCreateFs.actual_fs_release['releases'][0]['parties'][0]
        release['releases'][0]['parties'][3]['id'] = \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][3]['name'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][3]['identifier'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']
        release['releases'][0]['parties'][3]['address']['streetAddress'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][3]['address']['addressDetails']['country'] = procuring_entity_country_object
        release['releases'][0]['parties'][3]['address']['addressDetails']['region'] = procuring_entity_region_object
        release['releases'][0]['parties'][3]['address']['addressDetails']['locality'] = procuring_entity_locality_object
        release['releases'][0]['parties'][3]['contactPoint'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['contactPoint']
        release['releases'][0]['parties'][3]['roles'][0] = "procuringEntity"

        return release

    def pn_release_obligatory_data_model_without_lots_and_items_based_on_one_fs(self):
        release_id = GlobalClassCreatePn.actual_pn_release['releases'][0]['id']
        tender_id = GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['id']
        related_processes_id = GlobalClassCreatePn.actual_pn_release['releases'][0]['relatedProcesses'][0]['id']

        release = {
            "releases": [{
                "tender": {},
                "relatedProcesses": [{}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.pn_release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.pn_release_tender_section())
        release['releases'][0]['tender']['lotGroups'] = [{}]
        release['releases'][0]['tender']['lotGroups'][0].update(
            self.constructor.pn_release_tender_lot_group_option_to_combine())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['tender']['documents']
        del release['releases'][0]['tender']['lots']
        del release['releases'][0]['tender']['items']
        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in FS release: tender_id in FS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in FS release: release_id in FS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=related_processes_id,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in FS release: "
                             "tender_id in FS release must be uuid version 1")

        release['uri'] = f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_id}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['id'] = f"{GlobalClassCreatePn.pn_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = "Planning Notice"
        release['releases'][0]['tender']['description'] = "Contracting process is planned"
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "planning"
        release['releases'][0]['tender']['lotGroups'][0]['optionToCombine'] = False
        release['releases'][0]['tender']['tenderPeriod']['startDate'] = \
            GlobalClassCreatePn.payload['tender']['tenderPeriod']['startDate']
        release['releases'][0]['tender']['hasEnquiries'] = False
        release['releases'][0]['tender']['submissionMethod'][0] = "electronicSubmission"
        release['releases'][0]['tender']['submissionMethodDetails'] = \
            "Lista platformelor: achizitii, ebs, licitatie, yptender"
        release['releases'][0]['tender']['submissionMethodRationale'][0] = \
            "Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"
        release['releases'][0]['tender']['requiresElectronicCatalogue'] = False
        release['releases'][0]['hasPreviousNotice'] = False
        release['releases'][0]['purposeOfNotice']['isACallForCompetition'] = False
        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_ocid}"

        return release

    def ms_release_obligatory_two(self):
        release_id = GlobalClassCreatePn.actual_ms_release['releases'][0]['id']
        tender_id = GlobalClassCreatePn.actual_ms_release['releases'][0]['tender']['id']
        related_processes_id_first = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][0]['id']
        related_processes_id_second = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][1]['id']
        related_processes_id_third = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][2]['id']

        release = {
            "releases": [{
                "planning": {},
                "tender": {},
                "parties": [{}, {}, {}],
                "relatedProcesses": [{}, {}, {}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.ms_release_general_attributes())
        release['releases'][0]['planning'].update(self.constructor.ms_release_planning_section())
        release['releases'][0]['planning']['budget']['budgetBreakdown'] = [{}]
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0].update(
            self.constructor.ms_release_planning_budget_budget_breakdown_obj())
        release['releases'][0]['tender'].update(self.constructor.ms_release_tender_section())
        release['releases'][0]['parties'][2].update(self.constructor.release_parties_section())
        release['releases'][0]['parties'][2]['additionalIdentifiers'] = [{}]
        release['releases'][0]['parties'][2]['additionalIdentifiers'][0].update(
            self.constructor.release_parties_additional_identifiers())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][1].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][2].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['tender']['procurementMethodRationale']
        del release['releases'][0]['tender']['procurementMethodAdditionalInfo']
        del release['releases'][0]['tender']['contractPeriod']
        del release['releases'][0]['planning']['rationale']
        del release['releases'][0]['planning']['budget']['description']
        del release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['description']
        del release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['europeanUnionFunding']
        del release['releases'][0]['parties'][2]['additionalIdentifiers']
        del release['releases'][0]['parties'][2]['address']['postalCode']
        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in MS release: tender_id in MS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in MS release: release_id in MS release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=related_processes_id_first,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id[0] in MS release: "
                             "tender_id in MS release must be uuid version 1")
        try:
            is_it_uuid(
                uuid_to_test=related_processes_id_second,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id[1] in MS release: "
                             "tender_id in MS release must be uuid version 1")

        try:
            is_it_uuid(
                uuid_to_test=related_processes_id_third,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id[2] in MS release: "
                             "tender_id in MS release must be uuid version 1")

        try:
            procuring_entity_country_data = get_value_from_country_csv(
                country=
                GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )
            procuring_entity_country_object = {
                "scheme": procuring_entity_country_data[2],
                "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": procuring_entity_country_data[1],
                "uri": procuring_entity_country_data[3]
            }

            procuring_entity_region_data = get_value_from_region_csv(
                region=GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                country=
                GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            procuring_entity_region_object = {
                "scheme": procuring_entity_region_data[2],
                "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                "description": procuring_entity_region_data[1],
                "uri": procuring_entity_region_data[3]
            }

            if GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                'scheme'] == "CUATM":
                procuring_entity_locality_data = get_value_from_locality_csv(
                    locality=
                    GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'id'],
                    region=
                    GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                        'id'],
                    country=
                    GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                        'id'],
                    language=self.language
                )
                procuring_entity_locality_object = {
                    "scheme": procuring_entity_locality_data[2],
                    "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description": procuring_entity_locality_data[1],
                    "uri": procuring_entity_locality_data[3]
                }
            else:
                procuring_entity_locality_object = {
                    "scheme":
                        GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'scheme'],
                    "id": GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description":
                        GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        try:
            eligibility_criteria = None
            if self.language == "ro":
                eligibility_criteria = "Regulile generale privind naționalitatea și originea, precum și " \
                                       "alte criterii de eligibilitate sunt enumerate în Ghidul practic privind " \
                                       "procedurile de contractare a acțiunilor externe ale UE (PRAG)"
            elif self.language == "en":
                eligibility_criteria = "The general rules on nationality and origin, as well as other eligibility " \
                                       "criteria are listed in the Practical Guide to Contract Procedures for EU " \
                                       "External Actions (PRAG)"
        except ValueError:
            raise ValueError("Check language")

        release['uri'] = f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_ocid}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['id'] = f"{GlobalClassCreatePn.pn_ocid}-{release_id[29:42]}"
        release['releases'][0]['date'] = GlobalClassCreatePn.feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = GlobalClassCreatePn.payload['tender']['title']
        release['releases'][0]['tender']['description'] = GlobalClassCreatePn.payload['tender']['description']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "planning notice"
        release['releases'][0]['tender']['value']['amount'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount']
        release['releases'][0]['tender']['value']['currency'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        release['releases'][0]['tender']['procurementMethod'] = "open"
        release['releases'][0]['tender']['procurementMethodDetails'] = "testOpenTender"
        release['releases'][0]['tender']['mainProcurementCategory'] = \
            GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['mainProcurementCategory']

        release['releases'][0]['tender']['hasEnquiries'] = False
        release['releases'][0]['tender']['eligibilityCriteria'] = eligibility_criteria
        release['releases'][0]['tender']['procuringEntity']['id'] = \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['tender']['procuringEntity']['name'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['name']
        release['releases'][0]['tender']['acceleratedProcedure']['isAcceleratedProcedure'] = False
        release['releases'][0]['tender']['classification'] = \
            GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['classification']
        release['releases'][0]['tender']['designContest']['serviceContractAward'] = False
        release['releases'][0]['tender']['electronicWorkflows']['useOrdering'] = False
        release['releases'][0]['tender']['electronicWorkflows']['usePayment'] = False
        release['releases'][0]['tender']['electronicWorkflows']['acceptInvoicing'] = False
        release['releases'][0]['tender']['jointProcurement']['isJointProcurement'] = False
        release['releases'][0]['tender']['legalBasis'] = GlobalClassCreatePn.payload['tender']['legalBasis']
        release['releases'][0]['tender']['procedureOutsourcing']['procedureOutsourced'] = False
        release['releases'][0]['tender']['dynamicPurchasingSystem']['hasDynamicPurchasingSystem'] = False
        release['releases'][0]['tender']['framework']['isAFramework'] = False
        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id_first
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "planning"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_id}"
        release['releases'][0]['relatedProcesses'][1]['id'] = related_processes_id_second
        release['releases'][0]['relatedProcesses'][1]['relationship'][0] = "x_expenditureItem"
        release['releases'][0]['relatedProcesses'][1]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][1]['identifier'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['relatedProcesses'][1]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        release['releases'][0]['relatedProcesses'][2]['id'] = related_processes_id_third
        release['releases'][0]['relatedProcesses'][2]['relationship'][0] = "x_fundingSource"
        release['releases'][0]['relatedProcesses'][2]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][2]['identifier'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['relatedProcesses'][2]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateFs.fs_id}"
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = \
            GlobalClassCreateFs.actual_fs_release['releases'][0]['planning']['budget']['isEuropeanUnionFunded']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['sourceParty'] = \
            GlobalClassCreateFs.actual_fs_release['releases'][0]['planning']['budget']['sourceEntity']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['period'] = \
            GlobalClassCreateFs.actual_fs_release['releases'][0]['planning']['budget']['period']

        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['amount']['amount'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['amount']['currency'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0]['id'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            GlobalClassCreatePn.payload['planning']['budget']['budgetBreakdown'][0]['amount']['currency']
        release['releases'][0]['parties'][0] = GlobalClassCreateEi.actual_ei_release['releases'][0]['parties'][0]
        release['releases'][0]['parties'][1] = GlobalClassCreateFs.actual_fs_release['releases'][0]['parties'][0]
        release['releases'][0]['parties'][2]['id'] = \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][2]['name'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][2]['identifier'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['identifier']
        release['releases'][0]['parties'][2]['address']['streetAddress'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][2]['address']['addressDetails']['country'] = procuring_entity_country_object
        release['releases'][0]['parties'][2]['address']['addressDetails']['region'] = procuring_entity_region_object
        release['releases'][0]['parties'][2]['address']['addressDetails']['locality'] = procuring_entity_locality_object
        release['releases'][0]['parties'][2]['contactPoint'] = \
            GlobalClassCreatePn.payload['tender']['procuringEntity']['contactPoint']
        release['releases'][0]['parties'][2]['roles'][0] = "procuringEntity"

        return release
