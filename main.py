import requests
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, select_autoescape
from datetime import timedelta

teamId = '1375'
platform = "xboxone"
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
    matchDict = {'Score': 0, 'Shots': 0, 'TOA': 0, 'PPG': 0, 'PIM': 0, 'SHG': 0, 'Pass': 0, 'Hits': 0, 'Name': 0 }
    matchInfo = getMatchHistory(teamId, platform)[0]
    teamStats = matchInfo['clubs'][teamId]
    matchDict['Score'] = teamStats['scoreString']
    matchDict['Shots'] = teamStats['shots']
    matchDict['Name'] = teamStats['details']['name']
    matchDict['TOA'] = convertSeconds(int(teamStats['toa'])) 
    matchDict['PPG'] = teamStats['ppg']
    matchDict['PIM'] = matchInfo['aggregate'][teamId]['skpim']
    matchDict['SHG'] = matchInfo['aggregate'][teamId]['skshg']
    matchDict['Pass'] = '{:.1%}'.format(int(matchInfo['aggregate'][teamId]['skpasses'])/int(matchInfo['aggregate'][teamId]['skpassattempts']))
    matchDict['Hits'] = matchInfo['aggregate'][teamId]['skhits']
    return matchDict

def main():
    teamStats = getTeamStats(teamId)
    template = env.get_template('table.html')
    outputFromFile = template.render(teamValues = teamStats.values(), teamStat = teamStats)
    with open('tableTemp.html', 'w') as fh:
        fh.write(outputFromFile)
        fh.close()
main()
