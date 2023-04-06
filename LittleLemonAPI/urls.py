from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
#MENU ITEMS
    path('menu-items/', views.menu_items),
    path('menu-items/<int:id>', views.single_item),

#USER GROUPS
    path('groups/manager/users/', views.managers),
    path('groups/delivery-crew/users/', views.delivery_crew),
    path('users/', views.user),

#AUTHENTICATION
    path('users/users/me/', views.current_user),
    path('token/login/', obtain_auth_token),

#CART
    path('cart/menu-items/', views.cart),

#ORDERS
    path('orders/', views.orders),
    path('orders/<int:id>', views.single_orders),
]