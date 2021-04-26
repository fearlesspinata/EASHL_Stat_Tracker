import requests
from bs4 import BeautifulSoup
import pprint

teamId = '73254'
platform = 'ps4'

def getStats(teamID, platform):
    headers = {'referer': 'www.ea.com'}
    url =  f"https://proclubs.ea.com/api/nhl/clubs/matches?clubIds={teamID}&platform={platform}&matchType=club_private"
    r = requests.get(url, headers=headers)
    return r.json()

stats = getStats(teamId, platform)

pprint.pprint(stats[0]['players']['73254']['180231983'])