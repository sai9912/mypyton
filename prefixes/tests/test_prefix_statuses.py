import doctest

from . import TestCase
from services import prefix_service
from ..models import Prefix


from .. import actions


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(actions))
    return tests


class PrefixStatusesTestCase(TestCase):
    fixtures = ['prefixes.prefixstatuses.json']
    url = '/prefixes/'
    user = None

    def setUp(self):
        self.user = self.setUp_createAccount()

    def test_active(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        assert prefix.status_id == Prefix.ACTIVE
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertNotContains(response, 'Suspended prefixes')
        self.assertNotContains(response, 'Transferred prefixes')

    def test_inactive(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        prefix.status_id = Prefix.INACTIVE
        prefix.save()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Suspended prefixes')
        self.assertNotContains(response, 'Transferred prefixes')

    def test_expired(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        prefix.status_id = Prefix.EXPIRED
        prefix.save()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertContains(response, 'Suspended prefixes')
        self.assertNotContains(response, 'Transferred prefixes')

    def test_transferred(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        prefix.status_id = Prefix.TRANSFERRED
        prefix.save()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertNotContains(response, 'Suspended prefixes')
        self.assertContains(response, 'Transferred prefixes')

    def test_split(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        prefix.status_id = Prefix.SPLIT
        prefix.save()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertNotContains(response, 'Suspended prefixes')
        self.assertNotContains(response, 'Transferred prefixes')

    def test_frozen(self):
        prefix = prefix_service.find_item(user=self.user, prefix='53900011')
        prefix.status_id = Prefix.FROZEN
        prefix.save()
        response = self.client.get(self.url)
        assert response.status_code == 200
        self.assertNotContains(response, 'Suspended prefixes')
        self.assertNotContains(response, 'Transferred prefixes')
