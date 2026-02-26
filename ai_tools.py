"""AI tools for the Support module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class ListTickets(AssistantTool):
    name = "list_tickets"
    description = "List support tickets with optional filters by status or priority."
    module_id = "support"
    required_permission = "support.view_ticket"
    parameters = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Filter: open, in_progress, waiting_customer, resolved, closed"},
            "priority": {"type": "string", "description": "Filter: low, medium, high, urgent"},
            "search": {"type": "string", "description": "Search by subject or customer name"},
            "limit": {"type": "integer", "description": "Max results (default 20)"},
        },
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from support.models import Ticket
        from django.db.models import Q
        qs = Ticket.objects.select_related('customer', 'category').order_by('-created_at')
        if args.get('status'):
            qs = qs.filter(status=args['status'])
        if args.get('priority'):
            qs = qs.filter(priority=args['priority'])
        if args.get('search'):
            s = args['search']
            qs = qs.filter(Q(subject__icontains=s) | Q(customer__name__icontains=s))
        limit = args.get('limit', 20)
        return {
            "tickets": [
                {
                    "id": str(t.id),
                    "ticket_number": t.ticket_number,
                    "subject": t.subject,
                    "customer": t.customer.name if t.customer else None,
                    "category": t.category.name if t.category else None,
                    "priority": t.priority,
                    "status": t.status,
                    "assigned_to": t.assigned_to_name,
                    "created": str(t.created_at.date()),
                }
                for t in qs[:limit]
            ],
            "total": qs.count(),
        }


@register_tool
class CreateTicket(AssistantTool):
    name = "create_ticket"
    description = "Create a new support ticket."
    module_id = "support"
    required_permission = "support.change_ticket"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "subject": {"type": "string", "description": "Ticket subject"},
            "description": {"type": "string", "description": "Issue description"},
            "customer_id": {"type": "string", "description": "Customer ID"},
            "priority": {"type": "string", "description": "Priority: low, medium, high, urgent"},
            "category_id": {"type": "string", "description": "Category ID"},
        },
        "required": ["subject", "description"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from support.models import Ticket
        t = Ticket.objects.create(
            subject=args['subject'],
            description=args['description'],
            customer_id=args.get('customer_id'),
            priority=args.get('priority', 'medium'),
            category_id=args.get('category_id'),
            status='open',
        )
        return {"id": str(t.id), "ticket_number": t.ticket_number, "created": True}


@register_tool
class GetTicketStats(AssistantTool):
    name = "get_ticket_stats"
    description = "Get support ticket statistics: open count, by priority, by status, average resolution time."
    module_id = "support"
    required_permission = "support.view_ticket"
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from django.db.models import Count, Avg, F
        from support.models import Ticket
        open_tickets = Ticket.objects.exclude(status__in=['resolved', 'closed'])
        by_status = dict(open_tickets.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
        by_priority = dict(open_tickets.values_list('priority').annotate(c=Count('id')).values_list('priority', 'c'))
        return {
            "open_count": open_tickets.count(),
            "by_status": by_status,
            "by_priority": by_priority,
        }
