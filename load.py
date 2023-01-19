#TODO: duplicate handling per (job_title, company_name) for each append

import sqlalchemy
import pandas as pd
from transform import transform
import logging

# set the log level
logging.basicConfig(level=logging.INFO,
                    filename='load-logs.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filemode='w')

# get latest df of causal-jobs
df = transform()

# create engine and connect (requires running docker container)
try:
    engine = sqlalchemy.create_engine('postgresql://postgres:password@localhost:5432/causal-jobs-db')
    engine.connect()
except Exception as e:
    logging.error("Unable to establish database connection: {}".format(e))

# retrieve all unique email_id currently in table
all_unique_email_ids = pd.read_sql_query("SELECT DISTINCT email_id FROM causal_jobs_extended", con=engine)

# if (job_title, company_name) already exist in table remove from df (TODO)

# if the current email_id is not contained in the existing table append the data to it
try:
    if ~all_unique_email_ids['email_id'].str.contains(df.email_id[0]).any():
        df.to_sql('causal_jobs_extended', con=engine, if_exists='append', index=False)
        # store df locally to send to my email with send_email.py script (sanity check)
        df.to_csv('latest-causal-job.csv', index=False)
    else:
        df = pd.Series(['Indexed nothing. Working as intended if no email since last task execution.'])
        df.to_csv('latest-causal-job.csv', index=False)
except Exception as e:
    logging.error("Unable to append latest email data to database table: {}".format(e))

# close engine
engine.dispose()