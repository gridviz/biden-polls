#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import datetime as dt
import smtplib
from email.message import EmailMessage

# Get latest Biden trends from Real Clear Politics

url = "https://www.realclearpolitics.com/epolls/other/president-biden-job-approval-7320.html#polls"
headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X "}
r = requests.get(url, headers=headers)

soup = BeautifulSoup(r.text, "html.parser")

tables = soup.findAll("table", attrs={"class": "data"})

src = pd.read_html(str(tables))[0]

latest_df = src[:1].copy()

latest_df.columns = latest_df.columns.str.lower()

latest_df[["begin", "end"]] = (
    latest_df["date"].astype(str).str.split(" - ", n=1, expand=True)
)

date = (latest_df["end"] + "/2021").astype(str)

latest_df["date"] = pd.to_datetime(date).dt.date

latest_df.drop(["poll", "sample", "begin", "end"], axis=1, inplace=True)

# Import historical polling average for Biden from RCP via Wayback Machine

historical = pd.read_csv("data/processed/biden_history.csv")

historical.drop(["wayback_date", "wayback_time"], axis=1, inplace=True)

# Append latest to historical

full_df = historical.append(latest_df).reset_index(drop=True)

full_df["date"] = pd.to_datetime(full_df["date"])

full_df = full_df.sort_values("date", ascending=False)

full_df["candidate"] = "President Biden"

full_df['disapprove'] = full_df['disapprove'].round(2)
full_df['approve'] = full_df['approve'].round(2)
full_df['spread'] = full_df['spread'].round(2)

df_long = pd.melt(
    full_df,
    id_vars="date",
    value_vars=["approve", "disapprove", "spread"],
    var_name="value",
    value_name="variable",
)

date = latest_df.iloc[0, 0].strftime("%b. %d")
approve = latest_df.iloc[0, 1].round(2)
disapprove = latest_df.iloc[0, 2].round(2)
spread = latest_df.iloc[0, 3].round(2)

email = f"Yes! We've scraped President Biden's latest polling average from Real Clear Politics. As of {date}, his approval rating is {approve}%. Biden's dissapproval rating is {disapprove}%. That's a spread of {spread} percentage points. Get the latest data here: https://github.com/stiles/biden-polls/blob/main/data/processed/biden_polling_averages.csv"


df_long.to_csv("data/processed/biden_polling_averages_long.csv", index=False)
full_df.to_csv('data/processed/biden_polling_averages.csv', index=False)
    
# get email and password from environment variables
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
EMAIL_RECIPIENT = os.environ.get('EMAIL_RECIPIENT')
    
# set up email content
msg = EmailMessage()
msg['Subject'] = 'Github Actions: New Biden polling results from RCP!'
msg['From'] = EMAIL_ADDRESS
msg['To'] = EMAIL_RECIPIENT
msg.set_content(f'{email}')
    
# send email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)