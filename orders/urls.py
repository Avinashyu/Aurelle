from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:food_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:food_id>/', views.update_cart, name='update_cart'),
    path('', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.order_success, name='order_success'),
    path('track/', views.track_order, name='track_order'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]