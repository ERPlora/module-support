from django import forms
from django.utils.translation import gettext_lazy as _

from .models import TicketCategory, SupportSettings, Ticket

class TicketCategoryForm(forms.ModelForm):
    class Meta:
        model = TicketCategory
        fields = ['name', 'description', 'color', 'icon', 'is_active', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'color': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'icon': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'sort_order': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
        }

class SupportSettingsForm(forms.ModelForm):
    class Meta:
        model = SupportSettings
        fields = ['auto_assign', 'default_priority', 'sla_first_response_hours', 'sla_resolution_hours', 'enable_customer_notifications', 'close_resolved_after_days']
        widgets = {
            'auto_assign': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'default_priority': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'sla_first_response_hours': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'sla_resolution_hours': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'enable_customer_notifications': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'close_resolved_after_days': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
        }

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['ticket_number', 'subject', 'description', 'customer', 'category', 'priority', 'status', 'assigned_to', 'assigned_to_name', 'related_sale', 'related_product', 'first_response_at', 'resolved_at', 'closed_at']
        widgets = {
            'ticket_number': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'subject': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'customer': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'category': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'priority': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'status': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'assigned_to': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'assigned_to_name': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'related_sale': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'related_product': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'first_response_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'resolved_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'closed_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
        }

