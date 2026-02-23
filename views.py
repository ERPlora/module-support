"""
Support Module Views

Ticket management: dashboard, list, create, update, delete, assign, resolve, close.
Categories and settings management.
"""
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, F
from django.db.models.functions import ExtractWeek, ExtractYear
from django.shortcuts import get_object_or_404, render as django_render
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.accounts.decorators import login_required
from apps.core.htmx import htmx_view
from apps.modules_runtime.navigation import with_module_nav

from .models import Ticket, TicketCategory, TicketMessage, SupportSettings


# ============================================================================
# Constants
# ============================================================================

TICKET_SORT_FIELDS = {
    'number': 'ticket_number',
    'subject': 'subject',
    'priority': 'priority',
    'status': 'status',
    'created': 'created_at',
    'updated': 'updated_at',
}

PER_PAGE_CHOICES = [10, 25, 50, 100]


def _hub_id(request):
    return request.session.get('hub_id')


def _get_staff_name(request):
    """Get the display name of the current user from the session."""
    return request.session.get('display_name', request.session.get('username', _('Staff')))


def _get_staff_id(request):
    """Get the UUID of the current user from the session."""
    return request.session.get('user_id')


def _render_ticket_list(request, hub_id, per_page=10):
    """Render the tickets list partial after a mutation."""
    tickets = (
        Ticket.objects.filter(hub_id=hub_id, is_deleted=False)
        .select_related('customer', 'category')
        .order_by('-created_at')
    )
    paginator = Paginator(tickets, per_page)
    page_obj = paginator.get_page(1)
    categories = TicketCategory.objects.filter(
        hub_id=hub_id, is_deleted=False, is_active=True,
    ).order_by('sort_order', 'name')
    return django_render(request, 'support/partials/tickets_list.html', {
        'tickets': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'created',
        'sort_dir': 'desc',
        'status_filter': '',
        'priority_filter': '',
        'category_filter': '',
        'categories_list': categories,
        'per_page': per_page,
    })


def _render_category_list(request, hub_id):
    """Render the categories list partial after a mutation."""
    category_list = (
        TicketCategory.objects.filter(hub_id=hub_id, is_deleted=False)
        .annotate(
            ticket_count_val=Count(
                'tickets',
                filter=Q(tickets__is_deleted=False),
            )
        )
        .order_by('sort_order', 'name')
    )
    return django_render(request, 'support/partials/categories_list.html', {
        'categories': category_list,
        'search_query': '',
        'sort_field': 'name',
        'sort_dir': 'asc',
    })


# ============================================================================
# Dashboard
# ============================================================================

@login_required
@with_module_nav('support', 'dashboard')
@htmx_view('support/pages/dashboard.html', 'support/partials/dashboard_content.html')
def dashboard(request):
    """Support dashboard with ticket statistics and recent tickets."""
    hub = _hub_id(request)
    now = timezone.now()

    # Base querysets
    all_tickets = Ticket.objects.filter(hub_id=hub, is_deleted=False)
    open_tickets = all_tickets.filter(status__in=['open', 'in_progress', 'waiting_customer'])

    # Stats
    open_count = open_tickets.count()
    awaiting_response = all_tickets.filter(
        status__in=['open', 'in_progress'],
        first_response_at__isnull=True,
    ).count()

    # Resolved this week
    week_start = now - timezone.timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_this_week = all_tickets.filter(
        resolved_at__gte=week_start,
    ).count()

    # Average resolution time (hours) for resolved tickets
    resolved_tickets = all_tickets.filter(resolved_at__isnull=False)
    avg_resolution = None
    if resolved_tickets.exists():
        total_hours = 0
        count = 0
        for t in resolved_tickets[:100]:
            delta = t.resolved_at - t.created_at
            total_hours += delta.total_seconds() / 3600
            count += 1
        if count:
            avg_resolution = round(total_hours / count, 1)

    # SLA compliance rate
    # Tickets that got first response within SLA
    settings = SupportSettings.get_settings(hub)
    sla_response_hours = settings.sla_first_response_hours
    responded_tickets = all_tickets.filter(first_response_at__isnull=False)
    total_responded = responded_tickets.count()
    if total_responded > 0:
        compliant = 0
        for t in responded_tickets[:200]:
            deadline = t.created_at + timezone.timedelta(hours=sla_response_hours)
            if t.first_response_at <= deadline:
                compliant += 1
        sla_compliance = round((compliant / total_responded) * 100)
    else:
        sla_compliance = 100  # No tickets = 100% compliant

    # SLA breached count (tickets awaiting response past deadline)
    sla_breached_count = 0
    pending_response = all_tickets.filter(
        status__in=['open', 'in_progress'],
        first_response_at__isnull=True,
    )
    for t in pending_response:
        deadline = t.created_at + timezone.timedelta(hours=sla_response_hours)
        if now > deadline:
            sla_breached_count += 1

    # Priority breakdown
    priority_breakdown = (
        open_tickets
        .values('priority')
        .annotate(count=Count('id'))
        .order_by('priority')
    )
    priority_counts = {item['priority']: item['count'] for item in priority_breakdown}

    # Recent tickets (last 10)
    recent_tickets = (
        all_tickets
        .select_related('customer', 'category')
        .order_by('-created_at')[:10]
    )

    return {
        'open_count': open_count,
        'awaiting_response': awaiting_response,
        'resolved_this_week': resolved_this_week,
        'avg_resolution': avg_resolution,
        'sla_compliance': sla_compliance,
        'sla_breached_count': sla_breached_count,
        'priority_low': priority_counts.get('low', 0),
        'priority_medium': priority_counts.get('medium', 0),
        'priority_high': priority_counts.get('high', 0),
        'priority_urgent': priority_counts.get('urgent', 0),
        'recent_tickets': recent_tickets,
    }


