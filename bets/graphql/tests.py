from bets.factories import BetFactory, EventFactory, QuotaFactory
from bets.graphql.schema import Queries as BetQueries
from django.test.testcases import TestCase
import graphene

class QueryTest(TestCase):
    def setUp(self):
        self.first_event = EventFactory(active=True)
        self.second_event = EventFactory(active=True)
        self.first_quota = QuotaFactory(event=self.first_event, active=True)
        self.second_quota = QuotaFactory(event=self.first_event, active=True)
        self.first_bet = BetFactory(quota=second_quota)
        self.second_bet = BetFactory(quota=second_quota)
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

        self.query = """
            allEvents {
                ...{event_fields}
            }
        """.format(event_fields=self.event_fields)
        schema = graphene.Schema(query=Query)
        result = schema.execute(query)
        self.assertIsNone(result.errors)
