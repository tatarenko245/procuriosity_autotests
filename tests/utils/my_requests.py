import json
import allure
import requests


class Requests:
    @staticmethod
    @allure.step('# Prepared request: create Ei')
    def create_ei(host_of_request, access_token, x_operation_id, country, language, payload, test_mode=False):
        ei = requests.post(
            url=host_of_request + "/do/ei",
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json'},
            params={
                'country': country,
                'lang': language,
                'testMode': test_mode
            },
            json=payload)
        allure.attach(host_of_request + "/do/ei", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return ei

    @staticmethod
    @allure.step('Prepared request: update Ei')
    def update_ei(host_of_request, ei_ocid, ei_token, access_token, x_operation_id, payload, test_mode=False):
        ei = requests.post(
            url=host_of_request + f"/do/ei/{ei_ocid}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'X-TOKEN': ei_token,
                'Content-Type': 'application/json'},
            json=payload)
        allure.attach(host_of_request + f"/do/ei{ei_ocid}", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return ei

    @staticmethod
    @allure.step('Prepared request: create Fs')
    def create_fs(host_of_request, ei_ocid, access_token, x_operation_id, payload, test_mode=False):
        fs = requests.post(
            url=host_of_request + f"/do/fs/{ei_ocid}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json'},
            json=payload)
        allure.attach(host_of_request + f"/do/fs/{ei_ocid}", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return fs

    @staticmethod
    @allure.step('Prepared request: update Fs')
    def update_fs(host_of_request, ei_ocid, fs_id, fs_token, access_token, x_operation_id, payload, test_mode=False):
        fs = requests.post(
            url=host_of_request + f"/do/fs/{ei_ocid}/{fs_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': fs_token},
            json=payload)
        allure.attach(host_of_request + f"/do/fs/{ei_ocid}/{fs_id}", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return fs

    @staticmethod
    @allure.step('Prepared request: create Pn')
    def create_pn(host_of_request, access_token, x_operation_id, country,
                  language, pmd, payload, test_mode=False):
        pn = requests.post(
            url=host_of_request + f"/do/pn",
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json'
            },
            params={
                'country': country,
                'lang': language,
                'pmd': pmd,
                'testMode': test_mode
            },
            json=payload)
        allure.attach(host_of_request + f"/do/pn", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return pn

    @staticmethod
    @allure.step('Prepared request: update Pn')
    def update_pn(host_of_request, access_token, x_operation_id, pn_ocid, pn_id, pn_token, payload, test_mode=False):
        pn = requests.post(
            url=host_of_request + f"/do/pn/{pn_ocid}/{pn_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': pn_token
            },
            json=payload)
        allure.attach(host_of_request + f"/do/pn", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return pn

    @staticmethod
    @allure.step('Prepared request: cancel Pn')
    def cancel_pn(host_of_request, access_token, x_operation_id, pn_ocid, pn_id, pn_token, test_mode=False):
        pn = requests.post(
            url=host_of_request + f"/cancel/pn/{pn_ocid}/{pn_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': pn_token
            })
        allure.attach(host_of_request + f"/cancel/pn", 'URL')
        return pn

    @staticmethod
    @allure.step('Prepared request: create CnOnPn')
    def create_cnonpn(host_of_request, access_token, x_operation_id, pn_ocid, pn_id, pn_token, payload,
                      test_mode=False):
        cn = requests.post(
            url=host_of_request + f"/do/cn/{pn_ocid}/{pn_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': pn_token
            },
            json=payload)
        allure.attach(host_of_request + f"/do/cn", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return cn

    @staticmethod
    @allure.step('Prepared request: update CnOnPn')
    def update_cnonpn(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, pn_token, payload,
                      test_mode=False):
        cn = requests.post(
            url=host_of_request + f"/do/cn/{pn_ocid}/{tender_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': pn_token
            },
            json=payload)
        allure.attach(host_of_request + f"/do/cn", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return cn

    @staticmethod
    @allure.step('Prepared request: create Enquiry')
    def create_enquiry(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, payload, test_mode=False):
        enquiry = requests.post(
            url=host_of_request + f"/do/enquiry/{pn_ocid}/{tender_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json'
            },
            json=payload)
        allure.attach(host_of_request + f"/do/enquiry", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return enquiry

    @staticmethod
    @allure.step('Prepared request: create Answer')
    def create_answer(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, enquiry_id, enquiry_token,
                      payload, test_mode=False):
        answer = requests.post(
            url=host_of_request + f"/do/enquiry/{pn_ocid}/{tender_id}/{enquiry_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': enquiry_token
            },
            json=payload)
        allure.attach(host_of_request + f"/do/enquiry", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return answer

    @staticmethod
    @allure.step('Prepared request: create Bid')
    def create_bid(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, payload, test_mode=False):
        bid = requests.post(
            url=host_of_request + f"/do/bid/{pn_ocid}/{ev_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json'
            },
            json=payload)
        allure.attach(host_of_request + f"/do/bid", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return bid

    @staticmethod
    @allure.step('Prepared request: withdraw Bid')
    def withdraw_bid(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, bid_id, bid_token, test_mode=False):
        bid = requests.post(
            url=host_of_request + f"/cancel/bid/{pn_ocid}/{ev_id}/{bid_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': bid_token
            })
        allure.attach(host_of_request + f"/cancel/bid", 'URL')
        return bid

    @staticmethod
    @allure.step('Prepared request: create Declare non conflict interest')
    def create_declare_non_conflict_interest(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, award_id,
                                             award_token, payload, test_mode=False):
        declaration = requests.post(
            url=host_of_request + f"/do/declaration/{pn_ocid}/{ev_id}/{award_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': award_token
            },
            json=payload)
        allure.attach(host_of_request + f"/do/declaration", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return declaration

    @staticmethod
    @allure.step('Prepared request: award consideration')
    def create_award_consideration(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, award_id,
                                   award_token, test_mode=False):
        consideration = requests.post(
            url=host_of_request + f"/do/consideration/{pn_ocid}/{ev_id}/{award_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': award_token
            })
        allure.attach(host_of_request + f"/do/consideration", 'URL')
        return consideration

    @staticmethod
    @allure.step('Prepared request: award consideration')
    def create_award_evaluation(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, award_id,
                                award_token, payload, test_mode=False):
        consideration = requests.post(
            url=host_of_request + f"/do/award/{pn_ocid}/{ev_id}/{award_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': award_token
            },
            json=payload)
        allure.attach(host_of_request + f"/do/award", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return consideration

    @staticmethod
    @allure.step('Prepared request: award consideration')
    def create_protocol(host_of_request, access_token, x_operation_id, pn_ocid, pn_token, ev_id, lot_id,
                        test_mode=False):
        protocol = requests.post(
            url=host_of_request + f"/do/protocol/{pn_ocid}/{ev_id}/{lot_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': pn_token
            })
        allure.attach(host_of_request + f"/do/protocol", 'URL')
        return protocol

    @staticmethod
    @allure.step('Prepared request: create Submission')
    def create_submission(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, payload, test_mode=False):
        submission = requests.post(
            url=host_of_request + f"/do/submission/{pn_ocid}/{tender_id}",
            params={
                'testMode': test_mode
            },
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json'
            },
            json=payload)
        allure.attach(host_of_request + f"/do/submission", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return submission
