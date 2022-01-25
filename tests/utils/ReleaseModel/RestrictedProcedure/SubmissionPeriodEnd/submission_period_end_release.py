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

    def prepare_submission_object(self, sequence_number_of_submission, submission_payload,
                                  create_submission_feed_point_message):
        try:
            is_it_uuid(
                uuid_to_test=self.actual_tp_release[
                    'releases'][0]['submissions']['details'][sequence_number_of_submission]['id'],
                version=4
            )
        except ValueError:
            raise ValueError("Check your actual_tp_release['releases'][0]['submissions']['details'][i]['id']: "
                             "id must be uuid version 4")

        final_submissions_details_object = {
            "id": self.actual_tp_release[
                'releases'][0]['submissions']['details'][sequence_number_of_submission]['id'],
            "date": create_submission_feed_point_message['data']['operationDate'],
            "status": "pending",
            "candidates": []
        }

        try:
            """
            Calculate how many candidates contains into payload
            """
            candidates_identifier_id_list = list()
            for i in submission_payload['submission']['candidates']:
                for i_1 in i:
                    if i_1 == "identifier":
                        candidates_identifier_id_list.append(i['identifier']['id'])
        except Exception:
            raise Exception("Impossible to check calculate how many candidates contains into payload")

        for i in range(len(candidates_identifier_id_list)):
            submission_details_candidates_object = {
                "id": f"{submission_payload['submission']['candidates'][i]['identifier']['scheme']}-"
                      f"{submission_payload['submission']['candidates'][i]['identifier']['id']}",
                "name": submission_payload['submission']['candidates'][i]['name']
            }

            final_submissions_details_object['candidates'].append(submission_details_candidates_object)
        return final_submissions_details_object

    def prepare_qualification_object(self, cn_payload, sequence_number_of_submission, submission_id,
                                     submission_period_end_feed_point_message):
        status_details = None

        try:
            is_it_uuid(
                uuid_to_test=self.actual_tp_release[
                    'releases'][0]['qualifications'][sequence_number_of_submission]['id'],
                version=4
            )
        except ValueError:
            raise ValueError("Check your actual_tp_release['releases'][0]['submissions']['details'][i]['id']: "
                             "id must be uuid version 4")
        try:
            """
            FR.COM-7.13.1
            """
            if cn_payload['tender']['otherCriteria']['reductionCriteria'] == "none" and \
                    cn_payload['tender']['otherCriteria']['qualificationSystemMethods'] == ["manual"]:
                status_details = "awaiting"
        except Exception:
            raise Exception("Impossible to set correct statusDetails for qualification")

        qualification_object = {
            "id": self.actual_tp_release[
                    'releases'][0]['qualifications'][sequence_number_of_submission]['id'],
            "date": submission_period_end_feed_point_message['data']['operationDate'],
            "status": "pending",
            "statusDetails": status_details,
            "relatedSubmission": submission_id
        }

        final_qualification_mapper = {
            "id": qualification_object['id'],
            "value": qualification_object
        }
        return final_qualification_mapper
