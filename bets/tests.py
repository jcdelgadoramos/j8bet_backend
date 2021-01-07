from django.test import TestCase

from bets.factories import EventFactory
from bets.models import Event

class EventModelTest(TestCase):
    def setUp(self):
        self.event = EventFactory()
        super().setUp()

    def test_event(self):
        created_event = Event.objects.get(name=self.event.name)
        self.assertEqual(self.event.id, created_event.id)