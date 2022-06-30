#TODO: duplicate handling per (job_title, company_name) for each append

import sqlalchemy
import pandas as pd
from transform import transform

# get latest df of causal-jobs
df = transform()

# create engine and connect (requires running docker container)
engine = sqlalchemy.create_engine('postgresql://postgres:password@localhost:5432/causal-jobs-db')
engine.connect()

# retrieve all unique email_id currently in table
all_unique_email_ids = pd.read_sql_query("SELECT DISTINCT email_id FROM causal_jobs_extended", con=engine)

# if (job_title, company_name) already exist in table remove from df (TODO)

# if the current email_id is not contained in the existing table append the data to it
if ~all_unique_email_ids['email_id'].str.contains(df.email_id[0]).any():
    df.to_sql('causal_jobs_extended', con=engine, if_exists='append', index=False)

# close engine
engine.dispose()