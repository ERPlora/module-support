"""Tests for support views."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestDashboard:
    """Dashboard view tests."""

    def test_dashboard_loads(self, auth_client):
        """Test dashboard page loads."""
        url = reverse('support:dashboard')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_dashboard_htmx(self, auth_client):
        """Test dashboard HTMX partial."""
        url = reverse('support:dashboard')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication."""
        url = reverse('support:dashboard')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestTicketCategoryViews:
    """TicketCategory view tests."""

    def test_list_loads(self, auth_client):
        """Test list view loads."""
        url = reverse('support:ticket_categories_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_list_htmx(self, auth_client):
        """Test list HTMX partial."""
        url = reverse('support:ticket_categories_list')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_list_search(self, auth_client):
        """Test list search."""
        url = reverse('support:ticket_categories_list')
        response = auth_client.get(url, {'q': 'test'})
        assert response.status_code == 200

    def test_list_sort(self, auth_client):
        """Test list sorting."""
        url = reverse('support:ticket_categories_list')
        response = auth_client.get(url, {'sort': 'created_at', 'dir': 'desc'})
        assert response.status_code == 200

    def test_export_csv(self, auth_client):
        """Test CSV export."""
        url = reverse('support:ticket_categories_list')
        response = auth_client.get(url, {'export': 'csv'})
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']

    def test_export_excel(self, auth_client):
        """Test Excel export."""
        url = reverse('support:ticket_categories_list')
        response = auth_client.get(url, {'export': 'excel'})
        assert response.status_code == 200

    def test_add_form_loads(self, auth_client):
        """Test add form loads."""
        url = reverse('support:ticket_category_add')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_post(self, auth_client):
        """Test creating via POST."""
        url = reverse('support:ticket_category_add')
        data = {
            'name': 'New Name',
            'description': 'Test description',
            'color': 'New Color',
            'icon': 'New Icon',
            'is_active': 'on',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_edit_form_loads(self, auth_client, ticket_category):
        """Test edit form loads."""
        url = reverse('support:ticket_category_edit', args=[ticket_category.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_edit_post(self, auth_client, ticket_category):
        """Test editing via POST."""
        url = reverse('support:ticket_category_edit', args=[ticket_category.pk])
        data = {
            'name': 'Updated Name',
            'description': 'Test description',
            'color': 'Updated Color',
            'icon': 'Updated Icon',
            'is_active': '',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_delete(self, auth_client, ticket_category):
        """Test soft delete via POST."""
        url = reverse('support:ticket_category_delete', args=[ticket_category.pk])
        response = auth_client.post(url)
        assert response.status_code == 200
        ticket_category.refresh_from_db()
        assert ticket_category.is_deleted is True

    def test_toggle_status(self, auth_client, ticket_category):
        """Test toggle active status."""
        url = reverse('support:ticket_category_toggle_status', args=[ticket_category.pk])
        original = ticket_category.is_active
        response = auth_client.post(url)
        assert response.status_code == 200
        ticket_category.refresh_from_db()
        assert ticket_category.is_active != original

    def test_bulk_delete(self, auth_client, ticket_category):
        """Test bulk delete."""
        url = reverse('support:ticket_categories_bulk_action')
        response = auth_client.post(url, {'ids': str(ticket_category.pk), 'action': 'delete'})
        assert response.status_code == 200
        ticket_category.refresh_from_db()
        assert ticket_category.is_deleted is True

    def test_list_requires_auth(self, client):
        """Test list requires authentication."""
        url = reverse('support:ticket_categories_list')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestTicketViews:
    """Ticket view tests."""

    def test_list_loads(self, auth_client):
        """Test list view loads."""
        url = reverse('support:tickets_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_list_htmx(self, auth_client):
        """Test list HTMX partial."""
        url = reverse('support:tickets_list')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_list_search(self, auth_client):
        """Test list search."""
        url = reverse('support:tickets_list')
        response = auth_client.get(url, {'q': 'test'})
        assert response.status_code == 200

    def test_list_sort(self, auth_client):
        """Test list sorting."""
        url = reverse('support:tickets_list')
        response = auth_client.get(url, {'sort': 'created_at', 'dir': 'desc'})
        assert response.status_code == 200

    def test_export_csv(self, auth_client):
        """Test CSV export."""
        url = reverse('support:tickets_list')
        response = auth_client.get(url, {'export': 'csv'})
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']

    def test_export_excel(self, auth_client):
        """Test Excel export."""
        url = reverse('support:tickets_list')
        response = auth_client.get(url, {'export': 'excel'})
        assert response.status_code == 200

    def test_add_form_loads(self, auth_client):
        """Test add form loads."""
        url = reverse('support:ticket_add')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_post(self, auth_client):
        """Test creating via POST."""
        url = reverse('support:ticket_add')
        data = {
            'ticket_number': 'New Ticket Number',
            'subject': 'New Subject',
            'description': 'Test description',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_edit_form_loads(self, auth_client, ticket):
        """Test edit form loads."""
        url = reverse('support:ticket_edit', args=[ticket.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_edit_post(self, auth_client, ticket):
        """Test editing via POST."""
        url = reverse('support:ticket_edit', args=[ticket.pk])
        data = {
            'ticket_number': 'Updated Ticket Number',
            'subject': 'Updated Subject',
            'description': 'Test description',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_delete(self, auth_client, ticket):
        """Test soft delete via POST."""
        url = reverse('support:ticket_delete', args=[ticket.pk])
        response = auth_client.post(url)
        assert response.status_code == 200
        ticket.refresh_from_db()
        assert ticket.is_deleted is True

    def test_bulk_delete(self, auth_client, ticket):
        """Test bulk delete."""
        url = reverse('support:tickets_bulk_action')
        response = auth_client.post(url, {'ids': str(ticket.pk), 'action': 'delete'})
        assert response.status_code == 200
        ticket.refresh_from_db()
        assert ticket.is_deleted is True

    def test_list_requires_auth(self, client):
        """Test list requires authentication."""
        url = reverse('support:tickets_list')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestSettings:
    """Settings view tests."""

    def test_settings_loads(self, auth_client):
        """Test settings page loads."""
        url = reverse('support:settings')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_settings_requires_auth(self, client):
        """Test settings requires authentication."""
        url = reverse('support:settings')
        response = client.get(url)
        assert response.status_code == 302

