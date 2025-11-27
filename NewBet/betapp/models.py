from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Competition(models.Model):
    caption = models.CharField(max_length=128)
    league = models.CharField(max_length=12)
    number_of_matchdays = models.IntegerField()
    year = models.IntegerField()
    number_of_teams = models.IntegerField()
    current_matchday = models.IntegerField()
    api_id = models.IntegerField()

    def __str__(self):
        return self.caption


class Team(models.Model):
    name = models.CharField(max_length=256)
    crest_url = models.CharField(max_length=256, null=True, blank=True)
    squad_market_value = models.CharField(max_length=64, null=True, blank=True)
    code = models.CharField(max_length=12, null=True)
    short_name = models.CharField(max_length=64)
    competition = models.ForeignKey(Competition, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


STATUS_TAB = ((1, "SCHEDULED"),
              (2, "FINISHED"),
              (3, "PLAYING")
              )

BET_CHOICES = ((1, 1),
               (2, 2),
               (0, 0)
               )


class Fixture(models.Model):
    home_team = models.ForeignKey(Team, related_name='homeTeam', on_delete=models.CASCADE)
    away_team = models.ForeignKey(Team, related_name='awayTeam', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_TAB, default=1)
    matchday = models.IntegerField()
    competition = models.ForeignKey(Competition, related_name='competition', on_delete=models.CASCADE)
    date = models.DateTimeField()
    goals_home_team = models.IntegerField(default=None, null=True, blank=True)
    goals_away_team = models.IntegerField(default=None, null=True, blank=True)
    course_team_home_win = models.FloatField(default=1, blank=True)
    course_team_away_win = models.FloatField(default=1, blank=True)
    course_draw = models.FloatField(default=1, blank=True)
    fixture_result = models.IntegerField(default=-1, blank=True)
    
    # New fields for enhanced functionality
    api_fixture_id = models.IntegerField(null=True, blank=True)
    minute = models.IntegerField(null=True, blank=True)
    events = models.JSONField(null=True, blank=True)
    odds_bookmakers = models.JSONField(null=True, blank=True)
    last_odds_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.home_team.name + " - " + self.away_team.name)


# ADD THE MISSING AppUser MODEL
class AppUser(models.Model):
    cash = models.DecimalField(
        validators=[MinValueValidator(0.00)],
        max_digits=6, 
        decimal_places=2
    )
    bank_account_number = models.CharField(max_length=64)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Bet(models.Model):
    BET_RESULTS = ((0, "LOST"),
                   (1, "WON"),
                   (2, "PENDING")
                   )
    
    BET_TYPES = (
        (1, "Home Win"),
        (2, "Away Win"),
        (0, "Draw"),
        (3, "Over 2.5 Goals"),
        (4, "Under 2.5 Goals"),
        (5, "Both Teams Score"),
        (6, "Double Chance"),
    )

    bet_user = models.ForeignKey(AppUser, related_name="bet_user", on_delete=models.CASCADE)
    bet_amount = models.DecimalField(
        validators=[MinValueValidator(0.01)],
        max_digits=6, 
        decimal_places=2
    )
    fixture = models.ForeignKey(Fixture, related_name="fixture", on_delete=models.CASCADE)
    bet = models.IntegerField(choices=BET_TYPES)
    bet_course = models.FloatField(default=0)
    bet_result = models.IntegerField(default=2, blank=True, choices=BET_RESULTS)
    bookmaker = models.CharField(max_length=50, default="Custom")
    bet_placed_at = models.DateTimeField(auto_now_add=True)


class Bookmaker(models.Model):
    """Store different bookmakers"""
    name = models.CharField(max_length=100)
    api_id = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name