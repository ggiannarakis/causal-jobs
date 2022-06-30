from extract import main
import re
import numpy as np
import pandas as pd
from datetime import datetime

def transform():
    """
    retrieve the latest email of the 'causal-jobs' Gmail folder
    by calling the main function from extract.py.
    Transforms it into a pandas dataframe where each row is a job
    that the email contains, and each column contains info about it
    """

    # call main from extract.py and get its components
    body, msg_id, date = main()

    # init df and transform email body to string
    df = pd.DataFrame()
    body = str(body)

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
    for i in content:
        temp = i.replace('\n', '').replace('amp;', '').split('\r')
        job_title.append(temp[1])
        company_name.append(temp[2])
        job_location.append(temp[3])

    # define dataframe columns appropriately
    # ensure datetime type for date column
    df['job_title'] = job_title
    df['company_name'] = company_name
    df['job_location'] = job_location
    df[['city', 'region', 'country']] = df['job_location'].str.split(',', expand=True)
    df['email_id'] = msg_id
    df['email_date'] = datetime.strptime(date[:date.find('202')+4].replace(',', '').lstrip(), '%a %d %b %Y')

    # internal duplicate handling
    # keep only first occurrence of each job_title / company_name pair
    df = df.groupby(['job_title', 'company_name']).first().reset_index()

    return df