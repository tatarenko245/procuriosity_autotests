import allure
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster


# yield  то эе самое что и return, только идет по интерациям
class CassandraSession:
    def __init__(self, cassandra_username, cassandra_password, cassandra_cluster):
        auth_provider = PlainTextAuthProvider(
            username=cassandra_username,
            password=cassandra_password
        )
        self.cluster = Cluster([cassandra_cluster], auth_provider=auth_provider)
        self.ocds_keyspace = self.cluster.connect('ocds')

    def create_ei_process_cleanup_table_of_services(self, ei_id):
        return self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{ei_id}';").one(), \
               self.ocds_keyspace.execute(f"DELETE FROM budget_ei WHERE cp_id='{ei_id}';"), \
               self.ocds_keyspace.execute(f"DELETE FROM notice_budget_release WHERE cp_id='{ei_id}';"), \
               self.ocds_keyspace.execute(f"DELETE FROM notice_budget_offset WHERE cp_id='{ei_id}';"), \
               self.ocds_keyspace.execute(f"DELETE FROM notice_budget_compiled_release WHERE cp_id='{ei_id}';")

    def cleanup_steps_of_process(self, operation_id):
        yield
        get_process_id = self.ocds_keyspace.execute(
            f"SELECT * FROM orchestrator_operation WHERE operation_id = '{operation_id}';").one()
        process_id = get_process_id.process_id
        self.ocds_keyspace.execute(f"DELETE FROM orchestrator_operation_step WHERE process_id = '{process_id}';")

    def create_fs_process_cleanup_table_of_services(self, ei_id):
        return self.ocds_keyspace.execute(f"DELETE FROM orchestrator_context WHERE cp_id='{ei_id}';").one(), \
               self.ocds_keyspace.execute(f"DELETE FROM budget_ei WHERE cp_id='{ei_id}';"), \
               self.ocds_keyspace.execute(f"DELETE FROM budget_fs WHERE cp_id='{ei_id}';"), \
               self.ocds_keyspace.execute(f"DELETE FROM notice_budget_release WHERE cp_id='{ei_id}';"), \
               self.ocds_keyspace.execute(f"DELETE FROM notice_budget_offset WHERE cp_id='{ei_id}';"), \
               self.ocds_keyspace.execute(f"DELETE FROM notice_budget_compiled_release WHERE cp_id='{ei_id}';")

    def get_orchestrator_operation_step_by_x_operation_id(self, operation_id):
        rows_1 = self.ocds_keyspace.execute(
            f"SELECT * FROM orchestrator_operation WHERE operation_id = '{operation_id}';").one()
        process_id = rows_1.process_id
        steps = f"SELECT * FROM {self.ocds_keyspace.execute}.orchestrator_operation_step " \
               f"WHERE process_id = '{process_id}' ALLOW FILTERING;"
        with allure.step('Steps from Casandra DataBase'):
            allure.attach(steps, "Cassandra DataBase: steps of process")
        return steps
