import copy
import json
import time
import allure
import requests
from deepdiff import DeepDiff
from tests.utils.PayloadModel.Budget.Ei.ei_prepared_payload import EiPreparePayload
from tests.utils.PayloadModel.Budget.Fs.fs_prepared_payload import FsPreparePayload
from tests.utils.PayloadModel.RestrictedProcedure.CnOnPn.cnonpn_prepared_payload import CnOnPnPreparePayload
from tests.utils.PayloadModel.RestrictedProcedure.Pn.pn_prepared_payload import PnPreparePayload
from tests.utils.PayloadModel.RestrictedProcedure.Submission.submission_prepared_payload import SubmissionPreparePayload
from tests.utils.kafka_message import KafkaMessage
from tests.utils.my_requests import Requests
from tests.utils.platform_authorization import PlatformAuthorization


class TestCreateCn:
    @allure.title("Check Ev and MS releases data after CnOnPn creating without optional fields. \n"
                  "------------------------------------------------\n"
                  "create Ei: obligatory data model without items array;\n"
                  "create Fs: obligatory data model, treasury money;\n"
                  "create Pn: obligatory data model, without lots and items;\n"
                  "create CnOnPn: obligatory data model, with lots and items;\n")
    def test_check_pn_ms_releases_one(self, get_hosts, country, language, pmd, environment, connection_to_database):
        authorization = PlatformAuthorization(get_hosts[1])
        step_number = 1

        try:
            if environment == "dev":
                self.metadata_tender_url = "http://dev.public.eprocurement.systems/tenders"

            elif environment == "sandbox":
                self.metadata_tender_url = "http://public.eprocurement.systems/tenders"
        except ValueError:
            raise ValueError("Check your environment: You must use 'dev' or 'sandbox' environment in pytest command")

        with allure.step(f'# {step_number}. Authorization platform one: create Ei'):
            """
            Tender platform authorization for create expenditure item process.
            As result get Tender platform's access token and process operation-id.
            """
            create_ei_access_token = authorization.get_access_token_for_platform_one()
            create_ei_operation_id = authorization.get_x_operation_id(create_ei_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Ei'):
            """
            Send api request on BPE host for expenditure item creation.
            And save in variable ei_ocid.
            """
            ei_payload_class = copy.deepcopy(EiPreparePayload())
            create_ei_payload = ei_payload_class.create_ei_obligatory_data_model()

            Requests().create_ei(
                host_of_request=get_hosts[1],
                access_token=create_ei_access_token,
                x_operation_id=create_ei_operation_id,
                country=country,
                language=language,
                payload=create_ei_payload,
                test_mode=True)

            ei_feed_point_message = KafkaMessage(create_ei_operation_id).get_message_from_kafka()
            ei_ocid = ei_feed_point_message["data"]["outcomes"]["ei"][0]['id']
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Fs'):
            """
            Tender platform authorization for create financial source process.
            As result get Tender platform's access token and process operation-id.
            """
            create_fs_access_token = authorization.get_access_token_for_platform_one()
            create_fs_operation_id = authorization.get_x_operation_id(create_fs_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Fs'):
            """
            Send api request on BPE host for financial source creating.
            And save in variable fs_id.
            """
            time.sleep(1)
            fs_payload_class = copy.deepcopy(FsPreparePayload(ei_payload=create_ei_payload))
            create_fs_payload = fs_payload_class.create_fs_obligatory_data_model_treasury_money(
                ei_payload=create_ei_payload)

            Requests().create_fs(
                host_of_request=get_hosts[1],
                access_token=create_fs_access_token,
                x_operation_id=create_fs_operation_id,
                ei_ocid=ei_ocid,
                payload=create_fs_payload,
                test_mode=True)

            fs_feed_point_message = KafkaMessage(create_fs_operation_id).get_message_from_kafka()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Pn'):
            """
            Tender platform authorization for create planning notice process.
            As result get Tender platform's access token and process operation-id.
            """
            create_pn_access_token = authorization.get_access_token_for_platform_one()
            create_pn_operation_id = authorization.get_x_operation_id(create_pn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Pn'):
            """
            Send api request on BPE host for planning notice creating.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            And save in variable pn_ocid, pn_id, pn_token.
            """
            time.sleep(1)
            pn_payload_class = copy.deepcopy(PnPreparePayload(
                fs_payload=create_fs_payload,
                fs_feed_point_message=fs_feed_point_message))
            create_pn_payload = \
                pn_payload_class.create_pn_obligatory_data_model_without_lots_and_items_based_on_one_fs()

            Requests().create_pn(
                host_of_request=get_hosts[1],
                access_token=create_pn_access_token,
                x_operation_id=create_pn_operation_id,
                country=country,
                language=language,
                pmd=pmd,
                payload=create_pn_payload,
                test_mode=True)

            pn_feed_point_message = KafkaMessage(create_pn_operation_id).get_message_from_kafka()
            pn_ocid = pn_feed_point_message['data']['ocid']
            pn_id = pn_feed_point_message['data']['outcomes']['pn'][0]['id']
            pn_token = pn_feed_point_message['data']['outcomes']['pn'][0]['X-TOKEN']
            pn_url = pn_feed_point_message['data']['url']
            actual_ei_release_before_cn_creation = requests.get(
                url=f"{ei_feed_point_message['data']['url']}/{ei_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create CnOnPn'):
            """
            Tender platform authorization for create tender phase process.
            As result get Tender platform's access token and process operation-id.
            """
            create_cn_access_token = authorization.get_access_token_for_platform_one()
            create_cn_operation_id = authorization.get_x_operation_id(create_cn_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create CnOnPn'):
            """
            Send api request on BPE host for create tender phase process.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            try:
                """
                Get minSubmissionPeriodDuration value from dossier.rules for this testcase
                """
                min_submission_period_duration = int(connection_to_database.get_min_submission_period_duration_rules(
                    country=country,
                    pmd=pmd,
                    operation_type='all',
                    parameter='minSubmissionPeriodDuration'
                ))
            except Exception:
                raise Exception("Impossible to get minSubmissionPeriodDuration value from dossier.rules "
                                "for this testcase")

            cn_payload_class = copy.deepcopy(CnOnPnPreparePayload(host_for_services=get_hosts[2]))
            create_cn_payload = \
                cn_payload_class.create_cnonpn_obligatory_data_model(
                    actual_ei_release=actual_ei_release_before_cn_creation,
                    pre_qualification_period_end=min_submission_period_duration,
                    pn_payload=create_pn_payload)

            Requests().create_cnonpn(
                host_of_request=get_hosts[1],
                access_token=create_cn_access_token,
                x_operation_id=create_cn_operation_id,
                pn_ocid=pn_ocid,
                pn_id=pn_id,
                pn_token=pn_token,
                payload=create_cn_payload,
                test_mode=True)

            cn_feed_point_message = KafkaMessage(create_cn_operation_id).get_message_from_kafka()
            tp_id = cn_feed_point_message['data']['outcomes']['tp'][0]['id']
            actual_tp_release_before_submission_creating = requests.get(url=f"{pn_url}/{tp_id}").json()
            actual_ms_release_before_submission_creating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
            step_number += 1

        with allure.step(f'# {step_number}. Authorization platform one: create Submission'):
            """
            Tender platform authorization for create tender phase process.
            As result get Tender platform's access token and process operation-id.
            """
            create_submission_access_token = authorization.get_access_token_for_platform_one()
            create_submission_operation_id = authorization.get_x_operation_id(create_submission_access_token)
            step_number += 1

        with allure.step(f'# {step_number}. Send request to create Submission'):
            """
            Send api request on BPE host for create submission.
            Save synchronous result of sending the request and asynchronous result of sending the request.
            """
            time.sleep(1)
            submission_payload_class = copy.deepcopy(SubmissionPreparePayload())
            create_submission_payload = \
                submission_payload_class.create_submission_obligatory_data_model()

            synchronous_result_of_sending_the_request = Requests().create_submission(
                host_of_request=get_hosts[1],
                access_token=create_submission_access_token,
                x_operation_id=create_submission_operation_id,
                pn_ocid=pn_ocid,
                tender_id=tp_id,
                payload=create_submission_payload,
                test_mode=True)

            step_number += 1

        with allure.step(f'# {step_number}. See result'):
            """
            Check the results of TestCase.
            """

            with allure.step(f'# {step_number}.1. Check status code'):
                """
                Check the synchronous_result_of_sending_the_request.
                """
                with allure.step('Compare actual status code of sending the request and '
                                 'expected status code of sending request.'):
                    allure.attach(str(synchronous_result_of_sending_the_request.status_code),
                                  "Actual status code of sending the request.")
                    allure.attach(str(202), "Expected status code of sending request.")
                    assert str(synchronous_result_of_sending_the_request.status_code) == str(202)

            with allure.step(f'# {step_number}.2. Check message in feed point'):
                """
                Check the asynchronous_result_of_sending_the_request.
                """
                create_submission_feed_point_message = KafkaMessage(
                    create_submission_operation_id).get_message_from_kafka()

                allure.attach(str(create_submission_feed_point_message), 'Message in feed point')

                asynchronous_result_of_sending_the_request_was_checked = KafkaMessage(
                    create_submission_operation_id).create_submission_message_is_successful(
                    environment=environment,
                    kafka_message=create_submission_feed_point_message,
                    pn_ocid=pn_ocid,
                    tender_id=tp_id)

                try:
                    """
                    If asynchronous_result_of_sending_the_request was False, then return process steps by
                    operation-id.
                    """
                    if asynchronous_result_of_sending_the_request_was_checked is False:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_submission_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Compare actual asynchronous result of sending the request and '
                                 'expected asynchronous result of sending request.'):
                    allure.attach(str(asynchronous_result_of_sending_the_request_was_checked),
                                  "Actual asynchronous result of sending the request.")
                    allure.attach(str(True), "Expected asynchronous result of sending the request.")
                    assert str(asynchronous_result_of_sending_the_request_was_checked) == str(True)

            with allure.step(f'# {step_number}.3. Check TP release'):
                """
                Compare actual Tp release before submission creating and actual Tp release after submission creating.
                """
                allure.attach(str(json.dumps(actual_tp_release_before_submission_creating)),
                              "Actual TP release before submission creating")

                actual_tp_release_after_submission_creating = requests.get(url=f"{pn_url}/{tp_id}").json()
                allure.attach(str(json.dumps(actual_tp_release_after_submission_creating)),
                              "Actual TP release after submission creating")

                compare_releases = dict(DeepDiff(actual_tp_release_before_submission_creating,
                                                 actual_tp_release_after_submission_creating))
                expected_result = {}

                try:
                    """
                        If compare_releases !=expected_result, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        pass
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_submission_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing actual Tp release and expected Tp release.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing Tp releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Tp releases.")
                    assert str(compare_releases) == str(expected_result)

            with allure.step(f'# {step_number}.4. Check MS release'):
                """
                Compare actual Ms release before submission creating and actual Ms release after submission creating.
                """
                allure.attach(str(json.dumps(actual_ms_release_before_submission_creating)),
                              "Actual TP release before submission creating")

                actual_ms_release_after_submission_creating = requests.get(url=f"{pn_url}/{pn_ocid}").json()
                allure.attach(str(json.dumps(actual_ms_release_after_submission_creating)),
                              "Actual TP release after submission creating")

                compare_releases = dict(DeepDiff(actual_tp_release_before_submission_creating,
                                                 actual_tp_release_after_submission_creating))
                expected_result = {}

                try:
                    """
                        If TestCase was passed, then cLean up the database.
                        If TestCase was failed, then return process steps by operation-id.
                        """
                    if compare_releases == expected_result:
                        connection_to_database.ei_process_cleanup_table_of_services(ei_id=ei_ocid)

                        connection_to_database.fs_process_cleanup_table_of_services(ei_id=ei_ocid)

                        connection_to_database.pn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connection_to_database.cnonpn_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connection_to_database.submission_process_cleanup_table_of_services(pn_ocid=pn_ocid)

                        connection_to_database.cleanup_steps_of_process(operation_id=create_ei_operation_id)

                        connection_to_database.cleanup_steps_of_process(operation_id=create_fs_operation_id)

                        connection_to_database.cleanup_steps_of_process(operation_id=create_pn_operation_id)

                        connection_to_database.cleanup_steps_of_process(operation_id=create_cn_operation_id)

                        connection_to_database.cleanup_steps_of_process(operation_id=create_submission_operation_id)
                    else:
                        with allure.step('# Steps from Casandra DataBase'):
                            steps = connection_to_database.get_bpe_operation_step_by_operation_id(
                                operation_id=create_submission_operation_id)
                            allure.attach(steps, "Cassandra DataBase: steps of process")
                except ValueError:
                    raise ValueError("Can not return BPE operation step")

                with allure.step('Check a difference of comparing Ms release before cn creating and '
                                 'Ms release after cn creating.'):
                    allure.attach(str(compare_releases),
                                  "Actual result of comparing MS releases.")
                    allure.attach(str(expected_result),
                                  "Expected result of comparing Ms releases.")
                    assert str(compare_releases) == str(expected_result)