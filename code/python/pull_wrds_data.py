# --- Header -------------------------------------------------------------------
# See LICENSE file for details
#
# This code pulls data from WRDS
# ------------------------------------------------------------------------------
import os
from psycopg2 import connect, OperationalError
from getpass import getpass
import dotenv

import pandas as pd
from utils import read_config, setup_logging

log = setup_logging()

def main():
    '''
    Main function to pull data from WRDS.

    This function reads the configuration file, gets the WRDS login credentials, and pulls the data from WRDS.

    The data is then saved to a csv file.
    '''
    cfg = read_config('config/pull_data_cfg.yaml')
    wrds_login = get_wrds_login()
    wrds_us = pull_wrds_data(cfg, wrds_login)
    wrds_us.to_csv(cfg['cstat_us_sample_save_path'], index=False)

    
def get_wrds_login():
    '''
    Gets the WRDS login credentials.
    '''
    if os.path.exists('secrets.env'):
        dotenv.load_dotenv('secrets.env')
        wrds_username = os.getenv('WRDS_USERNAME')
        wrds_password = os.getenv('WRDS_PASSWORD')
        return {'wrds_username': wrds_username, 'wrds_password': wrds_password}
    else:
        wrds_username = input('Please provide a wrds username: ')
        wrds_password = getpass(
            'Please provide a wrds password (it will not show as you type): ')
        return {'wrds_username': wrds_username, 'wrds_password': wrds_password}
    
def pull_wrds_data(cfg, wrds_authentication):
    '''
    Pulls WRDS access data.
    '''
    wrds = connect_to_wrds(wrds_authentication)

    cur = wrds.cursor()

    log.info('Logged on to WRDS ...')

    dyn_var_str = ', '.join(cfg['dyn_vars'])

    stat_var_str = ', '.join(cfg['stat_vars'])

    log.info("Pulling dynamic Compustat data ... ")
    cur.execute(f"SELECT {dyn_var_str} FROM COMP.FUNDA WHERE {cfg['cs_filter']}")
    wrds_us_dynamic = pd.DataFrame(cur.fetchall(), columns=cfg['dyn_vars'])
    log.info("Pulling dynamic Compustat data ... Done!")

    log.info("Pulling static Compustat data ... ")
    cur.execute(f'SELECT {stat_var_str} FROM COMP.COMPANY')
    wrds_us_static = pd.DataFrame(cur.fetchall(), columns=cfg['stat_vars'])
    log.info("Pulling static Compustat data ... Done!")

    wrds.close()
    log.info("Disconnected from WRDS")

    wrds_us = pd.merge(wrds_us_static, wrds_us_dynamic, "inner", on="gvkey")

    return wrds_us


def connect_to_wrds(authentication: dict[str, str]):
    assert authentication['wrds_username'], 'No WRDS username provided'
    assert authentication['wrds_password'], 'No WRDS password provided'
    try:
        wrds = connect(
            dbname="wrds",
            user=authentication['wrds_username'],
            password=authentication['wrds_password'],
            host='wrds-pgdata.wharton.upenn.edu',
            port=9737,
            sslmode='require'
        )
    except OperationalError as e:
        log.error(
            'There was an authentication failure, please check that the user name and password provided in either in the secrets.env or in the terminal are correct. See full error below \n\n\n')
        raise e
    return wrds


if __name__ == '__main__':
    main()