# ============================================================================
# Ticket List (Datatable)
# ============================================================================

@login_required
@with_module_nav('support', 'list')
@htmx_view('support/pages/list.html', 'support/partials/tickets_content.html')
def ticket_list(request):
    """Tickets list with search, sort, filter, pagination."""
    hub = _hub_id(request)
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'created')
    sort_dir = request.GET.get('dir', 'desc')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    tickets = (
        Ticket.objects.filter(hub_id=hub, is_deleted=False)
        .select_related('customer', 'category')
    )

    # Status filter
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    # Priority filter
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)

    # Category filter
    if category_filter:
        tickets = tickets.filter(category_id=category_filter)

    # Search
    if search_query:
        tickets = tickets.filter(
            Q(ticket_number__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(customer__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Sort
    order_by = TICKET_SORT_FIELDS.get(sort_field, 'created_at')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    tickets = tickets.order_by(order_by)

    # Pagination
    paginator = Paginator(tickets, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    categories_list = TicketCategory.objects.filter(
        hub_id=hub, is_deleted=False, is_active=True,
    ).order_by('sort_order', 'name')

    context = {
        'tickets': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_field': sort_field,
        'sort_dir': sort_dir,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'categories_list': categories_list,
        'per_page': per_page,
    }

    # HTMX partial: swap only datatable body
    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'support/partials/tickets_list.html', context)

    context.update({
        'current_section': 'tickets',
        'page_title': str(_('Tickets')),
    })
    return context


# ============================================================================
# Ticket CRUD
# ============================================================================

@login_required
def ticket_add(request):
    """Add ticket -- renders in side panel via HTMX."""
    hub = _hub_id(request)
    categories = TicketCategory.objects.filter(
        hub_id=hub, is_deleted=False, is_active=True,
    ).order_by('sort_order', 'name')

    # Get customers for the dropdown
    try:
        from customers.models import Customer
        customers = Customer.objects.filter(
            hub_id=hub, is_deleted=False, is_active=True,
        ).order_by('name')
    except (ImportError, Exception):
        customers = []

    settings = SupportSettings.get_settings(hub)

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        if not subject:
            messages.error(request, _('Subject is required'))
            return django_render(request, 'support/partials/panel_ticket_add.html', {
                'categories': categories,
                'customers': customers,
                'settings': settings,
            })

        customer_id = request.POST.get('customer', '').strip() or None
        category_id = request.POST.get('category', '').strip() or None
        priority = request.POST.get('priority', settings.default_priority)

        ticket = Ticket(
            hub_id=hub,
            subject=subject,
            description=request.POST.get('description', '').strip(),
            priority=priority,
            created_by=_get_staff_id(request),
        )

        if customer_id:
            try:
                from customers.models import Customer
                ticket.customer = Customer.objects.get(
                    id=customer_id, hub_id=hub, is_deleted=False,
                )
            except Exception:
                pass

        if category_id:
            try:
                ticket.category = TicketCategory.objects.get(
                    id=category_id, hub_id=hub, is_deleted=False,
                )
            except Exception:
                pass

        ticket.save()

        # Create initial message from the description
        if ticket.description:
            TicketMessage.objects.create(
                hub_id=hub,
                ticket=ticket,
                message=ticket.description,
                author_id=_get_staff_id(request),
                author_name=str(_get_staff_name(request)),
                is_internal=False,
            )

        messages.success(request, _('Ticket %(number)s created successfully') % {
            'number': ticket.ticket_number,
        })
        return _render_ticket_list(request, hub)

    return django_render(request, 'support/partials/panel_ticket_add.html', {
        'categories': categories,
        'customers': customers,
        'settings': settings,
    })


@login_required
def ticket_edit(request, ticket_id):
    """Edit ticket -- renders in side panel via HTMX."""
    hub = _hub_id(request)
    ticket = get_object_or_404(Ticket, id=ticket_id, hub_id=hub, is_deleted=False)
    categories = TicketCategory.objects.filter(
        hub_id=hub, is_deleted=False, is_active=True,
    ).order_by('sort_order', 'name')

    try:
        from customers.models import Customer
        customers = Customer.objects.filter(
            hub_id=hub, is_deleted=False, is_active=True,
        ).order_by('name')
    except (ImportError, Exception):
        customers = []

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        if not subject:
            messages.error(request, _('Subject is required'))
            return django_render(request, 'support/partials/panel_ticket_edit.html', {
                'ticket': ticket,
                'categories': categories,
                'customers': customers,
            })

        ticket.subject = subject
        ticket.description = request.POST.get('description', '').strip()
        ticket.priority = request.POST.get('priority', ticket.priority)
        ticket.status = request.POST.get('status', ticket.status)

        customer_id = request.POST.get('customer', '').strip()
        if customer_id:
            try:
                from customers.models import Customer
                ticket.customer = Customer.objects.get(
                    id=customer_id, hub_id=hub, is_deleted=False,
                )
            except Exception:
                pass
        else:
            ticket.customer = None

        category_id = request.POST.get('category', '').strip()
        if category_id:
            try:
                ticket.category = TicketCategory.objects.get(
                    id=category_id, hub_id=hub, is_deleted=False,
                )
            except Exception:
                pass
        else:
            ticket.category = None

        ticket.updated_by = _get_staff_id(request)
        ticket.save()

        messages.success(request, _('Ticket updated successfully'))
        return _render_ticket_list(request, hub)

    return django_render(request, 'support/partials/panel_ticket_edit.html', {
        'ticket': ticket,
        'categories': categories,
        'customers': customers,
    })


@login_required
@require_POST
def ticket_delete(request, ticket_id):
    """Soft delete ticket."""
    hub = _hub_id(request)
    ticket = get_object_or_404(Ticket, id=ticket_id, hub_id=hub, is_deleted=False)
    ticket.is_deleted = True
    ticket.deleted_at = timezone.now()
    ticket.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    messages.success(request, _('Ticket %(number)s deleted') % {
        'number': ticket.ticket_number,
    })
    return _render_ticket_list(request, hub)


# ============================================================================
# Ticket Actions
# ============================================================================

@login_required
@require_POST
def ticket_assign(request, ticket_id):
    """Assign ticket to the current user."""
    hub = _hub_id(request)
    ticket = get_object_or_404(Ticket, id=ticket_id, hub_id=hub, is_deleted=False)

    user_id = _get_staff_id(request)
    user_name = str(_get_staff_name(request))
    ticket.assign(user_id, user_name)

    messages.success(request, _('Ticket assigned to %(name)s') % {'name': user_name})
    return _render_ticket_detail(request, ticket)


@login_required
@require_POST
def ticket_resolve(request, ticket_id):
    """Mark ticket as resolved."""
    hub = _hub_id(request)
    ticket = get_object_or_404(Ticket, id=ticket_id, hub_id=hub, is_deleted=False)
    ticket.resolve()

    messages.success(request, _('Ticket %(number)s marked as resolved') % {
        'number': ticket.ticket_number,
    })
    return _render_ticket_detail(request, ticket)


@login_required
@require_POST
def ticket_close(request, ticket_id):
    """Close a ticket."""
    hub = _hub_id(request)
    ticket = get_object_or_404(Ticket, id=ticket_id, hub_id=hub, is_deleted=False)
    ticket.close()

    messages.success(request, _('Ticket %(number)s closed') % {
        'number': ticket.ticket_number,
    })
    return _render_ticket_detail(request, ticket)


@login_required
@require_POST
def ticket_reopen(request, ticket_id):
    """Reopen a resolved/closed ticket."""
    hub = _hub_id(request)
    ticket = get_object_or_404(Ticket, id=ticket_id, hub_id=hub, is_deleted=False)
    ticket.reopen()

    messages.success(request, _('Ticket %(number)s reopened') % {
        'number': ticket.ticket_number,
    })
    return _render_ticket_detail(request, ticket)


def _render_ticket_detail(request, ticket):
    """Render the ticket detail partial (used after ticket actions)."""
    ticket.refresh_from_db()
    ticket_messages = ticket.messages.filter(is_deleted=False).order_by('created_at')
    return django_render(request, 'support/partials/detail_content.html', {
        'ticket': ticket,
        'ticket_messages': ticket_messages,
    })


# ============================================================================
# Ticket Messages
# ============================================================================

@login_required
@require_POST
def ticket_add_message(request, ticket_id):
    """Add a message/reply to a ticket."""
    hub = _hub_id(request)
    ticket = get_object_or_404(Ticket, id=ticket_id, hub_id=hub, is_deleted=False)

    message_text = request.POST.get('message', '').strip()
    if not message_text:
        messages.error(request, _('Message cannot be empty'))
        ticket_messages = ticket.messages.filter(is_deleted=False).order_by('created_at')
        return django_render(request, 'support/partials/ticket_messages.html', {
            'ticket': ticket,
            'ticket_messages': ticket_messages,
        })

    is_internal = request.POST.get('is_internal') == 'on'

    msg = TicketMessage.objects.create(
        hub_id=hub,
        ticket=ticket,
        message=message_text,
        author_id=_get_staff_id(request),
        author_name=str(_get_staff_name(request)),
        is_internal=is_internal,
    )

    # Track first response (only for non-internal messages)
    if not is_internal:
        ticket.record_first_response()

    # If ticket was waiting on customer, move to in_progress
    if ticket.status == 'waiting_customer' and not is_internal:
        ticket.status = 'in_progress'
        ticket.save(update_fields=['status', 'updated_at'])

    ticket_messages = ticket.messages.filter(is_deleted=False).order_by('created_at')
    return django_render(request, 'support/partials/ticket_messages.html', {
        'ticket': ticket,
        'ticket_messages': ticket_messages,
    })


# ============================================================================
# Ticket Detail
# ============================================================================

@login_required
@with_module_nav('support', 'list')
@htmx_view('support/pages/detail.html', 'support/partials/detail_content.html')
def ticket_detail(request, ticket_id):
    """Ticket detail view with message thread."""
    hub = _hub_id(request)
    ticket = get_object_or_404(
        Ticket.objects.select_related('customer', 'category'),
        id=ticket_id, hub_id=hub, is_deleted=False,
    )
    ticket_messages = ticket.messages.filter(is_deleted=False).order_by('created_at')

    return {
        'ticket': ticket,
        'ticket_messages': ticket_messages,
        'page_title': ticket.ticket_number,
    }


# ============================================================================
# Bulk Actions
# ============================================================================

@login_required
@require_POST
def ticket_bulk_action(request):
    """Bulk assign, close, or delete tickets."""
    hub = _hub_id(request)
    ids_str = request.POST.get('ids', '')
    action = request.POST.get('action', '')

    if not ids_str or not action:
        return _render_ticket_list(request, hub)

    ids = [uid.strip() for uid in ids_str.split(',') if uid.strip()]
    tickets = Ticket.objects.filter(hub_id=hub, id__in=ids, is_deleted=False)
    count = tickets.count()

    if action == 'assign':
        user_id = _get_staff_id(request)
        user_name = str(_get_staff_name(request))
        for ticket in tickets:
            ticket.assign(user_id, user_name)
        messages.success(request, _('%(count)d tickets assigned to %(name)s') % {
            'count': count, 'name': user_name,
        })
    elif action == 'close':
        for ticket in tickets:
            ticket.close()
        messages.success(request, _('%(count)d tickets closed') % {'count': count})
    elif action == 'delete':
        tickets.update(is_deleted=True, deleted_at=timezone.now())
        messages.success(request, _('%(count)d tickets deleted') % {'count': count})

    return _render_ticket_list(request, hub)


# ============================================================================
# Categories
# ============================================================================

@login_required
@with_module_nav('support', 'categories')
@htmx_view('support/pages/categories.html', 'support/partials/categories_content.html')
def categories(request):
    """Ticket categories list with search."""
    hub = _hub_id(request)
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'name')
    sort_dir = request.GET.get('dir', 'asc')

    category_list = (
        TicketCategory.objects.filter(hub_id=hub, is_deleted=False)
        .annotate(
            ticket_count_val=Count(
                'tickets',
                filter=Q(tickets__is_deleted=False),
            )
        )
    )

    if search_query:
        category_list = category_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    order_by = sort_field if sort_field in ('name', 'sort_order') else 'name'
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    category_list = category_list.order_by(order_by)

    context = {
        'categories': category_list,
        'search_query': search_query,
        'sort_field': sort_field,
        'sort_dir': sort_dir,
    }

    # HTMX partial: swap only datatable body
    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'support/partials/categories_list.html', context)

    return context


@login_required
def category_add(request):
    """Add category -- renders in side panel via HTMX."""
    hub = _hub_id(request)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, _('Name is required'))
            return django_render(request, 'support/partials/panel_category_add.html')

        TicketCategory.objects.create(
            hub_id=hub,
            name=name,
            description=request.POST.get('description', '').strip(),
            color=request.POST.get('color', 'primary'),
            icon=request.POST.get('icon', 'help-circle-outline'),
            sort_order=request.POST.get('sort_order', '0') or 0,
        )
        messages.success(request, _('Category added successfully'))
        return _render_category_list(request, hub)

    return django_render(request, 'support/partials/panel_category_add.html')


