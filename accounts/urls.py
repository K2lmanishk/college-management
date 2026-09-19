from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-panel/users/', views.manage_users, name='manage_users'),
    path('admin-panel/users/add/', views.add_user, name='add_user'),
    path('admin-panel/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
]
