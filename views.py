"""
Support Module Views
"""
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404, render as django_render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.accounts.decorators import login_required, permission_required
from apps.core.htmx import htmx_view
from apps.core.services import export_to_csv, export_to_excel
from apps.modules_runtime.navigation import with_module_nav

from .models import TicketCategory, SupportSettings, Ticket, TicketMessage

PER_PAGE_CHOICES = [10, 25, 50, 100]


# ======================================================================
# Dashboard
# ======================================================================

@login_required
@with_module_nav('support', 'dashboard')
@htmx_view('support/pages/index.html', 'support/partials/dashboard_content.html')
def dashboard(request):
    hub_id = request.session.get('hub_id')
    return {
        'total_ticket_categories': TicketCategory.objects.filter(hub_id=hub_id, is_deleted=False).count(),
        'total_tickets': Ticket.objects.filter(hub_id=hub_id, is_deleted=False).count(),
    }


# ======================================================================
# TicketCategory
# ======================================================================

TICKET_CATEGORY_SORT_FIELDS = {
    'name': 'name',
    'color': 'color',
    'icon': 'icon',
    'is_active': 'is_active',
    'sort_order': 'sort_order',
    'description': 'description',
    'created_at': 'created_at',
}

def _build_ticket_categories_context(hub_id, per_page=10):
    qs = TicketCategory.objects.filter(hub_id=hub_id, is_deleted=False).order_by('name')
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(1)
    return {
        'ticket_categories': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'name',
        'sort_dir': 'asc',
        'current_view': 'table',
        'per_page': per_page,
    }

def _render_ticket_categories_list(request, hub_id, per_page=10):
    ctx = _build_ticket_categories_context(hub_id, per_page)
    return django_render(request, 'support/partials/ticket_categories_list.html', ctx)

@login_required
@with_module_nav('support', 'list')
@htmx_view('support/pages/ticket_categories.html', 'support/partials/ticket_categories_content.html')
def ticket_categories_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'name')
    sort_dir = request.GET.get('dir', 'asc')
    page_number = request.GET.get('page', 1)
    current_view = request.GET.get('view', 'table')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    qs = TicketCategory.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(color__icontains=search_query) | Q(icon__icontains=search_query))

    order_by = TICKET_CATEGORY_SORT_FIELDS.get(sort_field, 'name')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    qs = qs.order_by(order_by)

    export_format = request.GET.get('export')
    if export_format in ('csv', 'excel'):
        fields = ['name', 'color', 'icon', 'is_active', 'sort_order', 'description']
        headers = ['Name', 'Color', 'Icon', 'Is Active', 'Sort Order', 'Description']
        if export_format == 'csv':
            return export_to_csv(qs, fields=fields, headers=headers, filename='ticket_categories.csv')
        return export_to_excel(qs, fields=fields, headers=headers, filename='ticket_categories.xlsx')

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'support/partials/ticket_categories_list.html', {
            'ticket_categories': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'sort_field': sort_field,
            'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
        })

    return {
        'ticket_categories': page_obj, 'page_obj': page_obj,
        'search_query': search_query, 'sort_field': sort_field,
        'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
    }

