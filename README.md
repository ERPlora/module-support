# Support

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `support` |
| **Version** | `1.0.0` |
| **Icon** | `headset-outline` |
| **Dependencies** | `customers` |

## Dependencies

This module requires the following modules to be installed:

- `customers`

## Models

### `TicketCategory`

TicketCategory(id, hub_id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, name, description, color, icon, is_active, sort_order)

| Field | Type | Details |
|-------|------|---------|
| `name` | CharField | max_length=100 |
| `description` | TextField | optional |
| `color` | CharField | max_length=20, choices: primary, success, warning, error, neutral |
| `icon` | CharField | max_length=50, choices: help-circle-outline, bug-outline, construct-outline, cut-outline, card-outline, shield-checkmark-outline, ... |
| `is_active` | BooleanField |  |
| `sort_order` | PositiveIntegerField |  |

**Properties:**

- `ticket_count`
- `open_ticket_count`

### `SupportSettings`

SupportSettings(id, hub_id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, auto_assign, default_priority, sla_first_response_hours, sla_resolution_hours, enable_customer_notifications, close_resolved_after_days)

| Field | Type | Details |
|-------|------|---------|
| `auto_assign` | BooleanField |  |
| `default_priority` | CharField | max_length=10, choices: low, medium, high, urgent |
| `sla_first_response_hours` | PositiveIntegerField |  |
| `sla_resolution_hours` | PositiveIntegerField |  |
| `enable_customer_notifications` | BooleanField |  |
| `close_resolved_after_days` | PositiveIntegerField |  |

**Methods:**

- `get_settings()` — Get or create the singleton settings for a hub.

### `Ticket`

Ticket(id, hub_id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, ticket_number, subject, description, customer, category, priority, status, assigned_to, assigned_to_name, related_sale, related_product, first_response_at, resolved_at, closed_at)

| Field | Type | Details |
|-------|------|---------|
| `ticket_number` | CharField | max_length=20 |
| `subject` | CharField | max_length=255 |
| `description` | TextField |  |
| `customer` | ForeignKey | → `customers.Customer`, on_delete=SET_NULL, optional |
| `category` | ForeignKey | → `support.TicketCategory`, on_delete=SET_NULL, optional |
| `priority` | CharField | max_length=10, choices: low, medium, high, urgent |
| `status` | CharField | max_length=20, choices: open, in_progress, waiting_customer, resolved, closed |
| `assigned_to` | UUIDField | max_length=32, optional |
| `assigned_to_name` | CharField | max_length=255, optional |
| `related_sale` | UUIDField | max_length=32, optional |
| `related_product` | UUIDField | max_length=32, optional |
| `first_response_at` | DateTimeField | optional |
| `resolved_at` | DateTimeField | optional |
| `closed_at` | DateTimeField | optional |

**Methods:**

- `assign()` — Assign ticket to a staff member.
- `resolve()` — Mark ticket as resolved.
- `close()` — Close the ticket.
- `reopen()` — Reopen a resolved or closed ticket.
- `record_first_response()` — Record the first staff response time if not already set.

**Properties:**

- `is_sla_breached_response` — Check if first response SLA is breached.
- `is_sla_breached_resolution` — Check if resolution SLA is breached.
- `response_time_hours` — Hours from creation to first response, or hours elapsed if no response yet.
- `resolution_time_hours` — Hours from creation to resolution, or hours elapsed if not resolved.
- `sla_response_deadline` — SLA deadline for first response.
- `sla_resolution_deadline` — SLA deadline for resolution.

### `TicketMessage`

TicketMessage(id, hub_id, created_at, updated_at, created_by, updated_by, is_deleted, deleted_at, ticket, message, author_id, author_name, is_internal, attachments)

| Field | Type | Details |
|-------|------|---------|
| `ticket` | ForeignKey | → `support.Ticket`, on_delete=CASCADE |
| `message` | TextField |  |
| `author_id` | UUIDField | max_length=32, optional |
| `author_name` | CharField | max_length=255 |
| `is_internal` | BooleanField |  |
| `attachments` | JSONField | optional |

## Cross-Module Relationships

| From | Field | To | on_delete | Nullable |
|------|-------|----|-----------|----------|
| `Ticket` | `customer` | `customers.Customer` | SET_NULL | Yes |
| `Ticket` | `category` | `support.TicketCategory` | SET_NULL | Yes |
| `TicketMessage` | `ticket` | `support.Ticket` | CASCADE | No |

