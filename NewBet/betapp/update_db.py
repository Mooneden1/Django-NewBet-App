from .api_connection import sports_api, get_competitions, get_fixtures, get_league_table
from .models import AppUser, User, Competition, Fixture, Team, Bet

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.conf import settings

from random import randint
from decimal import Decimal

import redis


r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB,
                      decode_responses=True)


def create_team(name, crest_url, short_name, competition):
    """
    Creates single Team object and saves it to db
    """
    try:
        Team.objects.get(name=name, competition=competition)
    except ObjectDoesNotExist:
        Team.objects.create(
            name=name,
            crest_url=crest_url,
            short_name=short_name,
            competition=competition
        )


def create_teams(league_name, competition):
    """
    Creates teams for a competition using The Sports DB
    """
    teams_data = sports_api.get_teams_by_league(league_name)
    
    if teams_data and 'teams' in teams_data:
        for team_data in teams_data['teams']:
            name = team_data['strTeam']
            crest_url = team_data['strTeamBadge']
            short_name = team_data['strTeamShort'] or name[:10]
            code = team_data['strTeamShort'] or name[:3].upper()

            create_team(name, crest_url, short_name, competition)


def get_team_balance(team_name, venue):
    """
    Gets simulated team balance (since The Sports DB doesn't have detailed stats)
    """
    # For demo purposes, generate random stats
    # In a real app, you'd get this from a more detailed API
    wins = randint(3, 10)
    draws = randint(2, 8)
    losses = randint(1, 7)

    balance = {
        "wins": wins,
        "draws": draws,
        "losses": losses
    }
    return balance


def calculate_result_odds(balance):
    """
    Calculates result odds based on simulated team balance
    """
    home_wins = balance['home_wins']
    home_draws = balance['home_draws']
    home_losses = balance['home_losses']
    away_wins = balance['away_wins']
    away_draws = balance['away_draws']
    away_losses = balance['away_losses']
    
    # Sum all games
    sum_of_fixtures = sum([home_wins, home_draws, home_losses, away_wins,
                           away_draws, away_losses])

    # Calculate prices of particular outcomes
    home_price = home_wins + away_losses
    draw_price = home_draws + away_draws
    away_price = home_losses + away_wins

    # If team price is 0 then assume probability is unlikely
    if home_price == 0:
        home_price = 0.1
    if draw_price == 0:
        draw_price = 0.1
    if away_price == 0:
        away_price = 0.1

    home_win = round(1 / (home_price / sum_of_fixtures), 2)
    draw = round(1 / (draw_price / sum_of_fixtures), 2)
    away_win = round(1 / (away_price / sum_of_fixtures), 2)

    odds = {
        'home_win': home_win,
        'draw': draw,
        'away_win': away_win
    }
    return odds


def calculate_odds(home_team_name, away_team_name):
    """
    Calculate odds for a fixture
    """
    home_team_balance = get_team_balance(home_team_name, 'home')
    away_team_balance = get_team_balance(away_team_name, 'away')

    both_teams_balance = {
        'home_wins': home_team_balance['wins'],
        'home_draws': home_team_balance['draws'],
        'home_losses': home_team_balance['losses'],
        'away_wins': away_team_balance['wins'],
        'away_draws': away_team_balance['draws'],
        'away_losses': away_team_balance['losses'],
    }

    return calculate_result_odds(both_teams_balance)


def create_fixture(home_team_name, away_team_name, date, competition, matchday=1):
    """
    Creates fixture and saves it to db
    """
    try:
        home_team = Team.objects.get(name=home_team_name, competition=competition)
        away_team = Team.objects.get(name=away_team_name, competition=competition)
        
        odds = calculate_odds(home_team_name, away_team_name)

        # Try to get fixture if exists, else create new fixture object
        try:
            fixture = Fixture.objects.get(
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                date=date
            )
        except ObjectDoesNotExist:
            Fixture.objects.create(
                home_team=home_team,
                away_team=away_team,
                competition=competition,
                matchday=matchday,
                date=date,
                course_team_home_win=odds['home_win'],
                course_team_away_win=odds['away_win'],
                course_draw=odds['draw']
            )
    except Team.DoesNotExist:
        print(f"Team not found: {home_team_name} or {away_team_name}")


