import requests
import json
from keys import CLIENT_ID, CLIENT_SECRET, CLIENT_CODE


response = requests.post(
                    url = 'https://www.strava.com/oauth/token',
                    data = {
                            'client_id': CLIENT_ID,
                            'client_secret': CLIENT_SECRET,
                            'code': CLIENT_CODE,
                            'grant_type': 'authorization_code'
                            }
                )
#Save json response as a variable
strava_tokens = response.json()
# Save tokens to file
with open('strava_tokens.json', 'w') as outfile:
    json.dump(strava_tokens, outfile)
# Open JSON file and print the file contents 
# to check it's worked properly
with open('strava_tokens.json') as check:
  data = json.load(check)
print(data)