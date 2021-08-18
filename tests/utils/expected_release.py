import copy

from tests.conftest import GlobalClassMetadata, GlobalClassCreateFs, GlobalClassCreatePn, GlobalClassCreateEi
from tests.utils.functions import is_it_uuid, get_value_from_country_csv, get_value_from_region_csv, \
    get_value_from_locality_csv, get_value_from_classification_cpv_dictionary_xls, get_value_from_cpvs_dictionary_csv, \
    get_value_from_classification_unit_dictionary_csv
from tests.utils.release_library import ReleaseLibrary


class ExpectedRelease:
    def __init__(self, environment, language):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.metadata_budget_url = None
        self.main_procurement_category = None
        try:
            if environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
            elif environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")
        GlobalClassMetadata.metadata_budget_url = self.metadata_budget_url

    def __prepare_expected_items_array(self, payload_items_array, release_items_array, release_lots_array=None):
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
            quantity_two = quantity_of_item_object_into_release-1
            while quantity_two >= 0:
                expected_items_array[quantity_two]['id'] = release_items_array[quantity_two]['id']
                """
                Enrich or delete optional fields: 
                - "internalId";
                - "additionalClassifications";
                - "deliveryAddress";
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

                if "deliveryAddress" in payload_items_array[quantity_two]:
                    item_country_data = get_value_from_country_csv(
                        country=payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['country']['id'],
                        language=self.language
                    )
                    item_country_object = {
                        "scheme": item_country_data[2],
                        "id": payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['country']['id'],
                        "description": item_country_data[1],
                        "uri": item_country_data[3]
                    }

                    item_region_data = get_value_from_region_csv(
                        region=payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['region']['id'],
                        country=payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['country']['id'],
                        language=self.language
                    )
                    item_region_object = {
                        "scheme": item_region_data[2],
                        "id": payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['region']['id'],
                        "description": item_region_data[1],
                        "uri": item_region_data[3]
                    }

                    if payload_items_array[quantity_two]['deliveryAddress']['addressDetails']['locality'][
                        'scheme'] == "CUATM":
                        item_locality_data = get_value_from_locality_csv(
                            locality=payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'locality']['id'],
                            region=payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'region']['id'],
                            country=payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'country']['id'],
                            language=self.language
                        )
                        item_locality_object = {
                            "scheme": item_locality_data[2],
                            "id": payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'locality']['id'],
                            "description": item_locality_data[1],
                            "uri": item_locality_data[3]
                        }
                    else:
                        item_locality_object = {
                            "scheme":
                                payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                    'locality']['scheme'],
                            "id": payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'locality']['id'],
                            "description": payload_items_array[quantity_two]['deliveryAddress']['addressDetails'][
                                'locality']['description']
                        }

                    expected_items_array[quantity_two]['deliveryAddress']['addressDetails']['country'] = \
                        item_country_object
                    expected_items_array[quantity_two]['deliveryAddress']['addressDetails']['region'] = \
                        item_region_object
                    expected_items_array[quantity_two]['deliveryAddress']['addressDetails']['locality'] = \
                        item_locality_object
                    expected_items_array[quantity_two]['deliveryAddress']['streetAddress'] = \
                        payload_items_array['deliveryAddress']['streetAddress']
                    if "postalCode" in payload_items_array['deliveryAddress']:
                        expected_items_array[quantity_two]['deliveryAddress']['postalCode'] = \
                            payload_items_array['deliveryAddress']['postalCode']
                    else:
                        del expected_items_array[quantity_two]['deliveryAddress']['postalCode']
                else:
                    del expected_items_array[quantity_two]['deliveryAddress']

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

    def __prepare_expected_lots_array(self, payload_lots_array, release_lots_array):
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
            quantity_two = quantity_of_lot_object_into_release-1
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

    def ei_release_full_data_model(self, operation_date, release_date):

        release_id = GlobalClassCreateEi.actual_ei_release['releases'][0]['id']
        tender_id = GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['id']

        release = {
            "releases": [{
                "planning": {},
                "tender": {},
                "buyer": {},
                "parties": [{}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['planning'].update(self.constructor.release_planning_section())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['tender']['items'] = [{}]
        release['releases'][0]['tender']['items'][0].update(self.constructor.release_tender_item_object())
        release['releases'][0]['buyer'].update(self.constructor.release_buyer_section())
        release['releases'][0]['parties'][0].update(self.constructor.release_parties_section())

        del release['releases'][0]['purposeOfNotice']
        del release['releases'][0]['hasPreviousNotice']
        del release['releases'][0]['tender']['lots']
        del release['releases'][0]['tender']['procuringEntity']
        del release['releases'][0]['tender']['framework']
        del release['releases'][0]['tender']['dynamicPurchasingSystem']
        del release['releases'][0]['tender']['procedureOutsourcing']
        del release['releases'][0]['tender']['legalBasis']
        del release['releases'][0]['tender']['jointProcurement']
        del release['releases'][0]['tender']['electronicWorkflows']
        del release['releases'][0]['tender']['designContest']
        del release['releases'][0]['tender']['acceleratedProcedure']
        del release['releases'][0]['tender']['eligibilityCriteria']
        del release['releases'][0]['tender']['procurementMethod']
        del release['releases'][0]['tender']['procurementMethodDetails']
        del release['releases'][0]['tender']['value']
        del release['releases'][0]['tender']['requiresElectronicCatalogue']
        del release['releases'][0]['tender']['submissionMethodRationale']
        del release['releases'][0]['tender']['submissionMethodDetails']
        del release['releases'][0]['tender']['submissionMethod']
        del release['releases'][0]['tender']['hasEnquiries']
        del release['releases'][0]['tender']['tenderPeriod']
        del release['releases'][0]['tender']['lotGroups']
        del release['releases'][0]['planning']['budget']['budgetBreakdown']
        del release['releases'][0]['planning']['budget']['description']
        del release['releases'][0]['planning']['budget']['europeanUnionFunding']
        del release['releases'][0]['planning']['budget']['isEuropeanUnionFunded']
        del release['releases'][0]['planning']['budget']['verified']
        del release['releases'][0]['planning']['budget']['sourceEntity']
        del release['releases'][0]['planning']['budget']['project']
        del release['releases'][0]['planning']['budget']['projectID']
        del release['releases'][0]['planning']['budget']['uri']

        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in EI release: tender_id in EI release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in EI release: release_id in EI release must be uuid version 4")

        try:
            if GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "03" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "1" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "2" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "3" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "44" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "48":
                self.main_procurement_category = "goods"
            elif GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "45":
                self.main_procurement_category = "works"
            elif GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "5" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "6" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "7" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "8" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "92" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "98":
                self.main_procurement_category = "services"
        except ValueError:
            raise ValueError("main_procurement_category was not defined")

        try:
            buyer_country_data = get_value_from_country_csv(
                country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_country_object = {
                "scheme": buyer_country_data[2],
                "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                "description": buyer_country_data[1],
                "uri": buyer_country_data[3]
            }

            buyer_region_data = get_value_from_region_csv(
                region=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_region_object = {
                "scheme": buyer_region_data[2],
                "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                "description": buyer_region_data[1],
                "uri": buyer_region_data[3]
            }

            if GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                buyer_locality_data = get_value_from_locality_csv(
                    locality=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    region=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                    country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )
                buyer_locality_object = {
                    "scheme": buyer_locality_data[2],
                    "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": buyer_locality_data[1],
                    "uri": buyer_locality_data[3]
                }
            else:
                buyer_locality_object = {
                    "scheme": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality'][
                        'description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            tender_classification_id = get_value_from_classification_cpv_dictionary_xls(
                GlobalClassCreateEi.payload['tender']['classification']['id'], self.language)
        except ValueError:
            raise ValueError("Check tender.classification.id")

        expected_items_array = None
        try:
            for o in GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['items']:
                for i in o['classification']:
                    if i == "id":
                        try:
                            is_it_uuid(
                                uuid_to_test=o['classification']['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your item_id in EI release: "
                                             "item_id in EI release must be uuid version 4")
            list_of_item_classification_id = list()
            for o in GlobalClassCreateEi.payload['tender']['items']:
                for id_ in o['classification']:
                    if id_ == "id":
                        list_of_item_classification_id.append(id_)
            quantity = len(list_of_item_classification_id)
            while quantity > 0:
                try:
                    tender_item_country_data = get_value_from_country_csv(
                        country=GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['country']['id'],
                        language=self.language
                    )
                    tender_item_country_object = {
                        "scheme": tender_item_country_data[2],
                        "id": GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['country']['id'],
                        "description": tender_item_country_data[1],
                        "uri": tender_item_country_data[3]
                    }

                    tender_item_region_data = get_value_from_region_csv(
                        region=GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['region']['id'],
                        country=GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['country']['id'],
                        language=self.language
                    )
                    tender_item_region_object = {
                        "scheme": tender_item_region_data[2],
                        "id": GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['region']['id'],
                        "description": tender_item_region_data[1],
                        "uri": tender_item_region_data[3]
                    }

                    if GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                        'addressDetails']['locality']['scheme'] == "CUATM":
                        tender_item_locality_data = get_value_from_locality_csv(
                            locality=GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            region=GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['region']['id'],
                            country=GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['country']['id'],
                            language=self.language
                        )
                        tender_item_locality_object = {
                            "scheme": tender_item_locality_data[2],
                            "id": GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            "description": tender_item_locality_data[1],
                            "uri": tender_item_locality_data[3]
                        }
                    else:
                        tender_item_locality_object = {
                            "scheme": GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['scheme'],
                            "id": GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            "description":
                                GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                    'addressDetails']['locality']['description']
                        }
                except ValueError:
                    raise ValueError("Check 'tender.items.deliveryAddress.addressDetails' object")
                cpv_data = get_value_from_classification_cpv_dictionary_xls(
                    cpv=GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['classification']['id'],
                    language=self.language
                )
                cpvs_data = get_value_from_cpvs_dictionary_csv(
                    cpvs=GlobalClassCreateEi.payload['tender']['items'][quantity - 1][
                        'additionalClassifications'][0]['id'],
                    language=self.language
                )
                unit_data = get_value_from_classification_unit_dictionary_csv(
                    unit_id=GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['unit']['id'],
                    language=self.language
                )

                expected_items_array = GlobalClassCreateEi.payload['tender']['items']
                expected_items_array[quantity - 1]['id'] = \
                    GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['items'][quantity - 1]['id']
                expected_items_array[quantity - 1]['quantity'] = \
                    float(GlobalClassCreateEi.payload['tender']['items'][quantity - 1]['quantity'])
                expected_items_array[quantity - 1]['classification']['id'] = cpv_data[0]
                expected_items_array[quantity - 1]['classification']['scheme'] = "CPV"
                expected_items_array[quantity - 1]['classification']['description'] = cpv_data[1]
                expected_items_array[quantity - 1]['additionalClassifications'][0]['id'] = cpvs_data[0]
                expected_items_array[quantity - 1]['additionalClassifications'][0]['scheme'] = "CPVS"
                expected_items_array[quantity - 1]['additionalClassifications'][0]['description'] = cpvs_data[2]
                expected_items_array[quantity - 1]['unit']['id'] = unit_data[0]
                expected_items_array[quantity - 1]['unit']['name'] = unit_data[1]
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails']['country'] = \
                    tender_item_country_object
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails']['region'] = \
                    tender_item_region_object
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails']['locality'] = \
                    tender_item_locality_object
                quantity -= 1
        except ValueError:
            raise ValueError("Expected items array was not prepared")

        del release['releases'][0]['planning']['budget']['amount']

        release['uri'] = f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"

        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['id'] = f"{GlobalClassCreateEi.ei_ocid}-{release_id[29:42]}"
        release['releases'][0]['date'] = release_date
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = GlobalClassCreateEi.payload['tender']['title']
        release['releases'][0]['tender']['description'] = GlobalClassCreateEi.payload['tender']['description']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['tender']['items'] = expected_items_array
        release['releases'][0]['tender']['mainProcurementCategory'] = self.main_procurement_category
        release['releases'][0]['tender']['classification']['id'] = tender_classification_id[0]
        release['releases'][0]['tender']['classification']['description'] = tender_classification_id[1]
        release['releases'][0]['tender']['classification']['scheme'] = "CPV"
        release['releases'][0]['buyer']['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"
        release['releases'][0]['buyer']['name'] = GlobalClassCreateEi.payload['buyer']['name']
        release['releases'][0]['parties'][0]['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = GlobalClassCreateEi.payload['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['identifier']['uri'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['uri']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            GlobalClassCreateEi.payload['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['postalCode'] = \
            GlobalClassCreateEi.payload['buyer']['address']['postalCode']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = buyer_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = buyer_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = buyer_locality_object
        release['releases'][0]['parties'][0]['additionalIdentifiers'] = \
            GlobalClassCreateEi.payload['buyer']['additionalIdentifiers']
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['contactPoint']['faxNumber'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['faxNumber']
        release['releases'][0]['parties'][0]['contactPoint']['url'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['url']
        release['releases'][0]['parties'][0]['details'] = GlobalClassCreateEi.payload['buyer']['details']
        release['releases'][0]['parties'][0]['roles'][0] = "buyer"
        release['releases'][0]['planning']['budget']['id'] = tender_classification_id[0]
        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            GlobalClassCreateEi.payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            GlobalClassCreateEi.payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['rationale'] = GlobalClassCreateEi.payload['planning']['rationale']
        return release

    def ei_release_obligatory_data_model(self, operation_date, release_date):

        release_id = GlobalClassCreateEi.actual_ei_release['releases'][0]['id']
        tender_id = GlobalClassCreateEi.actual_ei_release['releases'][0]['tender']['id']

        release = {
            "releases": [{
                "planning": {},
                "tender": {},
                "buyer": {},
                "parties": [{}]
            }]
        }

        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['planning'].update(self.constructor.release_planning_section())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['buyer'].update(self.constructor.release_buyer_section())
        release['releases'][0]['parties'][0].update(self.constructor.release_parties_section())

        del release['releases'][0]['purposeOfNotice']
        del release['releases'][0]['hasPreviousNotice']
        del release['releases'][0]['tender']['lots']
        del release['releases'][0]['tender']['procuringEntity']
        del release['releases'][0]['tender']['framework']
        del release['releases'][0]['tender']['dynamicPurchasingSystem']
        del release['releases'][0]['tender']['procedureOutsourcing']
        del release['releases'][0]['tender']['legalBasis']
        del release['releases'][0]['tender']['jointProcurement']
        del release['releases'][0]['tender']['electronicWorkflows']
        del release['releases'][0]['tender']['designContest']
        del release['releases'][0]['tender']['acceleratedProcedure']
        del release['releases'][0]['tender']['eligibilityCriteria']
        del release['releases'][0]['tender']['procurementMethod']
        del release['releases'][0]['tender']['value']
        del release['releases'][0]['tender']['procurementMethodDetails']
        del release['releases'][0]['tender']['requiresElectronicCatalogue']
        del release['releases'][0]['tender']['submissionMethodRationale']
        del release['releases'][0]['tender']['submissionMethodDetails']
        del release['releases'][0]['tender']['submissionMethod']
        del release['releases'][0]['tender']['hasEnquiries']
        del release['releases'][0]['tender']['tenderPeriod']
        del release['releases'][0]['tender']['lotGroups']
        del release['releases'][0]['planning']['budget']['budgetBreakdown']
        del release['releases'][0]['planning']['budget']['description']
        del release['releases'][0]['planning']['budget']['europeanUnionFunding']
        del release['releases'][0]['planning']['budget']['isEuropeanUnionFunded']
        del release['releases'][0]['planning']['budget']['verified']
        del release['releases'][0]['planning']['budget']['sourceEntity']
        del release['releases'][0]['planning']['budget']['project']
        del release['releases'][0]['planning']['budget']['projectID']
        del release['releases'][0]['planning']['budget']['uri']

        try:
            is_it_uuid(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in EI release: tender_id in EI release must be uuid version 4")

        try:
            is_it_uuid(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in EI release: release_id in EI release must be uuid version 4")

        try:

            if GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "03" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "1" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "2" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "3" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "44" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "48":
                self.main_procurement_category = "goods"
            elif GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "45":
                self.main_procurement_category = "works"
            elif GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "5" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "6" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "7" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0] == "8" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "92" or \
                    GlobalClassCreateEi.payload['tender']['classification']['id'][0:2] == "98":
                self.main_procurement_category = "services"
        except ValueError:
            raise ValueError("main_procurement_category was not defined")

        try:
            buyer_country_data = get_value_from_country_csv(
                country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_country_object = {
                "scheme": buyer_country_data[2],
                "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                "description": buyer_country_data[1],
                "uri": buyer_country_data[3]
            }

            buyer_region_data = get_value_from_region_csv(
                region=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            buyer_region_object = {
                "scheme": buyer_region_data[2],
                "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                "description": buyer_region_data[1],
                "uri": buyer_region_data[3]
            }

            if GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                buyer_locality_data = get_value_from_locality_csv(
                    locality=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    region=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['region']['id'],
                    country=GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )
                buyer_locality_object = {
                    "scheme": buyer_locality_data[2],
                    "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": buyer_locality_data[1],
                    "uri": buyer_locality_data[3]
                }
            else:
                buyer_locality_object = {
                    "scheme": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": GlobalClassCreateEi.payload['buyer']['address']['addressDetails']['locality'][
                        'description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            tender_classification_id = get_value_from_classification_cpv_dictionary_xls(
                GlobalClassCreateEi.payload['tender']['classification']['id'], self.language)
        except ValueError:
            raise ValueError("Check tender.classification.id")

        del release['releases'][0]['planning']['budget']['amount']
        del release['releases'][0]['tender']['description']
        del release['releases'][0]['tender']['items']
        del release['releases'][0]['parties'][0]['identifier']['uri']
        del release['releases'][0]['parties'][0]['address']['postalCode']
        del release['releases'][0]['parties'][0]['additionalIdentifiers']
        del release['releases'][0]['parties'][0]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][0]['contactPoint']['url']
        del release['releases'][0]['parties'][0]['details']
        del release['releases'][0]['planning']['rationale']
        release['uri'] = f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"

        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['id'] = f"{GlobalClassCreateEi.ei_ocid}-{release_id[29:42]}"
        release['releases'][0]['date'] = release_date
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = GlobalClassCreateEi.payload['tender']['title']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['tender']['mainProcurementCategory'] = self.main_procurement_category
        release['releases'][0]['tender']['classification']['id'] = tender_classification_id[0]
        release['releases'][0]['tender']['classification']['description'] = tender_classification_id[1]
        release['releases'][0]['tender']['classification']['scheme'] = "CPV"
        release['releases'][0]['buyer']['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"
        release['releases'][0]['buyer']['name'] = GlobalClassCreateEi.payload['buyer']['name']
        release['releases'][0]['parties'][0]['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = GlobalClassCreateEi.payload['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            GlobalClassCreateEi.payload['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            GlobalClassCreateEi.payload['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = buyer_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = buyer_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = buyer_locality_object
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            GlobalClassCreateEi.payload['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['roles'][0] = "buyer"
        release['releases'][0]['planning']['budget']['id'] = tender_classification_id[0]
        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            GlobalClassCreateEi.payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            GlobalClassCreateEi.payload['planning']['budget']['period']['endDate']
        return release

    def ei_tender_items_array_release(self, payload, actual_items_array):
        expected_items_array = None
        try:
            for o in actual_items_array:
                for i in o:
                    if i == "id":
                        try:
                            is_it_uuid(
                                uuid_to_test=o['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your item_id in EI release: "
                                             "item_id in EI release must be uuid version 4")
            list_of_item_classification_id = list()
            for o in payload['tender']['items']:
                for id_ in o['classification']:
                    if id_ == "id":
                        list_of_item_classification_id.append(id_)
            quantity = len(list_of_item_classification_id)
            while quantity > 0:
                try:
                    tender_item_country_data = get_value_from_country_csv(
                        country=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['country']['id'],
                        language=self.language
                    )
                    tender_item_country_object = {
                        "scheme": tender_item_country_data[2],
                        "id": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['country']['id'],
                        "description": tender_item_country_data[1],
                        "uri": tender_item_country_data[3]
                    }

                    tender_item_region_data = get_value_from_region_csv(
                        region=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['region']['id'],
                        country=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['country']['id'],
                        language=self.language
                    )
                    tender_item_region_object = {
                        "scheme": tender_item_region_data[2],
                        "id": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                            'addressDetails']['region']['id'],
                        "description": tender_item_region_data[1],
                        "uri": tender_item_region_data[3]
                    }

                    if payload['tender']['items'][quantity - 1]['deliveryAddress'][
                        'addressDetails']['locality']['scheme'] == "CUATM":
                        tender_item_locality_data = get_value_from_locality_csv(
                            locality=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            region=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['region']['id'],
                            country=payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['country']['id'],
                            language=self.language
                        )
                        tender_item_locality_object = {
                            "scheme": tender_item_locality_data[2],
                            "id": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            "description": tender_item_locality_data[1],
                            "uri": tender_item_locality_data[3]
                        }
                    else:
                        tender_item_locality_object = {
                            "scheme": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['scheme'],
                            "id": payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                'addressDetails']['locality']['id'],
                            "description":
                                payload['tender']['items'][quantity - 1]['deliveryAddress'][
                                    'addressDetails']['locality']['description']
                        }
                except ValueError:
                    raise ValueError("Check 'tender.items.deliveryAddress.addressDetails' object")
                cpv_data = get_value_from_classification_cpv_dictionary_xls(
                    cpv=payload['tender']['items'][quantity - 1]['classification']['id'],
                    language=self.language
                )
                cpvs_data = get_value_from_cpvs_dictionary_csv(
                    cpvs=payload['tender']['items'][quantity - 1][
                        'additionalClassifications'][0]['id'],
                    language=self.language
                )
                unit_data = get_value_from_classification_unit_dictionary_csv(
                    unit_id=payload['tender']['items'][quantity - 1]['unit']['id'],
                    language=self.language
                )

                expected_items_array = payload['tender']['items']
                expected_items_array[quantity - 1]['id'] = \
                    actual_items_array[quantity - 1]['id']
                expected_items_array[quantity - 1]['quantity'] = float(
                    payload['tender']['items'][quantity - 1]['quantity'])
                expected_items_array[quantity - 1]['classification']['id'] = cpv_data[0]
                expected_items_array[quantity - 1]['classification']['scheme'] = "CPV"
                expected_items_array[quantity - 1]['classification']['description'] = cpv_data[1]
                expected_items_array[quantity - 1]['additionalClassifications'][0]['id'] = cpvs_data[0]
                expected_items_array[quantity - 1]['additionalClassifications'][0]['scheme'] = "CPVS"
                expected_items_array[quantity - 1]['additionalClassifications'][0]['description'] = cpvs_data[2]
                expected_items_array[quantity - 1]['unit']['id'] = unit_data[0]
                expected_items_array[quantity - 1]['unit']['name'] = unit_data[1]
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails'][
                    'country'] = tender_item_country_object
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails'][
                    'region'] = tender_item_region_object
                expected_items_array[quantity - 1]['deliveryAddress']['addressDetails'][
                    'locality'] = tender_item_locality_object
                quantity -= 1
        except ValueError:
            raise ValueError("Expected items array was not prepared")
        return expected_items_array

    def fs_release_full_data_model_own_money_payer_id_is_not_equal_funder_id(self, operation_date, release_date):

        release_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['id']
        tender_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['tender']['id']
        related_processes_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['relatedProcesses'][0]['id']

        release = {
            "releases": [{
                "tender": {},
                "parties": [{}, {}],
                "planning": {},
                "relatedProcesses": [{}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['parties'][0].update(self.constructor.release_parties_section())
        release['releases'][0]['parties'][1].update(self.constructor.release_parties_section())
        release['releases'][0]['planning'].update(self.constructor.release_planning_section())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['planning']['budget']['budgetBreakdown']
        del release['releases'][0]['purposeOfNotice']
        del release['releases'][0]['hasPreviousNotice']
        del release['releases'][0]['tender']['lots']
        del release['releases'][0]['tender']['procuringEntity']
        del release['releases'][0]['tender']['framework']
        del release['releases'][0]['tender']['dynamicPurchasingSystem']
        del release['releases'][0]['tender']['procedureOutsourcing']
        del release['releases'][0]['tender']['legalBasis']
        del release['releases'][0]['tender']['jointProcurement']
        del release['releases'][0]['tender']['electronicWorkflows']
        del release['releases'][0]['tender']['designContest']
        del release['releases'][0]['tender']['acceleratedProcedure']
        del release['releases'][0]['tender']['eligibilityCriteria']
        del release['releases'][0]['tender']['procurementMethod']
        del release['releases'][0]['tender']['value']
        del release['releases'][0]['tender']['procurementMethodDetails']
        del release['releases'][0]['tender']['requiresElectronicCatalogue']
        del release['releases'][0]['tender']['submissionMethodRationale']
        del release['releases'][0]['tender']['submissionMethodDetails']
        del release['releases'][0]['tender']['submissionMethod']
        del release['releases'][0]['tender']['hasEnquiries']
        del release['releases'][0]['tender']['tenderPeriod']
        del release['releases'][0]['tender']['lotGroups']
        del release['releases'][0]['tender']['title']
        del release['releases'][0]['tender']['description']
        del release['releases'][0]['tender']['mainProcurementCategory']
        del release['releases'][0]['tender']['classification']
        del release['releases'][0]['tender']['items']
        del release['releases'][0]['parties'][0]['details']
        del release['releases'][0]['parties'][1]['details']

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

        try:
            funder_country_data = get_value_from_country_csv(
                country=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            funder_country_object = {
                "scheme": funder_country_data[2],
                "id": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['country']['id'],
                "description": funder_country_data[1],
                "uri": funder_country_data[3]
            }

            funder_region_data = get_value_from_region_csv(
                region=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['region']['id'],
                country=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            funder_region_object = {
                "scheme": funder_region_data[2],
                "id": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['region']['id'],
                "description": funder_region_data[1],
                "uri": funder_region_data[3]
            }

            if GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                funder_locality_data = get_value_from_locality_csv(
                    locality=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['id'],
                    region=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['region']['id'],
                    country=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )

                funder_locality_object = {
                    "scheme": funder_locality_data[2],
                    "id": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": funder_locality_data[1],
                    "uri": funder_locality_data[3]
                }
            else:
                funder_locality_object = {
                    "scheme": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality'][
                        'description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            payer_country_data = get_value_from_country_csv(
                country=
                GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            payer_country_object = {
                "scheme": payer_country_data[2],
                "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": payer_country_data[1],
                "uri": payer_country_data[3]
            }

            payer_region_data = get_value_from_region_csv(
                region=GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                country=
                GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            payer_region_object = {
                "scheme": payer_region_data[2],
                "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                "description": payer_region_data[1],
                "uri": payer_region_data[3]
            }

            if GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                'scheme'] == "CUATM":
                payer_locality_data = get_value_from_locality_csv(
                    locality=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'id'],
                    region=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                        'id'],
                    country=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                        'id'],
                    language=self.language
                )
                payer_locality_object = {
                    "scheme": payer_locality_data[2],
                    "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description": payer_locality_data[1],
                    "uri": payer_locality_data[3]
                }
            else:
                payer_locality_object = {
                    "scheme":
                        GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'scheme'],
                    "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description":
                        GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        release['uri'] = f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateFs.fs_id}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['id'] = f"{GlobalClassCreateFs.fs_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = release_date
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "active"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['parties'][0]['id'] = \
            f"{GlobalClassCreateFs.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateFs.payload['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = GlobalClassCreateFs.payload['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            GlobalClassCreateFs.payload['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            GlobalClassCreateFs.payload['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            GlobalClassCreateFs.payload['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['identifier']['uri'] = \
            GlobalClassCreateFs.payload['buyer']['identifier']['uri']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            GlobalClassCreateFs.payload['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['postalCode'] = \
            GlobalClassCreateFs.payload['buyer']['address']['postalCode']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = funder_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = funder_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = funder_locality_object
        release['releases'][0]['parties'][0]['additionalIdentifiers'] = \
            GlobalClassCreateFs.payload['buyer']['additionalIdentifiers']
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            GlobalClassCreateFs.payload['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            GlobalClassCreateFs.payload['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            GlobalClassCreateFs.payload['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['contactPoint']['faxNumber'] = \
            GlobalClassCreateFs.payload['buyer']['contactPoint']['faxNumber']
        release['releases'][0]['parties'][0]['contactPoint']['url'] = \
            GlobalClassCreateFs.payload['buyer']['contactPoint']['url']
        release['releases'][0]['parties'][0]['roles'][0] = "funder"

        release['releases'][0]['parties'][1]['id'] = \
            f"{GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][1]['name'] = GlobalClassCreateFs.payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][1]['identifier']['scheme'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['scheme']
        release['releases'][0]['parties'][1]['identifier']['id'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['id']
        release['releases'][0]['parties'][1]['identifier']['legalName'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['legalName']
        release['releases'][0]['parties'][1]['identifier']['uri'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['uri']
        release['releases'][0]['parties'][1]['address']['streetAddress'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][1]['address']['postalCode'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['postalCode']
        release['releases'][0]['parties'][1]['address']['addressDetails']['country'] = payer_country_object
        release['releases'][0]['parties'][1]['address']['addressDetails']['region'] = payer_region_object
        release['releases'][0]['parties'][1]['address']['addressDetails']['locality'] = payer_locality_object
        release['releases'][0]['parties'][1]['additionalIdentifiers'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['additionalIdentifiers']
        release['releases'][0]['parties'][1]['contactPoint']['name'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['name']
        release['releases'][0]['parties'][1]['contactPoint']['telephone'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['telephone']
        release['releases'][0]['parties'][1]['contactPoint']['email'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['email']
        release['releases'][0]['parties'][1]['contactPoint']['faxNumber'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['faxNumber']
        release['releases'][0]['parties'][1]['contactPoint']['url'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['url']
        release['releases'][0]['parties'][1]['roles'][0] = "payer"

        release['releases'][0]['planning']['budget']['id'] = GlobalClassCreateFs.payload['planning']['budget']['id']
        release['releases'][0]['planning']['budget']['description'] = GlobalClassCreateFs.payload['planning']['budget'][
            'description']
        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['projectIdentifier'] = \
            GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding']['projectIdentifier']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['projectName'] = \
            GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding']['projectName']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['uri'] = \
            GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding']['uri']
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = True
        release['releases'][0]['planning']['budget']['verified'] = True
        release['releases'][0]['planning']['budget']['sourceEntity']['id'] = \
            f"{GlobalClassCreateFs.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateFs.payload['buyer']['identifier']['id']}"
        release['releases'][0]['planning']['budget']['sourceEntity']['name'] = GlobalClassCreateFs.payload['buyer'][
            'name']
        release['releases'][0]['planning']['budget']['project'] = GlobalClassCreateFs.payload['planning']['budget'][
            'project']
        release['releases'][0]['planning']['budget']['projectID'] = \
            GlobalClassCreateFs.payload['planning']['budget']['projectID']
        release['releases'][0]['planning']['budget']['uri'] = GlobalClassCreateFs.payload['planning']['budget']['uri']
        release['releases'][0]['planning']['rationale'] = GlobalClassCreateFs.payload['planning']['rationale']

        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        return release

    def fs_release_full_data_model_treasury_money(self, operation_date, release_date):

        release_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['id']
        tender_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['tender']['id']
        related_processes_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['relatedProcesses'][0]['id']
        release = {
            "releases": [{
                "tender": {},
                "parties": [{}],
                "planning": {},
                "relatedProcesses": [{}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['parties'][0].update(self.constructor.release_parties_section())
        release['releases'][0]['planning'].update(self.constructor.release_planning_section())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['planning']['budget']['budgetBreakdown']
        del release['releases'][0]['purposeOfNotice']
        del release['releases'][0]['hasPreviousNotice']
        del release['releases'][0]['tender']['lots']
        del release['releases'][0]['tender']['procuringEntity']
        del release['releases'][0]['tender']['framework']
        del release['releases'][0]['tender']['dynamicPurchasingSystem']
        del release['releases'][0]['tender']['procedureOutsourcing']
        del release['releases'][0]['tender']['legalBasis']
        del release['releases'][0]['tender']['jointProcurement']
        del release['releases'][0]['tender']['electronicWorkflows']
        del release['releases'][0]['tender']['designContest']
        del release['releases'][0]['tender']['acceleratedProcedure']
        del release['releases'][0]['tender']['eligibilityCriteria']
        del release['releases'][0]['tender']['procurementMethod']
        del release['releases'][0]['tender']['procurementMethodDetails']
        del release['releases'][0]['tender']['value']
        del release['releases'][0]['tender']['requiresElectronicCatalogue']
        del release['releases'][0]['tender']['submissionMethodRationale']
        del release['releases'][0]['tender']['submissionMethodDetails']
        del release['releases'][0]['tender']['submissionMethod']
        del release['releases'][0]['tender']['hasEnquiries']
        del release['releases'][0]['tender']['tenderPeriod']
        del release['releases'][0]['tender']['lotGroups']
        del release['releases'][0]['tender']['title']
        del release['releases'][0]['tender']['description']
        del release['releases'][0]['tender']['mainProcurementCategory']
        del release['releases'][0]['tender']['classification']
        del release['releases'][0]['tender']['items']
        del release['releases'][0]['parties'][0]['details']

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

        try:
            payer_country_data = get_value_from_country_csv(
                country=
                GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            payer_country_object = {
                "scheme": payer_country_data[2],
                "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": payer_country_data[1],
                "uri": payer_country_data[3]
            }

            payer_region_data = get_value_from_region_csv(
                region=GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                country=
                GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            payer_region_object = {
                "scheme": payer_region_data[2],
                "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                "description": payer_region_data[1],
                "uri": payer_region_data[3]
            }

            if GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                'scheme'] == "CUATM":
                payer_locality_data = get_value_from_locality_csv(
                    locality=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'id'],
                    region=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                        'id'],
                    country=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                        'id'],
                    language=self.language
                )
                payer_locality_object = {
                    "scheme": payer_locality_data[2],
                    "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description": payer_locality_data[1],
                    "uri": payer_locality_data[3]
                }
            else:
                payer_locality_object = {
                    "scheme":
                        GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'scheme'],
                    "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description":
                        GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        release['uri'] = f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateFs.fs_id}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['id'] = f"{GlobalClassCreateFs.fs_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = release_date
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"

        release['releases'][0]['parties'][0]['id'] = \
            f"{GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = GlobalClassCreateFs.payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['legalName']
        release['releases'][0]['parties'][0]['identifier']['uri'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['uri']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['postalCode'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['postalCode']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = payer_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = payer_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = payer_locality_object
        release['releases'][0]['parties'][0]['additionalIdentifiers'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['additionalIdentifiers']
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['email']
        release['releases'][0]['parties'][0]['contactPoint']['faxNumber'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['faxNumber']
        release['releases'][0]['parties'][0]['contactPoint']['url'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['url']
        release['releases'][0]['parties'][0]['roles'][0] = "payer"

        release['releases'][0]['planning']['budget']['id'] = GlobalClassCreateFs.payload['planning']['budget']['id']
        release['releases'][0]['planning']['budget']['description'] = GlobalClassCreateFs.payload['planning']['budget'][
            'description']
        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['projectIdentifier'] = \
            GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding']['projectIdentifier']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['projectName'] = \
            GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding']['projectName']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['uri'] = \
            GlobalClassCreateFs.payload['planning']['budget']['europeanUnionFunding']['uri']
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = True
        release['releases'][0]['planning']['budget']['verified'] = False
        release['releases'][0]['planning']['budget']['sourceEntity']['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
        f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"
        release['releases'][0]['planning']['budget']['sourceEntity']['name'] = \
            f"{GlobalClassCreateEi.payload['buyer']['name']}"
        release['releases'][0]['planning']['budget']['project'] = GlobalClassCreateFs.payload['planning']['budget'][
            'project']
        release['releases'][0]['planning']['budget']['projectID'] = \
            GlobalClassCreateFs.payload['planning']['budget']['projectID']
        release['releases'][0]['planning']['budget']['uri'] = GlobalClassCreateFs.payload['planning']['budget']['uri']
        release['releases'][0]['planning']['rationale'] = GlobalClassCreateFs.payload['planning']['rationale']

        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        return release

    def fs_release_obligatory_data_model_treasury_money(self, operation_date, release_date):

        release_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['id']
        tender_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['tender']['id']
        related_processes_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['relatedProcesses'][0]['id']

        release = {
            "releases": [{
                "tender": {},
                "parties": [{}],
                "planning": {},
                "relatedProcesses": [{}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['parties'][0].update(self.constructor.release_parties_section())
        release['releases'][0]['planning'].update(self.constructor.release_planning_section())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['purposeOfNotice']
        del release['releases'][0]['hasPreviousNotice']
        del release['releases'][0]['tender']['lots']
        del release['releases'][0]['tender']['framework']
        del release['releases'][0]['tender']['procuringEntity']
        del release['releases'][0]['tender']['dynamicPurchasingSystem']
        del release['releases'][0]['tender']['procedureOutsourcing']
        del release['releases'][0]['tender']['legalBasis']
        del release['releases'][0]['tender']['jointProcurement']
        del release['releases'][0]['tender']['electronicWorkflows']
        del release['releases'][0]['tender']['designContest']
        del release['releases'][0]['tender']['acceleratedProcedure']
        del release['releases'][0]['tender']['eligibilityCriteria']
        del release['releases'][0]['tender']['procurementMethod']
        del release['releases'][0]['tender']['value']
        del release['releases'][0]['tender']['procurementMethodDetails']
        del release['releases'][0]['tender']['requiresElectronicCatalogue']
        del release['releases'][0]['tender']['submissionMethodRationale']
        del release['releases'][0]['tender']['submissionMethodDetails']
        del release['releases'][0]['tender']['submissionMethod']
        del release['releases'][0]['tender']['hasEnquiries']
        del release['releases'][0]['tender']['tenderPeriod']
        del release['releases'][0]['tender']['lotGroups']
        del release['releases'][0]['tender']['title']
        del release['releases'][0]['tender']['description']
        del release['releases'][0]['tender']['mainProcurementCategory']
        del release['releases'][0]['tender']['classification']
        del release['releases'][0]['tender']['items']
        del release['releases'][0]['parties'][0]['identifier']['uri']
        del release['releases'][0]['parties'][0]['additionalIdentifiers']
        del release['releases'][0]['parties'][0]['address']['postalCode']
        del release['releases'][0]['parties'][0]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][0]['contactPoint']['url']
        del release['releases'][0]['parties'][0]['details']
        del release['releases'][0]['planning']['budget']['budgetBreakdown']
        del release['releases'][0]['planning']['budget']['id']
        del release['releases'][0]['planning']['budget']['description']
        del release['releases'][0]['planning']['budget']['europeanUnionFunding']
        del release['releases'][0]['planning']['budget']['project']
        del release['releases'][0]['planning']['budget']['projectID']
        del release['releases'][0]['planning']['budget']['uri']
        del release['releases'][0]['planning']['rationale']

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

        try:
            payer_country_data = get_value_from_country_csv(
                country=
                GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            payer_country_object = {
                "scheme": payer_country_data[2],
                "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": payer_country_data[1],
                "uri": payer_country_data[3]
            }

            payer_region_data = get_value_from_region_csv(
                region=GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                country=
                GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            payer_region_object = {
                "scheme": payer_region_data[2],
                "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                "description": payer_region_data[1],
                "uri": payer_region_data[3]
            }

            if GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                'scheme'] == "CUATM":
                payer_locality_data = get_value_from_locality_csv(
                    locality=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'id'],
                    region=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                        'id'],
                    country=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                        'id'],
                    language=self.language
                )
                payer_locality_object = {
                    "scheme": payer_locality_data[2],
                    "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description": payer_locality_data[1],
                    "uri": payer_locality_data[3]
                }
            else:
                payer_locality_object = {
                    "scheme":
                        GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'scheme'],
                    "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description":
                        GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        release['uri'] = f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateFs.fs_id}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['id'] = f"{GlobalClassCreateFs.fs_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = release_date
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"

        release['releases'][0]['parties'][0]['id'] = \
            f"{GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = GlobalClassCreateFs.payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['legalName']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = payer_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = payer_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = payer_locality_object
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['email']
        release['releases'][0]['parties'][0]['roles'][0] = "payer"

        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = False
        release['releases'][0]['planning']['budget']['verified'] = False
        release['releases'][0]['planning']['budget']['sourceEntity']['id'] = \
            f"{GlobalClassCreateEi.payload['buyer']['identifier']['scheme']}-"
        f"{GlobalClassCreateEi.payload['buyer']['identifier']['id']}"

        release['releases'][0]['planning']['budget']['sourceEntity']['name'] = GlobalClassCreateEi.payload['buyer'][
            'name']

        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        return release

    def fs_release_obligatory_data_model_own_money_payer_id_is_not_equal_funder_id(self, operation_date, release_date):
        release_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['id']
        tender_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['tender']['id']
        related_processes_id = GlobalClassCreateFs.actual_fs_release['releases'][0]['relatedProcesses'][0]['id']

        release = {
            "releases": [{
                "tender": {},
                "parties": [{}, {}],
                "planning": {},
                "relatedProcesses": [{}]
            }]
        }
        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['parties'][0].update(self.constructor.release_parties_section())
        release['releases'][0]['parties'][1].update(self.constructor.release_parties_section())
        release['releases'][0]['planning'].update(self.constructor.release_planning_section())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['purposeOfNotice']
        del release['releases'][0]['hasPreviousNotice']
        del release['releases'][0]['tender']['lots']
        del release['releases'][0]['tender']['procuringEntity']
        del release['releases'][0]['tender']['framework']
        del release['releases'][0]['tender']['dynamicPurchasingSystem']
        del release['releases'][0]['tender']['procedureOutsourcing']
        del release['releases'][0]['tender']['legalBasis']
        del release['releases'][0]['tender']['jointProcurement']
        del release['releases'][0]['tender']['electronicWorkflows']
        del release['releases'][0]['tender']['designContest']
        del release['releases'][0]['tender']['acceleratedProcedure']
        del release['releases'][0]['tender']['eligibilityCriteria']
        del release['releases'][0]['tender']['procurementMethod']
        del release['releases'][0]['tender']['procurementMethodDetails']
        del release['releases'][0]['tender']['value']
        del release['releases'][0]['tender']['requiresElectronicCatalogue']
        del release['releases'][0]['tender']['submissionMethodRationale']
        del release['releases'][0]['tender']['submissionMethodDetails']
        del release['releases'][0]['tender']['submissionMethod']
        del release['releases'][0]['tender']['hasEnquiries']
        del release['releases'][0]['tender']['tenderPeriod']
        del release['releases'][0]['tender']['lotGroups']
        del release['releases'][0]['tender']['title']
        del release['releases'][0]['tender']['description']
        del release['releases'][0]['tender']['mainProcurementCategory']
        del release['releases'][0]['tender']['classification']
        del release['releases'][0]['tender']['items']
        del release['releases'][0]['parties'][0]['details']
        del release['releases'][0]['parties'][1]['details']
        del release['releases'][0]['parties'][0]['identifier']['uri']
        del release['releases'][0]['parties'][0]['additionalIdentifiers']
        del release['releases'][0]['parties'][0]['address']['postalCode']
        del release['releases'][0]['parties'][0]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][0]['contactPoint']['url']
        del release['releases'][0]['parties'][1]['identifier']['uri']
        del release['releases'][0]['parties'][1]['additionalIdentifiers']
        del release['releases'][0]['parties'][1]['address']['postalCode']
        del release['releases'][0]['parties'][1]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][1]['contactPoint']['url']
        del release['releases'][0]['planning']['budget']['budgetBreakdown']
        del release['releases'][0]['planning']['budget']['id']
        del release['releases'][0]['planning']['budget']['description']
        del release['releases'][0]['planning']['budget']['europeanUnionFunding']
        del release['releases'][0]['planning']['budget']['project']
        del release['releases'][0]['planning']['budget']['projectID']
        del release['releases'][0]['planning']['budget']['uri']
        del release['releases'][0]['planning']['rationale']

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

        try:
            funder_country_data = get_value_from_country_csv(
                country=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            funder_country_object = {
                "scheme": funder_country_data[2],
                "id": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['country']['id'],
                "description": funder_country_data[1],
                "uri": funder_country_data[3]
            }

            funder_region_data = get_value_from_region_csv(
                region=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['region']['id'],
                country=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            funder_region_object = {
                "scheme": funder_region_data[2],
                "id": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['region']['id'],
                "description": funder_region_data[1],
                "uri": funder_region_data[3]
            }

            if GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                funder_locality_data = get_value_from_locality_csv(
                    locality=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['id'],
                    region=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['region']['id'],
                    country=GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )

                funder_locality_object = {
                    "scheme": funder_locality_data[2],
                    "id": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": funder_locality_data[1],
                    "uri": funder_locality_data[3]
                }
            else:
                funder_locality_object = {
                    "scheme": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": GlobalClassCreateFs.payload['buyer']['address']['addressDetails']['locality'][
                        'description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            payer_country_data = get_value_from_country_csv(
                country=
                GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            payer_country_object = {
                "scheme": payer_country_data[2],
                "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": payer_country_data[1],
                "uri": payer_country_data[3]
            }

            payer_region_data = get_value_from_region_csv(
                region=GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                country=
                GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                language=self.language
            )

            payer_region_object = {
                "scheme": payer_region_data[2],
                "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                "description": payer_region_data[1],
                "uri": payer_region_data[3]
            }

            if GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                'scheme'] == "CUATM":
                payer_locality_data = get_value_from_locality_csv(
                    locality=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'id'],
                    region=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                        'id'],
                    country=
                    GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                        'id'],
                    language=self.language
                )
                payer_locality_object = {
                    "scheme": payer_locality_data[2],
                    "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description": payer_locality_data[1],
                    "uri": payer_locality_data[3]
                }
            else:
                payer_locality_object = {
                    "scheme":
                        GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'scheme'],
                    "id": GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality'][
                        'id'],
                    "description":
                        GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality'][
                            'description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        release['uri'] = f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateFs.fs_id}"
        release['version'] = "1.1"
        release['extensions'][
            0] = "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json"
        release['extensions'][
            1] = "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"
        release['publisher']['name'] = "M-Tender"
        release['publisher']['uri'] = "https://www.mtender.gov.md"
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = GlobalClassCreateFs.fs_id
        release['releases'][0]['id'] = f"{GlobalClassCreateFs.fs_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = release_date
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "active"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['parties'][0]['id'] = \
            f"{GlobalClassCreateFs.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateFs.payload['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = GlobalClassCreateFs.payload['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            GlobalClassCreateFs.payload['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            GlobalClassCreateFs.payload['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            GlobalClassCreateFs.payload['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            GlobalClassCreateFs.payload['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = funder_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = funder_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = funder_locality_object
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            GlobalClassCreateFs.payload['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            GlobalClassCreateFs.payload['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            GlobalClassCreateFs.payload['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['roles'][0] = "funder"

        release['releases'][0]['parties'][1]['id'] = \
            f"{GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][1]['name'] = GlobalClassCreateFs.payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][1]['identifier']['scheme'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['scheme']
        release['releases'][0]['parties'][1]['identifier']['id'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['id']
        release['releases'][0]['parties'][1]['identifier']['legalName'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['identifier']['legalName']
        release['releases'][0]['parties'][1]['address']['streetAddress'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][1]['address']['addressDetails']['country'] = payer_country_object
        release['releases'][0]['parties'][1]['address']['addressDetails']['region'] = payer_region_object
        release['releases'][0]['parties'][1]['address']['addressDetails']['locality'] = payer_locality_object
        release['releases'][0]['parties'][1]['contactPoint']['name'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['name']
        release['releases'][0]['parties'][1]['contactPoint']['telephone'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['telephone']
        release['releases'][0]['parties'][1]['contactPoint']['email'] = \
            GlobalClassCreateFs.payload['tender']['procuringEntity']['contactPoint']['email']
        release['releases'][0]['parties'][1]['roles'][0] = "payer"

        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            GlobalClassCreateFs.payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            GlobalClassCreateFs.payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = False
        release['releases'][0]['planning']['budget']['verified'] = True
        release['releases'][0]['planning']['budget']['sourceEntity']['id'] = \
            f"{GlobalClassCreateFs.payload['buyer']['identifier']['scheme']}-" \
            f"{GlobalClassCreateFs.payload['buyer']['identifier']['id']}"
        release['releases'][0]['planning']['budget']['sourceEntity']['name'] = \
            GlobalClassCreateFs.payload['buyer']['name']
        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreateEi.ei_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_budget_url}/{GlobalClassCreateEi.ei_ocid}/{GlobalClassCreateEi.ei_ocid}"
        return release

    def pn_release_obligatory_data_model_without_lots_and_items_based_on_one_fs(
            self, operation_date, release_date):
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
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['tender']['lots']
        del release['releases'][0]['tender']['procuringEntity']
        del release['releases'][0]['tender']['framework']
        del release['releases'][0]['tender']['dynamicPurchasingSystem']
        del release['releases'][0]['tender']['procedureOutsourcing']
        del release['releases'][0]['tender']['legalBasis']
        del release['releases'][0]['tender']['jointProcurement']
        del release['releases'][0]['tender']['electronicWorkflows']
        del release['releases'][0]['tender']['designContest']
        del release['releases'][0]['tender']['acceleratedProcedure']
        del release['releases'][0]['tender']['eligibilityCriteria']
        del release['releases'][0]['tender']['procurementMethod']
        del release['releases'][0]['tender']['procurementMethodDetails']
        del release['releases'][0]['tender']['mainProcurementCategory']
        del release['releases'][0]['tender']['classification']
        del release['releases'][0]['tender']['items']
        del release['releases'][0]['tender']['value']

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
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['id'] = f"{GlobalClassCreatePn.pn_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = release_date
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

    def ms_release_obligatory_data_model_with_three_parties_object(
            self, operation_date, release_date):
        release_id = GlobalClassCreatePn.actual_ms_release['releases'][0]['id']
        tender_id = GlobalClassCreatePn.actual_ms_release['releases'][0]['tender']['id']
        related_processes_id_first = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][0]['id']
        related_processes_id_second = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][1]['id']
        related_processes_id_third = GlobalClassCreatePn.actual_ms_release['releases'][0]['relatedProcesses'][2]['id']

        release = {
            "releases": [{
                "tender": {},
                "planning": {},
                "parties": [{}, {}, {}],
                "relatedProcesses": [{}, {}, {}]
            }]
        }

        release.update(self.constructor.metadata_release())
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['tender']['procuringEntity'].update(self.constructor.release_procuring_entity_section())
        release['releases'][0]['planning'].update(self.constructor.release_planning_section())
        release['releases'][0]['planning']['budget']['budgetBreakdown'] = [{}]
        release['releases'][0]['planning']['budget']['budgetBreakdown'][0].update(
            self.constructor.release_planning_budget_budget_breakdown_obj())
        release['releases'][0]['parties'][0].update(self.constructor.release_parties_section())
        release['releases'][0]['parties'][1].update(self.constructor.release_parties_section())
        release['releases'][0]['parties'][2].update(self.constructor.release_parties_section())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][1].update(self.constructor.release_related_processes_section())
        release['releases'][0]['relatedProcesses'][2].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['hasPreviousNotice']
        del release['releases'][0]['purposeOfNotice']
        del release['releases'][0]['tender']['lots']
        del release['releases'][0]['tender']['submissionMethodDetails']
        del release['releases'][0]['tender']['lotGroups']
        del release['releases'][0]['tender']['tenderPeriod']
        del release['releases'][0]['tender']['submissionMethod']
        del release['releases'][0]['tender']['submissionMethodRationale']
        del release['releases'][0]['tender']['requiresElectronicCatalogue']
        del release['releases'][0]['tender']['items']
        del release['releases'][0]['planning']['budget']['id']
        del release['releases'][0]['planning']['budget']['period']
        del release['releases'][0]['planning']['budget']['sourceEntity']
        del release['releases'][0]['planning']['budget']['europeanUnionFunding']
        del release['releases'][0]['planning']['budget']['verified']
        del release['releases'][0]['planning']['budget']['project']
        del release['releases'][0]['planning']['budget']['projectID']
        del release['releases'][0]['planning']['budget']['uri']
        del release['releases'][0]['parties'][0]['identifier']['uri']
        del release['releases'][0]['parties'][0]['additionalIdentifiers']
        del release['releases'][0]['parties'][0]['address']['postalCode']
        del release['releases'][0]['parties'][0]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][0]['contactPoint']['url']
        del release['releases'][0]['parties'][0]['details']
        del release['releases'][0]['parties'][1]['identifier']['uri']
        del release['releases'][0]['parties'][1]['additionalIdentifiers']
        del release['releases'][0]['parties'][1]['address']['postalCode']
        del release['releases'][0]['parties'][1]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][1]['contactPoint']['url']
        del release['releases'][0]['parties'][1]['details']
        del release['releases'][0]['parties'][2]['identifier']['uri']
        del release['releases'][0]['parties'][2]['additionalIdentifiers']
        del release['releases'][0]['parties'][2]['address']['postalCode']
        del release['releases'][0]['parties'][2]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][2]['contactPoint']['url']
        del release['releases'][0]['parties'][2]['details']

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
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['id'] = f"{GlobalClassCreatePn.pn_ocid}-{release_id[29:42]}"
        release['releases'][0]['date'] = release_date
        release['releases'][0]['tag'][0] = "compiled"
        release['releases'][0]['language'] = self.language
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['title'] = GlobalClassCreatePn.payload['tender']['title']
        release['releases'][0]['tender']['description'] = GlobalClassCreatePn.payload['tender']['description']
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "planning notice"
        release['releases'][0]['tender']['value']['amount'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['amount']
        release['releases'][0]['tender']['value']['currency'] = \
            GlobalClassCreateFs.payload['planning']['budget']['amount']['currency']
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
        release['releases'][0]['planning']['rationale'] = GlobalClassCreatePn.payload['planning']['rationale']
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
        release['releases'][0]['planning']['budget']['description'] = \
            GlobalClassCreatePn.payload['planning']['budget']['description']
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

        return release

    def pn_release_obligatory_data_model_with_lots_and_items_based_on_one_fs(
            self, operation_date, release_date):
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
        release['releases'][0].update(self.constructor.release_general_attributes())
        release['releases'][0]['tender'].update(self.constructor.release_tender_section())
        release['releases'][0]['tender']['items'] = [{}]
        release['releases'][0]['tender']['items'][0].update(self.constructor.release_tender_item_object())
        release['releases'][0]['tender']['lots'] = [{}]
        release['releases'][0]['tender']['lots'][0].update(self.constructor.release_tender_lot_object())
        release['releases'][0]['relatedProcesses'][0].update(self.constructor.release_related_processes_section())

        del release['releases'][0]['tender']['procuringEntity']
        del release['releases'][0]['tender']['framework']
        del release['releases'][0]['tender']['dynamicPurchasingSystem']
        del release['releases'][0]['tender']['procedureOutsourcing']
        del release['releases'][0]['tender']['legalBasis']
        del release['releases'][0]['tender']['jointProcurement']
        del release['releases'][0]['tender']['electronicWorkflows']
        del release['releases'][0]['tender']['designContest']
        del release['releases'][0]['tender']['acceleratedProcedure']
        del release['releases'][0]['tender']['eligibilityCriteria']
        del release['releases'][0]['tender']['procurementMethod']
        del release['releases'][0]['tender']['procurementMethodDetails']
        del release['releases'][0]['tender']['mainProcurementCategory']
        del release['releases'][0]['tender']['classification']
        del release['releases'][0]['tender']['value']
        del release['releases'][0]['tender']['items'][0]['deliveryAddress']
        del release['releases'][0]['tender']['items'][0]['additionalClassifications']
        del release['releases'][0]['tender']['lots'][0]['internalId']
        del release['releases'][0]['tender']['lots'][0]['placeOfPerformance']['address']['postalCode']
        del release['releases'][0]['tender']['lots'][0]['placeOfPerformance']['description']

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
        release['publishedDate'] = operation_date
        release['releases'][0]['ocid'] = GlobalClassCreatePn.pn_id
        release['releases'][0]['id'] = f"{GlobalClassCreatePn.pn_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = release_date
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
        release['releases'][0]['tender']['items'] = self.__prepare_expected_items_array(
            payload_items_array=GlobalClassCreatePn.payload['tender']['items'],
            release_items_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['items'],
            release_lots_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['lots']
        )
        release['releases'][0]['tender']['lots'] = self.__prepare_expected_lots_array(
            payload_lots_array=GlobalClassCreatePn.payload['tender']['lots'],
            release_lots_array=GlobalClassCreatePn.actual_pn_release['releases'][0]['tender']['lots'])
        release['releases'][0]['hasPreviousNotice'] = False
        release['releases'][0]['purposeOfNotice']['isACallForCompetition'] = False
        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = GlobalClassCreatePn.pn_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_tender_url}/{GlobalClassCreatePn.pn_ocid}/{GlobalClassCreatePn.pn_ocid}"
        return release
