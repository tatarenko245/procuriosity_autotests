from tests.utils.date_class import Date
from tests.utils.functions import is_it_uuid, get_value_from_classification_cpv_dictionary_xls, \
    get_value_from_country_csv, get_value_from_region_csv, \
    get_value_from_locality_csv, get_value_from_classification_unit_dictionary_csv


class CnOnPnExpectedRelease:
    def __init__(self, environment, language, pmd, pn_ocid, pn_id, cn_feed_point_message,
                 tender_id, cn_payload, actual_np_release):
        self.language = language
        self.pn_ocid = pn_ocid
        self.pn_id = pn_id
        self.np_id = tender_id
        self.cn_feed_point_message = cn_feed_point_message
        self.cn_payload = cn_payload
        self.actual_np_release = actual_np_release
        self.metadata_tender_url = None
        self.procurement_method_details = None

        try:
            if environment == "dev":
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.metadata_document_url = "https://dev.bpe.eprocurement.systems/api/v1/storage/get"
                self.publisher_name = "M-Tender"
                self.publisher_uri = "https://www.mtender.gov.md"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"]
            elif environment == "sandbox":
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.metadata_document_url = "http://storage.eprocurement.systems/get"
                self.publisher_name = "Viešųjų pirkimų tarnyba"
                self.publisher_uri = "https://vpt.lrv.lt"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.json"]
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

    def cn_release_obligatory_data_model_without_lots_and_items_based_on_one_fs(self):
        try:
            is_it_uuid(
                uuid_to_test=self.actual_np_release['releases'][0]['tender']['id'],
                version=4
            )
        except ValueError:
            raise ValueError("Check your actual_np_release['releases'][0]['tender']['id']: "
                             "id must be uuid version 4")
        try:
            for n in self.actual_np_release['releases'][0]['relatedProcesses']:
                for n_1 in n:
                    if n_1 == "id":
                        is_it_uuid(
                            uuid_to_test=n['id'],
                            version=1
                        )
        except ValueError:
            raise ValueError("Check your actual_np_release['releases'][0]['relatedProcesses'][*]['id']: "
                             "id must be uuid version 1")

        try:
            """
            Check how many quantity of object into release_lots_array.
            Check release_lots_array[*]['id'] -> is it uuid.
            """
            list_of_release_lot_id = list()
            for lot_object in self.actual_np_release['releases'][0]['tender']['lots']:
                for i in lot_object:
                    if i == "id":
                        list_of_release_lot_id.append(lot_object['id'])
                        try:
                            is_it_uuid(
                                uuid_to_test=lot_object['id'],
                                version=4
                            )
                        except ValueError:
                            raise ValueError("Check your items array in release: "
                                             "release_items_array.id in release must be uuid version 4")
            quantity_of_lot_object_into_release = len(list_of_release_lot_id)
        except KeyError:
            raise KeyError("Check ['releases']['tender']['items'][*]['id']")

        try:
            """
            Check how many quantity of object into release_items_array.
            Check release_items_array[*]['id'] -> is it uuid.
            """
            list_of_release_item_id = list()
            for item_object in self.actual_np_release['releases'][0]['tender']['items']:
                for i in item_object:
                    if i == "id":
                        list_of_release_item_id.append(item_object['id'])
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
            Prepare items array framework.
            """
            items_array = []
            for n in range(quantity_of_item_object_into_release):
                cpv_data = get_value_from_classification_cpv_dictionary_xls(
                    cpv=self.cn_payload['tender']['items'][n]['classification']['id'],
                    language=self.language)

                unit_data = get_value_from_classification_unit_dictionary_csv(
                    unit_id=self.cn_payload['tender']['items'][n]['unit']['id'],
                    language=self.language)

                item_object = {
                    "id": list_of_release_item_id[n],
                    "description": self.cn_payload['tender']['items'][n]['description'],
                    "classification": {
                        "scheme": "CPV",
                        "id": cpv_data[0],
                        "description": cpv_data[1]
                    },
                    "quantity": float(self.cn_payload['tender']['items'][n]['quantity']),
                    "unit": {
                        "name": unit_data[1],
                        "id": unit_data[0]
                    },
                    "relatedLot": self.actual_np_release['releases'][0]['tender']['lots'][n]['id']
                }
                items_array.append(item_object)
        except ValueError:
            raise ValueError("Impossible to build expected items array framework.")

        try:
            """
            Prepare lots array framework.
            """
            lots_array = []
            for n in range(quantity_of_lot_object_into_release):
                try:
                    lot_country_data = get_value_from_country_csv(
                        country=self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                            'addressDetails']['country']['id'],
                        language=self.language
                    )
                    lot_country_object = {
                        "scheme": lot_country_data[2],
                        "id": self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                            'addressDetails']['country']['id'],
                        "description": lot_country_data[1],
                        "uri": lot_country_data[3]
                    }

                    lot_region_data = get_value_from_region_csv(
                        region=self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                            'addressDetails']['region']['id'],
                        country=self.cn_payload['tender']['lots'][n]['placeOfPerformance'][
                            'address']['addressDetails']['country']['id'],
                        language=self.language
                    )

                    lot_region_object = {
                        "scheme": lot_region_data[2],
                        "id": self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                            'addressDetails']['region']['id'],
                        "description": lot_region_data[1],
                        "uri": lot_region_data[3]
                    }

                    if \
                            self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['scheme'] == "CUATM":
                        lot_locality_data = get_value_from_locality_csv(
                            locality=self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['id'],
                            region=self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                                'addressDetails']['region']['id'],
                            country=self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                                'addressDetails']['country']['id'],
                            language=self.language
                        )
                        lot_locality_object = {
                            "scheme": lot_locality_data[2],
                            "id": self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['id'],
                            "description": lot_locality_data[1],
                            "uri": lot_locality_data[3]
                        }
                    else:
                        lot_locality_object = {
                            "scheme": self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['scheme'],
                            "id": self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['id'],
                            "description": self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                                'addressDetails']['locality']['description']
                        }
                except ValueError:
                    raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

                lot_object = {
                    "id": list_of_release_lot_id[n],
                    "title": self.cn_payload['tender']['lots'][n]['title'],
                    "description": self.cn_payload['tender']['lots'][n]['description'],
                    "status": "active",
                    "statusDetails": "empty",
                    "value": {
                        "amount": self.cn_payload['tender']['lots'][n]['value']['amount'],
                        "currency": self.cn_payload['tender']['lots'][n]['value']['currency']
                    },
                    "contractPeriod": {
                        "startDate": self.cn_payload['tender']['lots'][n]['contractPeriod']['startDate'],
                        "endDate": self.cn_payload['tender']['lots'][n]['contractPeriod']['endDate']
                    },
                    "placeOfPerformance": {
                        "address": {
                            "streetAddress": self.cn_payload['tender']['lots'][n]['placeOfPerformance']['address'][
                                'streetAddress'],
                            "addressDetails": {
                                "country": lot_country_object,
                                "region": lot_region_object,
                                "locality": lot_locality_object
                            }
                        }
                    },
                    "hasOptions": False,
                    "hasRecurrence": False,
                    "hasRenewal": False
                }
                lots_array.append(lot_object)
        except ValueError:
            raise ValueError("Impossible to build expected lots array framework.")

        release = {
            "uri": f"{self.metadata_tender_url}/{self.pn_ocid}/{self.np_id}",
            "version": "1.1",
            "extensions": self.extensions,
            "publisher": {
                "name": self.publisher_name,
                "uri": self.publisher_uri
            },
            "license": "http://opendefinition.org/licenses/",
            "publicationPolicy": "http://opendefinition.org/licenses/",
            "publishedDate": self.cn_feed_point_message['data']['operationDate'],
            "releases": [
                {
                    "ocid": self.np_id,
                    "id": f"{self.np_id}-{self.actual_np_release['releases'][0]['id'][46:59]}",
                    "date": self.cn_feed_point_message['data']['operationDate'],
                    "tag": [
                        "tender"
                    ],
                    "language": self.language,
                    "initiationType": "tender",
                    "tender": {
                        "id": self.actual_np_release['releases'][0]['tender']['id'],
                        "status": "active",
                        "statusDetails": "negotiation",
                        "items": items_array,
                        "lots": lots_array,
                        "lotGroups": [
                            {
                                "optionToCombine": False
                            }
                        ],
                        "hasEnquiries": False,
                        "documents": [
                            {
                                "id": self.cn_payload['tender']['documents'][0]['id'],
                                "documentType": self.cn_payload['tender']['documents'][0]['documentType'],
                                "title": self.cn_payload['tender']['documents'][0]['title'],
                                "description": self.cn_payload['tender']['documents'][0]['description'],
                                "url": f"{self.metadata_document_url}/"
                                       f"{self.cn_payload['tender']['documents'][0]['id']}",
                                "datePublished": self.cn_feed_point_message['data']['operationDate'],
                                "relatedLots": [self.actual_np_release['releases'][0]['tender']['lots'][0]['id']
                                                ]
                            }
                        ],
                        "awardCriteria": "priceOnly",
                        "submissionMethod": [
                            "electronicSubmission"
                        ],
                        "submissionMethodDetails": "Lista platformelor: achizitii, ebs, licitatie, yptender",
                        "submissionMethodRationale": [
                            "Ofertele vor fi primite prin intermediul unei platforme electronice de achiziții publice"
                        ],
                        "requiresElectronicCatalogue": False
                    },
                    "hasPreviousNotice": True,
                    "purposeOfNotice": {
                        "isACallForCompetition": True
                    },
                    "relatedProcesses": [
                        {
                            "id": self.actual_np_release['releases'][0]['relatedProcesses'][0]['id'],
                            "relationship": [
                                "parent"
                            ],
                            "scheme": "ocid",
                            "identifier": self.pn_ocid,
                            "uri": f"{self.metadata_tender_url}/{self.pn_ocid}/{self.pn_ocid}"
                        },
                        {
                            "id": self.actual_np_release['releases'][0]['relatedProcesses'][1]['id'],
                            "relationship": [
                                "planning"
                            ],
                            "scheme": "ocid",
                            "identifier": self.pn_id,
                            "uri": f"{self.metadata_tender_url}/{self.pn_ocid}/{self.pn_id}"
                        }
                    ]
                }
            ]
        }
        return release

    def update_cn_amendments_array(self):
        try:
            is_it_uuid(
                uuid_to_test=self.actual_np_release['releases'][0]['tender']['amendments'][0]['id'],
                version=4
            )
        except ValueError:
            raise ValueError("Check your actual_np_release['releases'][0]['tender']['amendments']: "
                             "id must be uuid version 4")

        amendments_array = [{
            "id": self.actual_np_release['releases'][0]['tender']['amendments'][0]['id'],
            "date": self.cn_feed_point_message['data']['operationDate'],
            "releaseID":
                f"{self.np_id}-{self.actual_np_release['releases'][0]['tender']['amendments'][0]['releaseID'][46:59]}",
            "amendsReleaseID":
                f"{self.np_id}-"
                f"{self.actual_np_release['releases'][0]['tender']['amendments'][0]['amendsReleaseID'][46:59]}",
            "rationale": "General change of Contract Notice"
        }]
        return amendments_array
