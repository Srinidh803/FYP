# webpage/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.player_profile, name='player_profile'),
    path('add-player/<str:username>/', views.add_player, name='add_player'),
    path('chat/', views.chat_page, name='chat'),
    path('post/create/', views.create_post, name='create_post'),
    path('rate/<str:username>/', views.rate_player, name='rate_player'),
    path('manage-requests/', views.manage_requests, name='manage_requests'),

    
    # Auth Views
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]
