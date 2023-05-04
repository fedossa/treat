# --- Header -------------------------------------------------------------------
# See LICENSE file for details
#
# This code pulls data from WRDS
# ------------------------------------------------------------------------------
import logging
import os
from psycopg2 import connect, OperationalError
from getpass import getpass

import hydra
import pandas as pd


# pylint: disable=E1120

log = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="../../conf", config_name="config")
def main(cfg):
    secrets = cfg['secrets']
    pull_wrds_params = cfg['pull_data']['pull_wrds_params']
    wrds_login = {} if secrets['prompt'] else secrets['wrds_authentication']
    dyn_vars, stat_vars, cs_filter = pull_wrds_params.values()

    wrds_us = pull_wrds_data(dyn_vars, stat_vars, cs_filter, wrds_login)
    wrds_us.to_csv(cfg['pull_data']['cstat_us_sample'], index=False)


def pull_wrds_data(dyn_vars, stat_vars, cs_filter, wrds_authentication):
    '''
    Pulls WRDS access data.
    '''
    wrds = connect_to_wrds(wrds_authentication)

    cur = wrds.cursor()

    log.info('Logged on to WRDS ...')

    dyn_var_str = ', '.join(dyn_vars)

    stat_var_str = ', '.join(stat_vars)

    log.info("Pulling dynamic Compustat data ... ")
    cur.execute(f"SELECT {dyn_var_str} FROM COMP.FUNDA WHERE {cs_filter}")
    wrds_us_dynamic = pd.DataFrame(cur.fetchall(), columns=dyn_vars)
    log.info("Pulling dynamic Compustat data ... Done!")

    log.info("Pulling static Compustat data ... ")
    cur.execute(f'SELECT {stat_var_str} FROM COMP.COMPANY')
    wrds_us_static = pd.DataFrame(cur.fetchall(), columns=stat_vars)
    log.info("Pulling static Compustat data ... Done!")

    wrds.close()
    log.info("Disconnected from WRDS")

    wrds_us = pd.merge(wrds_us_static, wrds_us_dynamic, "inner", on="gvkey")

    return wrds_us


def connect_to_wrds(authentication):

    if authentication:
        user = authentication['wrds_user']
        passwd = authentication['wrds_pwd']
    else:
        user = input('Please provide a wrds username: ')
        passwd = getpass(
            'Please provide a wrds password (it will not show as you type): ')

    try:
        wrds = connect(
            dbname="wrds",
            user=user,
            password=passwd,
            host='wrds-pgdata.wharton.upenn.edu',
            port=9737,
            sslmode='require'
        )
    except OperationalError as e:
        log.error(
            'There was an authentication failure, please check that the user name and password provided in either in the config.csv or in the terminal are correct. See full error below \n\n\n')
        raise e
    return wrds


if __name__ == '__main__':
    main()
