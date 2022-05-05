import json
import allure
import requests


class PlatformQueryRequest:
    @staticmethod
    @allure.step('# Prepared request: create Expenditure item.')
    def create_ei_process(host_to_bpe, access_token, x_operation_id, country, language, payload, testMode=False):
        request = requests.post(
            url=f"{host_to_bpe}/do/ei",
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "Content-Type": "application/json"},
            params={
                "country": country,
                "lang": language,
                "testMode": testMode
            },
            json=payload)
        allure.attach(f"{host_to_bpe}/do/ei", "URL")
        allure.attach(json.dumps(payload), "Prepared payload")
        return request

    # @staticmethod
    # @allure.step('Prepared request: update ExpenditureItem')
    # def update_ei(host_of_request, ei_ocid, ei_token, access_token, x_operation_id, payload, test_mode=False):
    #     ei = requests.post(
    #         url=host_of_request + f"/do/ei/{ei_ocid}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'X-TOKEN': ei_token,
    #             'Content-Type': 'application/json'},
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/ei{ei_ocid}", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return ei

    @staticmethod
    @allure.step('# Prepared request: create Financial source.')
    def create_fs_process(host_to_bpe, ei_cpid, access_token, x_operation_id, payload, testMode=False):
        request = requests.post(
            url=f"{host_to_bpe}/do/fs/{ei_cpid}",
            params={
                "testMode": testMode
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "Content-Type": "application/json"},
            json=payload)
        allure.attach(f"{host_to_bpe}/do/fs/{ei_cpid}", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return request

    #
    # @staticmethod
    # @allure.step('Prepared request: update FinancialSource')
    # def update_fs(host_of_request, ei_ocid, fs_id, fs_token, access_token, x_operation_id, payload, test_mode=False):
    #     fs = requests.post(
    #         url=host_of_request + f"/do/fs/{ei_ocid}/{fs_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': fs_token},
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/fs/{ei_ocid}/{fs_id}", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return fs

    @staticmethod
    @allure.step('# Prepared request: create Planing notice.')
    def create_pn_process(host_to_bpe, access_token, x_operation_id, payload, country, language, pmd, testMode=False):
        request = requests.post(
            url=f"{host_to_bpe}/do/pn",
            params={
                "testMode": testMode,
                "country": country,
                "lang": language,
                "pmd": pmd
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "Content-Type": "application/json"},
            json=payload)
        allure.attach(f"{host_to_bpe}/do/pn", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return request

    @staticmethod
    @allure.step('# Prepared request: create Aggregated Plan.')
    def create_ap_process(host_to_bpe, access_token, x_operation_id, payload, country, language, pmd, testMode=False):
        request = requests.post(
            url=f"{host_to_bpe}/do/ap",
            params={
                "testMode": testMode,
                "country": country,
                "lang": language,
                "pmd": pmd
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "Content-Type": "application/json"},
            json=payload)
        allure.attach(f"{host_to_bpe}/do/ap", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return request

    @staticmethod
    @allure.step('# Prepared request: update Aggregated Plan.')
    def update_ap_process(host_to_bpe, ap_cpid, ap_ocid, access_token, x_operation_id, ap_token, payload,
                          testMode=False):
        request = requests.post(
            url=f"{host_to_bpe}/do/ap/{ap_cpid}/{ap_ocid}",
            params={
                "testMode": testMode
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "X-TOKEN": ap_token,
                "Content-Type": "application/json"},
            json=payload)
        allure.attach(f"{host_to_bpe}/do/ap/{ap_cpid}/{ap_ocid}", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return request

    @staticmethod
    @allure.step('# Prepared request: do Outsourcing Plan.')
    def do_outsourcing_process(host_to_bpe, access_token, x_operation_id, ap_cpid, ap_ocid, pn_cpid, pn_ocid,
                               pn_token, testMode=False):
        request = requests.post(
            url=f"{host_to_bpe}/do/outsourcing/{pn_cpid}/{pn_ocid}",
            params={
                "testMode": testMode,
                "FA": ap_cpid,
                "AP": ap_ocid
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "X-TOKEN": pn_token,
                "Content-Type": "application/json"}
        )
        allure.attach(f"{host_to_bpe}/do/outsourcing/{pn_cpid}/{pn_ocid}", 'URL')
        return request

    @staticmethod
    @allure.step('# Prepared request: do Relation Aggregated Plan.')
    def do_relation_proces(host_to_bpe, access_token, x_operation_id, pn_cpid, pn_ocid, ap_cpid, ap_ocid,
                           ap_token, testMode=False):
        request = requests.post(
            url=f"{host_to_bpe}/do/relation/{ap_cpid}/{ap_ocid}",
            params={
                "testMode": testMode,
                "CP": pn_cpid,
                "PN": pn_ocid
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "X-TOKEN": ap_token,
                "Content-Type": "application/json"}
        )
        allure.attach(f"{host_to_bpe}/do/relation/{ap_cpid}/{ap_ocid}", 'URL')
        return request

    @staticmethod
    @allure.step('# Prepared request: create Framework Establishment.')
    def create_fe_process(host_to_bpe, access_token, x_operation_id, ap_cpid, ap_ocid, ap_token, payload,
                          testMode=False):
        """Send request for 'FE process'."""

        request = requests.post(
            url=f"{host_to_bpe}/do/fe/{ap_cpid}/{ap_ocid}",
            params={
                "testMode": testMode
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "X-TOKEN": ap_token,
                "Content-Type": "application/json"},
            json=payload
        )
        allure.attach(f"{host_to_bpe}/do/fe/{ap_cpid}/{ap_ocid}", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return request

    @staticmethod
    @allure.step('# Prepared request: Amend Framework Establishment.')
    def amend_fe_process(host_to_bpe, access_token, x_operation_id, ap_cpid, ap_ocid, ap_token, payload,
                         testMode=False):
        """Send request for 'Amend FE process'."""

        request = requests.post(
            url=f"{host_to_bpe}/amend/fe/{ap_cpid}/{ap_ocid}",
            params={
                "testMode": testMode
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "X-TOKEN": ap_token,
                "Content-Type": "application/json"},
            json=payload
        )

        allure.attach(f"{host_to_bpe}/amend/fe/{ap_cpid}/{ap_ocid}", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return request

    @staticmethod
    @allure.step('# Prepared request: Create Submission .')
    def create_submission_process(host_to_bpe, access_token, x_operation_id, ap_cpid, ap_ocid, payload,
                                  test_mode=False):
        """Send request for 'Create Submission process'."""

        request = requests.post(
            url=f"{host_to_bpe}/do/submission/{ap_cpid}/{ap_ocid}",
            params={
                "testMode": test_mode
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "Content-Type": "application/json"},
            json=payload
        )

        allure.attach(f"{host_to_bpe}/do/submission/{ap_cpid}/{ap_ocid}", 'URL')
        allure.attach(json.dumps(payload), 'Prepared payload')
        return request

    @staticmethod
    @allure.step('# Prepared request: Withdraw Submission .')
    def withdraw_submission_process(host_to_bpe, access_token, x_operation_id, ap_cpid, ap_ocid, submission_id,
                                    submission_token, test_mode=False):
        """Send request for 'Withdraw Submission process'."""

        request = requests.post(
            url=f"{host_to_bpe}/cancel/submission/{ap_cpid}/{ap_ocid}/{submission_id}",
            params={
                "testMode": test_mode
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-OPERATION-ID": x_operation_id,
                "Content-Type": "application/json",
                "X-TOKEN": submission_token}
        )

        allure.attach(f"{host_to_bpe}/cancel/submission/{ap_cpid}/{ap_ocid}/{submission_id}", 'URL')
        return request

    # @staticmethod
    # @allure.step('Prepared request: create PN_release')
    # def createPn(host_of_request, access_token, x_operation_id, country,
    #              language, pmd, payload, test_mode=False):
    #     pn = requests.post(
    #         url=host_of_request + f"/do/pn",
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json'
    #         },
    #         params={
    #             'country': country,
    #             'lang': language,
    #             'pmd': pmd,
    #             'testMode': test_mode
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/pn", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return pn
    #
    # @staticmethod
    # @allure.step('Prepared request: update PN_release')
    # def update_pn(host_of_request, access_token, x_operation_id, pn_ocid, pn_id, pn_token, payload, test_mode=False):
    #     pn = requests.post(
    #         url=host_of_request + f"/do/pn/{pn_ocid}/{pn_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/pn", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return pn
    #
    # @staticmethod
    # @allure.step('Prepared request: cancel PN_release')
    # def cancel_pn(host_of_request, access_token, x_operation_id, pn_ocid, pn_id, pn_token, test_mode=False):
    #     pn = requests.post(
    #         url=host_of_request + f"/cancel/pn/{pn_ocid}/{pn_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         })
    #     allure.attach(host_of_request + f"/cancel/pn", 'URL')
    #     return pn
    #
    # @staticmethod
    # @allure.step('Prepared request: create CnOnPn')
    # def createCnOnPn(host_of_request, access_token, x_operation_id, pn_ocid, pn_id, pn_token, payload,
    #                  test_mode=False):
    #     cn = requests.post(
    #         url=host_of_request + f"/do/cn/{pn_ocid}/{pn_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/cn", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return cn
    #
    # @staticmethod
    # @allure.step('Prepared request: update CnOnPn')
    # def update_cnonpn(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, pn_token, payload,
    #                   test_mode=False):
    #     cn = requests.post(
    #         url=host_of_request + f"/do/cn/{pn_ocid}/{tender_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/cn", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return cn
    #
    # @staticmethod
    # @allure.step('Prepared request: create Enquiry')
    # def create_enquiry(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, payload, test_mode=False):
    #     enquiry = requests.post(
    #         url=host_of_request + f"/do/enquiry/{pn_ocid}/{tender_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json'
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/enquiry", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return enquiry
    #
    # @staticmethod
    # @allure.step('Prepared request: create Answer')
    # def create_answer(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, enquiry_id, enquiry_token,
    #                   payload, test_mode=False):
    #     answer = requests.post(
    #         url=host_of_request + f"/do/enquiry/{pn_ocid}/{tender_id}/{enquiry_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': enquiry_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/enquiry", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return answer
    #
    # @staticmethod
    # @allure.step('Prepared request: create Bid')
    # def submit_bid(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, payload, test_mode=False):
    #     bid = requests.post(
    #         url=host_of_request + f"/do/bid/{pn_ocid}/{tender_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json'
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/bid", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return bid
    #
    # @staticmethod
    # @allure.step('Prepared request: withdraw Bid')
    # def withdraw_bid(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, bid_id, bid_token,
    #                  test_mode=False):
    #     bid = requests.post(
    #         url=host_of_request + f"/cancel/bid/{pn_ocid}/{tender_id}/{bid_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': bid_token
    #         })
    #     allure.attach(host_of_request + f"/cancel/bid", 'URL')
    #     return bid
    #
    # @staticmethod
    # @allure.step('Prepared request: create Declare non conflict interest')
    # def create_declare_non_conflict_interest(host_of_request, access_token, x_operation_id, pn_ocid, tender_id,
    #                                          award_id, award_token, payload,
    #                                          test_mode=False):
    #     declaration = requests.post(
    #         url=host_of_request + f"/do/declaration/{pn_ocid}/{tender_id}/{award_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': award_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/declaration", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return declaration
    #
    # @staticmethod
    # @allure.step('Prepared request: award consideration')
    # def do_award_consideration(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, award_id,
    #                            award_token, test_mode=False):
    #     consideration = requests.post(
    #         url=host_of_request + f"/do/consideration/{pn_ocid}/{tender_id}/{award_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': award_token
    #         })
    #     allure.attach(host_of_request + f"/do/consideration", 'URL')
    #     return consideration
    #
    # @staticmethod
    # @allure.step('Prepared request: award consideration')
    # def do_award_evaluation(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, award_id,
    #                         award_token, payload, test_mode=False):
    #     consideration = requests.post(
    #         url=host_of_request + f"/do/award/{pn_ocid}/{tender_id}/{award_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': award_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/award", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return consideration
    #
    # @staticmethod
    # @allure.step('Prepared request: protocol')
    # def do_protocol(host_of_request, access_token, x_operation_id, pn_ocid, pn_token, tender_id, lot_id,
    #                 test_mode=False):
    #     protocol = requests.post(
    #         url=host_of_request + f"/do/protocol/{pn_ocid}/{tender_id}/{lot_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         })
    #     allure.attach(host_of_request + f"/do/protocol", 'URL')
    #     return protocol
    #
    # @staticmethod
    # @allure.step('Prepared request: create Submission')
    # def create_submission(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, payload, test_mode=False):
    #     submission = requests.post(
    #         url=host_of_request + f"/do/submission/{pn_ocid}/{tender_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json'
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/submission", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return submission
    #
    # @staticmethod
    # @allure.step('Prepared request: create QualificationDeclaration')
    # def create_qualification(host_of_request, access_token, x_operation_id, pn_ocid, tender_id, qualification_id,
    #                          qualification_token, payload, test_mode=False):
    #     qualification = requests.post(
    #         url=host_of_request + f"/do/qualification/{pn_ocid}/{tender_id}/{qualification_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'X-TOKEN': qualification_token,
    #             'Content-Type': 'application/json'
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/qualification", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return qualification
    #
    # @staticmethod
    # @allure.step('Prepared request: create Declare non conflict interest')
    # def create_declaration_qualification_non_conflict_interest(
    #         host_of_request, access_token, x_operation_id, pn_ocid, tender_id, qualification_id, qualification_token,
    #         payload, test_mode=False):
    #     declaration = requests.post(
    #         url=host_of_request + f"/do/declaration/qualification/{pn_ocid}/{tender_id}/{qualification_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': qualification_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/declaration/qualification", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return declaration
    #
    # @staticmethod
    # @allure.step('Prepared request: award consideration')
    # def create_consideration_qualification(host_of_request, access_token, x_operation_id, pn_ocid, tender_id,
    #                                        qualification_id, qualification_token, test_mode=False):
    #     consideration = requests.post(
    #         url=host_of_request + f"/do/consideration/qualification/{pn_ocid}/{tender_id}/{qualification_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': qualification_token
    #         })
    #     allure.attach(host_of_request + f"/do/consideration/qualification", 'URL')
    #     return consideration
    #
    # @staticmethod
    # @allure.step('Prepared request: award consideration')
    # def create_qualification_protocol(host_of_request, access_token, x_operation_id, pn_ocid, pn_token, tender_id,
    #                                   test_mode=False):
    #     protocol = requests.post(
    #         url=host_of_request + f"/do/protocol/qualification/{pn_ocid}/{tender_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         })
    #     allure.attach(host_of_request + f"/do/protocol/qualification", 'URL')
    #     return protocol
    #
    # @staticmethod
    # @allure.step('Prepared request: award consideration')
    # def do_second_stage(host_of_request, access_token, x_operation_id, pn_ocid, pn_token, tender_id, payload,
    #                     test_mode=False):
    #     second_stage = requests.post(
    #         url=host_of_request + f"/do/secondStage/{pn_ocid}/{tender_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/secondStage", 'URL')
    #     allure.attach(json.dumps(payload), "Prepared payload")
    #     return second_stage
    #
    # @staticmethod
    # @allure.step('Prepared request: award consideration')
    # def withdraw_qualification_protocol(host_of_request, access_token, x_operation_id, pn_ocid, pn_token, tender_id,
    #                                     test_mode=False):
    #     protocol = requests.post(
    #         url=host_of_request + f"/cancel/protocol/{pn_ocid}/{tender_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         })
    #     allure.attach(host_of_request + f"/cancel/protocol", 'URL')
    #     return protocol
    #
    # @staticmethod
    # @allure.step('Prepared request: award consideration')
    # def apply_qualification_protocol(host_of_request, access_token, x_operation_id, pn_ocid, pn_token, tender_id,
    #                                  test_mode=False):
    #     protocol = requests.post(
    #         url=host_of_request + f"/apply/protocol/{pn_ocid}/{tender_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         })
    #     allure.attach(host_of_request + f"/apply/protocol", 'URL')
    #     return protocol
    #
    # @staticmethod
    # @allure.step('Prepared request: createAward')
    # def createAward_for_limitedProcedure(host_of_request, access_token, x_operation_id, pn_ocid, pn_token, tender_id,
    #                                      lot_id, payload, test_mode=False):
    #     award = requests.post(
    #         url=host_of_request + f"/do/award/{pn_ocid}/{tender_id}",
    #         params={
    #             'lotId': lot_id,
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': pn_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/award/{pn_ocid}/{tender_id}", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return award
    #
    # @staticmethod
    # @allure.step('Prepared request: evaluateAward')
    # def evaluateAward_for_limitedProcedure(host_of_request, access_token, x_operation_id, pn_ocid,
    #                                        tender_id, award_id, award_token, payload, test_mode=False):
    #     award = requests.post(
    #         url=host_of_request + f"/do/award/{pn_ocid}/{tender_id}/{award_id}",
    #         params={
    #             'testMode': test_mode
    #         },
    #         headers={
    #             'Authorization': 'Bearer ' + access_token,
    #             'X-OPERATION-ID': x_operation_id,
    #             'Content-Type': 'application/json',
    #             'X-TOKEN': award_token
    #         },
    #         json=payload)
    #     allure.attach(host_of_request + f"/do/award/{pn_ocid}/{tender_id}/{award_id}", 'URL')
    #     allure.attach(json.dumps(payload), 'Prepared payload')
    #     return award
