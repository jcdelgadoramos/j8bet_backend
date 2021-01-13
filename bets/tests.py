from bets.graphql.schema import Queries as BetQuery
from bets.factories import BetFactory, EventFactory, QuotaFactory
from bets.models import Bet, Prize, Quota
from django.core.exceptions import ValidationError
from django.test import TestCase
from graphene import Schema


class BetModelsTest(TestCase):
    """
    This class contains tests performed on Models in Bets application.
    """

    def setUp(self):
        self.event = EventFactory(active=True)
        self.first_quota = QuotaFactory(event=self.event, active=True)
        self.second_quota = QuotaFactory(event=self.event, active=True)
        self.first_quota.refresh_from_db()
        self.second_quota.refresh_from_db()
        super().setUp()

    def test_01_on_setup(self):
        """
        This test evaluates basic events from setUp() objects
        """

        # New events should always have 'completed=None'
        self.assertIsNone(self.event.completed)
        self.assertEqual(self.event.__str__(), self.event.name)
        self.assertEqual(
            self.first_quota.__str__(),
            "{event} - {prob}".format(
                event=self.first_quota.event, prob=self.first_quota.probability
            ),
        )

    def test_02_multiple_quotas(self):
        """
        This test evaluates creating Quotas from (in)active Quotas
        """

        # First quota should be inactive
        self.assertFalse(self.first_quota.active)
        self.first_quota.save()

        # Second quota should be active
        self.assertTrue(self.second_quota.active)

        with self.assertRaises(ValidationError):
            # Should fail since first_quota is supposed to be inactive
            BetFactory(quota=self.first_quota)

        bet = BetFactory(quota=self.second_quota)
        # Bet should be created, and must have 'won=None' and 'active=True'
        self.assertIsInstance(bet, Bet)
        self.assertEqual(
            bet.__str__(),
            "{event} - {user} - {amount}".format(
                event=bet.quota.event,
                user=bet.user,
                amount=bet.transaction.__str__(),
            ),
        )
        self.assertIsNone(bet.won)
        self.assertTrue(bet.active)

    def test_03_event_saving_incomplete(self):
        """
        This test evaluates the whole Event saving process
        when the Event is still incomplete.
        """

        event = EventFactory(active=True)
        event.save()
        # Event must be incomplete
        self.assertIsNone(event.completed)

        quota = QuotaFactory(event=event, active=True)
        event.active = False
        event.save()
        quota.refresh_from_db()
        # Quota must be inactive
        self.assertFalse(quota.active)

    def test_04_event_saving_completed(self):
        """
        This test evaluates the whole Event saving process
        when the Event is completed.
        """

        first_quota = Quota.objects.get(id=self.second_quota.id)
        first_bet = BetFactory(quota=first_quota)
        second_quota = QuotaFactory(event=self.event, active=True)
        second_bet = BetFactory(quota=second_quota)
        self.event.completed = True
        self.event.save()
        first_quota.refresh_from_db()
        second_quota.refresh_from_db()
        first_bet.refresh_from_db()
        second_bet.refresh_from_db()
        # Both quotas should be inactive
        self.assertFalse(first_quota.active)
        self.assertFalse(second_quota.active)

        # Both bets should be won
        self.assertTrue(first_bet.won)
        self.assertTrue(second_bet.won)

        # Both bets should be inactive
        self.assertFalse(first_bet.active)
        self.assertFalse(second_bet.active)

        # Two prizes should be created
        self.assertEqual(Prize.objects.count(), 2)

        # Evaluate Prize __str__ representation
        prize = Prize.objects.first()
        self.assertEqual(
            prize.__str__(),
            "{event} - {user} - {amount}".format(
                event=prize.bet.quota.event,
                user=prize.user,
                amount=prize.reward,
            ),
        )

    def test_05_event_saving_not_completed(self):
        """
        This test evaluates the whole Event saving process
        when the Event is not completed.
        """

        first_quota = Quota.objects.get(id=self.second_quota.id)
        first_bet = BetFactory(quota=first_quota)
        second_quota = QuotaFactory(event=self.event, active=True)
        second_bet = BetFactory(quota=second_quota)
        self.event.completed = False
        self.event.save()
        first_quota.refresh_from_db()
        second_quota.refresh_from_db()
        first_bet.refresh_from_db()
        second_bet.refresh_from_db()
        # Both quotas should be inactive
        self.assertFalse(first_quota.active)
        self.assertFalse(second_quota.active)

        # Both bets should be lost
        self.assertFalse(first_bet.won)
        self.assertFalse(second_bet.won)

        # Both bets should be inactive
        self.assertFalse(first_bet.active)
        self.assertFalse(second_bet.active)

        # No prizes should be created
        self.assertEqual(Prize.objects.count(), 0)


class QueryTest(TestCase):
    def setUp(self):
        self.first_event = EventFactory(active=True)
        self.second_event = EventFactory(active=True)
        self.first_quota = QuotaFactory(event=self.first_event, active=True)
        self.second_quota = QuotaFactory(event=self.first_event, active=True)
        self.first_bet = BetFactory(quota=self.second_quota)
        self.second_bet = BetFactory(quota=self.second_quota)
        self.event_fields = """
            id,
            name,
            description,
            rules,
            creationDate,
            modificationDate,
            expirationDate,
            active
        """
        super().setUp()

    def test_01_get_events(self):
        """
        This test evaluates retrieving events.
        """

        query = """
            query getAllEvents {{
                events: allEvents {{
                    {fields}
                }}
            }}
        """.format(fields=self.event_fields)
        schema = Schema(query=BetQuery)
        result = schema.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            str(self.first_event.id), result.data['events'][0]['id'])
        self.assertEqual(
            self.first_event.name, result.data['events'][0]['name'])
        self.assertEqual(
            self.first_event.description,
            result.data['events'][0]['description'])
        self.assertEqual(
            self.first_event.rules, result.data['events'][0]['rules'])
        self.assertEqual(
            self.first_event.active, result.data['events'][0]['active'])
