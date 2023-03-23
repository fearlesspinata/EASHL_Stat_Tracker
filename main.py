import requests
from collections import namedtuple, Counter
import pprint
import json
from bs4 import BeautifulSoup as bsoup
from jinja2 import Environment, PackageLoader, select_autoescape
from datetime import timedelta

# def convertSeconds(seconds):
#    toa = str(timedelta(seconds=seconds))
#    toa = toa.replace('0:', '', 1)
#    return toa

# def getMatchHistory(teamId, platform):
#    headers = {'referer': 'www.ea.com'}
#    url =  f"https://proclubs.ea.com/api/nhl/clubs/matches?clubIds={teamId}&platform={platform}&matchType=club_private"
#    r = requests.get(url, headers=headers)
#    return r.json()

# def getClubInfo(teamId):
#    matchInfo = getMatchHistory(teamId, platform)
#    clubInfo = matchInfo[0]['clubs']
#    return clubInfo

# def getPlayerId():
#    playerName = input('Please provide player\'s name ')
#    clubInfo = getClubInfo(teamId)
#    playerStruct = clubInfo[0]['players']['1375']
#    for playerId in playerStruct:
#        if playerStruct[playerId]['playername'] == playerName:
#            return playerId

# def getPlayerStats(getPlayerId):
#    skaterDict= {'skgoals': 0, 'skassists': 0, 'skplusmin': 0}
#    goalieDict = {'glsavepct': 0, 'glgaa': 0, 'glshots': 0}
#    playerId = getPlayerId()
#    clubInfo = getClubInfo(teamId)
#    playerStruct = clubInfo[0]['players']['1375']
#
#    if playerStruct[playerId]['position'] != 'goalie':
#        for skStat in skaterDict:
#            skaterDict[skStat] = playerStruct[playerId][skStat]
#        return skaterDict
#    else:
#        for glStat in goalieDict:
#            goalieDict[glStat] = playerStruct[playerId][glStat]
#        return goalieDict

# def getTeamStats(teamId):
#    matchDict = {'Score': 0, 'Shots': 0, 'TOA': 0, 'PPG': 0, 'PIM': 0, 'SHG': 0, 'Pass': 0, 'Hits': 0, 'Name': 0 }
#    matchInfo = getMatchHistory(teamId, platform)[0]
#    teamStats = matchInfo['clubs'][teamId]
#    matchDict['Score'] = teamStats['scoreString']
#    matchDict['Shots'] = teamStats['shots']
#    matchDict['Name'] = teamStats['details']['name']
#    matchDict['TOA'] = convertSeconds(int(teamStats['toa']))
#    matchDict['PPG'] = teamStats['ppg']
#    matchDict['PIM'] = matchInfo['aggregate'][teamId]['skpim']
#    matchDict['SHG'] = matchInfo['aggregate'][teamId]['skshg']
#    matchDict['Pass'] = '{:.1%}'.format(int(matchInfo['aggregate'][teamId]['skpasses'])/int(matchInfo['aggregate'][teamId]['skpassattempts']))
#    matchDict['Hits'] = matchInfo['aggregate'][teamId]['skhits']
#    return matchDict


class Team:
    """
    A class to instantiate a given team as an object. Many of the methods and variables of
    this class are intended to private as in most cases users would not likely be interacting
    with them much and will require little input from them other than the base information
    required to instantiate the class. There will be some additional methods that will
    be added later that would be called on from with the django framework (or whatever
    framework I choose for the project but the methods will mostly just to help convert some
    of the datapoints that we get from EA's API into a human readable format.
    """
    def __init__(self, team):
        self.headers = {'referer': 'www.ea.com',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-language': 'en-US,en;q=0.9',
                        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36'}
        self.team = team
        self.platform = 'common-gen5'
        self._team_info_endpoint = f"https://proclubs.ea.com/api/nhl/clubs/search?clubName={self.team}&platform={self.platform}"
        self.session = requests.Session()
        self.team_id = self._get_team_id()
        self._last_match_endpoint = f"https://proclubs.ea.com/api/nhl/clubs/matches?clubIds={self.team_id}&platform={self.platform}&matchType=club_private"
        self.team_stats = self._get_team_stats()
        self.last_ten_games = self._last_10_results()

    def _get_team_id(self):
        response = self.session.get(self._team_info_endpoint, headers=self.headers)
        for item in response.json():
            team_info = response.json()[item]
        return team_info['clubId']

    def _get_team_stats(self):
        response = self.session.get(self._team_info_endpoint, headers=self.headers)
        for item in response.json():
            team_stats = response.json()[item]
        return team_stats

    def _last_10_results(self):
        count = 9
        last_ten_results = []
        Last_ten_games = namedtuple('Record', ['w', 'l', 'otl'])
        while count >= 0:
            current_result = self.team_stats['recentResult' + str(count)]
            if current_result == '0':
                last_ten_results.append('w')
            if current_result == '1':
                last_ten_results.append('otl')
            if current_result == '2':
                last_ten_results.append('l')
            count -= 1
        count_record = Counter(last_ten_results)
        last_ten_record = Last_ten_games(count_record['w'], count_record['l'], count_record['otl'])
        return last_ten_record


class Player:

    def __init__(self, player_name, platform):
        self.headers = {'referer': 'www.ea.com',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-language': 'en-US,en;q=0.9',
                        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36'}
        self.player_name = player_name
        self.platform = platform
        self.player_endpoint = f'https://proclubs.ea.com/api/nhl/members/search?platform={self.platform}&memberName={self.player_name}'
        self.session = requests.Session()
        self.player_stats = self._get_player_stat()

    def _get_player_stat(self):
        response = self.session.get(self.player_endpoint, headers=self.headers)
        return response.json()['members'][0]