def create_fixtures(league_id, competition):
    """
    Creates fixtures for a competition using The Sports DB
    """
    events_data = sports_api.get_events_by_league(league_id)
    
    if events_data and 'events' in events_data:
        matchday = 1
        for event in events_data['events']:
            home_team = event['strHomeTeam']
            away_team = event['strAwayTeam']
            date_str = event['dateEvent']
            time_str = event.get('strTime', '15:00:00')
            date = f"{date_str} {time_str}"
            
            create_fixture(home_team, away_team, date, competition, matchday)
            
            # Simple matchday increment for demo
            if len(events_data['events']) > 10:
                matchday = (matchday % 5) + 1  # Cycle through 5 matchdays


def create_competition(league_id, league_name):
    """
    Creates competition and its teams/fixtures using The Sports DB
    """
    try:
        # Try to get existing competition
        comp = Competition.objects.get(caption=league_name, api_id=league_id)
        print(f"Competition {league_name} already exists")
        return comp
    except ObjectDoesNotExist:
        # Create new competition
        comp = Competition(
            caption=league_name,
            league=league_name[:12],
            number_of_matchdays=38,
            year=2024,
            number_of_teams=20,
            current_matchday=1,
            api_id=league_id
        )
        comp.save()
        print(f"Created competition: {league_name}")
        
        # Create teams and fixtures
        create_teams(league_name, comp)
        create_fixtures(league_id, comp)
        
        return comp


def get_team(name, competition):
    """
    Gets Team object from db based on team name and competition
    """
    return Team.objects.get(name=name, competition=competition)


def get_fixture(away_team_name, home_team_name, competition):
    """
    Gets Fixture object
    """
    away_team = get_team(away_team_name, competition)
    home_team = get_team(home_team_name, competition)
    return Fixture.objects.get(
        home_team=home_team,
        away_team=away_team,
        competition=competition
    )


def get_fixture_result(goals_home_team, goals_away_team):
    """
    Returns fixture result based on home/away goals
    """
    if goals_home_team > goals_away_team:
        return 1
    elif goals_home_team == goals_away_team:
        return 0
    elif goals_home_team < goals_away_team:
        return 2


def cash_user(bet):
    """
    Transfers money to AppUser account if user won their bet
    """
    app_user = bet.bet_user
    if bet.bet_result == 1:
        cash_win = bet.bet_amount * Decimal(bet.bet_course)
        app_user.cash += cash_win
        app_user.save()


def check_bets(fixture):
    """
    Checks all bets related to given fixture
    """
    bets = Bet.objects.filter(fixture=fixture)

    for bet in bets:
        if bet.bet == fixture.fixture_result:
            bet.bet_result = 1
            bet.save()
            cash_user(bet)
        else:
            bet.bet_result = 0
            bet.save()


def update_fixture(fixture, goals_away_team, goals_home_team):
    """
    Updates given fixture with away/home goals
    """
    if fixture.status == 1 or fixture.status == 3:
        fixture.goals_home_team = goals_home_team
        fixture.goals_away_team = goals_away_team
        fixture.status = 2
        fixture.fixture_result = get_fixture_result(goals_home_team, goals_away_team)
        fixture.save()
        check_bets(fixture)


def update_fixtures(api_id, matchday=""):
    """
    Updates fixtures with data from API
    Note: The Sports DB doesn't have live score updates in the free version
    This is a placeholder for when you upgrade to a paid API
    """
    print(f"Would update fixtures for competition {api_id}")
    # For now, we'll just update odds
    update_odds_in_fixtures(api_id)


def update_odds_in_fixtures(api_id):
    """
    Updates odds for scheduled fixtures
    """
    fixtures = Fixture.objects.filter(status=1, competition__api_id=api_id)

    for fixture in fixtures:
        odds = calculate_odds(fixture.home_team.name, fixture.away_team.name)
        fixture.course_team_home_win = odds['home_win']
        fixture.course_draw = odds['draw']
        fixture.course_team_away_win = odds['away_win']
        fixture.save()


def create_team_standing(competition_id):
    """
    Creates team standing in Redis
    Note: The Sports DB has limited standing data, so we'll simulate it
    """
    competition = get_object_or_404(Competition, id=competition_id)
    teams = Team.objects.filter(competition=competition)
    
    for i, team in enumerate(teams):
        matchday = 1
        position = i + 1  # Simple ranking for demo
        list_name = "{}:{}:standing".format(competition.id, team.id)
        if not r.hexists(list_name, matchday):
            r.hset(list_name, matchday, position)