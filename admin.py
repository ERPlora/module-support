from django.contrib import admin

from .models import Ticket, TicketCategory, TicketMessage, SupportSettings


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'icon', 'is_active', 'sort_order')
    list_filter = ('is_active', 'color')
    search_fields = ('name',)
    ordering = ('sort_order', 'name')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_number', 'subject', 'customer', 'category',
        'priority', 'status', 'assigned_to_name', 'created_at',
    )
    list_filter = ('status', 'priority', 'category')
    search_fields = ('ticket_number', 'subject', 'customer__name')
    readonly_fields = ('ticket_number', 'first_response_at', 'resolved_at', 'closed_at')
    ordering = ('-created_at',)


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author_name', 'is_internal', 'created_at')
    list_filter = ('is_internal',)
    search_fields = ('message', 'author_name')
    ordering = ('-created_at',)


@admin.register(SupportSettings)
class SupportSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'auto_assign', 'default_priority',
        'sla_first_response_hours', 'sla_resolution_hours',
    )
