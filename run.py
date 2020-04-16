#!/usr/bin/env python

import sys
import json
import shutil

sys.path.insert(0, 'src') # add library code to path
from dataIngestion import *


data_ingest_params = 'config/dataIngestion.json'


def load_params(fp):
    with open(fp) as fh:
        param = json.load(fh)

    return param


def main(targets):

    # make the clean target
    if 'clean' in targets:
      #TODO!!!!! - ask aaron
       
    # make the data target
    if 'collect_data' in targets:
        cfg = load_params(data_ingest_params)
        
        collect_data(**cfg)

    return


if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
