# ------------------------------------------------------------------------------
# This reads the config file in project root and stores all variables in a list
# named cfg.
#
# (c) TRR 266 - Read LICENSE for details
# ------------------------------------------------------------------------------

import pandas as pd
from pathlib import Path


def read_config():
    my_file = Path("config.csv")

    if not my_file.is_file():
        return 'Not found'

    df = pd.read_csv("config.csv", comment="#", index_col='variable')
    cfg = df['value'].to_dict()
    return cfg
