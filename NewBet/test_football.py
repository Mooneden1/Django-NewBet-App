# test_sportsdb_simple.py
import requests
import json

def test_sportsdb():
    print("Testing The Sports DB API (100% FREE)...")
    
    # Test 1: Get all leagues
    url = "https://www.thesportsdb.com/api/v1/json/3/all_leagues.php"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ The Sports DB API IS WORKING!")
            
            # Show football leagues
            football_leagues = [league for league in data['leagues'] if league['strSport'] == 'Soccer']
            print(f"Found {len(football_leagues)} football leagues")
            
            # Show top 5 leagues
            for league in football_leagues[:5]:
                print(f" - {league['strLeague']} (ID: {league['idLeague']})")
            
            return True
        else:
            print(f"Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def test_premier_league():
    print("\nTesting Premier League data...")
    
    # Premier League ID is 4328
    url = "https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4328"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'events' in data and data['events']:
                print(f"✅ Found {len(data['events'])} Premier League matches:")
                for event in data['events'][:5]:  # Show first 5
                    home = event['strHomeTeam']
                    away = event['strAwayTeam']
                    date = event['dateEvent']
                    print(f" - {home} vs {away} on {date}")
            else:
                print("No events found for Premier League")
            return True
        else:
            print(f"Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_teams():
    print("\nTesting team data...")
    
    url = "https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php?l=English%20Premier%20League"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'teams' in data:
                print(f"✅ Found {len(data['teams'])} Premier League teams:")
                for team in data['teams'][:5]:  # Show first 5
                    print(f" - {team['strTeam']} ({team['strStadium']})")
            return True
        else:
            print(f"Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("THE SPORTS DB API TEST - 100% FREE")
    print("=" * 50)
    
    if test_sportsdb():
        test_premier_league()
        test_teams()
    
    print("\n" + "=" * 50)
    print("If you see data above, your betting site will work!")
    print("=" * 50)