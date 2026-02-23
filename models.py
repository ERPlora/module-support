from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models.base import HubBaseModel


# ============================================================================
# Ticket Category
# ============================================================================

class TicketCategory(HubBaseModel):
    COLOR_CHOICES = [
        ('primary', _('Blue')),
        ('success', _('Green')),
        ('warning', _('Orange')),
        ('error', _('Red')),
        ('neutral', _('Gray')),
    ]

    ICON_CHOICES = [
        ('help-circle-outline', _('General')),
        ('bug-outline', _('Bug')),
        ('construct-outline', _('Product Issue')),
        ('cut-outline', _('Service Issue')),
        ('card-outline', _('Billing')),
        ('shield-checkmark-outline', _('Warranty')),
        ('alert-circle-outline', _('Complaint')),
        ('bulb-outline', _('Suggestion')),
        ('chatbox-outline', _('Feedback')),
    ]

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default='primary',
        verbose_name=_('Color'),
    )
    icon = models.CharField(
        max_length=50,
        choices=ICON_CHOICES,
        default='help-circle-outline',
        verbose_name=_('Icon'),
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_('Sort Order'))

    class Meta(HubBaseModel.Meta):
        db_table = 'support_ticketcategory'
        ordering = ['sort_order', 'name']
        verbose_name = _('Ticket Category')
        verbose_name_plural = _('Ticket Categories')

    def __str__(self):
        return self.name

    @property
    def ticket_count(self):
        return self.tickets.filter(is_deleted=False).count()

    @property
    def open_ticket_count(self):
        return self.tickets.filter(
            is_deleted=False,
            status__in=['open', 'in_progress', 'waiting_customer'],
        ).count()


# ============================================================================
# Support Settings (singleton per hub)
# ============================================================================

