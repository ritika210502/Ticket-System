from django.urls import path
from . import views

urlpatterns = [
    path('create-ticket/', views.create_ticket_view, name='create_ticket'),
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('', views.ticket_list_view, name='ticket_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/',views.logout_view, name='logout'),
]
