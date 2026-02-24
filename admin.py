from django.contrib import admin

from .models import TicketCategory, Ticket, TicketMessage

@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'color', 'icon']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'subject', 'customer', 'category', 'created_at']
    search_fields = ['ticket_number', 'subject', 'description', 'priority']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'author_id', 'author_name', 'is_internal', 'created_at']
    search_fields = ['message', 'author_name']
    readonly_fields = ['created_at', 'updated_at']

