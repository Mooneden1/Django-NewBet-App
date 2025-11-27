# betapp/cron.py - Updated for modern APIs
import kronos
from django.utils import timezone
from .models import *
from .update_db import update_fixtures, create_team_standing
from .api_connection import football_apis

@kronos.register('*/3 * * * *')  # Every 3 minutes
def check_fixtures_status():
    """
    Update fixture statuses (replaces old change_status function)
    Now uses live data from APIs
    """
    now = timezone.now()
    
    # Update scheduled fixtures that should be live
    scheduled_fixtures = Fixture.objects.filter(status=1)  # SCHEDULED
    for fixture in scheduled_fixtures:
        if fixture.date <= now:
            # Check if match actually started via API
            if fixture.api_fixture_id:
                match_data = football_apis.get_match_details_af(fixture.api_fixture_id)
                if match_data and 'response' in match_data:
                    status = match_data['response'][0]['fixture']['status']['short']
                    if status in ['LIVE', '1H', '2H', 'HT']:
                        fixture.status = 3  # LIVE
                    elif status == 'FT':
                        fixture.status = 2  # FINISHED
                    else:
                        fixture.status = 1  # Keep as scheduled
                    fixture.save()

@kronos.register('*/5 * * * *')  # Every 5 minutes
def update_live_data():
    """
    Update live match data including scores, events, etc.
    """
    live_matches = Fixture.objects.filter(status=3)  # LIVE matches
    
    for match in live_matches:
        if match.api_fixture_id:
            # Get live events
            events_data = football_apis.get_match_events_af(match.api_fixture_id)
            if events_data and 'response' in events_data:
                match.events = events_data['response']
            
            # Get current match data
            match_data = football_apis.get_match_details_af(match.api_fixture_id)
            if match_data and 'response' in match_data:
                fixture_data = match_data['response'][0]
                
                # Update score
                match.goals_home_team = fixture_data['goals']['home']
                match.goals_away_team = fixture_data['goals']['away']
                
                # Update minute
                status_info = fixture_data['fixture']['status']
                match.minute = status_info.get('elapsed')
                
                # Update status if finished
                if status_info['short'] == 'FT':
                    match.status = 2  # FINISHED
                    # Process finished match
                    from .update_db import check_bets
                    check_bets(match)
                
                match.save()

@kronos.register('0 */6 * * *')  # Every 6 hours
def update_fixtures_and_odds():
    """
    Update fixtures data and odds periodically
    """
    competitions = Competition.objects.all()
    for competition in competitions:
        # Update fixtures
        update_fixtures(api_id=competition.api_id)
        
        # Update standings
        create_team_standing(competition_id=competition.id)
        
        # Update odds for upcoming matches
        upcoming_matches = Fixture.objects.filter(
            competition=competition,
            status=1,  # SCHEDULED
            date__gte=timezone.now()
        )
        
        for match in upcoming_matches:
            if match.api_fixture_id:
                odds_data = football_apis.get_match_odds_af(match.api_fixture_id)
                if odds_data and 'response' in odds_data:
                    match.odds_bookmakers = odds_data['response']
                    match.last_odds_update = timezone.now()
                    match.save()