# betapp/api_connection.py - The Sports DB (100% FREE, no API key)
import requests
import json
from datetime import datetime

class TheSportsDB:
    def __init__(self):
        self.base_url = "https://www.thesportsdb.com/api/v1/json/3/"
    
    def make_request(self, endpoint):
        """Make API request - completely free, no API key needed"""
        url = self.base_url + endpoint
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def get_all_leagues(self):
        """Get all football leagues"""
        return self.make_request("all_leagues.php")

    def get_teams_by_league(self, league_name):
        """Get teams by league name"""
        return self.make_request(f"search_all_teams.php?l={league_name}")

    def get_events_by_league(self, league_id):
        """Get events/fixtures by league ID"""
        return self.make_request(f"eventsseason.php?id={league_id}")

    def get_latest_events(self, league_id=4328):
        """Get latest events - Premier League by default"""
        return self.make_request(f"eventsseason.php?id={league_id}")

    def get_league_table(self, league_id):
        """Get league table"""
        return self.make_request(f"lookuptable.php?l={league_id}&s=2024-2025")

    def get_live_scores(self):
        """Get live scores (limited)"""
        return self.make_request("livescore.php?l=4328")

# Initialize the API
sports_api = TheSportsDB()

# Popular League IDs
LEAGUE_IDS = {
    'premier_league': 4328,
    'la_liga': 4335,
    'serie_a': 4332,
    'bundesliga': 4331,
    'champions_league': 4480,
    'europa_league': 4481
}

# Backward compatibility functions
def get_competitions(id="", season=""):
    return sports_api.get_all_leagues()

def get_fixtures(competition_id, matchday=None):
    return sports_api.get_events_by_league(competition_id)

def get_league_table(competition_id, matchday=None):
    return sports_api.get_league_table(competition_id)

def get_team_last_fixtures(team_api_id):
    return sports_api.get_latest_events()