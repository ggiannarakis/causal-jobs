import streamlit as st
import sqlalchemy
import pandas as pd
import numpy as np
import pandas as pd
from os import path
from PIL import Image
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import plotly.express as px
from IPython.display import HTML

engine = sqlalchemy.create_engine('postgresql://postgres:password@localhost:5432/causal-jobs-db');
engine.connect();

# get metadata and table
metadata = sqlalchemy.MetaData()
causal_jobs = sqlalchemy.Table('causal_jobs_extended', metadata, autoload=True, autoload_with=engine)

# define query for the table (select *)
query = sqlalchemy.select([causal_jobs])

# execute and get query results
ResultProxy = engine.connect().execute(query)
ResultSet = ResultProxy.fetchall()

# this is the main df to be analyzed
df = pd.DataFrame(ResultSet)

# enforce email order
df = df.sort_values(by=['email_date'])

st.write("""
# causal-jobs
Automatically generated in:
""", date.today())

st.write("""

---

This is the latest weekly report containing, as always, 
information on the status of causal inference in the European job market. 
It is based on accumulated information starting early May 2022. 
Latest vacancies, the rate of relevant job postings, 
most "causal" companies and other info can be found here.

Disclaimer: This app is automatically created by accessing 
daily job alert emails and retrieving the relevant 
information through an ETL pipeline. There are days when 
the number of new job postings exceeds a threshold, 
and not every causal-job is contained in the email this app feeds on. 
As a result, some causal-jobs might never make it into the pipeline, 
meaning that the database I have created is by no means complete. 
However, this doesn't happen too often, and info listed in the report can serve 
as a solid indication on the status of causal inference in the European job market.

Code can be found at https://github.com/ggiannarakis/causal-jobs

---
""")

# get most recent date in the df
latest_date = df['email_date'].max()
# get the email id corresponding to it
# sometimes there are two emails on the same data hence select the last line
latest_id = df.loc[df.email_date == latest_date].email_id.iloc[-1]

# print selected columns from most recent email
latest_jobs = df.loc[df.email_date >= latest_date - timedelta(days=7)]
latest_jobs = latest_jobs.rename(columns={"job_title":"Job",
                                          "company_name":"Company",
                                          "job_location": "Location",
                                          "email_date": "Date"})

st.write("### What are the latest jobs?", latest_jobs[['Job', 'Company', 'Location', 'Date']])

st.write("""
### New kids on the block?
Are there any of the above companies listing "causal inference" in their vacancy for the first time?
""")

# find, if any, companies listing "causal inference" in the job description for the first time:
companies_in_latest_email = set(latest_jobs.Company.unique())
companies_in_past_emails = set(pd.concat([df, latest_jobs]).drop_duplicates(keep=False).Company.unique())
new_companies = companies_in_latest_email - companies_in_past_emails

# if there are such companies, welcome them to the causal revolution!
if len(new_companies) != 0:
    st.write('Yes! Welcome {} to the causal revolution!'.format(new_companies))
else:
    st.write('Nope. All companies seen above have posted causal-jobs before!')

# how many jobs did we get per email?
daily_jobs = df.groupby('email_date').size()
ax = daily_jobs.plot(figsize=(15,6), lw=2, colormap='jet', marker='.', markersize=10);
ax.set_xlabel("Email date");
ax.set_ylabel("Number of causal jobs");