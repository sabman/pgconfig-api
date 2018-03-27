import unittest
import tornado.testing
import tests.base


class PGBadgerTestCase(tests.base.DefaultTestCase):
    def test_conf_stderr(self):
        self.run_test('conf', 'stderr')

    def test_conf_csvlog(self):
        self.run_test('conf', 'csvlog')

    def test_conf_syslog(self):
        self.run_test('conf', 'syslog')

    def test_alter_system_stderr(self):
        self.run_test('alter_system', 'stderr')

    def test_alter_system_csvlog(self):
        self.run_test('alter_system', 'csvlog')

    def test_alter_system_syslog(self):
        self.run_test('alter_system', 'syslog')

    def run_test(self, parameter_format, log_format):
        test_config = self.get_config()
        test_url = test_config[parameter_format][log_format]['url']
        expected_test_result = test_config[parameter_format][log_format][
            'content']

        response = self.fetch(test_url)
        self.assertEqual(response.code, 200)

        diff = '\n'
        diff += self.unidiff_output(response.body.strip(),
                                    expected_test_result.strip())
        self.assertEqual(response.body.strip(), expected_test_result.strip(),
                         diff)

    def get_config(self):
        test_data = dict()

        for parameter_format in ['conf', 'alter_system']:
            test_data[parameter_format] = dict()
            if parameter_format == 'conf':
                default_output = """
# Generated by PGConfig 2.0 beta
## http://pgconfig.org

# Logging configuration for pgbadger
logging_collector = on
log_checkpoints = on
log_connections = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0
lc_messages = 'C'

# Adjust the minimum time to collect data
log_min_duration_statement = '10s'
log_autovacuum_min_duration = 0
"""
            elif parameter_format == 'alter_system':
                default_output = """
-- Generated by PGConfig 2.0 beta
---- http://pgconfig.org

-- Logging configuration for pgbadger
ALTER SYSTEM SET logging_collector TO 'on';
ALTER SYSTEM SET log_checkpoints TO 'on';
ALTER SYSTEM SET log_connections TO 'on';
ALTER SYSTEM SET log_connections TO 'on';
ALTER SYSTEM SET log_disconnections TO 'on';
ALTER SYSTEM SET log_lock_waits TO 'on';
ALTER SYSTEM SET log_temp_files TO '0';
ALTER SYSTEM SET lc_messages TO 'C';

-- Adjust the minimum time to collect data
ALTER SYSTEM SET log_min_duration_statement TO '10s';
ALTER SYSTEM SET log_autovacuum_min_duration TO '0';
"""

            for log_format in ['stderr', 'csvlog', 'syslog']:

                test_data[parameter_format][log_format] = dict()
                expected_output = default_output

                test_data[parameter_format][log_format][
                    "url"] = '/v1/generators/pgbadger/get-config?format={}&log_format={}'.format(
                        parameter_format, log_format)

                if log_format == 'stderr':

                    if parameter_format == 'conf':
                        expected_output += """
# 'stderr' format configuration
log_destination = 'stderr'
log_line_preffix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
"""
                    elif parameter_format == 'alter_system':
                        expected_output += """
-- 'stderr' format configuration
ALTER SYSTEM SET log_destination TO 'stderr';
ALTER SYSTEM SET log_line_preffix TO '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';
"""

                elif log_format == 'csvlog':
                    if parameter_format == 'conf':
                        expected_output += """
# 'csvlog' format configuration
log_destination = 'csvlog'
"""
                    elif parameter_format == 'alter_system':
                        expected_output += """
-- 'csvlog' format configuration
ALTER SYSTEM SET log_destination TO 'csvlog';
"""

                elif log_format == 'syslog':
                    if parameter_format == 'conf':
                        expected_output += """
# 'syslog' format configuration
log_destination = 'syslog'
log_line_prefix = 'user=%u,db=%d,app=%a,client=%h '
syslog_facility = 'LOCAL0'
syslog_ident = 'postgres'
"""
                    elif parameter_format == 'alter_system':
                        expected_output += """
-- 'syslog' format configuration
ALTER SYSTEM SET log_destination TO 'syslog';
ALTER SYSTEM SET log_line_prefix TO 'user=%u,db=%d,app=%a,client=%h ';
ALTER SYSTEM SET syslog_facility TO 'LOCAL0';
ALTER SYSTEM SET syslog_ident TO 'postgres';
"""

                test_data[parameter_format][log_format][
                    "content"] = expected_output

        return test_data