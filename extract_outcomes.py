#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 16:42:52 2020

@author: jonyoung
"""

# import what we need
import pandas as pd
import numpy as np

# set directories
metadata_dir = '/home/k1511004/Data/PSYSCAN/WP5_data/FEP/metadata/'

# function to calculate response to treatment at each timepoint
def response_to_treatment(x) :
    
    total_panss = x[0]
    baseline_panss = x[1]
    
    if np.isnan(baseline_panss) :
        
        return 'N/A'
    
    elif total_panss / baseline_panss < 0.8 :
        
        return 'response'
    
    else :
        
        return 'non-response'
    
def get_baseline_total_panns(row):
       
    if row['timepointid'] == 'Baseline' :
        
        baseline_total_panss = row['total_panss']
        return baseline_total_panss
        
    else :
        
        subjectid = row['subjectid']
        subjectid_extract = extract[extract['subjectid'] == subjectid]
        subjectid_baseline_extract = subjectid_extract[subjectid_extract['timepointid'] == 'Baseline']
        
        if len(subjectid_baseline_extract) == 0 :
            
            return np.NaN
        
        else :
            
            return subjectid_baseline_extract['total_panss'].iloc[0]

# if Y, M  and D fields are run together to make an integer
def correct_integer_dates(date) :
    
    if isinstance(date, (int, long)) :
        
        # convert to str and add hyphens
        date_str = str(date)
        date = date_str[:4] + '-' + date_str[4:6] + '-' + date_str[6:]
        
    return date
    

# if month and day fields are obviously the wrong way round, swap them back
def correct_swapped_dates(date_str) :
    
    print (date_str)
    date_str_bits = date_str.split('-')
    
    if int(date_str_bits[2]) > 12 :
        
        date_str = str(date_str_bits[0] + '-' + date_str_bits[2] + '-' + date_str_bits[1])
        
    return date_str

# catch-all correction
def correct_date(date) :
    
    
    
    # make sure date is a string, and print
    date = str(date)
    print (date)
    
    # skip nans
    if not date == 'nan' :
    
        # if there are two dates, take the first
        date = date.split(',')[0]
        
        # replace and slashes with hyphens
        date = date.replace('/', '-')
        
        # if date is a single string of digits, add hyphens
        if len(date) == 8 and date.isdigit() :
            
            date = date[:4] + '-' + date[4:6] + '-' + date[6:]
            
        # check if final element is length 4
        # if so date is DD-MM-YYYY rather than YYYY-MM-DD so flip it
        date_elements = date.split('-')
        if len(date_elements[2]) == 4 :
            
            date = date_elements[2] + '-' + date_elements[1] + '-' + date_elements[0]
        
        # if first element has len <4, missing digit from year - can it
        date_elements = date.split('-')
        if len(date_elements[0]) < 4 :
            
            date = np.NaN
        
        # if middle element > 12, month and day are flipped    
        if int(date_elements[1]) > 12 :
            
            date = date_elements[0] + '-' + date_elements[2] + '-' + date_elements[1]
    
    return date
        
        
    

# read in the extract
# extract = pd.read_excel(metadata_dir + 'PSYSCAN_full_extract_02_04_20_2.xlsx')
extract = pd.read_csv(metadata_dir + 'PSYSCAN_full_extract_02_04_20_macbook.csv', delimiter='|', dtype=str, low_memory=False)

# filter out FEPs
extract = extract[extract['subjectid'].apply(lambda x: x[:4]) == 'PSYF']

# select desired columns
panss_cols = list(filter(lambda x: 'panss' in x, extract.columns))
cols = ['subjectid', 'dob', 'timepointid', 'assessment_date'] + panss_cols
extract = extract[cols]

# filter on timepoints of interest: baseline, 2 and 6 months
extract = extract[extract['timepointid'].isin(['Baseline', 'Month_2', 'Month_6'])]


# resave
#extract.to_excel(metadata_dir + 'PSYSCAN_full_extract_19_02_20_PANSS_only.xlsx')

## filter out missing vals in PANSS
#extract = extract.dropna()
#
## filter out malformed dates and correct dates with (visibly) swapped day and month fields
##extract['assessment_date'] = extract['assessment_date'].apply(lambda x: correct_integer_dates(x))
##extract['assessment_date'] = extract['assessment_date'].apply(lambda x: x.split(',')[0])
##extract['assessment_date'] = extract['assessment_date'].apply(lambda x: correct_swapped_dates(x))
extract['assessment_date'] = extract['assessment_date'].apply(lambda x: correct_date(x))
##extract = extract[extract['assessment_date'].apply(lambda x: int(str(x).split('/')[-1]) > 2015)]
#
# pad timepointids
extract['timepointid'] = extract['timepointid'].apply(lambda x: x.replace('_6', '_06').replace('_2', '_02').replace('_3', '_03').replace('_9', '_09'))
#
# calculate total panss
extract[panss_cols] = extract[panss_cols].apply(pd.to_numeric)
extract['total_panss'] = extract[panss_cols].sum(axis=1)
#
## calculate remission according to the Andreasen criteria in 
## Andreasen, Nancy & Carpenter, William & Kane, John & Lasser, Robert & Marder, Stephen & Weinberger, Daniel. (2005). 
## Remission in Schizophrenia: Proposed Criteria and Rationale for Consensus. 
## The American journal of psychiatry. 162. 441-9. 10.1176/appi.ajp.162.3.441.
## criterion is score <= 3 in all PANSS items
extract['Andreasen remission'] = extract[panss_cols].apply(lambda x: all(x<=3), axis=1)
#
## calculate age at each assessment
extract['assessment age'] = pd.to_timedelta(pd.to_datetime(extract['assessment_date'], format='%Y/%m/%d') - pd.to_datetime(extract['dob'], format='%Y/%m/%d'))
extract['assessment age'] = extract['assessment age'].apply(lambda x: x.days) / 365.0

# calculate response to treatment
# N/A if baseline panss is not available
extract['baseline_panss'] = extract.apply(get_baseline_total_panns, axis =1)
extract['response_to_treatment'] = extract[['total_panss', 'baseline_panss']].apply(response_to_treatment, axis=1)

#
## extract outcomes only
#extract = extract[['subjectid', 'dob', 'timepointid', 'assessment_date', 'assessment age', 'total_panss', 'Andreasen remission']]
#

#
## extract outcomes only
#outcomes = extract[['subjectid', 'timepointid', 'assessment_date', 'assessment age', 'Andreasen remission', 'response_to_treatment']]
#
# pivot to outcomes by subject
outcomes_by_subject = pd.pivot_table(extract, index = ['subjectid'], columns = ['timepointid'], values=['assessment_date', 'assessment age', 'Andreasen remission', 'response_to_treatment', 'total_panss'] + panss_cols, aggfunc=lambda x: ' '.join(str(v) for v in x))
#
## reorder values
#outcomes_by_subject = outcomes_by_subject.reindex(['assessment_date', 'assessment age', 'Andreasen remission', 'response_to_treatment'], level=0, axis=1)
#
# sort by timepoint
outcomes_by_subject.sort_index(axis='columns', level = 1, sort_remaining = False, inplace=True)
##
# swap levels for neatness
outcomes_by_subject.columns = outcomes_by_subject.columns.swaplevel(0, 1)
outcomes_by_subject.reset_index(inplace=True)

# save results
outcomes_by_subject.columns = outcomes_by_subject.columns.map('|'.join).str.strip('|')
outcomes_by_subject.to_excel(metadata_dir + 'Month_02_Month_06_outcomes.xlsx')
#
## Month 6 remission
##Month_06_remission = outcomes_by_subject[outcomes_by_subject[('Month_06', 'Andreasen remission')].notnull()][[('subjectid', ''), ('Month_06', 'Andreasen remission')]]
#Month_06_remission = outcomes_by_subject[outcomes_by_subject[('Month_06', 'Andreasen remission')].notnull()][[('subjectid', ''), ('Month_06', 'Andreasen remission'), ('Month_06', 'assessment age')]]
#Month_06_remission.reset_index(inplace=True, drop=True)
#
## Month 6 treatment response
#Month_06_treatment_response = outcomes_by_subject[outcomes_by_subject[('Month_06', 'response_to_treatment')].isin([('subjectid', ''), 'response', 'non-response'])][[('subjectid', ''), ('Month_06', 'response_to_treatment')]]
#Month_06_treatment_response.reset_index(inplace=True, drop=True)
#
## both results
#Month_06_outcomes = Month_06_remission.merge(Month_06_treatment_response, left_on = 'subjectid', right_on = 'subjectid')
#
## save results
#Month_06_outcomes.columns = Month_06_outcomes.columns.map('|'.join).str.strip('|')
##Month_06_outcomes.to_excel(metadata_dir + 'Month_06_outcomes.xlsx')