from django.urls import path
from . import views

urlpatterns = [
    path('author/<int:author_id>/', views.author_details, name='author_details'),
    path('author_view/', views.author_view, name='author_view'),
    path('profile/<int:profile_id>', views.profile_details, name='profile_details'),
    # authentication
    path('signup/', views.register_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # user profile
    path('my-profile/', views.user_profile_view, name='user_profile'),
]
