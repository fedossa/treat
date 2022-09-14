# --- Header -------------------------------------------------------------------
# See LICENSE file for details
#
# This code pulls data from WRDS
# ------------------------------------------------------------------------------
from read_config import read_config
from psycopg2 import connect, OperationalError
from getpass import getpass

import pandas as pd


def connect_to_wrds():
    cfg = read_config()

    try:
        if cfg == 'Not found':
            wrds = connect(
                dbname="wrds",
                user=input('Please provide a wrds username: '),
                password=getpass(
                    'Please provide a wrds password (it will not show as you type): '),
                host='wrds-pgdata.wharton.upenn.edu',
                port=9737,
                sslmode='require')
            return wrds
        else:
            wrds = connect(
                dbname="wrds",
                user=cfg['wrds_user'],
                password=cfg['wrds_pwd'],
                host='wrds-pgdata.wharton.upenn.edu',
                port=9737,
                sslmode='require')
            return wrds
    except OperationalError as e:
        print(
            'There was an authentication failure, please check that the user name and password provided in either in the config.csv or in the terminal are correct. See full error below \n\n\n')
        raise e


def pull_wrds_data(dyn_vars, stat_vars, cs_filter):
    '''
    Pulls WRDS access data.
    '''
    wrds = connect_to_wrds()

    cur = wrds.cursor()

    print('Logged on to WRDS ...')

    dyn_var_str = ','.join(dyn_vars)

    stat_var_str = ','.join(stat_vars)

    print("Pulling dynamic Compustat data ... ")
    cur.execute(f"SELECT {dyn_var_str} FROM COMP.FUNDA WHERE {cs_filter}")
    wrds_us_dynamic = pd.DataFrame(cur.fetchall(), columns=dyn_vars)

    print("Pulling static Compustat data ... ")
    cur.execute(f'SELECT {stat_var_str} FROM COMP.COMPANY')
    wrds_us_static = pd.DataFrame(cur.fetchall(), columns=stat_vars)
    wrds.close()
    print("Disconnected from WRDS")

    wrds_us = pd.merge(wrds_us_static, wrds_us_dynamic,
                       on="gvkey", how="inner")

    return wrds_us


def main():
    dyn_vars = [
        "gvkey", "conm", "cik", "fyear", "datadate", "indfmt", "sich",
        "consol", "popsrc", "datafmt", "curcd", "curuscn", "fyr",
        "act", "ap", "aqc", "aqs", "acqsc", "at", "ceq", "che", "cogs",
        "csho", "dlc", "dp", "dpc", "dt", "dvpd", "exchg", "gdwl", "ib",
        "ibc", "intan", "invt", "lct", "lt", "ni", "capx", "oancf",
        "ivncf", "fincf", "oiadp", "pi", "ppent", "ppegt", "rectr",
        "sale", "seq", "txt", "xint", "xsga", "costat", "mkvalt", "prcc_f",
        "recch", "invch", "apalch", "txach", "aoloch",
        "gdwlip", "spi", "wdp", "rcp"
    ]

    stat_vars = ["gvkey", "loc", "sic", "spcindcd", "ipodate", "fic"]

    cs_filter = "consol='C' and (indfmt='INDL' or indfmt='FS') and datafmt='STD' and popsrc='D'"

    wrds_us = pull_wrds_data(dyn_vars, stat_vars, cs_filter)

    wrds_us.to_csv('data/pulled/cstat_us_sample.csv', index=False)

    print("Done")


if __name__ == '__main__':
    main()
