from django.urls import path
from . import views

urlpatterns = [
    path('create-ticket/', views.create_ticket_view, name='create_ticket'),
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('ticket/<int:ticket_id>/activity/', views.ticket_activity_view, name='ticket_activity'),
    path('ticket/<int:ticket_id>/update-status/', views.update_ticket_status_view, name='update_ticket_status'),
    path('ticket/<int:ticket_id>/add-comment/', views.add_comment_view, name='add_comment'),
    # path('notifications/', views.notification_list_view, name='notification_list'),

]
