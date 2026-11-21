from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),

    # Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # Restaurant Dashboard
    path('dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),

    # Menu Management
    path('manage-menu/', views.manage_menu, name='manage_menu'),
    path('manage-menu/add/', views.add_food, name='add_food'),
    path('manage-menu/edit/<int:food_id>/', views.edit_food, name='edit_food'),
    path('manage-menu/delete/<int:food_id>/', views.delete_food, name='delete_food'),
    path('manage-menu/toggle/<int:food_id>/', views.toggle_food, name='toggle_food'),

    # Order Management
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]