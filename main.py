import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape
from datetime import timedelta
import pprint

teamId = '1375'
platform = input('What is the platform of the player you\'re searching? (enter ps4 or xboxone): ').lower()
env = Environment(
    loader=PackageLoader('nhl21Stats', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

def convertSeconds(seconds):
    toa = str(timedelta(seconds=seconds))
    toa = toa.replace('0:', '', 1)
    return toa

def getMatchHistory(teamId, platform):
    headers = {'referer': 'www.ea.com'}
    url =  f"https://proclubs.ea.com/api/nhl/clubs/matches?clubIds={teamId}&platform={platform}&matchType=club_private"
    r = requests.get(url, headers=headers)
    return r.json()

def getClubInfo(teamId):
    matchInfo = getMatchHistory(teamId, platform)
    clubInfo = matchInfo[0]['clubs']
    return clubInfo

def getPlayerId():
    playerName = input('Please provide player\'s name ')
    clubInfo = getClubInfo(teamId)
    playerStruct = clubInfo[0]['players']['1375']
    for playerId in playerStruct:
        if playerStruct[playerId]['playername'] == playerName:
            return playerId

def getPlayerStats(getPlayerId):
    skaterDict= {'skgoals': 0, 'skassists': 0, 'skplusmin': 0}
    goalieDict = {'glsavepct': 0, 'glgaa': 0, 'glshots': 0}
    playerId = getPlayerId()
    clubInfo = getClubInfo(teamId)
    playerStruct = clubInfo[0]['players']['1375']

    if playerStruct[playerId]['position'] != 'goalie':
        for skStat in skaterDict:
            skaterDict[skStat] = playerStruct[playerId][skStat]
        return skaterDict
    else:
        for glStat in goalieDict:
            goalieDict[glStat] = playerStruct[playerId][glStat]
        return goalieDict
                
def getTeamStats(teamId):
    matchDict = {'scoreString': 0, 'shots': 0, 'name': 0, 'toa': 0}
    matchInfo = getMatchHistory(teamId, platform)[0]
    teamStats = matchInfo['clubs'][teamId]
    matchDict['scoreString'] = teamStats['scoreString']
    matchDict['shots'] = teamStats['shots']
    matchDict['name'] = teamStats['name']
    matchDict['toa'] = convertSeconds(int(teamStats['toa'])) 
    return matchDict

template = env.get_template('table.html')
outputFromFile = template.render(playerStat ='variables', playerStatHeader='here')

with open('tableTemp.html', 'w') as fh:
    fh.write(outputFromFile)
    fh.close()


    

<<<<<<< HEAD
#matchInfo = getMatchHistory(teamId, platform)[0]['clubs'][teamId]['toa']
#pprint.pprint(matchInfo)
=======
pprint.pprint(stats[0]['players']['73254']['1716353852'])
>>>>>>> dd21aaa932c38a866af30de6ee1e65e1eea36398
