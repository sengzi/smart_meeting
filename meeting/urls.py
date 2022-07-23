from django.urls import path
from . import views
# from django.contrib.auth import views

urlpatterns = [
    path('', views.main_page, name="meeting"),
    path('about', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('group_meeting', views.group_meeting, name="group_meeting"),
    path('register', views.register, name="register"),
    path('signup', views.signup, name="signup"),
    path('logout', views.logout, name="logout"),
    path('voting',views.voting,name="voting"),
    path('calendar',views.group_meeting,name="calendar"),
    path('voting_wait',views.voting_wait,name="voting_wait"),
    path('voting_done',views.voting_done,name="voting_done"),
    path('profile', views.profile, name="profile"),
    path('appointment', views.appointment, name="appointment"),
]