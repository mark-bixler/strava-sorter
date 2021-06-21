#!/usr/bin/env python3
"""
app.py
"""

__author__ = "Mark Bixler"
__version__ = "0.1.0"
__license__ = "MIT"

import pandas as pd
import requests
import time
import json
import datetime

from pandas.io.json import json_normalize
from keys import CLIENT_ID, CLIENT_SECRET
from math import floor

def main():
    # Get the tokens from file to connect to Strava
    print("Getting strava tokens...")
    with open('strava_tokens.json') as json_file:
        strava_tokens = json.load(json_file)

    # Check for expired token
    if strava_tokens['expires_at'] < time.time():
      # Refresh Token
      print("Refreshing Tokens")
      response = requests.post(
            url = 'https://www.strava.com/oauth/token',
            data = {
                'client_id': [CLIENT_ID],
                'client_secret': [CLIENT_SECRET],
                'grant_type': 'refresh_token',
                'refresh_token': strava_tokens['refresh_token']
                })
            
      new_strava_tokens = response.json

      with open('strava_tokens.json', 'w') as outfile:
        json.dump(new_strava_tokens, outfile)
      
      strava_tokens = new_strava_tokens

    # Loop through all activities
    page = 1
    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens['access_token']

    activities = pd.DataFrame(columns= [
      "date", 
      "name",
      "type",
      "distance",
      "moving_time",
      "pace",
      "average_speed", 
      "total_elevation_gain"
    ])

    while True:

      # Get first page of activities from Strava with all fields
      print(f"Getting Data...{page}")
      r = requests.get(url + '?access_token=' + access_token + '&per_page=200' \
        + '&page=' + str(page))
      r = r.json()

      if (not r):
        break

      for x in range(len(r)):
        if(
          r[x]['type'] == 'Run' and 
          5400 <= r[x]['distance'] <= 5800 and 
          110 <= r[x]['total_elevation_gain'] <= 130 and
          "Counter".lower() not in (r[x]['name']).lower()
          ):
          
          # Convert Date to Readable Format
          date = datetime.datetime.strptime(
            r[x]['start_date_local'],"%Y-%m-%dT%H:%M:%SZ")
          date_format = "%m-%d-%Y"

          # Convert AVG Speed to PACE
          sec_mile = 1609.344 / r[x]['average_speed']
          min_mile = sec_mile / 60
          minutes = floor(min_mile)
          seconds = floor(round(sec_mile % 60))
          
          # Solving for Correct PACE Formatting
          if(seconds == 60):
            seconds = 0
            minutes = minutes + 1

          # Store all values
          activities.loc[x + (page-1)*200,'date'] = date.strftime(date_format)
          activities.loc[x + (page-1)*200,'name'] = r[x]['name']
          activities.loc[x + (page-1)*200,'type'] = r[x]['type']
          activities.loc[x + (page-1)*200,'distance'] = \
            round((r[x]['distance']/1609),2)
          activities.loc[x + (page-1)*200,'moving_time'] = \
            str(datetime.timedelta(seconds=r[x]['moving_time']))
          activities.loc[x + (page-1)*200,'pace'] = \
            ("%d:%02d" % (minutes, seconds))
          activities.loc[x + (page-1)*200,'average_speed'] = \
            r[x]['average_speed']
          activities.loc[x + (page-1)*200,'total_elevation_gain'] = \
            round(r[x]['total_elevation_gain']*3.281)

      # Get Next Page
      page += 1

    # Export to CSV
    activities.to_csv('strava_activities.csv')


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()