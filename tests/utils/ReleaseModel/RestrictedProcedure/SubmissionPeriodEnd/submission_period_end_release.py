from tests.utils.functions import is_it_uuid
from tests.utils.services.e_mdm_service import MdmService


class SubmissionPeriodEndExpectedRelease:
    def __init__(self, language, country, pmd, phase, actual_tp_release, host_for_service):
        self.language = language
        self.country = country
        self.pmd = pmd
        self.phase = phase
        self.actual_tp_release = actual_tp_release
        self.mdm_class = MdmService(host=host_for_service)

    def prepare_criteria_object_source_procuring_entity(self):
        expected_criteria_array_source_procuring_entity = {}

        criteria_from_mdm = self.mdm_class.get_criteria(
            language=self.language,
            country=self.country,
            pmd=self.pmd,
            phase=self.phase)

        try:
            """
            Check how many quantity of object contains criteria_from_mdm
            """
            list_of_mdm_tender_criteria_id = list()
            for criteria_object in criteria_from_mdm['data']:
                for i in criteria_object:
                    if i == "id":
                        list_of_mdm_tender_criteria_id.append(i)
            quantity_of_criteria_object_into_mdm = len(list_of_mdm_tender_criteria_id)
        except Exception:
            raise Exception("Impossible to check how many quantity of object contains criteria_from_mdm")

        for c in range(quantity_of_criteria_object_into_mdm):
            criteria_framework = {
                "id": criteria_from_mdm['data'][c]['id'],
                "title": criteria_from_mdm['data'][c]['title'],
                "source": "procuringEntity",
                "relatesTo": "qualification",
                "description": criteria_from_mdm['data'][c]['description'],
                "classification": criteria_from_mdm['data'][c]['classification'],
                "requirementGroups": []
            }

            criteria_groups_from_mdm = self.mdm_class.get_requirement_groups(
                language=self.language,
                country=self.country,
                pmd=self.pmd,
                phase=self.phase,
                criterion_id=criteria_from_mdm['data'][c]['id'])

            try:
                """
                Check how many quantity of object into criteria_groups_from_mdm
                """
                list_of_mdm_tender_criteria_groups_id = list()
                for group_object in criteria_groups_from_mdm['data']:
                    for i in group_object:
                        if i == "id":
                            list_of_mdm_tender_criteria_groups_id.append(i)
                quantity_of_criteria_groups_object_into_mdm = len(list_of_mdm_tender_criteria_groups_id)
            except Exception:
                raise Exception("Impossible to check how many quantity of object contains criteria_groups_from_mdm")

            for g in range(quantity_of_criteria_groups_object_into_mdm):
                requirement_groups_framework = {
                    "id": criteria_groups_from_mdm['data'][g]['id'],
                    "description": criteria_groups_from_mdm['data'][g]['description'],
                    "requirements": []
                }
                criteria_framework['requirementGroups'].append(requirement_groups_framework)

                criteria_groups_requirements_from_mdm = self.mdm_class.get_requirements(
                    language=self.language,
                    country=self.country,
                    pmd=self.pmd,
                    phase=self.phase,
                    requirement_group_id=criteria_groups_from_mdm['data'][g]['id'])

                try:
                    """
                    Check how many quantity of object into criteria_groups_requirements_from_mdm
                    """
                    list_of_mdm_tender_criteria_groups_id = list()
                    for group_object in criteria_groups_from_mdm['data']:
                        for i in group_object:
                            if i == "id":
                                list_of_mdm_tender_criteria_groups_id.append(i)
                    quantity_of_criteria_groups_object_into_mdm = len(list_of_mdm_tender_criteria_groups_id)
                except Exception:
                    raise Exception("Impossible to check how many quantity of object contains "
                                    "criteria_groups_requirements_from_mdm")

                for r in range(quantity_of_criteria_groups_object_into_mdm):
                    requirements_framework = {
                        "id": criteria_groups_requirements_from_mdm['data'][r]['id'],
                        "title": criteria_groups_requirements_from_mdm['data'][r]['title'],
                        "dataType": "boolean",
                        "status": "active",
                        "dataPublished": self.actual_tp_release['releases'][0]['preQualification'][
                            'period']['endDate'],
                        "description": criteria_groups_requirements_from_mdm['data'][r]['description']
                    }
                    criteria_framework['requirementGroups'][g]['requirements'].append(requirements_framework)

                    expected_criteria_array_source_procuring_entity.update(criteria_framework)

        return expected_criteria_array_source_procuring_entity

    def prepare_submissions_array(self, how_many_submission_was_created):
        final_submissions_object = {
            "details": []
        }
        for i in range(how_many_submission_was_created):
            try:
                is_it_uuid(
                    uuid_to_test=self.actual_tp_release['releases'][0]['submissions']['details'][i]['id'],
                    version=4
                )
            except ValueError:
                raise ValueError("Check your actual_tp_release['releases'][0]['submissions']['details'][i]['id']: "
                                 "id must be uuid version 4")

            submissions_details = {
                "id": self.actual_tp_release['releases'][0]['submissions']['details'][i]['id'],
                "date": "",
                "status": "",
                "candidates": [{
                    "id": "",
                    "name": ""
                }]
            }
            final_submissions_object['details'].append(submissions_details)
        return final_submissions_object