@login_required
def ticket_category_add(request):
    hub_id = request.session.get('hub_id')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        color = request.POST.get('color', '').strip()
        icon = request.POST.get('icon', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        sort_order = int(request.POST.get('sort_order', 0) or 0)
        obj = TicketCategory(hub_id=hub_id)
        obj.name = name
        obj.description = description
        obj.color = color
        obj.icon = icon
        obj.is_active = is_active
        obj.sort_order = sort_order
        obj.save()
        return _render_ticket_categories_list(request, hub_id)
    return django_render(request, 'support/partials/panel_ticket_category_add.html', {})

@login_required
def ticket_category_edit(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(TicketCategory, pk=pk, hub_id=hub_id, is_deleted=False)
    if request.method == 'POST':
        obj.name = request.POST.get('name', '').strip()
        obj.description = request.POST.get('description', '').strip()
        obj.color = request.POST.get('color', '').strip()
        obj.icon = request.POST.get('icon', '').strip()
        obj.is_active = request.POST.get('is_active') == 'on'
        obj.sort_order = int(request.POST.get('sort_order', 0) or 0)
        obj.save()
        return _render_ticket_categories_list(request, hub_id)
    return django_render(request, 'support/partials/panel_ticket_category_edit.html', {'obj': obj})

@login_required
@require_POST
def ticket_category_delete(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(TicketCategory, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_deleted = True
    obj.deleted_at = timezone.now()
    obj.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return _render_ticket_categories_list(request, hub_id)

@login_required
@require_POST
def ticket_category_toggle_status(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(TicketCategory, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_active = not obj.is_active
    obj.save(update_fields=['is_active', 'updated_at'])
    return _render_ticket_categories_list(request, hub_id)

@login_required
@require_POST
def ticket_categories_bulk_action(request):
    hub_id = request.session.get('hub_id')
    ids = [i.strip() for i in request.POST.get('ids', '').split(',') if i.strip()]
    action = request.POST.get('action', '')
    qs = TicketCategory.objects.filter(hub_id=hub_id, is_deleted=False, id__in=ids)
    if action == 'activate':
        qs.update(is_active=True)
    elif action == 'deactivate':
        qs.update(is_active=False)
    elif action == 'delete':
        qs.update(is_deleted=True, deleted_at=timezone.now())
    return _render_ticket_categories_list(request, hub_id)


# ======================================================================
# Ticket
# ======================================================================

TICKET_SORT_FIELDS = {
    'subject': 'subject',
    'ticket_number': 'ticket_number',
    'customer': 'customer',
    'category': 'category',
    'priority': 'priority',
    'status': 'status',
    'created_at': 'created_at',
}

def _build_tickets_context(hub_id, per_page=10):
    qs = Ticket.objects.filter(hub_id=hub_id, is_deleted=False).order_by('subject')
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(1)
    return {
        'tickets': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'subject',
        'sort_dir': 'asc',
        'current_view': 'table',
        'per_page': per_page,
    }

def _render_tickets_list(request, hub_id, per_page=10):
    ctx = _build_tickets_context(hub_id, per_page)
    return django_render(request, 'support/partials/tickets_list.html', ctx)

@login_required
@with_module_nav('support', 'list')
@htmx_view('support/pages/tickets.html', 'support/partials/tickets_content.html')
def tickets_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'subject')
    sort_dir = request.GET.get('dir', 'asc')
    page_number = request.GET.get('page', 1)
    current_view = request.GET.get('view', 'table')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    qs = Ticket.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(Q(ticket_number__icontains=search_query) | Q(subject__icontains=search_query) | Q(description__icontains=search_query) | Q(priority__icontains=search_query))

    order_by = TICKET_SORT_FIELDS.get(sort_field, 'subject')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    qs = qs.order_by(order_by)

    export_format = request.GET.get('export')
    if export_format in ('csv', 'excel'):
        fields = ['subject', 'ticket_number', 'customer', 'category', 'priority', 'status']
        headers = ['Subject', 'Ticket Number', 'customers.Customer', "Name(id='TicketCategory', ctx=Load())", 'Priority', 'Status']
        if export_format == 'csv':
            return export_to_csv(qs, fields=fields, headers=headers, filename='tickets.csv')
        return export_to_excel(qs, fields=fields, headers=headers, filename='tickets.xlsx')

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'support/partials/tickets_list.html', {
            'tickets': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'sort_field': sort_field,
            'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
        })

    return {
        'tickets': page_obj, 'page_obj': page_obj,
        'search_query': search_query, 'sort_field': sort_field,
        'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
    }

@login_required
def ticket_add(request):
    hub_id = request.session.get('hub_id')
    if request.method == 'POST':
        ticket_number = request.POST.get('ticket_number', '').strip()
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', '').strip()
        status = request.POST.get('status', '').strip()
        assigned_to = request.POST.get('assigned_to', '').strip()
        assigned_to_name = request.POST.get('assigned_to_name', '').strip()
        related_sale = request.POST.get('related_sale', '').strip()
        related_product = request.POST.get('related_product', '').strip()
        first_response_at = request.POST.get('first_response_at') or None
        resolved_at = request.POST.get('resolved_at') or None
        closed_at = request.POST.get('closed_at') or None
        obj = Ticket(hub_id=hub_id)
        obj.ticket_number = ticket_number
        obj.subject = subject
        obj.description = description
        obj.priority = priority
        obj.status = status
        obj.assigned_to = assigned_to
        obj.assigned_to_name = assigned_to_name
        obj.related_sale = related_sale
        obj.related_product = related_product
        obj.first_response_at = first_response_at
        obj.resolved_at = resolved_at
        obj.closed_at = closed_at
        obj.save()
        return _render_tickets_list(request, hub_id)
    return django_render(request, 'support/partials/panel_ticket_add.html', {})

@login_required
def ticket_edit(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(Ticket, pk=pk, hub_id=hub_id, is_deleted=False)
    if request.method == 'POST':
        obj.ticket_number = request.POST.get('ticket_number', '').strip()
        obj.subject = request.POST.get('subject', '').strip()
        obj.description = request.POST.get('description', '').strip()
        obj.priority = request.POST.get('priority', '').strip()
        obj.status = request.POST.get('status', '').strip()
        obj.assigned_to = request.POST.get('assigned_to', '').strip()
        obj.assigned_to_name = request.POST.get('assigned_to_name', '').strip()
        obj.related_sale = request.POST.get('related_sale', '').strip()
        obj.related_product = request.POST.get('related_product', '').strip()
        obj.first_response_at = request.POST.get('first_response_at') or None
        obj.resolved_at = request.POST.get('resolved_at') or None
        obj.closed_at = request.POST.get('closed_at') or None
        obj.save()
        return _render_tickets_list(request, hub_id)
    return django_render(request, 'support/partials/panel_ticket_edit.html', {'obj': obj})

@login_required
@require_POST
def ticket_delete(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(Ticket, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_deleted = True
    obj.deleted_at = timezone.now()
    obj.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return _render_tickets_list(request, hub_id)

@login_required
@require_POST
def tickets_bulk_action(request):
    hub_id = request.session.get('hub_id')
    ids = [i.strip() for i in request.POST.get('ids', '').split(',') if i.strip()]
    action = request.POST.get('action', '')
    qs = Ticket.objects.filter(hub_id=hub_id, is_deleted=False, id__in=ids)
    if action == 'delete':
        qs.update(is_deleted=True, deleted_at=timezone.now())
    return _render_tickets_list(request, hub_id)


# ======================================================================
# Settings
# ======================================================================

@login_required
@permission_required('support.manage_settings')
@with_module_nav('support', 'settings')
@htmx_view('support/pages/settings.html', 'support/partials/settings_content.html')
def settings_view(request):
    hub_id = request.session.get('hub_id')
    config, _ = SupportSettings.objects.get_or_create(hub_id=hub_id)
    if request.method == 'POST':
        config.auto_assign = request.POST.get('auto_assign') == 'on'
        config.default_priority = request.POST.get('default_priority', '').strip()
        config.sla_first_response_hours = request.POST.get('sla_first_response_hours', config.sla_first_response_hours)
        config.sla_resolution_hours = request.POST.get('sla_resolution_hours', config.sla_resolution_hours)
        config.enable_customer_notifications = request.POST.get('enable_customer_notifications') == 'on'
        config.close_resolved_after_days = request.POST.get('close_resolved_after_days', config.close_resolved_after_days)
        config.save()
    return {'config': config}

