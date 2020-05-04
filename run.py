#!/usr/bin/env python

#imports
import sys
import json
import shutil


#import functions from files
sys.path.insert(0, 'src') # add library code to path
sys.path.insert(0, 'test_src')
from data_ingestion import *
from train_test import *


#get config file path names
data_ingest_params = 'config/dataIngestion.json'
test_ingest_params = 'config/test.json'

#function to load the config files into json
def load_params(fp):
    with open(fp) as fh:
        param = json.load(fh)

    return param


#main function to run
def main(targets):

    # make the clean target
    if 'clean' in targets:
        shutil.rmtree('testData/', ignore_errors=True)
        shutil.rmtree('data/', ignore_errors=True)
        
    #test data ingestion process
    if 'test_data_ingestion' in targets:
        cfg = load_params(test_ingest_params)
        test_ingestion(cfg["websites"], cfg["outdir"])
       
    #collect the data 
    if 'data_ingestion' in targets:
        cfg = load_params(data_ingest_params)
        
        collect_data(**cfg)
    return

#first call to start data pipeline
if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)