class SupportSettings(HubBaseModel):
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]

    auto_assign = models.BooleanField(
        default=False,
        verbose_name=_('Auto-assign tickets'),
        help_text=_('Automatically assign new tickets to available staff'),
    )
    default_priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('Default Priority'),
    )
    sla_first_response_hours = models.PositiveIntegerField(
        default=24,
        verbose_name=_('SLA First Response (hours)'),
        help_text=_('Maximum hours for first response to a ticket'),
    )
    sla_resolution_hours = models.PositiveIntegerField(
        default=72,
        verbose_name=_('SLA Resolution (hours)'),
        help_text=_('Maximum hours for ticket resolution'),
    )
    enable_customer_notifications = models.BooleanField(
        default=True,
        verbose_name=_('Enable Customer Notifications'),
        help_text=_('Send email notifications to customers on ticket updates'),
    )
    close_resolved_after_days = models.PositiveIntegerField(
        default=7,
        verbose_name=_('Auto-close Resolved After (days)'),
        help_text=_('Automatically close resolved tickets after this many days'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'support_supportsettings'
        verbose_name = _('Support Settings')
        verbose_name_plural = _('Support Settings')

    def __str__(self):
        return 'Support Settings'

    @classmethod
    def get_settings(cls, hub_id):
        """Get or create the singleton settings for a hub."""
        settings, _ = cls.objects.get_or_create(hub_id=hub_id)
        return settings


# ============================================================================
# Ticket
# ============================================================================

class Ticket(HubBaseModel):
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]

    STATUS_CHOICES = [
        ('open', _('Open')),
        ('in_progress', _('In Progress')),
        ('waiting_customer', _('Waiting on Customer')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]

    # Identification
    ticket_number = models.CharField(
        max_length=20,
        verbose_name=_('Ticket Number'),
        help_text=_('Auto-generated ticket reference number'),
    )

    # Content
    subject = models.CharField(max_length=255, verbose_name=_('Subject'))
    description = models.TextField(verbose_name=_('Description'))

    # Relations
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='support_tickets',
        verbose_name=_('Customer'),
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name=_('Category'),
    )

    # Classification
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_('Priority'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name=_('Status'),
    )

    # Assignment
    assigned_to = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Assigned To'),
        help_text=_('UUID of the assigned staff member'),
    )
    assigned_to_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Assigned To Name'),
    )

    # Related objects (optional cross-module references)
    related_sale = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Related Sale'),
    )
    related_product = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Related Product'),
    )

    # SLA tracking timestamps
    first_response_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('First Response At'),
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Resolved At'),
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Closed At'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'support_ticket'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hub_id', 'ticket_number']),
            models.Index(fields=['hub_id', 'status']),
            models.Index(fields=['hub_id', 'priority']),
            models.Index(fields=['hub_id', 'assigned_to']),
        ]
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')

    def __str__(self):
        return f'{self.ticket_number} - {self.subject}'

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self._generate_ticket_number()
        super().save(*args, **kwargs)

    def _generate_ticket_number(self):
        """Generate the next ticket number for this hub (TK-00001 format)."""
        last_ticket = (
            Ticket.all_objects
            .filter(hub_id=self.hub_id)
            .order_by('-ticket_number')
            .values_list('ticket_number', flat=True)
            .first()
        )
        if last_ticket:
            try:
                last_num = int(last_ticket.split('-')[1])
                next_num = last_num + 1
            except (IndexError, ValueError):
                next_num = 1
        else:
            next_num = 1
        return f'TK-{next_num:05d}'

    # --- SLA Properties ---

    @property
    def is_sla_breached_response(self):
        """Check if first response SLA is breached."""
        if self.first_response_at:
            return False
        if self.status == 'closed':
            return False
        try:
            settings = SupportSettings.get_settings(self.hub_id)
            sla_hours = settings.sla_first_response_hours
        except Exception:
            sla_hours = 24
        deadline = self.created_at + timezone.timedelta(hours=sla_hours)
        return timezone.now() > deadline

    @property
    def is_sla_breached_resolution(self):
        """Check if resolution SLA is breached."""
        if self.resolved_at or self.status in ('resolved', 'closed'):
            return False
        try:
            settings = SupportSettings.get_settings(self.hub_id)
            sla_hours = settings.sla_resolution_hours
        except Exception:
            sla_hours = 72
        deadline = self.created_at + timezone.timedelta(hours=sla_hours)
        return timezone.now() > deadline

    @property
    def response_time_hours(self):
        """Hours from creation to first response, or hours elapsed if no response yet."""
        if self.first_response_at:
            delta = self.first_response_at - self.created_at
            return round(delta.total_seconds() / 3600, 1)
        delta = timezone.now() - self.created_at
        return round(delta.total_seconds() / 3600, 1)

    @property
    def resolution_time_hours(self):
        """Hours from creation to resolution, or hours elapsed if not resolved."""
        if self.resolved_at:
            delta = self.resolved_at - self.created_at
            return round(delta.total_seconds() / 3600, 1)
        delta = timezone.now() - self.created_at
        return round(delta.total_seconds() / 3600, 1)

    @property
    def sla_response_deadline(self):
        """SLA deadline for first response."""
        try:
            settings = SupportSettings.get_settings(self.hub_id)
            sla_hours = settings.sla_first_response_hours
        except Exception:
            sla_hours = 24
        return self.created_at + timezone.timedelta(hours=sla_hours)

    @property
    def sla_resolution_deadline(self):
        """SLA deadline for resolution."""
        try:
            settings = SupportSettings.get_settings(self.hub_id)
            sla_hours = settings.sla_resolution_hours
        except Exception:
            sla_hours = 72
        return self.created_at + timezone.timedelta(hours=sla_hours)

    # --- Actions ---

    def assign(self, user_id, user_name=''):
        """Assign ticket to a staff member."""
        self.assigned_to = user_id
        self.assigned_to_name = user_name
        if self.status == 'open':
            self.status = 'in_progress'
        self.save(update_fields=[
            'assigned_to', 'assigned_to_name', 'status', 'updated_at',
        ])

    def resolve(self):
        """Mark ticket as resolved."""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_at', 'updated_at'])

    def close(self):
        """Close the ticket."""
        self.status = 'closed'
        self.closed_at = timezone.now()
        if not self.resolved_at:
            self.resolved_at = timezone.now()
        self.save(update_fields=[
            'status', 'closed_at', 'resolved_at', 'updated_at',
        ])

    def reopen(self):
        """Reopen a resolved or closed ticket."""
        self.status = 'open'
        self.resolved_at = None
        self.closed_at = None
        self.save(update_fields=[
            'status', 'resolved_at', 'closed_at', 'updated_at',
        ])

    def record_first_response(self):
        """Record the first staff response time if not already set."""
        if not self.first_response_at:
            self.first_response_at = timezone.now()
            self.save(update_fields=['first_response_at', 'updated_at'])


# ============================================================================
# Ticket Message
# ============================================================================

class TicketMessage(HubBaseModel):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Ticket'),
    )
    message = models.TextField(verbose_name=_('Message'))
    author_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Author ID'),
    )
    author_name = models.CharField(
        max_length=255,
        verbose_name=_('Author Name'),
    )
    is_internal = models.BooleanField(
        default=False,
        verbose_name=_('Internal Note'),
        help_text=_('Internal notes are only visible to staff'),
    )
    attachments = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_('Attachments'),
        help_text=_('List of attachment file paths or URLs'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'support_ticketmessage'
        ordering = ['created_at']
        verbose_name = _('Ticket Message')
        verbose_name_plural = _('Ticket Messages')

    def __str__(self):
        return f'{self.ticket.ticket_number} - {self.author_name}'
