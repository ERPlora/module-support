from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Ticket, TicketCategory, TicketMessage, SupportSettings


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'subject', 'description', 'customer', 'category',
            'priority', 'status',
        ]
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Ticket subject'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 4,
                'placeholder': _('Describe the issue in detail...'),
            }),
            'customer': forms.Select(attrs={
                'class': 'select',
            }),
            'category': forms.Select(attrs={
                'class': 'select',
            }),
            'priority': forms.Select(attrs={
                'class': 'select',
            }),
            'status': forms.Select(attrs={
                'class': 'select',
            }),
        }


class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 3,
                'placeholder': _('Type your reply...'),
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
        }


class TicketCategoryForm(forms.ModelForm):
    class Meta:
        model = TicketCategory
        fields = ['name', 'description', 'color', 'icon', 'is_active', 'sort_order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Category name'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 2,
                'placeholder': _('Category description (optional)'),
            }),
            'color': forms.Select(attrs={
                'class': 'select',
            }),
            'icon': forms.Select(attrs={
                'class': 'select',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'sort_order': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'placeholder': '0',
            }),
        }


class SupportSettingsForm(forms.ModelForm):
    class Meta:
        model = SupportSettings
        fields = [
            'auto_assign', 'default_priority',
            'sla_first_response_hours', 'sla_resolution_hours',
            'enable_customer_notifications', 'close_resolved_after_days',
        ]
        widgets = {
            'auto_assign': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'default_priority': forms.Select(attrs={
                'class': 'select',
            }),
            'sla_first_response_hours': forms.NumberInput(attrs={
                'class': 'input',
                'min': '1',
                'placeholder': '24',
            }),
            'sla_resolution_hours': forms.NumberInput(attrs={
                'class': 'input',
                'min': '1',
                'placeholder': '72',
            }),
            'enable_customer_notifications': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'close_resolved_after_days': forms.NumberInput(attrs={
                'class': 'input',
                'min': '1',
                'placeholder': '7',
            }),
        }


class TicketFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': _('Search by number, subject, customer...'),
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All Status')),
            ('open', _('Open')),
            ('in_progress', _('In Progress')),
            ('waiting_customer', _('Waiting on Customer')),
            ('resolved', _('Resolved')),
            ('closed', _('Closed')),
        ],
        widget=forms.Select(attrs={
            'class': 'select',
        }),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All Priorities')),
            ('low', _('Low')),
            ('medium', _('Medium')),
            ('high', _('High')),
            ('urgent', _('Urgent')),
        ],
        widget=forms.Select(attrs={
            'class': 'select',
        }),
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=TicketCategory.objects.none(),
        empty_label=_('All Categories'),
        widget=forms.Select(attrs={
            'class': 'select',
        }),
    )
