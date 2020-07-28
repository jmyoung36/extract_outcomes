#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 11:48:11 2020

@author: jonyoung
"""

# import what we need
import pandas as pd
import numpy as np

# set directories
#metadata_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/FEP/metadata/'
metadata_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/PSYSCAN_outcomes/'

# read in the extract
#extract = pd.read_excel(metadata_dir + 'PSYSCAN_full_extract_19_02_20.xlsx')
extract = pd.read_csv(metadata_dir + 'FullExtract_AllSites_2019_12_13.csv')


# filter out FEPs
extract = extract[extract['subjectid'].apply(lambda x: x[:4]) == 'PSYF']

# select desired columns
panss_cols = filter(lambda x: 'panss' in x, extract.columns)
cols = ['subjectid', 'dob', 'psyscansubjectstatus', 'timepointid', 'assessment_date'] + panss_cols
extract = extract[cols]
extract = extract[extract['timepointid'] == 'Month_6']