@login_required
def category_edit(request, category_id):
    """Edit category -- renders in side panel via HTMX."""
    hub = _hub_id(request)
    category = get_object_or_404(TicketCategory, id=category_id, hub_id=hub, is_deleted=False)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, _('Name is required'))
            return django_render(request, 'support/partials/panel_category_edit.html', {
                'category': category,
            })

        category.name = name
        category.description = request.POST.get('description', '').strip()
        category.color = request.POST.get('color', 'primary')
        category.icon = request.POST.get('icon', 'help-circle-outline')
        category.is_active = request.POST.get('is_active') == 'on'
        category.sort_order = request.POST.get('sort_order', '0') or 0
        category.save()
        messages.success(request, _('Category updated successfully'))
        return _render_category_list(request, hub)

    return django_render(request, 'support/partials/panel_category_edit.html', {
        'category': category,
    })


@login_required
@require_POST
def category_delete(request, category_id):
    """Soft delete category."""
    hub = _hub_id(request)
    category = get_object_or_404(TicketCategory, id=category_id, hub_id=hub, is_deleted=False)
    category.is_deleted = True
    category.deleted_at = timezone.now()
    category.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    messages.success(request, _('Category deleted successfully'))
    return _render_category_list(request, hub)


# ============================================================================
# Settings
# ============================================================================

