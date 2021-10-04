from django.contrib import admin
from django.urls import path, include

from . import views
app_name = 'recommend'
urlpatterns = [
    path('', views.index, name = "home"),
    path('recommend/', views.recommend, name = "recommend"),
    path('<int:movie_id>/', views.movie_details, name = 'movie_details')
]
