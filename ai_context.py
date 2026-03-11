"""
AI context for the Support module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: Support

### Models

**TicketCategory** — classifies support tickets.
- `name` (str): category label
- `color` (choice): primary, success, warning, error, neutral
- `icon` (choice): icon identifier for the category
- `sort_order` (int): display ordering
- `is_active` (bool)

**SupportSettings** — singleton per hub.
- `auto_assign` (bool): automatically assign new tickets to available staff
- `default_priority` (choice): low, medium, high, urgent (default: medium)
- `sla_first_response_hours` (int, default 24): hours for first response SLA
- `sla_resolution_hours` (int, default 72): hours for resolution SLA
- `enable_customer_notifications` (bool, default True)
- `close_resolved_after_days` (int, default 7): auto-close resolved tickets after N days
- Accessed via: `SupportSettings.get_settings(hub_id)`

**Ticket** — a support issue.
- `ticket_number` (str): auto-generated reference e.g. "TK-00001"
- `subject` (str): issue title
- `description` (text): full problem description
- `customer` (FK → customers.Customer, nullable)
- `category` (FK → TicketCategory, nullable)
- `priority` (choice): low, medium, high, urgent
- `status` (choice): open, in_progress, waiting_customer, resolved, closed
- `assigned_to` (UUID, nullable): staff member UUID
- `assigned_to_name` (str): staff name copy
- `related_sale` (UUID, nullable): links to a sale
- `related_product` (UUID, nullable): links to a product
- `first_response_at`, `resolved_at`, `closed_at` (datetime, nullable): SLA tracking

**TicketMessage** — threaded messages within a ticket.
- `ticket` (FK → Ticket)
- `message` (text): message body
- `author_id` (UUID, nullable): sender's user UUID
- `author_name` (str): sender display name
- `is_internal` (bool, default False): internal notes hidden from customers
- `attachments` (JSON list, nullable): file paths or URLs

### Key flows

1. **Open a ticket**: create Ticket with subject, description, priority. ticket_number is auto-generated.
2. **Assign**: call ticket.assign(user_id, user_name) — sets assigned_to and moves status to in_progress.
3. **Reply**: create TicketMessage. First staff reply triggers ticket.record_first_response().
4. **Resolve**: call ticket.resolve() — sets status="resolved", resolved_at=now.
5. **Close**: call ticket.close() — sets status="closed", closed_at=now.
6. **Reopen**: call ticket.reopen() — resets to status="open", clears resolved/closed timestamps.
7. **SLA check**: use ticket.is_sla_breached_response and ticket.is_sla_breached_resolution properties.

### Relationships
- Ticket.customer → customers.Customer
- Ticket.category → TicketCategory
- TicketMessage.ticket → Ticket
- Ticket.related_sale, related_product → UUID references (no FK)
"""