@login_required
@with_module_nav('support', 'settings')
@htmx_view('support/pages/settings.html', 'support/partials/settings_content.html')
def settings_view(request):
    """Support module settings."""
    hub = _hub_id(request)
    settings = SupportSettings.get_settings(hub)

    if request.method == 'POST':
        settings.auto_assign = request.POST.get('auto_assign') == 'on'
        settings.default_priority = request.POST.get('default_priority', 'medium')
        settings.sla_first_response_hours = int(
            request.POST.get('sla_first_response_hours', '24') or 24
        )
        settings.sla_resolution_hours = int(
            request.POST.get('sla_resolution_hours', '72') or 72
        )
        settings.enable_customer_notifications = request.POST.get(
            'enable_customer_notifications'
        ) == 'on'
        settings.close_resolved_after_days = int(
            request.POST.get('close_resolved_after_days', '7') or 7
        )
        settings.save()
        messages.success(request, _('Settings saved successfully'))

    total_tickets = Ticket.objects.filter(hub_id=hub, is_deleted=False).count()
    open_tickets = Ticket.objects.filter(
        hub_id=hub, is_deleted=False,
        status__in=['open', 'in_progress', 'waiting_customer'],
    ).count()
    total_categories = TicketCategory.objects.filter(hub_id=hub, is_deleted=False).count()

    return {
        'settings': settings,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'total_categories': total_categories,
    }
