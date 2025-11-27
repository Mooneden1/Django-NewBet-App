"""NewBet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, re_path
from django.contrib.auth import views as av
from betapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CompetitionsView.as_view(), name="competitions"),
    path('competition/<int:id>/', CompetitionView.as_view(), name="competition"),
    path('finished_fixtures/<int:id>/', FinishedFixturesView.as_view(), name="finished-fixtures"),
    path('competition_table/<int:id>/', CompetitionTableView.as_view(), name="competition-table"),
    path('login/', av.LoginView.as_view(template_name="register/login_form.html"), name="login"),
    path('logout/', av.LogoutView.as_view(next_page="/"), name="logout"),
    path('register/', RegisterView.as_view(), name="register"),
    path('bet_fixture/<int:id>/', BetFixtureView.as_view(), name="bet-fixture"),
    path('account_details/', AccountDetailsView.as_view(), name="account-details"),
    path('show_team/<int:team_id>/', ShowTeamView.as_view(), name="show-team"),
    path('add_competitions/<int:season>/', AddCompetitionsView.as_view(), name="add-competitions"),
    path('team_standings/<int:competition_id>/<int:team_id>/', TeamStandingsView.as_view(), name="team-standings"),
]