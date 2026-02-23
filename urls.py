from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Tickets
    path('list/', views.ticket_list, name='list'),
    path('add/', views.ticket_add, name='add'),
    path('<uuid:ticket_id>/', views.ticket_detail, name='detail'),
    path('<uuid:ticket_id>/edit/', views.ticket_edit, name='edit'),
    path('<uuid:ticket_id>/delete/', views.ticket_delete, name='delete'),
    path('<uuid:ticket_id>/assign/', views.ticket_assign, name='assign'),
    path('<uuid:ticket_id>/resolve/', views.ticket_resolve, name='resolve'),
    path('<uuid:ticket_id>/close/', views.ticket_close, name='close'),
    path('<uuid:ticket_id>/reopen/', views.ticket_reopen, name='reopen'),
    path('<uuid:ticket_id>/message/', views.ticket_add_message, name='add_message'),
    path('bulk/', views.ticket_bulk_action, name='bulk_action'),

    # Categories
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<uuid:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<uuid:category_id>/delete/', views.category_delete, name='category_delete'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
