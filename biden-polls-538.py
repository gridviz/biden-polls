#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import datetime as dt
import smtplib
from email.message import EmailMessage

# Get latest Biden trends from 539
url = "https://projects.fivethirtyeight.com/biden-approval-data/approval_topline.csv"

src = pd.read_csv(url)

src.rename(columns={'modeldate':'date', 'approve_estimate':'approve', 'disapprove_estimate':'disapprove'} , inplace=True)

src['spread'] = src['approve'] - src['disapprove']

src['disapprove'] = src['disapprove'].round(2)
src['approve'] = src['approve'].round(2)
src['spread'] = src['spread'].round(2)

src['datetime'] = pd.to_datetime(src['timestamp'])
src['date'] = src['datetime'].dt.strftime('%m-%d-%y')
src['date_display'] = src['datetime'].dt.strftime('%b. %d')

src.drop_duplicates(subset=['date', 'subgroup'], keep='last', inplace=True)

for g in src["subgroup"].unique():
    src[src["subgroup"] == g].to_csv(
        f"data/processed/biden_approval_trend_538_{g.replace(' ', '_').lower()}.csv",
        index=False,
    )

df_long = pd.melt(
    src,
    id_vars="date",
    value_vars=["approve", "disapprove", "spread"],
    var_name="value",
    value_name="variable",
)

src['date'] = pd.to_datetime(src['date'])
latest_df = src[src['date'] == src['date'].max()]

for g in latest_df["subgroup"].unique():
    latest_df[latest_df["subgroup"] == g].to_csv(
        f"data/processed/biden_approval_trend_538_latest_{g.replace(' ', '_').lower()}.csv",
        index=False,
    )

date = latest_df.iloc[0, 12]
approve = latest_df.iloc[0, 3].round(1)
disapprove = latest_df.iloc[0, 6].round(1)
spread = latest_df.iloc[0, 10].round(1)

email = f"Yes! We've scraped President Biden's latest polling average from 538. As of {date}, his approval rating is {approve}%. His dissapproval rating is {disapprove}%. That's a spread of {spread} percentage points. Get the latest data here: https://github.com/stiles/biden-polls/blob/main/data/processed/biden_approval_trend_all_polls.csv"
    
# get email and password from environment variables
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECIPIENT = os.environ.get('EMAIL_RECIPIENT')
    
# set up email content
msg = EmailMessage()
msg['Subject'] = 'Github Actions: New Biden polling results from 538!'
msg['From'] = EMAIL_ADDRESS
msg['To'] = EMAIL_RECIPIENT
msg.set_content(f'{email}')
    
# send email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)