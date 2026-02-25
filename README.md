# Support Module

Customer support ticket system with SLA tracking.

## Features

- Create and manage support tickets with auto-generated ticket numbers (TK-00001 format)
- Categorize tickets with customizable categories (color-coded, with icons)
- Assign tickets to staff members with status workflow (open, in progress, waiting on customer, resolved, closed)
- Priority levels: low, medium, high, urgent
- SLA tracking for first response time and resolution time with breach detection
- Threaded ticket messages with support for internal notes (staff-only) and attachments
- Link tickets to customers, sales, and products for cross-module context
- Configurable settings: auto-assign, default priority, SLA thresholds, customer notifications, auto-close resolved tickets
- Dashboard with ticket metrics and SLA compliance overview

## Installation

This module is installed automatically via the ERPlora Marketplace.

**Dependencies**: Requires `customers` module.

## Configuration

Access settings via: **Menu > Support > Settings**

Configurable options include:
- Auto-assign new tickets to available staff
- Default ticket priority
- SLA first response time (hours)
- SLA resolution time (hours)
- Customer email notifications
- Auto-close resolved tickets after N days

## Usage

Access via: **Menu > Support**

### Views

| View | URL | Description |
|------|-----|-------------|
| Dashboard | `/m/support/dashboard/` | Ticket metrics, SLA status, and overview |
| Tickets | `/m/support/list/` | List, create and manage support tickets |
| Categories | `/m/support/categories/` | Manage ticket categories with colors and icons |
| Settings | `/m/support/settings/` | Module configuration |

## Models

| Model | Description |
|-------|-------------|
| `TicketCategory` | Ticket category with name, description, color, icon, active status, and sort order |
| `SupportSettings` | Singleton settings per hub for auto-assign, default priority, SLA thresholds, notifications, and auto-close |
| `Ticket` | Support ticket with auto-generated number, subject, description, customer link, category, priority, status, staff assignment, SLA timestamps, and cross-module references |
| `TicketMessage` | Threaded message on a ticket with author info, internal note flag, and attachments |

## Permissions

| Permission | Description |
|------------|-------------|
| `support.view_ticket` | View tickets |
| `support.add_ticket` | Create new tickets |
| `support.change_ticket` | Edit existing tickets |
| `support.delete_ticket` | Delete tickets |
| `support.close_ticket` | Close tickets |
| `support.assign_ticket` | Assign tickets to staff |
| `support.view_category` | View ticket categories |
| `support.manage_categories` | Manage ticket categories |
| `support.manage_settings` | Manage module settings |

## Integration with Other Modules

- **customers**: Tickets can be linked to a customer record via the `customer` foreign key.

## License

MIT

## Author

ERPlora Team - support@erplora.com
