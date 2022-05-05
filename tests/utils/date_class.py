import datetime
import time

import pytz


class Date:
    @staticmethod
    def expenditureItem_period(start=0, end=90):
        date = datetime.datetime.now()
        duration_date_start = date + datetime.timedelta(days=start)
        start_date = duration_date_start.strftime('%Y-%m-%dT%H:%M:%SZ')
        duration_date_end = date + datetime.timedelta(days=end)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return start_date, end_date

    @staticmethod
    def financialSource_period(start=0, end=89):
        date = datetime.datetime.now()
        duration_date_start = date + datetime.timedelta(days=start)
        start_date = duration_date_start.strftime('%Y-%m-%dT%H:%M:%SZ')
        duration_date_end = date + datetime.timedelta(days=end)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return start_date, end_date

    @staticmethod
    def time_at_now():
        date = datetime.datetime.now()
        date_now = date.strftime('%Y-%m-%dT%H:%M:%SZ')
        time_at_now_milliseconds = date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        timestamp_now = int(
            time.mktime(
                datetime.datetime.strptime(time_at_now_milliseconds, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())) * 1000
        return date_now, timestamp_now

    @staticmethod
    def planningNotice_period():
        date = datetime.datetime.now()
        duration_date_start = date + datetime.timedelta(days=31)
        start_date = duration_date_start.strftime('%Y-%m-01T%H:%M:%SZ')
        return start_date

    @staticmethod
    def contactPeriod(maxDurationOfFA=None):
        date = datetime.datetime.now()
        if maxDurationOfFA is None:
            duration_date_start = date + datetime.timedelta(days=60)
            start_date = duration_date_start.strftime('%Y-%m-%dT%H:%M:%SZ')
            duration_date_end = date + datetime.timedelta(days=80)
            end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            days = int(maxDurationOfFA)/60/60/24
            duration_date_start = date + datetime.timedelta(days=1)
            start_date = duration_date_start.strftime('%Y-%m-%dT%H:%M:%SZ')
            duration_date_end = date + datetime.timedelta(days=days-1)
            end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return start_date, end_date

    @staticmethod
    def tenderPeriod_endDate(interval=35):
        date = datetime.datetime.now(pytz.utc)

        duration_date_tender_end = date + datetime.timedelta(seconds=interval)
        end_date = duration_date_tender_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return end_date

    @staticmethod
    def enquiryPeriod_endDate(interval=20):
        date = datetime.datetime.now(pytz.utc)
        duration_date_end = date + datetime.timedelta(seconds=interval)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return end_date

    @staticmethod
    def old_period():
        date = datetime.datetime.now()
        duration_date_start = date - datetime.timedelta(days=365)
        start_date = duration_date_start.strftime('%Y-%m-%dT%H:%M:%SZ')
        duration_date_end = date - datetime.timedelta(days=350)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return start_date, end_date

    @staticmethod
    def duration_period():
        date = datetime.datetime.now()
        duration_date_start = date + datetime.timedelta(days=0)
        start_date = duration_date_start.strftime('%Y-%m-%dT%H:%M:%SZ')
        duration_date_end = date + datetime.timedelta(days=20)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return start_date, end_date

    @staticmethod
    def sum_date(addition_date, addition_seconds):
        """Summation the dates."""

        first_addition = datetime.datetime.strptime(addition_date, '%Y-%m-%dT%H:%M:%SZ')
        second_addition = int(addition_seconds)
        sum_as_date = datetime.datetime.strftime(first_addition + datetime.timedelta(seconds=second_addition),
                                                 '%Y-%m-%dT%H:%M:%SZ')
        return sum_as_date

    @staticmethod
    def sub_date(reduction_date, subtractor_date):
        """Subtraction the dates."""

        reduction = datetime.datetime.strptime(reduction_date, '%Y-%m-%dT%H:%M:%SZ')
        subtractor = datetime.datetime.strptime(subtractor_date, '%Y-%m-%dT%H:%M:%SZ')
        difference = reduction - subtractor
        return int(difference.total_seconds())

    @staticmethod
    def preQualificationPeriod_endDate(interval_seconds: int):
        date = datetime.datetime.now(pytz.utc)
        duration_date_end = date + datetime.timedelta(seconds=interval_seconds)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return end_date

    @staticmethod
    def selectiveProcedure_enquiryPeriod_endDate(preQualification_period_endDate, interval_seconds: int):
        duration_date_end = datetime.datetime.strptime(
            preQualification_period_endDate, '%Y-%m-%dT%H:%M:%SZ') - datetime.timedelta(seconds=interval_seconds)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return end_date

    @staticmethod
    def selectiveProcedure_enquiryPeriod_endDate_after_unsuspended(create_answer_date, interval_seconds: int):
        duration_date_end = datetime.datetime.strptime(
            create_answer_date, '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(seconds=interval_seconds)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return end_date

    @staticmethod
    def selectiveProcedure_preQualificationPeriod_endDate_after_unsuspended(create_answer_date,
                                                                            interval_seconds: int):
        duration_date_end = datetime.datetime.strptime(
            create_answer_date, '%Y-%m-%dT%H:%M:%SZ') + datetime.timedelta(seconds=interval_seconds)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return end_date

    @staticmethod
    def get_min_date(dates_list):
        new_dates_list = list()
        for d in range(len(dates_list)):
            new_dates_list.append(datetime.datetime.strptime(dates_list[d], "%Y-%m-%dT%H:%M:%SZ"))
        min_date = min(new_dates_list)
        return min_date.strftime('%Y-%m-%dT%H:%M:%SZ')

    def __del__(self):
        print(f"The instance of Date class {__name__} was deleted.")