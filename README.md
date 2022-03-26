# Biden Polls
Tracking President Biden's polling averages from [Real Clear Politics](https://www.realclearpolitics.com/epolls/other/president-biden-job-approval-7320.html#polls) and [FiveThirtyEight](https://projects.fivethirtyeight.com/biden-approval-rating/). 

A Github action runs the scrape at noon and 6 p.m. Pacific each day and, if there's new data, appends it to two [historical](https://github.com/stiles/biden-polls/blob/main/data/processed/biden_polling_averages.csv) [timeseries](https://github.com/stiles/biden-polls/blob/main/data/processed/biden_approval_trend_538_all_polls.csv). It also sends an email notifying me about the Biden's latest average ratings from both sources. 
