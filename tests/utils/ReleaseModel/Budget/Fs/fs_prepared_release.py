import copy
from tests.utils.ReleaseModel.Budget.Fs.fs_release_library import ReleaseLibrary
from tests.utils.functions_collection import check_uuid_version, get_value_from_country_csv, get_value_from_region_csv, \
    get_value_from_locality_csv


class FsExpectedRelease:
    def __init__(self, environment, language, ei_ocid, fs_payload, fs_feed_point_message, actual_fs_release):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.language = language
        self.ei_ocid = ei_ocid
        self.fs_id = fs_feed_point_message["data"]["outcomes"]["fs"][0]['id']
        self.fs_payload = fs_payload
        self.fs_feed_point_message = fs_feed_point_message
        self.actual_fs_release = actual_fs_release

        self.metadata_budget_url = None
        self.main_procurement_category = None
        try:
            if environment == "dev":
                self.metadata_budget_url = "http://dev.public.eprocurement.systems/budgets"
                self.publisher_name = "M-Tender"
                self.publisher_uri = "https://www.mtender.gov.md"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.js"]
            elif environment == "sandbox":
                self.metadata_budget_url = "http://public.eprocurement.systems/budgets"
                self.publisher_name = "Viešųjų pirkimų tarnyba"
                self.publisher_uri = "https://vpt.lrv.lt"
                self.extensions = [
                    "https://raw.githubusercontent.com/open-contracting/ocds_bid_extension/v1.1.1/extension.json",
                    "https://raw.githubusercontent.com/open-contracting/ocds_enquiry_extension/v1.1.1/extension.json"]
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

    def fs_release_full_data_model_own_money_payer_id_is_not_equal_funder_id(self):

        release_id = self.actual_fs_release['releases'][0]['id']
        tender_id = self.actual_fs_release['releases'][0]['tender']['id']
        related_processes_id = self.actual_fs_release['releases'][0]['relatedProcesses'][0]['id']

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

        try:
            check_uuid_version(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in Fs release: tender_id in Fs release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in Fs release: release_id in Fs release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=related_processes_id,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in Fs release: "
                             "tender_id in Fs release must be uuid version 1")

        try:
            funder_country_data = get_value_from_country_csv(
                country=self.fs_payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            funder_country_object = {
                "scheme": funder_country_data[2],
                "id": self.fs_payload['buyer']['address']['addressDetails']['country']['id'],
                "description": funder_country_data[1],
                "uri": funder_country_data[3]
            }

            funder_region_data = get_value_from_region_csv(
                region=self.fs_payload['buyer']['address']['addressDetails']['region']['id'],
                country=self.fs_payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            funder_region_object = {
                "scheme": funder_region_data[2],
                "id": self.fs_payload['buyer']['address']['addressDetails']['region']['id'],
                "description": funder_region_data[1],
                "uri": funder_region_data[3]
            }

            if self.fs_payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                funder_locality_data = get_value_from_locality_csv(
                    locality=self.fs_payload['buyer']['address']['addressDetails']['locality']['id'],
                    region=self.fs_payload['buyer']['address']['addressDetails']['region']['id'],
                    country=self.fs_payload['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )

                funder_locality_object = {
                    "scheme": funder_locality_data[2],
                    "id": self.fs_payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": funder_locality_data[1],
                    "uri": funder_locality_data[3]
                }
            else:
                funder_locality_object = {
                    "scheme": self.fs_payload['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": self.fs_payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": self.fs_payload['buyer']['address']['addressDetails']['locality'][
                        'description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            payer_country_data = get_value_from_country_csv(
                country=self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            payer_country_object = {
                "scheme": payer_country_data[2],
                "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'],
                "description": payer_country_data[1],
                "uri": payer_country_data[3]
            }

            payer_region_data = get_value_from_region_csv(
                region=self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'],
                country=self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            payer_region_object = {
                "scheme": payer_region_data[2],
                "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'],
                "description": payer_region_data[1],
                "uri": payer_region_data[3]
            }

            if \
                    self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'scheme'] == "CUATM":
                payer_locality_data = get_value_from_locality_csv(
                    locality=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['id'],
                    region=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['region']['id'],
                    country=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['country']['id'],
                    language=self.language
                )
                payer_locality_object = {
                    "scheme": payer_locality_data[2],
                    "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'],
                    "description": payer_locality_data[1],
                    "uri": payer_locality_data[3]
                }
            else:
                payer_locality_object = {
                    "scheme":
                        self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['scheme'],
                    "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'],
                    "description":
                        self.fs_payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        # uncomment this code:
        # release['releases'][0]['language'] = self.language
        # ==========================

        # del thi code:
        del release['releases'][0]['language']
        # ============================

        release['uri'] = f"{self.metadata_budget_url}/{self.ei_ocid}/{self.fs_id}"
        release['version'] = "1.1"
        release['extensions'] = self.extensions
        release['publisher']['name'] = self.publisher_name
        release['publisher']['uri'] = self.publisher_uri
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = self.fs_feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = self.fs_id
        release['releases'][0]['id'] = f"{self.fs_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = self.fs_feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "active"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['parties'][0]['id'] = f"{self.fs_payload['buyer']['identifier']['scheme']}-" \
                                                     f"{self.fs_payload['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = self.fs_payload['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = self.fs_payload['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = self.fs_payload['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            self.fs_payload['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['identifier']['uri'] = self.fs_payload['buyer']['identifier']['uri']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            self.fs_payload['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['postalCode'] = \
            self.fs_payload['buyer']['address']['postalCode']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = funder_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = funder_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = funder_locality_object
        release['releases'][0]['parties'][0]['additionalIdentifiers'] = \
            self.fs_payload['buyer']['additionalIdentifiers']
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            self.fs_payload['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            self.fs_payload['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            self.fs_payload['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['contactPoint']['faxNumber'] = \
            self.fs_payload['buyer']['contactPoint']['faxNumber']
        release['releases'][0]['parties'][0]['contactPoint']['url'] = \
            self.fs_payload['buyer']['contactPoint']['url']
        release['releases'][0]['parties'][0]['roles'][0] = "funder"

        release['releases'][0]['parties'][1]['id'] = \
            f"{self.fs_payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{self.fs_payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][1]['name'] = self.fs_payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][1]['identifier']['scheme'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['scheme']
        release['releases'][0]['parties'][1]['identifier']['id'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['id']
        release['releases'][0]['parties'][1]['identifier']['legalName'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['legalName']
        release['releases'][0]['parties'][1]['identifier']['uri'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['uri']
        release['releases'][0]['parties'][1]['address']['streetAddress'] = \
            self.fs_payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][1]['address']['postalCode'] = \
            self.fs_payload['tender']['procuringEntity']['address']['postalCode']
        release['releases'][0]['parties'][1]['address']['addressDetails']['country'] = payer_country_object
        release['releases'][0]['parties'][1]['address']['addressDetails']['region'] = payer_region_object
        release['releases'][0]['parties'][1]['address']['addressDetails']['locality'] = payer_locality_object
        release['releases'][0]['parties'][1]['additionalIdentifiers'] = \
            self.fs_payload['tender']['procuringEntity']['additionalIdentifiers']
        release['releases'][0]['parties'][1]['contactPoint']['name'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['name']
        release['releases'][0]['parties'][1]['contactPoint']['telephone'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['telephone']
        release['releases'][0]['parties'][1]['contactPoint']['email'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['email']
        release['releases'][0]['parties'][1]['contactPoint']['faxNumber'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['faxNumber']
        release['releases'][0]['parties'][1]['contactPoint']['url'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['url']
        release['releases'][0]['parties'][1]['roles'][0] = "payer"

        release['releases'][0]['planning']['budget']['id'] = self.fs_payload['planning']['budget']['id']
        release['releases'][0]['planning']['budget']['description'] = \
            self.fs_payload['planning']['budget']['description']
        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            self.fs_payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            self.fs_payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            self.fs_payload['planning']['budget']['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            self.fs_payload['planning']['budget']['amount']['currency']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['projectIdentifier'] = \
            self.fs_payload['planning']['budget']['europeanUnionFunding']['projectIdentifier']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['projectName'] = \
            self.fs_payload['planning']['budget']['europeanUnionFunding']['projectName']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['uri'] = \
            self.fs_payload['planning']['budget']['europeanUnionFunding']['uri']
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = True
        release['releases'][0]['planning']['budget']['verified'] = True
        release['releases'][0]['planning']['budget']['sourceEntity']['id'] = \
            f"{self.fs_payload['buyer']['identifier']['scheme']}" \
            f"-{self.fs_payload['buyer']['identifier']['id']}"
        release['releases'][0]['planning']['budget']['sourceEntity']['name'] = self.fs_payload['buyer'][
            'name']
        release['releases'][0]['planning']['budget']['project'] = self.fs_payload['planning']['budget'][
            'project']
        release['releases'][0]['planning']['budget']['projectID'] = \
            self.fs_payload['planning']['budget']['projectID']
        release['releases'][0]['planning']['budget']['uri'] = self.fs_payload['planning']['budget']['uri']
        release['releases'][0]['planning']['rationale'] = self.fs_payload['planning']['rationale']

        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = self.ei_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_budget_url}/{self.ei_ocid}/{self.ei_ocid}"
        return release

    def fs_release_full_data_model_treasury_money(self, ei_payload):

        release_id = self.actual_fs_release['releases'][0]['id']
        tender_id = self.actual_fs_release['releases'][0]['tender']['id']
        related_processes_id = self.actual_fs_release['releases'][0]['relatedProcesses'][0]['id']
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

        try:
            check_uuid_version(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in Fs release: tender_id in Fs release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in Fs release: release_id in Fs release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=related_processes_id,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in Fs release: "
                             "tender_id in Fs release must be uuid version 1")

        try:
            payer_country_data = get_value_from_country_csv(
                country=self.fs_payload['tender']['procuringEntity']['address'][
                    'addressDetails']['country']['id'],
                language=self.language
            )

            payer_country_object = {
                "scheme": payer_country_data[2],
                "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": payer_country_data[1],
                "uri": payer_country_data[3]
            }

            payer_region_data = get_value_from_region_csv(
                region=self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                country=self.fs_payload['tender']['procuringEntity']['address']['addressDetails'][
                    'country']['id'],
                language=self.language
            )

            payer_region_object = {
                "scheme": payer_region_data[2],
                "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                "description": payer_region_data[1],
                "uri": payer_region_data[3]
            }

            if \
                    self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'scheme'] == "CUATM":
                payer_locality_data = get_value_from_locality_csv(
                    locality=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['id'],
                    region=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['region']['id'],
                    country=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['country']['id'],
                    language=self.language)

                payer_locality_object = {
                    "scheme": payer_locality_data[2],
                    "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'],
                    "description": payer_locality_data[1],
                    "uri": payer_locality_data[3]}
            else:
                payer_locality_object = {
                    "scheme":
                        self.fs_payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['scheme'],
                    "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails'][
                        'locality']['id'],
                    "description":
                        self.fs_payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        # uncomment this code:
        # release['releases'][0]['language'] = self.language
        # ==========================

        # del thi code:
        del release['releases'][0]['language']
        # ============================

        release['uri'] = f"{self.metadata_budget_url}/{self.ei_ocid}/{self.fs_id}"
        release['version'] = "1.1"
        release['extensions'] = self.extensions
        release['publisher']['name'] = self.publisher_name
        release['publisher']['uri'] = self.publisher_uri
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = self.fs_feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = self.fs_id
        release['releases'][0]['id'] = f"{self.fs_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = self.fs_feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"

        release['releases'][0]['parties'][0]['id'] = \
            f"{self.fs_payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{self.fs_payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = self.fs_payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['legalName']
        release['releases'][0]['parties'][0]['identifier']['uri'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['uri']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            self.fs_payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['postalCode'] = \
            self.fs_payload['tender']['procuringEntity']['address']['postalCode']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = payer_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = payer_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = payer_locality_object
        release['releases'][0]['parties'][0]['additionalIdentifiers'] = \
            self.fs_payload['tender']['procuringEntity']['additionalIdentifiers']
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['email']
        release['releases'][0]['parties'][0]['contactPoint']['faxNumber'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['faxNumber']
        release['releases'][0]['parties'][0]['contactPoint']['url'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['url']
        release['releases'][0]['parties'][0]['roles'][0] = "payer"

        release['releases'][0]['planning']['budget']['id'] = self.fs_payload['planning']['budget']['id']
        release['releases'][0]['planning']['budget']['description'] = self.fs_payload['planning']['budget'][
            'description']
        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            self.fs_payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            self.fs_payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            self.fs_payload['planning']['budget']['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            self.fs_payload['planning']['budget']['amount']['currency']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['projectIdentifier'] = \
            self.fs_payload['planning']['budget']['europeanUnionFunding']['projectIdentifier']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['projectName'] = \
            self.fs_payload['planning']['budget']['europeanUnionFunding']['projectName']
        release['releases'][0]['planning']['budget']['europeanUnionFunding']['uri'] = \
            self.fs_payload['planning']['budget']['europeanUnionFunding']['uri']
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = True
        release['releases'][0]['planning']['budget']['verified'] = False
        release['releases'][0]['planning']['budget']['sourceEntity']['id'] = \
            f"{ei_payload['buyer']['identifier']['scheme']}" \
            f"-{ei_payload['buyer']['identifier']['id']}"
        release['releases'][0]['planning']['budget']['sourceEntity']['name'] = f"{ei_payload['buyer']['name']}"
        release['releases'][0]['planning']['budget']['project'] = self.fs_payload['planning']['budget'][
            'project']
        release['releases'][0]['planning']['budget']['projectID'] = \
            self.fs_payload['planning']['budget']['projectID']
        release['releases'][0]['planning']['budget']['uri'] = self.fs_payload['planning']['budget']['uri']
        release['releases'][0]['planning']['rationale'] = self.fs_payload['planning']['rationale']

        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = self.ei_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_budget_url}/{self.ei_ocid}/{self.ei_ocid}"
        return release

    def fs_release_obligatory_data_model_own_money_payer_id_is_not_equal_funder_id(self):
        release_id = self.actual_fs_release['releases'][0]['id']
        tender_id = self.actual_fs_release['releases'][0]['tender']['id']
        related_processes_id = self.actual_fs_release['releases'][0]['relatedProcesses'][0]['id']

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
        del release['releases'][0]['planning']['budget']['id']
        del release['releases'][0]['planning']['budget']['description']
        del release['releases'][0]['planning']['budget']['europeanUnionFunding']
        del release['releases'][0]['planning']['budget']['project']
        del release['releases'][0]['planning']['budget']['projectID']
        del release['releases'][0]['planning']['budget']['uri']
        del release['releases'][0]['planning']['rationale']

        try:
            check_uuid_version(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in Fs release: tender_id in Fs release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in Fs release: release_id in Fs release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=related_processes_id,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in Fs release: "
                             "tender_id in Fs release must be uuid version 1")

        try:
            funder_country_data = get_value_from_country_csv(
                country=self.fs_payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            funder_country_object = {
                "scheme": funder_country_data[2],
                "id": self.fs_payload['buyer']['address']['addressDetails']['country']['id'],
                "description": funder_country_data[1],
                "uri": funder_country_data[3]
            }

            funder_region_data = get_value_from_region_csv(
                region=self.fs_payload['buyer']['address']['addressDetails']['region']['id'],
                country=self.fs_payload['buyer']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            funder_region_object = {
                "scheme": funder_region_data[2],
                "id": self.fs_payload['buyer']['address']['addressDetails']['region']['id'],
                "description": funder_region_data[1],
                "uri": funder_region_data[3]
            }

            if self.fs_payload['buyer']['address']['addressDetails']['locality']['scheme'] == "CUATM":
                funder_locality_data = get_value_from_locality_csv(
                    locality=self.fs_payload['buyer']['address']['addressDetails']['locality']['id'],
                    region=self.fs_payload['buyer']['address']['addressDetails']['region']['id'],
                    country=self.fs_payload['buyer']['address']['addressDetails']['country']['id'],
                    language=self.language
                )

                funder_locality_object = {
                    "scheme": funder_locality_data[2],
                    "id": self.fs_payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": funder_locality_data[1],
                    "uri": funder_locality_data[3]
                }
            else:
                funder_locality_object = {
                    "scheme": self.fs_payload['buyer']['address']['addressDetails']['locality']['scheme'],
                    "id": self.fs_payload['buyer']['address']['addressDetails']['locality']['id'],
                    "description": self.fs_payload['buyer']['address']['addressDetails']['locality']['description']
                }
        except ValueError:
            raise ValueError("Check 'buyer.address.addressDetails' object")

        try:
            payer_country_data = get_value_from_country_csv(
                country=self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            payer_country_object = {
                "scheme": payer_country_data[2],
                "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'],
                "description": payer_country_data[1],
                "uri": payer_country_data[3]
            }

            payer_region_data = get_value_from_region_csv(
                region=self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'],
                country=self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'],
                language=self.language
            )

            payer_region_object = {
                "scheme": payer_region_data[2],
                "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'],
                "description": payer_region_data[1],
                "uri": payer_region_data[3]
            }

            if \
                    self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'scheme'] == "CUATM":
                payer_locality_data = get_value_from_locality_csv(
                    locality=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['id'],
                    region=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['region']['id'],
                    country=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['country']['id'],
                    language=self.language
                )
                payer_locality_object = {
                    "scheme": payer_locality_data[2],
                    "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'],
                    "description": payer_locality_data[1],
                    "uri": payer_locality_data[3]
                }
            else:
                payer_locality_object = {
                    "scheme": self.fs_payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['scheme'],
                    "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'],
                    "description": self.fs_payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        # uncomment this code:
        # release['releases'][0]['language'] = self.language
        # ==========================

        # del thi code:
        del release['releases'][0]['language']
        # ============================

        release['uri'] = f"{self.metadata_budget_url}/{self.ei_ocid}/{self.fs_id}"
        release['version'] = "1.1"
        release['extensions'] = self.extensions
        release['publisher']['name'] = self.publisher_name
        release['publisher']['uri'] = self.publisher_uri
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = self.fs_feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = self.fs_id
        release['releases'][0]['id'] = f"{self.fs_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = self.fs_feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "active"
        release['releases'][0]['tender']['statusDetails'] = "empty"
        release['releases'][0]['parties'][0]['id'] = \
            f"{self.fs_payload['buyer']['identifier']['scheme']}-" \
            f"{self.fs_payload['buyer']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = self.fs_payload['buyer']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            self.fs_payload['buyer']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            self.fs_payload['buyer']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            self.fs_payload['buyer']['identifier']['legalName']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            self.fs_payload['buyer']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = funder_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = funder_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = funder_locality_object
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            self.fs_payload['buyer']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            self.fs_payload['buyer']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            self.fs_payload['buyer']['contactPoint']['email']
        release['releases'][0]['parties'][0]['roles'][0] = "funder"

        release['releases'][0]['parties'][1]['id'] = \
            f"{self.fs_payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{self.fs_payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][1]['name'] = self.fs_payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][1]['identifier']['scheme'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['scheme']
        release['releases'][0]['parties'][1]['identifier']['id'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['id']
        release['releases'][0]['parties'][1]['identifier']['legalName'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['legalName']
        release['releases'][0]['parties'][1]['address']['streetAddress'] = \
            self.fs_payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][1]['address']['addressDetails']['country'] = payer_country_object
        release['releases'][0]['parties'][1]['address']['addressDetails']['region'] = payer_region_object
        release['releases'][0]['parties'][1]['address']['addressDetails']['locality'] = payer_locality_object
        release['releases'][0]['parties'][1]['contactPoint']['name'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['name']
        release['releases'][0]['parties'][1]['contactPoint']['telephone'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['telephone']
        release['releases'][0]['parties'][1]['contactPoint']['email'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['email']
        release['releases'][0]['parties'][1]['roles'][0] = "payer"

        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            self.fs_payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            self.fs_payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            self.fs_payload['planning']['budget']['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            self.fs_payload['planning']['budget']['amount']['currency']
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = False
        release['releases'][0]['planning']['budget']['verified'] = True
        release['releases'][0]['planning']['budget']['sourceEntity']['id'] = \
            f"{self.fs_payload['buyer']['identifier']['scheme']}" \
            f"-{self.fs_payload['buyer']['identifier']['id']}"
        release['releases'][0]['planning']['budget']['sourceEntity']['name'] = self.fs_payload['buyer']['name']
        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = self.ei_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_budget_url}/{self.ei_ocid}/{self.ei_ocid}"
        return release

    def fs_release_obligatory_data_model_treasury_money(self, ei_payload):

        release_id = self.actual_fs_release['releases'][0]['id']
        tender_id = self.actual_fs_release['releases'][0]['tender']['id']
        related_processes_id = self.actual_fs_release['releases'][0]['relatedProcesses'][0]['id']

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

        del release['releases'][0]['parties'][0]['identifier']['uri']
        del release['releases'][0]['parties'][0]['additionalIdentifiers']
        del release['releases'][0]['parties'][0]['address']['postalCode']
        del release['releases'][0]['parties'][0]['contactPoint']['faxNumber']
        del release['releases'][0]['parties'][0]['contactPoint']['url']
        del release['releases'][0]['planning']['budget']['id']
        del release['releases'][0]['planning']['budget']['description']
        del release['releases'][0]['planning']['budget']['europeanUnionFunding']
        del release['releases'][0]['planning']['budget']['project']
        del release['releases'][0]['planning']['budget']['projectID']
        del release['releases'][0]['planning']['budget']['uri']
        del release['releases'][0]['planning']['rationale']

        try:
            check_uuid_version(
                uuid_to_test=tender_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your tender_id in Fs release: tender_id in Fs release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=release_id,
                version=4
            )
        except ValueError:
            raise ValueError("Check your release_id in Fs release: release_id in Fs release must be uuid version 4")

        try:
            check_uuid_version(
                uuid_to_test=related_processes_id,
                version=1
            )
        except ValueError:
            raise ValueError("Check your related_processes_id in Fs release: "
                             "tender_id in Fs release must be uuid version 1")

        try:
            payer_country_data = get_value_from_country_csv(
                country=self.fs_payload['tender']['procuringEntity']['address'][
                    'addressDetails']['country']['id'],
                language=self.language
            )

            payer_country_object = {
                "scheme": payer_country_data[2],
                "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['country'][
                    'id'],
                "description": payer_country_data[1],
                "uri": payer_country_data[3]
            }

            payer_region_data = get_value_from_region_csv(
                region=self.fs_payload['tender']['procuringEntity']['address'][
                    'addressDetails']['region']['id'],
                country=self.fs_payload['tender']['procuringEntity']['address'][
                    'addressDetails']['country']['id'],
                language=self.language
            )

            payer_region_object = {
                "scheme": payer_region_data[2],
                "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['region'][
                    'id'],
                "description": payer_region_data[1],
                "uri": payer_region_data[3]
            }

            if \
                    self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality'][
                        'scheme'] == "CUATM":
                payer_locality_data = get_value_from_locality_csv(
                    locality=self.fs_payload['tender']['procuringEntity']['address'][
                        'addressDetails']['locality']['id'],
                    region=self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['region']['id'],
                    country=self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['country']['id'],
                    language=self.language
                )
                payer_locality_object = {
                    "scheme": payer_locality_data[2],
                    "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'],
                    "description": payer_locality_data[1],
                    "uri": payer_locality_data[3]
                }
            else:
                payer_locality_object = {
                    "scheme": self.fs_payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['scheme'],
                    "id": self.fs_payload['tender']['procuringEntity']['address']['addressDetails']['locality']['id'],
                    "description": self.fs_payload['tender']['procuringEntity']['address']['addressDetails'][
                            'locality']['description']
                }
        except ValueError:
            raise ValueError("Check 'tender.procuringEntity.address.addressDetails' object")

        # uncomment this code:
        # release['releases'][0]['language'] = self.language
        # ==========================

        # del thi code:
        del release['releases'][0]['language']
        # ============================

        release['uri'] = f"{self.metadata_budget_url}/{self.ei_ocid}/{self.fs_id}"
        release['version'] = "1.1"
        release['extensions'] = self.extensions
        release['publisher']['name'] = self.publisher_name
        release['publisher']['uri'] = self.publisher_uri
        release['license'] = "http://opendefinition.org/licenses/"
        release['publicationPolicy'] = "http://opendefinition.org/licenses/"
        release['publishedDate'] = self.fs_feed_point_message['data']['operationDate']
        release['releases'][0]['ocid'] = self.fs_id
        release['releases'][0]['id'] = f"{self.fs_id}-{release_id[46:59]}"
        release['releases'][0]['date'] = self.fs_feed_point_message['data']['operationDate']
        release['releases'][0]['tag'][0] = "planning"
        release['releases'][0]['initiationType'] = "tender"
        release['releases'][0]['tender']['id'] = tender_id
        release['releases'][0]['tender']['status'] = "planning"
        release['releases'][0]['tender']['statusDetails'] = "empty"

        release['releases'][0]['parties'][0]['id'] = \
            f"{self.fs_payload['tender']['procuringEntity']['identifier']['scheme']}-" \
            f"{self.fs_payload['tender']['procuringEntity']['identifier']['id']}"
        release['releases'][0]['parties'][0]['name'] = self.fs_payload['tender']['procuringEntity']['name']
        release['releases'][0]['parties'][0]['identifier']['scheme'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['scheme']
        release['releases'][0]['parties'][0]['identifier']['id'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['id']
        release['releases'][0]['parties'][0]['identifier']['legalName'] = \
            self.fs_payload['tender']['procuringEntity']['identifier']['legalName']
        release['releases'][0]['parties'][0]['address']['streetAddress'] = \
            self.fs_payload['tender']['procuringEntity']['address']['streetAddress']
        release['releases'][0]['parties'][0]['address']['addressDetails']['country'] = payer_country_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['region'] = payer_region_object
        release['releases'][0]['parties'][0]['address']['addressDetails']['locality'] = payer_locality_object
        release['releases'][0]['parties'][0]['contactPoint']['name'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['name']
        release['releases'][0]['parties'][0]['contactPoint']['telephone'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['telephone']
        release['releases'][0]['parties'][0]['contactPoint']['email'] = \
            self.fs_payload['tender']['procuringEntity']['contactPoint']['email']
        release['releases'][0]['parties'][0]['roles'][0] = "payer"

        release['releases'][0]['planning']['budget']['period']['startDate'] = \
            self.fs_payload['planning']['budget']['period']['startDate']
        release['releases'][0]['planning']['budget']['period']['endDate'] = \
            self.fs_payload['planning']['budget']['period']['endDate']
        release['releases'][0]['planning']['budget']['amount']['amount'] = \
            self.fs_payload['planning']['budget']['amount']['amount']
        release['releases'][0]['planning']['budget']['amount']['currency'] = \
            self.fs_payload['planning']['budget']['amount']['currency']
        release['releases'][0]['planning']['budget']['isEuropeanUnionFunded'] = False
        release['releases'][0]['planning']['budget']['verified'] = False
        release['releases'][0]['planning']['budget']['sourceEntity']['id'] = \
            f"{ei_payload['buyer']['identifier']['scheme']}-{ei_payload['buyer']['identifier']['id']}"
        release['releases'][0]['planning']['budget']['sourceEntity']['name'] = ei_payload['buyer']['name']

        release['releases'][0]['relatedProcesses'][0]['id'] = related_processes_id
        release['releases'][0]['relatedProcesses'][0]['relationship'][0] = "parent"
        release['releases'][0]['relatedProcesses'][0]['scheme'] = "ocid"
        release['releases'][0]['relatedProcesses'][0]['identifier'] = self.ei_ocid
        release['releases'][0]['relatedProcesses'][0]['uri'] = \
            f"{self.metadata_budget_url}/{self.ei_ocid}/{self.ei_ocid}"
        return release
