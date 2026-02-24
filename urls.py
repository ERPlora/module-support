from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # TicketCategory
    path('ticket_categories/', views.ticket_categories_list, name='ticket_categories_list'),
    path('ticket_categories/add/', views.ticket_category_add, name='ticket_category_add'),
    path('ticket_categories/<uuid:pk>/edit/', views.ticket_category_edit, name='ticket_category_edit'),
    path('ticket_categories/<uuid:pk>/delete/', views.ticket_category_delete, name='ticket_category_delete'),
    path('ticket_categories/<uuid:pk>/toggle/', views.ticket_category_toggle_status, name='ticket_category_toggle_status'),
    path('ticket_categories/bulk/', views.ticket_categories_bulk_action, name='ticket_categories_bulk_action'),

    # Ticket
    path('tickets/', views.tickets_list, name='tickets_list'),
    path('tickets/add/', views.ticket_add, name='ticket_add'),
    path('tickets/<uuid:pk>/edit/', views.ticket_edit, name='ticket_edit'),
    path('tickets/<uuid:pk>/delete/', views.ticket_delete, name='ticket_delete'),
    path('tickets/bulk/', views.tickets_bulk_action, name='tickets_bulk_action'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
