#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 17:09:50 2020

@author: jonyoung
"""

# import what we need
import pandas as pd
import numpy as np

# function to replace malformed dates
def replace_misformatted_dates(date_str) :
    
    date_str_bits = date_str.split('-')
    if not (len(date_str_bits[0]) == 4) :
        
        return np.NaN
    
    if not (len(date_str_bits[1]) == 2) :
        
        return np.NaN
    
    if int(date_str_bits[1]) > 12 :
        
        return np.NaN
    
    if not (len(date_str_bits[2]) == 2) :
        
        return np.NaN
    
    else :
        
        return date_str
    
    

# set directories
metadata_dir = '/home/jonyoung/IoP_data/Data/PSYSCAN/WP5_data/FEP/metadata/'

# read in the metadata
demographics = pd.read_csv(metadata_dir + 'PSYSCAN_demographics_19_02_20.csv')
full_extract = pd.read_excel(metadata_dir + 'PSYSCAN_full_extract_19_02_20.xlsx')
full_image_list = pd.read_excel(metadata_dir + 'PSYSCAN_unfiltered_imagelist_19_02_20.xlsx')
T1_filepaths = pd.read_excel(metadata_dir + 'T1w_filepaths-1.xlsx', header=None)

# get columns we need from imagelist
# rename subject ID, reformat filepath
full_image_list = full_image_list[['subjectid', 'filepath', 'seriesdate']]
full_image_list.columns = ['Subject ID', 'filepath', 'seriesdate']
full_image_list['filepath'] = full_image_list['filepath'].apply(lambda x: '/'.join(x.split('/')[1:3]) + '/sMRI/' + '/'.join(x.split('/')[4:6]) + '/')

# extract subject id and refomat filepaths to match full image list
T1_filepaths['Subject ID'] = T1_filepaths[0].apply(lambda x: x.split('/')[5])
T1_filepaths = T1_filepaths[['Subject ID', 0]]
T1_filepaths.columns = ['Subject ID', 'filepath']
T1_filepaths['filepath'] = T1_filepaths['filepath'].apply(lambda x: '/'.join(x.split('/')[5:]))

# join image list to T1 filepaths to get series dates for T1 subjects
# trim any final '/' on filepaths to ensure matching
full_image_list['filepath'] = full_image_list['filepath'].apply(lambda x: x.strip('/'))
T1_filepaths['filepath'] = T1_filepaths['filepath'].apply(lambda x: x.strip('/'))
T1_series_date = T1_filepaths.merge(full_image_list, on = 'filepath', how = 'left')
T1_series_date = T1_series_date[['Subject ID_x', 'seriesdate']]
T1_series_date.columns = ['Subject ID', 'seriesdate']

# join series dates with demographics
demographics = demographics.merge(T1_series_date, on = 'Subject ID')

# get columns we need from full extract
# filter for baseline
full_extract = full_extract[full_extract['timepointid'] == 'Baseline']
full_extract = full_extract[['subjectid', 'assessment_date']]
full_extract.columns = ['Subject ID', 'assessment_date']

# join assessment dates with demnographics
demographics = demographics.merge(full_extract, on = 'Subject ID', how = 'left')

# standardise format of dates to YYYY-MM-DD
#demographics['assessment_date'] = demographics['assessment_date'].apply(lambda x: x.replace('/', '-'))
#demographics['assessment_date'] = demographics['assessment_date'].apply(lambda x: replace_misformatted_dates(x))
#
## calculate age at assessment and scan
#demographics['assessment age'] = pd.to_timedelta(pd.to_datetime(demographics['assessment_date'], format='%Y/%m/%d') - pd.to_datetime(demographics['Date of Birth'], format='%Y/%m/%d'))
#demographics['assessment age'] = demographics['assessment age'].apply(lambda x: x.days) / 365.0
#demographics['scan age'] = pd.to_timedelta(pd.to_datetime(demographics['seriesdate'], format='%Y/%m/%d') - pd.to_datetime(demographics['Date of Birth'], format='%Y/%m/%d'))
#demographics['scan age'] = demographics['scan age'].apply(lambda x: x.days) / 365.0
#
## save
#demographics.to_csv(metadata_dir + 'PSYSCAN_demographics_age_19_02_20.csv')