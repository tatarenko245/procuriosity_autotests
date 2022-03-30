import copy
from tests.utils.PayloadModels.SelectiveProcedure.StartSecondStage.start_second_stage_library import PayloadLibrary
from tests.utils.date_class import Date


class StartSecondStagePreparePayload:
    def __init__(self, tender_period_interval):
        self.constructor = copy.deepcopy(PayloadLibrary())
        self.tenderPeriodEnd = Date().tender_period_end_date(interval=tender_period_interval)

    def create_start_second_stage_data_model(self):
        payload = {
            "tender": {}
        }

        payload['tender'].update(self.constructor.tender_object())
        payload['tender']['tenderPeriod']['endDate'] = self.tenderPeriodEnd

        return payload
