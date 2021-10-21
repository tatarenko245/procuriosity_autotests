import json
import allure
import requests


class Requests:
    @staticmethod
    @allure.step('# Prepared request: create EI')
    def create_ei(host_of_request, access_token, x_operation_id, country, language, payload):
        ei = requests.post(
            url=host_of_request + "/do/ei",
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json'},
            params={
                'country': country,
                'lang': language
            },
            json=payload)
        allure.attach(host_of_request + "/do/ei", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return ei

    @staticmethod
    @allure.step('Prepared request: update EI')
    def update_ei(host_of_request, ei_ocid, ei_token, access_token, x_operation_id, payload):
        ei = requests.post(
            url=host_of_request + f"/do/ei/{ei_ocid}",
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
    @allure.step('Prepared request: create FS')
    def create_fs(host_of_request, ei_ocid, access_token, x_operation_id, payload):
        fs = requests.post(
            url=host_of_request + f"/do/fs/{ei_ocid}",
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json'},
            json=payload)
        allure.attach(host_of_request + f"/do/fs/{ei_ocid}", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return fs

    @staticmethod
    @allure.step('Prepared request: update FS')
    def update_fs(host_of_request, ei_ocid, fs_id, fs_token, access_token, x_operation_id, payload):
        fs = requests.post(
            url=host_of_request + f"/do/fs/{ei_ocid}/{fs_id}",
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
    @allure.step('Prepared request: create PN')
    def create_pn(host_of_request, access_token, x_operation_id, country,
                  language, pmd, payload):
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
                'pmd': pmd
            },
            json=payload)
        allure.attach(host_of_request + f"/do/pn", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return pn

    @staticmethod
    @allure.step('Prepared request: update PN')
    def update_pn(host_of_request, access_token, x_operation_id, pn_ocid, pn_id, pn_token, payload):
        pn = requests.post(
            url=host_of_request + f"/do/pn/{pn_ocid}/{pn_id}",
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
    @allure.step('Prepared request: cancel PN')
    def cancel_pn(host_of_request, access_token, x_operation_id, pn_ocid, pn_id, pn_token):
        pn = requests.post(
            url=host_of_request + f"/cancel/pn/{pn_ocid}/{pn_id}",
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
    def create_cnonpn(host_of_request, access_token, x_operation_id, pn_ocid, pn_id, pn_token, payload):
        cn = requests.post(
            url=host_of_request + f"/do/cn/{pn_ocid}/{pn_id}",
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
    def update_cnonpn(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, pn_token, payload):
        cn = requests.post(
            url=host_of_request + f"/do/cn/{pn_ocid}/{ev_id}",
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
    def create_enquiry(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, payload):
        enquiry = requests.post(
            url=host_of_request + f"/do/enquiry/{pn_ocid}/{ev_id}",
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
    def create_answer(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, enquiry_id, enquiry_token,
                      payload):
        answer = requests.post(
            url=host_of_request + f"/do/enquiry/{pn_ocid}/{ev_id}/{enquiry_id}",
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
    def create_bid(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, payload):
        bid = requests.post(
            url=host_of_request + f"/do/bid/{pn_ocid}/{ev_id}",
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
    def withdraw_bid(host_of_request, access_token, x_operation_id, pn_ocid, ev_id, bid_id, bid_token):
        bid = requests.post(
            url=host_of_request + f"/cancel/bid/{pn_ocid}/{ev_id}/{bid_id}",
            headers={
                'Authorization': 'Bearer ' + access_token,
                'X-OPERATION-ID': x_operation_id,
                'Content-Type': 'application/json',
                'X-TOKEN': bid_token
            })
        allure.attach(host_of_request + f"/cancel/bid", 'URL')
        return bid