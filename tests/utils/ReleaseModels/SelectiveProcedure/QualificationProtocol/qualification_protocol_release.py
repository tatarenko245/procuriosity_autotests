import copy

from tests.utils.ReleaseModels.SelectiveProcedure.QualificationProtocol.qualification_protocol_library import \
    ReleaseLibrary


class QualificationProtocolExpectedRelease:
    def __init__(self, actual_tp_release):
        self.constructor = copy.deepcopy(ReleaseLibrary())
        self.actual_tp_release = actual_tp_release

    def prepare_qualification_object(self, submission_payload, qualification_protocol_feed_point_message):
        invitation_object = {}

        invitation_object.update(self.constructor.invitation_object())
        for i in range(len(submission_payload['submission']['candidates'])):
            invitation_object['tenderers'].append(self.constructor.invitation_tenderers_object())

            invitation_object['tenderers'][i]['id'] = \
                f"{submission_payload['submission']['candidates'][i]['identifier']['scheme']}-" \
                f"{submission_payload['submission']['candidates'][i]['identifier']['id']}"

            invitation_object['tenderers'][i]['name'] = submission_payload['submission']['candidates'][i]['name']

            for q in self.actual_tp_release['releases'][0]['qualifications']:
                for q_1 in q['requirementResponses']:
                    if q_1['relatedTenderer']['id'] == invitation_object['tenderers'][i]['id']:
                        invitation_object['relatedQualification'] = q['id']

        for q in self.actual_tp_release['releases'][0]['invitations']:
            if q['tenderers'] == invitation_object['tenderers'] and \
                    q['relatedQualification'] == invitation_object['relatedQualification']:
                invitation_object['id'] = q['id']

        invitation_object['status'] = "pending"
        invitation_object['date'] = qualification_protocol_feed_point_message['data']['operationDate']

        final_invitation_mapper = {
            "id": invitation_object['id'],
            "value": invitation_object
        }
        return final_invitation_mapper

    def prepare_award_object(self, cn_payload, apply_protocol_feed_point_message):
        award_array = list()

        for i in range(len(cn_payload['tender']['lots'])):
            award_object = {}
            award_object.update(self.constructor.award_object())

            award_object['relatedLots'].append(self.actual_tp_release['releases'][0]['tender']['lots'][i]['id'])
            award_object['date'] = apply_protocol_feed_point_message['data']['operationDate']
            award_object['statusDetails'] = "lackOfQualifications"
            award_object['status'] = "unsuccessful"
            award_object['description'] = "Other reasons (discontinuation of procedure)"
            award_object['title'] = "Lot is not awarded"

            for a in range(len(self.actual_tp_release['releases'][0]['awards'])):
                if self.actual_tp_release['releases'][0]['awards'][a]['relatedLots'] == award_object['relatedLots']:
                    award_object['id'] = self.actual_tp_release['releases'][0]['awards'][a]['id']

            final_award_mapper = {
                "id": award_object['id'],
                "value": award_object
            }
            award_array.append(final_award_mapper)
        return award_array
