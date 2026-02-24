"""Tests for support models."""
import pytest
from django.utils import timezone

from support.models import TicketCategory, Ticket


@pytest.mark.django_db
class TestTicketCategory:
    """TicketCategory model tests."""

    def test_create(self, ticket_category):
        """Test TicketCategory creation."""
        assert ticket_category.pk is not None
        assert ticket_category.is_deleted is False

    def test_str(self, ticket_category):
        """Test string representation."""
        assert str(ticket_category) is not None
        assert len(str(ticket_category)) > 0

    def test_soft_delete(self, ticket_category):
        """Test soft delete."""
        pk = ticket_category.pk
        ticket_category.is_deleted = True
        ticket_category.deleted_at = timezone.now()
        ticket_category.save()
        assert not TicketCategory.objects.filter(pk=pk).exists()
        assert TicketCategory.all_objects.filter(pk=pk).exists()

    def test_queryset_excludes_deleted(self, hub_id, ticket_category):
        """Test default queryset excludes deleted."""
        ticket_category.is_deleted = True
        ticket_category.deleted_at = timezone.now()
        ticket_category.save()
        assert TicketCategory.objects.filter(hub_id=hub_id).count() == 0

    def test_toggle_active(self, ticket_category):
        """Test toggling is_active."""
        original = ticket_category.is_active
        ticket_category.is_active = not original
        ticket_category.save()
        ticket_category.refresh_from_db()
        assert ticket_category.is_active != original


@pytest.mark.django_db
class TestTicket:
    """Ticket model tests."""

    def test_create(self, ticket):
        """Test Ticket creation."""
        assert ticket.pk is not None
        assert ticket.is_deleted is False

    def test_str(self, ticket):
        """Test string representation."""
        assert str(ticket) is not None
        assert len(str(ticket)) > 0

    def test_soft_delete(self, ticket):
        """Test soft delete."""
        pk = ticket.pk
        ticket.is_deleted = True
        ticket.deleted_at = timezone.now()
        ticket.save()
        assert not Ticket.objects.filter(pk=pk).exists()
        assert Ticket.all_objects.filter(pk=pk).exists()

    def test_queryset_excludes_deleted(self, hub_id, ticket):
        """Test default queryset excludes deleted."""
        ticket.is_deleted = True
        ticket.deleted_at = timezone.now()
        ticket.save()
        assert Ticket.objects.filter(hub_id=hub_id).count() == 0


