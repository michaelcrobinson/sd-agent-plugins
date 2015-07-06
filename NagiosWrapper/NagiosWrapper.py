# add os functions and variables calling environment variables.
# test everything in a python console!

import subprocess
import os

pg_dbname = os.environ.get('POSTGRESQL_DATABASE')
pg_user = os.environ.get('POSTGRESQL_USERNAME')

# Need warning and critical thresholds for each type of check

# This can be shared with table and btree bloat thresholds, express in %
pg_bloat_warn = os.environ.get('PG_TABLEBLOAT_WARNING')
pg_bloat_crit = os.environ.get('PG_TABLEBLOAT_CRITICAL')


# this can be shared with Last Vacuum and Last Analyze thresholds, express in time (s, M, H)
pg_lastvac_warn = os.environ.get('PG_LASTVACUUM_WARNING')
pg_lastvac_crit = os.environ.get('PG_LASTVACUUM_CRITICAL')

# express in size (B, KB, MB)
pg_idle_warn = os.environ.get('PG_IDLE_WARNING')
pg_idle_crit = os.environ.get('PG_IDLE_CRITICAL')

# express in count; warn should be above average or half of max, crit a bit below max connections
pg_backend_warn = os.environ.get('PG_BACKEND_WARNING')
pg_backend_crit = os.environ.get('PG_BACKEND_CRITICAL')

###############################################
# This command list includes the following checks:
# connection - validate the database is up and accessible
# configuration - validate the database configuration
# table_bloat - get a list of tables that have exceeded a certain amount of bload
# btree_bloat - get a list of indexes that have exceeded a certain amount of bload
# last_vacuum - get a list of tables/indexes that have not been vacuumed (auto or not) within a period of time
# last_analyze - get a list of tables/indexes that have not been analyzed (auto or not) within a period of time
# oldest_idlexact - count the number of idle connections on the database
# backends - number of connections compared to maximum
# backends_status - number of connections and relation to their status
#
# To add additional commands, see the output of "check_pgactivity --list" for all available checks


nagiosPluginsCommandLines = [
    "/usr/local/src/check_pgactivity/check_pgactivity --username " + pg_user + " --dbname " + pg_dbname + " -s connection",
    "/usr/local/src/check_pgactivity/check_pgactivity --username " + pg_user + " --dbname " + pg_dbname + " -s configuration",
    "/usr/local/src/check_pgactivity/check_pgactivity --username " + pg_user + " --dbname " + pg_dbname + " -s table_bloat  -w " + pg_bloat_warn + " -c " + pg_bloat_crit,
    "/usr/local/src/check_pgactivity/check_pgactivity --username " + pg_user + " --dbname " + pg_dbname + " -s btree_bloat  -w " + pg_bloat_warn + " -c " + pg_bloat_crit,
    "/usr/local/src/check_pgactivity/check_pgactivity --username " + pg_user + " --dbname " + pg_dbname + " -s last_vacuum  -w " + pg_lastvac_warn + " -c " + pg_lastvac_crit,
    "/usr/local/src/check_pgactivity/check_pgactivity --username " + pg_user + " --dbname " + pg_dbname + " -s last_analyze  -w " + pg_lastvac_warn + " -c " + pg_lastvac_crit,
    "/usr/local/src/check_pgactivity/check_pgactivity --username " + pg_user + " --dbname " + pg_dbname + " -s oldest_idlexact  -w " + pg_idle_warn + " -c " + pg_idle_crit,
    "/usr/local/src/check_pgactivity/check_pgactivity --username " + pg_user + " --dbname " + pg_dbname + " -s backends -w " + pg_backend_warn + " -c " pg_backend_crit,
    "/usr/local/src/check_pgactivity/check_pgactivity --username " + pg_user + " --dbname " + pg_dbname + " -s backends_status"
]


class NagiosWrapper:
    def __init__(self, agentConfig, checksLogger, rawConfig):
        self.agentConfig = agentConfig
        self.checksLogger = checksLogger
        self.rawConfig = rawConfig

    def run(self):
        data = {}
        for pluginCommandLine in nagiosPluginsCommandLines:

            # subprocess needs a list containing the command and
            # its parameters
            pluginCommandLineList = pluginCommandLine.split(" ")
            # the check command to retrieve it's name
            pluginCommand = pluginCommandLineList[0]

            p = subprocess.Popen(
                pluginCommandLineList,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, err = p.communicate()

            self.checksLogger.debug(
                'Output of {0}: {1}'.format(pluginCommand, out)
            )

            if err:
                self.checksLogger.error(
                    'Error executing {0}: {1}'.format(pluginCommand, err)
                )

            # the check command name = return value:
            # 0 - OK
            # 1 - WARNING
            # 2 - CRITICAL
            # 3 - UNKNOWN
            data[pluginCommand.split("/")[-1]] = p.returncode

            # add performance data if it exists
            perfData = out.split("|")
            if len(perfData) > 1:
                data[perfData[1].split(";")[0].split("=")[0]] = perfData[
                    1].split(";")[0].split("=")[1]

        return data
