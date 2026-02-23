from django.utils.translation import gettext_lazy as _

MODULE_ID = 'support'
MODULE_NAME = _('Support')
MODULE_VERSION = '1.0.0'
MODULE_ICON = 'headset-outline'
MODULE_DESCRIPTION = _('Customer support ticket system with SLA tracking')
MODULE_AUTHOR = 'ERPlora'
MODULE_CATEGORY = 'support'

MENU = {
    'label': _('Support'),
    'icon': 'headset-outline',
    'order': 60,
}

NAVIGATION = [
    {'label': _('Dashboard'), 'icon': 'speedometer-outline', 'id': 'dashboard'},
    {'label': _('Tickets'), 'icon': 'ticket-outline', 'id': 'list'},
    {'label': _('Categories'), 'icon': 'pricetags-outline', 'id': 'categories'},
    {'label': _('Settings'), 'icon': 'settings-outline', 'id': 'settings'},
]

DEPENDENCIES = ['customers']

PERMISSIONS = [
    'support.view_ticket',
    'support.add_ticket',
    'support.change_ticket',
    'support.delete_ticket',
    'support.close_ticket',
    'support.assign_ticket',
    'support.view_category',
    'support.manage_categories',
    'support.manage_settings',
]
