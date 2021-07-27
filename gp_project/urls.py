from django.urls import path
from . import views
from gp_project.views import *

urlpatterns = [
    path("", views.index, name="index"),
    path('about/', views.about,name="about"),

]
