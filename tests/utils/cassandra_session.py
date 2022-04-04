class CassandraSession:
    @staticmethod
    def cleanup_table_of_services_for_expenditureItem(connect_to_ocds, cp_id):
        connect_to_ocds.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{cp_id}';").one()
        connect_to_ocds.execute(f"DELETE FROM budget_ei WHERE cp_id='{cp_id}';")
        connect_to_ocds.execute(f"DELETE FROM notice_budget_release WHERE cp_id='{cp_id}';")
        connect_to_ocds.execute(f"DELETE FROM notice_budget_offset WHERE cp_id='{cp_id}';")
        connect_to_ocds.execute(f"DELETE FROM notice_budget_compiled_release WHERE cp_id='{cp_id}';")

    @staticmethod
    def get_processId_by_operationId(connect_to_ocds, operation_id):
        get_process_id = connect_to_ocds.execute(
            f"SELECT * FROM orchestrator_operation WHERE operation_id = '{operation_id}';").one()
        process_id = get_process_id.process_id
        return process_id

    @staticmethod
    def cleanup_ocds_orchestratorOperationStep_by_operationId(connect_to_ocds, operation_id):
        get_process_id = connect_to_ocds.execute(
            f"SELECT * FROM orchestrator_operation WHERE operation_id = '{operation_id}';").one()

        process_id = get_process_id.process_id
        connect_to_ocds.execute(f"DELETE FROM orchestrator_operation_step WHERE process_id = '{process_id}';")

    @staticmethod
    def cleanup_orchestrator_steps_by_cpid(connect_to_orchestrator, cpid):
        connect_to_orchestrator.execute(f"DELETE FROM steps WHERE cpid = '{cpid}' ALLOW FILTERING;")

    @staticmethod
    def get_maxDurationOfFA_from_access_rules(connect_to_access, country, pmd):
        value = connect_to_access.execute(
            f"""SELECT value FROM access.rules WHERE 
            country ='{country}' and pmd='{pmd}' and operation_type='all' and parameter ='maxDurationOfFA' 
            ALLOW FILTERING;""").one()
        return value.value

    @staticmethod
    def cleanup_table_of_services_for_aggregatedPlan(connect_to_ocds, connect_to_access, ap_ocid):
        connect_to_ocds.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{ap_ocid}';").one()
        connect_to_access.execute(f"DELETE FROM tenders WHERE cpid='{ap_ocid}';")
        connect_to_ocds.execute(f"DELETE FROM notice_release WHERE cp_id='{ap_ocid}';")
        connect_to_ocds.execute(f"DELETE FROM notice_offset WHERE cp_id='{ap_ocid}';")
        connect_to_ocds.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{ap_ocid}';")

    # def fs_process_cleanup_table_of_services(self, ei_id):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{ei_id}';").one()
    #     self.ocds_keyspace.execute(f"DELETE FROM budget_ei WHERE cp_id='{ei_id}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM budget_fs WHERE cp_id='{ei_id}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_budget_release WHERE cp_id='{ei_id}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_budget_offset WHERE cp_id='{ei_id}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_budget_compiled_release WHERE cp_id='{ei_id}';")
    #
    # def pn_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.ocds_keyspace.execute(f"DELETE FROM budget_fs WHERE cp_id='{pn_ocid}';")
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def cnonpn_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.clarification_keyspace.execute(f"DELETE FROM periods WHERE cpid='{pn_ocid}';")
    #     self.auctions_keyspace.execute(f"DELETE FROM auctions WHERE cpid='{pn_ocid}';")
    #     self.submission_keyspace.execute(f"DELETE FROM periods WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def bid_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.submission_keyspace.execute(f"DELETE FROM bids WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def submission_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.clarification_keyspace.execute(f"DELETE FROM periods WHERE cpid='{pn_ocid}';")
    #     self.dossier_keyspace.execute(f"DELETE FROM submission WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def qualification_declaration_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM qualifications WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM period WHERE cpid='{pn_ocid}';")
    #     self.dossier_keyspace.execute(f"DELETE FROM submission WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def tender_period_end_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.evaluation_keyspace.execute(f"DELETE FROM awards WHERE cpid='{pn_ocid}';")
    #     self.submission_keyspace.execute(f"DELETE FROM bids WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def enquiry_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.clarification_keyspace.execute(f"DELETE FROM enquiries WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def get_bpe_operation_step_by_operation_id(self, operation_id):
    #     rows_1 = self.ocds_keyspace.execute(
    #         f"SELECT * FROM orchestrator_operation WHERE operation_id = '{operation_id}';").one()
    #     process_id = rows_1.process_id
    #     steps = f"SELECT * FROM ocds.orchestrator_operation_step WHERE process_id = '{process_id}' ALLOW FILTERING;"
    #     return steps
    #
    # def get_offset_extended_from_clarification_rules(self, country, pmd):
    #     data = self.clarification_keyspace.execute(f"SELECT value FROM rules WHERE country='{country}' "
    #                                                f"AND pmd='{pmd}' AND operation_type='all' "
    #                                                f"AND parameter='offsetExtended';").one()
    #     return data.value
    #
    # def get_bid_status_from_submission_bids_by_on_ocid(self, pn_ocid):
    #     get_bid_status = self.submission_keyspace.execute(
    #         f"SELECT status FROM bids WHERE cpid = '{pn_ocid}';").one()
    #     process_id = get_bid_status.status
    #     return process_id
    #
    # def get_bpe_operation_step_by_operation_id_from_orchestrator(self, operation_id):
    #     steps = self.orchestrator_keyspace.execute(
    #         f"SELECT * FROM steps WHERE operation_id = '{operation_id}' ALLOW FILTERING;").one()
    #     return steps
    #
    # def get_min_bids_from_evaluation_rules(self, country, pmd, operation_type, parameter):
    #     value = self.evaluation_keyspace.execute(
    #         f"""SELECT "value" FROM rules WHERE "country"='{country}' AND "pmd" = '{pmd}' AND
    #         "operation_type" = '{operation_type}' AND "parameter" = '{parameter}';""").one()
    #     return value.value
    #
    # def set_min_bids_from_evaluation_rules(self, value, country, pmd, operation_type, parameter):
    #     self.evaluation_keyspace.execute(
    #         f"""UPDATE rules SET value = '{value}' WHERE "country"='{country}' AND "pmd" ='{pmd}'
    #         AND "operation_type" = '{operation_type}' AND "parameter" = '{parameter}';""").one()
    #
    # def get_bids_from_submission_bids(self, cpid, bid_id):
    #     value = self.submission_keyspace.execute(
    #         f"SELECT * FROM submission.bids WHERE cpid = '{cpid}' AND id = '{bid_id}' ALLOW FILTERING;"
    #     ).one()
    #     return value.json_data
    #
    # def get_min_bids_from_submission_rules(self, country, pmd, operation_type, parameter):
    #     value = self.submission_keyspace.execute(
    #         f"""SELECT "value" FROM rules WHERE "country"='{country}' AND "pmd" = '{pmd}' AND
    #         "operation_type" = '{operation_type}' AND "parameter" = '{parameter}';""").one()
    #     return value.value
    #
    # def get_offset_from_clarification_rules(self, country, pmd, operation_type, parameter):
    #     value = self.clarification_keyspace.execute(
    #         f"""SELECT "value" FROM rules WHERE "country"='{country}' AND "pmd" = '{pmd}' AND
    #         "operation_type" = '{operation_type}' AND "parameter" = '{parameter}';""").one()
    #     return value.value
    #
    # def get_offset_from_submission_rules(self, country, pmd, operation_type, parameter):
    #     value = self.submission_keyspace.execute(
    #         f"""SELECT "value" FROM rules WHERE "country"='{country}' AND "pmd" = '{pmd}' AND
    #         "operation_type" = '{operation_type}' AND "parameter" = '{parameter}';""").one()
    #     return value.value
    #
    # def set_min_bids_from_submission_rules(self, value, country, pmd, operation_type, parameter):
    #     self.submission_keyspace.execute(
    #         f"""UPDATE rules SET value = '{value}' WHERE "country"='{country}' AND "pmd" ='{pmd}'
    #         AND "operation_type" = '{operation_type}' AND "parameter" = '{parameter}';""").one()
    #
    # def declaration_cleanup_table_of_services(self, pn_ocid, ev_id):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{ev_id}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.evaluation_keyspace.execute(f"DELETE FROM awards WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def award_consideration_cleanup_table_of_services(self, pn_ocid, ev_id):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{ev_id}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.evaluation_keyspace.execute(f"DELETE FROM awards WHERE cpid='{pn_ocid}';")
    #     self.submission_keyspace.execute(f"DELETE FROM bids WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def award_evaluation_cleanup_table_of_services(self, pn_ocid, ev_id):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{ev_id}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.evaluation_keyspace.execute(f"DELETE FROM awards WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def qualification_consideration_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM qualifications WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM period WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def qualification_protocol_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM qualifications WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM period WHERE cpid='{pn_ocid}';")
    #     self.dossier_keyspace.execute(f"DELETE FROM submission WHERE cpid='{pn_ocid}';")
    #     self.dossier_keyspace.execute(f"DELETE FROM period WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def withdraw_qualification_protocol_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM qualifications WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM period WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def apply_qualification_protocol_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM qualifications WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM period WHERE cpid='{pn_ocid}';")
    #     self.submission_keyspace.execute(f"DELETE FROM bids WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def qualification_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM qualifications WHERE cpid='{pn_ocid}';")
    #     self.qualification_keyspace.execute(f"DELETE FROM period WHERE cpid='{pn_ocid}';")
    #     self.dossier_keyspace.execute(f"DELETE FROM submission WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def createAward_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.evaluation_keyspace.execute(f"DELETE FROM awards WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def evaluateAward_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.evaluation_keyspace.execute(f"DELETE FROM awards WHERE cpid='{pn_ocid}';")
    #     self.contracting_keyspace.execute(f"DELETE FROM awards WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def protocol_process_cleanup_table_of_services(self, pn_ocid):
    #     self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{pn_ocid}';").one()
    #     self.access_keyspace.execute(f"DELETE FROM tenders WHERE cpid='{pn_ocid}';")
    #     self.evaluation_keyspace.execute(f"DELETE FROM awards WHERE cpid='{pn_ocid}';")
    #     self.contracting_keyspace.execute(f"DELETE FROM awards WHERE cpid='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_release WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_offset WHERE cp_id='{pn_ocid}';")
    #     self.ocds_keyspace.execute(f"DELETE FROM notice_compiled_release WHERE cp_id='{pn_ocid}';")
    #
    # def get_min_submission_period_duration_rules(self, country, pmd, operation_type, parameter):
    #     value = self.dossier_keyspace.execute(
    #         f"""SELECT "value" FROM rules WHERE "country"='{country}' AND "pmd" = '{pmd}' AND
    #         "operation_type" = '{operation_type}' AND "parameter" = '{parameter}';""").one()
    #     return value.value
    #
    # def get_period_shift_rules(self, country, pmd, operation_type, parameter):
    #     value = self.clarification_keyspace.execute(
    #         f"""SELECT "value" FROM rules WHERE "country"='{country}' AND "pmd" = '{pmd}' AND
    #         "operation_type" = '{operation_type}' AND "parameter" = '{parameter}';""").one()
    #     return value.value
    #
    # def get_min_submissions_from_dossier_rules(self, country, pmd, operation_type, parameter):
    #     value = self.dossier_keyspace.execute(
    #         f"""SELECT "value" FROM rules WHERE "country"='{country}' AND "pmd" = '{pmd}' AND
    #         "operation_type" = '{operation_type}' AND "parameter" = '{parameter}';""").one()
    #     return value.value
    #

    def __del__(self):
        print(f"The instance of CassandraSession class {__name__} was deleted.")