## URL Endpoints

Base path: `/m/support/`

| Path | Name | Method |
|------|------|--------|
| `(root)` | `dashboard` | GET |
| `list/` | `list` | GET |
| `categories/` | `categories` | GET |
| `ticket_categories/` | `ticket_categories_list` | GET |
| `ticket_categories/add/` | `ticket_category_add` | GET/POST |
| `ticket_categories/<uuid:pk>/edit/` | `ticket_category_edit` | GET |
| `ticket_categories/<uuid:pk>/delete/` | `ticket_category_delete` | GET/POST |
| `ticket_categories/<uuid:pk>/toggle/` | `ticket_category_toggle_status` | GET |
| `ticket_categories/bulk/` | `ticket_categories_bulk_action` | GET/POST |
| `tickets/` | `tickets_list` | GET |
| `tickets/add/` | `ticket_add` | GET/POST |
| `tickets/<uuid:pk>/edit/` | `ticket_edit` | GET |
| `tickets/<uuid:pk>/delete/` | `ticket_delete` | GET/POST |
| `tickets/bulk/` | `tickets_bulk_action` | GET/POST |
| `settings/` | `settings` | GET |

## Permissions

| Permission | Description |
|------------|-------------|
| `support.view_ticket` | View Ticket |
| `support.add_ticket` | Add Ticket |
| `support.change_ticket` | Change Ticket |
| `support.delete_ticket` | Delete Ticket |
| `support.close_ticket` | Close Ticket |
| `support.assign_ticket` | Assign Ticket |
| `support.view_category` | View Category |
| `support.manage_categories` | Manage Categories |
| `support.manage_settings` | Manage Settings |

**Role assignments:**

- **admin**: All permissions
- **manager**: `add_ticket`, `assign_ticket`, `change_ticket`, `close_ticket`, `manage_categories`, `view_category`, `view_ticket`
- **employee**: `add_ticket`, `view_category`, `view_ticket`

## Navigation

| View | Icon | ID | Fullpage |
|------|------|----|----------|
| Dashboard | `speedometer-outline` | `dashboard` | No |
| Tickets | `ticket-outline` | `list` | No |
| Categories | `pricetags-outline` | `categories` | No |
| Settings | `settings-outline` | `settings` | No |

## AI Tools

Tools available for the AI assistant:

### `list_tickets`

List support tickets with optional filters by status or priority.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter: open, in_progress, waiting_customer, resolved, closed |
| `priority` | string | No | Filter: low, medium, high, urgent |
| `search` | string | No | Search by subject or customer name |
| `limit` | integer | No | Max results (default 20) |

### `create_ticket`

Create a new support ticket.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject` | string | Yes | Ticket subject |
| `description` | string | Yes | Issue description |
| `customer_id` | string | No | Customer ID |
| `priority` | string | No | Priority: low, medium, high, urgent |
| `category_id` | string | No | Category ID |

### `get_ticket_stats`

Get support ticket statistics: open count, by priority, by status, average resolution time.

## File Structure

```
README.md
__init__.py
admin.py
ai_tools.py
apps.py
forms.py
locale/
  en/
    LC_MESSAGES/
      django.po
  es/
    LC_MESSAGES/
      django.po
migrations/
  0001_initial.py
  __init__.py
models.py
module.py
static/
  support/
    css/
      support.css
    js/
templates/
  support/
    pages/
      categories.html
      category_add.html
      category_edit.html
      dashboard.html
      detail.html
      index.html
      list.html
      settings.html
      ticket_add.html
      ticket_categories.html
      ticket_category_add.html
      ticket_category_edit.html
      ticket_edit.html
      tickets.html
    partials/
      categories_content.html
      categories_list.html
      category_add_content.html
      category_edit_content.html
      dashboard_content.html
      detail_content.html
      panel_category_add.html
      panel_category_edit.html
      panel_ticket_add.html
      panel_ticket_category_add.html
      panel_ticket_category_edit.html
      panel_ticket_edit.html
      settings_content.html
      ticket_add_content.html
      ticket_categories_content.html
      ticket_categories_list.html
      ticket_category_add_content.html
      ticket_category_edit_content.html
      ticket_edit_content.html
      ticket_messages.html
      tickets_content.html
      tickets_list.html
tests/
  __init__.py
  conftest.py
  test_models.py
  test_views.py
urls.py
views.py
```
