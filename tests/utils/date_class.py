import datetime
import time


class Date:
    @staticmethod
    def expenditure_item_period(start=0, end=90):
        date = datetime.datetime.now()
        duration_date_start = date + datetime.timedelta(days=start)
        start_date = duration_date_start.strftime('%Y-%m-%dT%H:%M:%SZ')
        duration_date_end = date + datetime.timedelta(days=end)
        end_date = duration_date_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        return start_date, end_date

    @staticmethod
    def financial_source_period(start=0, end=89):
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
    def planning_notice_period():
        date = datetime.datetime.now()
        duration_date_start = date + datetime.timedelta(days=31)
        start_date = duration_date_start.strftime('%Y-%m-01T%H:%M:%SZ')
        return start_date

    @staticmethod
    def contact_period():
        date = datetime.datetime.now()
        duration_date_start = date + datetime.timedelta(days=60)
        start_date = duration_date_start.strftime('%Y-%m-01T%H:%M:%SZ')
        duration_date_end = date + datetime.timedelta(days=80)
        end_date = duration_date_end.strftime('%Y-%m-01T%H:%M:%SZ')
        return start_date, end_date
