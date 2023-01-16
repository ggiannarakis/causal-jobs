from extract import main
import re
import numpy as np
import pandas as pd
from datetime import datetime

import logging

# set the log level
logging.basicConfig(level=logging.DEBUG,
                    filename='transform-logs.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filemode='w')

def transform():
    """
    Retrieves the latest email of the 'causal-jobs' Gmail folder
    by calling the main function from extract.py.
    Transforms it into a pandas dataframe where each row is a job
    that the email contains, and each column contains info about it
    """

    # call main from extract.py and get its components
    try:
        body, msg_id, date = main()
    except Exception as e:
        logging.error("Unable to extract email components: extract.py main function failed: {}".format(e))

    # init df and transform email body to string
    df = pd.DataFrame()
    body = str(body)

    # find the total number of jobs found (if over a threshold, they are not included in the email)
    # the threshold used to be 10, it was lowered in July 2022 to 6
    job_number = re.search(r"\d+", body)
    job_number = job_number.group()

    # UPDATE Sep 13, 2022: Linkedin no longer precedes the first job
    # with a '---' hence breaking the indices computed below
    # For now, will be manually adding a '---' right after the
    # 'match your preferences' part of the email body string
    # so the algorithm will proceed as normal
    for m in re.finditer('match your preferences', body):
        idx_to_insert = m.end()

    body = body[:idx_to_insert] + '---------------------------------------------------------' + body[idx_to_insert:]

    # get end position of each job by selecting the string element
    # right before each 'View Job' occurrence
    idx_to_end = []
    for m in re.finditer('View job', body):
        idx_to_end.append(m.start() - 1)

    # get start position of each job by selecting the string element
    # right after each '---' occurrence
    idx_to_start = []
    for m in re.finditer('---------------------------------------------------------', body):
        idx_to_start.append(m.end() + 1)
        if len(idx_to_start) > len(idx_to_end) - 1:
            break

    # concatenate the ending indices list to the starting one
    all_idxs = (idx_to_start + idx_to_end)
    all_idxs_sorted = np.sort(np.asarray(all_idxs))

    # take advantage of the 1-1 correspondence between the two lists
    # by creating a list of tuples whose first element is the
    # starting index of a job and second element is the ending index
    zipped_idx = list(zip(idx_to_start, idx_to_end))

    # create and populate list of strings with each job
    content = []
    for i in zipped_idx:
        start, end = i
        content.append(body[start:end])

    job_title = []
    company_name = []
    job_location = []

    # clean each job and split its elements (title, company, location)
    # UPDATE Sep 13, 2022: Minor changes in '\r', '\n' occurrence,
    # adapting this part too
    for i in content:
        temp = i.replace('\n', '').replace('amp;', '').split('\r')
        job_title.append(temp[2])
        company_name.append(temp[3])
        job_location.append(temp[4])

    # define dataframe columns appropriately
    # ensure datetime type for date column
    df['job_title'] = job_title
    df['company_name'] = company_name
    df['job_location'] = job_location
    # geographic format no longer regular
    # commenting out analytic information
    # simply duplicating the location on city, region, country columns
    # to comply with db table
    # df[['city', 'region', 'country']] = df['job_location'].str.split(',', expand=True)
    df['city'] = job_location
    df['region'] = job_location
    df['country'] = job_location
    df['email_id'] = msg_id
    df['email_date'] = datetime.strptime(date[:date.find('202')+4].replace(',', '').lstrip(), '%a %d %b %Y')

    # internal duplicate handling
    # keep only first occurrence of each job_title / company_name pair
    df = df.groupby(['job_title', 'company_name']).first().reset_index()

    return df