from datetime import datetime
from decimal import Decimal

from bets.factories import (
    AffairFactory,
    BetFactory,
    EventFactory,
    QuotaFactory,
    TagFactory,
)
from bets.graphql.types import (
    AffairType,
    BetType,
    EventType,
    PrizeType,
    QuotaType,
    TagType,
    TransactionType,
)
from bets.models import Affair, Bet, Event, Prize, Quota
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from graphene.relay import Node
from graphql.error.located_error import GraphQLLocatedError
from graphql_jwt.testcases import JSONWebTokenTestCase
from j8bet_backend.constants import BET_CONSUMER, BET_MANAGER
from users.factories import UserFactory


class BetModelsTest(TestCase):
    """
    This class contains tests performed on Models in Bets application.
    """

    def setUp(self):
        self.bet_manager_group = Group.objects.get(name=BET_MANAGER)
        self.bet_manager = UserFactory.create(groups=(self.bet_manager_group,))
        self.event = EventFactory(active=True, manager=self.bet_manager)
        self.first_quota = QuotaFactory(
            event=self.event, active=True, manager=self.bet_manager
        )
        self.second_quota = QuotaFactory(
            event=self.event, active=True, manager=self.bet_manager
        )
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


class QueryTest(JSONWebTokenTestCase):
    def setUp(self):
        self.first_tag = TagFactory()
        self.second_tag = TagFactory()
        self.first_affair = AffairFactory(
            tags=[self.first_tag, self.second_tag]
        )
        self.second_affair = AffairFactory(
            tags=[
                self.first_tag,
            ]
        )
        self.first_event = EventFactory(active=True, affair=self.first_affair)
        self.second_event = EventFactory(active=True, affair=self.first_affair)
        self.first_quota = QuotaFactory(event=self.first_event, active=True)
        self.second_quota = QuotaFactory(event=self.first_event, active=True)
        self.first_bet = BetFactory(
            quota=self.second_quota, coeficient=Decimal(2.5),
        )
        self.second_bet = BetFactory(
            quota=self.second_quota, coeficient=Decimal(2.5),
        )
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
        self.user = UserFactory()
        super().setUp()

    def test_00_hello(self):
        """
        This test evaluates the HelloQuery
        """

        self.client.authenticate(self.user)
        query = """
            query hello {
                hola: hello(name: "tester")
            }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual("Hello tester!", result.data["hola"])

    def test_01_get_all_tags(self):
        """
        This test evaluates retrieving all tags.
        """

        query = """
            query getAllTags {
                tags: allTags {
                    edges {
                        node {
                            id,
                            name,
                            creationDate,
                            modificationDate
                        }
                    }
                }
            }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_tag.id,
            int(
                Node.from_global_id(
                    result.data["tags"]["edges"][0]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.first_tag.name,
            result.data["tags"]["edges"][0]["node"]["name"],
        )
        self.assertEqual(
            self.first_tag.creation_date,
            datetime.strptime(
                result.data["tags"]["edges"][0]["node"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_tag.modification_date,
            datetime.strptime(
                result.data["tags"]["edges"][0]["node"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_tag.id,
            int(
                Node.from_global_id(
                    result.data["tags"]["edges"][1]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.second_tag.name,
            result.data["tags"]["edges"][1]["node"]["name"],
        )
        self.assertEqual(
            self.second_tag.creation_date,
            datetime.strptime(
                result.data["tags"]["edges"][1]["node"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_tag.modification_date,
            datetime.strptime(
                result.data["tags"]["edges"][1]["node"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )

    def test_02_get_tag(self):
        """
        This test evaluates retrieving a single tag.
        """

        query_by_id = """
            query getTagById {{
                tag: tagById(id: "{id}") {{
                    id,
                    name,
                    creationDate,
                    modificationDate
                }}
            }}
        """.format(
            id=Node.to_global_id(TagType.__name__, self.first_tag.id)
        )
        result = self.client.execute(query_by_id)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_tag.id,
            int(Node.from_global_id(result.data["tag"]["id"])[1]),
        )
        self.assertEqual(self.first_tag.name, result.data["tag"]["name"])
        self.assertEqual(
            self.first_tag.creation_date,
            datetime.strptime(
                result.data["tag"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_tag.modification_date,
            datetime.strptime(
                result.data["tag"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        query_by_name = """
            query getTagsByName {{
                tags: allTags (name: \"{name}\") {{
                    edges {{
                        node {{
                            id,
                            name,
                            creationDate,
                            modificationDate
                        }}
                    }}
                }}
            }}
        """.format(
            name=self.second_tag.name
        )
        result = self.client.execute(query_by_name)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.second_tag.id,
            int(
                Node.from_global_id(
                    result.data["tags"]["edges"][0]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.second_tag.name,
            result.data["tags"]["edges"][0]["node"]["name"],
        )
        self.assertEqual(
            self.second_tag.creation_date,
            datetime.strptime(
                result.data["tags"]["edges"][0]["node"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_tag.modification_date,
            datetime.strptime(
                result.data["tags"]["edges"][0]["node"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )

    def test_03_get_all_affairs(self):
        """
        This test evaluates retrieving all affairs.
        """

        query = """
            query getAllAffairs {
                affairs: allAffairs {
                    edges {
                        node {
                            id,
                            description,
                            creationDate,
                            modificationDate,
                            tags {
                                edges{
                                    node{
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertIn(
            int(
                Node.from_global_id(
                    result.data["affairs"]["edges"][0]["node"]["id"]
                )[1]
            ),
            [self.first_affair.id, self.second_affair.id],
        )
        self.assertEqual(
            self.first_affair.description,
            result.data["affairs"]["edges"][0]["node"]["description"],
        )
        self.assertEqual(
            self.first_affair.creation_date,
            datetime.strptime(
                result.data["affairs"]["edges"][0]["node"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_affair.modification_date,
            datetime.strptime(
                result.data["affairs"]["edges"][0]["node"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_tag.name,
            result.data["affairs"]["edges"][0]["node"]["tags"]["edges"][0][
                "node"
            ]["name"],
        )
        self.assertEqual(
            self.second_tag.name,
            result.data["affairs"]["edges"][0]["node"]["tags"]["edges"][1][
                "node"
            ]["name"],
        )
        self.assertEqual(
            self.second_affair.id,
            int(
                Node.from_global_id(
                    result.data["affairs"]["edges"][1]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.second_affair.description,
            result.data["affairs"]["edges"][1]["node"]["description"],
        )
        self.assertEqual(
            self.second_affair.creation_date,
            datetime.strptime(
                result.data["affairs"]["edges"][1]["node"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_affair.modification_date,
            datetime.strptime(
                result.data["affairs"]["edges"][1]["node"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )

    def test_04_get_affair(self):
        """
        This test evaluates retrieving a single affair.
        """

        query = """
            query getAffairById {{
                affair: affairById(id: "{id}") {{
                    id,
                    description,
                    tags {{
                        edges {{
                            node {{
                                id,
                                name,
                                creationDate,
                                modificationDate
                            }}
                        }}
                    }}
                    creationDate,
                    modificationDate
                }}
            }}
        """.format(
            id=Node.to_global_id(AffairType.__name__, self.first_affair.id)
        )
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_affair.id,
            int(Node.from_global_id(result.data["affair"]["id"])[1]),
        )
        self.assertEqual(
            self.first_affair.description, result.data["affair"]["description"]
        )
        self.assertEqual(
            self.first_affair.creation_date,
            datetime.strptime(
                result.data["affair"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_affair.modification_date,
            datetime.strptime(
                result.data["affair"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_tag.name,
            result.data["affair"]["tags"]["edges"][0]["node"]["name"],
        )

    def test_05_get_all_events(self):
        """
        This test evaluates retrieving all events.
        """

        query = """
            query getAllEvents {{
                events: allEvents {{
                    edges {{
                        node {{
                            {fields}
                        }}
                    }}
                }}
            }}
        """.format(
            fields=self.event_fields
        )
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_event.id,
            int(
                Node.from_global_id(
                    result.data["events"]["edges"][0]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.first_event.name,
            result.data["events"]["edges"][0]["node"]["name"],
        )
        self.assertEqual(
            self.first_event.description,
            result.data["events"]["edges"][0]["node"]["description"],
        )
        self.assertEqual(
            self.first_event.rules,
            result.data["events"]["edges"][0]["node"]["rules"],
        )
        self.assertEqual(
            self.first_event.creation_date,
            datetime.strptime(
                result.data["events"]["edges"][0]["node"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_event.modification_date,
            datetime.strptime(
                result.data["events"]["edges"][0]["node"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_event.expiration_date,
            datetime.strptime(
                result.data["events"]["edges"][0]["node"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.first_event.active,
            result.data["events"]["edges"][0]["node"]["active"],
        )
        self.assertEqual(
            self.second_event.id,
            int(
                Node.from_global_id(
                    result.data["events"]["edges"][1]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.second_event.name,
            result.data["events"]["edges"][1]["node"]["name"],
        )
        self.assertEqual(
            self.second_event.description,
            result.data["events"]["edges"][1]["node"]["description"],
        )
        self.assertEqual(
            self.second_event.rules,
            result.data["events"]["edges"][1]["node"]["rules"],
        )
        self.assertEqual(
            self.second_event.creation_date,
            datetime.strptime(
                result.data["events"]["edges"][1]["node"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_event.modification_date,
            datetime.strptime(
                result.data["events"]["edges"][1]["node"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_event.expiration_date,
            datetime.strptime(
                result.data["events"]["edges"][1]["node"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.second_event.active,
            result.data["events"]["edges"][1]["node"]["active"],
        )

    def test_06_get_event(self):
        """
        This test evaluates retrieving a single event.
        """

        query = """
            query getEventById {{
                event: eventById(id: "{id}") {{
                    {fields}
                }}
            }}
        """.format(
            id=Node.to_global_id(EventType.__name__, self.first_event.id),
            fields=self.event_fields,
        )
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_event.id,
            int(Node.from_global_id(result.data["event"]["id"])[1]),
        )
        self.assertEqual(self.first_event.name, result.data["event"]["name"])
        self.assertEqual(
            self.first_event.description, result.data["event"]["description"]
        )
        self.assertEqual(self.first_event.rules, result.data["event"]["rules"])
        self.assertEqual(
            self.first_event.creation_date,
            datetime.strptime(
                result.data["event"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_event.modification_date,
            datetime.strptime(
                result.data["event"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_event.expiration_date,
            datetime.strptime(
                result.data["event"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.first_event.active, result.data["event"]["active"]
        )

    def test_07_get_all_quotas(self):
        """
        This test evaluates retrieving all quotas.
        """

        query = """
            query getAllQuotas {{
                quotas: allQuotas {{
                    edges {{
                        node {{
                            id,
                            probability,
                            creationDate,
                            modificationDate,
                            expirationDate,
                            active,
                            event {{
                                {event_fields}
                            }}
                        }}
                    }}
                }}
            }}
        """.format(
            event_fields=self.event_fields
        )
        result = self.client.execute(query)
        self.first_quota.refresh_from_db()
        self.second_quota.refresh_from_db()
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_quota.id,
            int(
                Node.from_global_id(
                    result.data["quotas"]["edges"][0]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            float(self.first_quota.probability),
            result.data["quotas"]["edges"][0]["node"]["probability"],
        )
        self.assertEqual(
            self.first_quota.creation_date,
            datetime.strptime(
                result.data["quotas"]["edges"][0]["node"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_quota.modification_date,
            datetime.strptime(
                result.data["quotas"]["edges"][0]["node"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_quota.expiration_date,
            datetime.strptime(
                result.data["quotas"]["edges"][0]["node"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.first_quota.active,
            result.data["quotas"]["edges"][0]["node"]["active"],
        )
        self.assertEqual(
            self.first_quota.event.id,
            int(
                Node.from_global_id(
                    result.data["quotas"]["edges"][0]["node"]["event"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.second_quota.id,
            int(
                Node.from_global_id(
                    result.data["quotas"]["edges"][1]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            float(self.second_quota.probability),
            result.data["quotas"]["edges"][1]["node"]["probability"],
        )
        self.assertEqual(
            self.second_quota.creation_date,
            datetime.strptime(
                result.data["quotas"]["edges"][1]["node"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_quota.modification_date,
            datetime.strptime(
                result.data["quotas"]["edges"][1]["node"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_quota.expiration_date,
            datetime.strptime(
                result.data["quotas"]["edges"][1]["node"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.second_quota.active,
            result.data["quotas"]["edges"][1]["node"]["active"],
        )
        self.assertEqual(
            self.second_quota.event.id,
            int(
                Node.from_global_id(
                    result.data["quotas"]["edges"][1]["node"]["event"]["id"]
                )[1]
            ),
        )

    def test_08_get_quota(self):
        """
        This test evaluates retrieving a single quota.
        """

        query = """
            query getQuotaById {{
                quota: quotaById(id: "{id}") {{
                    id,
                    probability,
                    creationDate,
                    modificationDate,
                    expirationDate,
                    active,
                    event {{
                        {event_fields}
                    }}
                }}
            }}
        """.format(
            id=Node.to_global_id(QuotaType.__name__, self.first_quota.id),
            event_fields=self.event_fields,
        )
        result = self.client.execute(query)
        self.first_quota.refresh_from_db()
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_quota.id,
            int(Node.from_global_id(result.data["quota"]["id"])[1]),
        )
        self.assertEqual(
            float(self.first_quota.probability),
            result.data["quota"]["probability"],
        )
        self.assertEqual(
            self.first_quota.creation_date,
            datetime.strptime(
                result.data["quota"]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_quota.modification_date,
            datetime.strptime(
                result.data["quota"]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_quota.expiration_date,
            datetime.strptime(
                result.data["quota"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.first_quota.active, result.data["quota"]["active"]
        )
        self.assertEqual(
            self.first_quota.event.id,
            int(Node.from_global_id(result.data["quota"]["event"]["id"])[1]),
        )

    def test_09_get_all_bets(self):
        """
        This test evaluates retrieving all bets.
        """

        self.client.authenticate(self.user)
        query = """
            query getAllBets {{
                bets: allBets {{
                    edges {{
                        node {{
                            id,
                            transaction {{
                                id,
                                amount,
                                description,
                            }},
                            quota {{
                                id,
                                probability,
                                active
                                event {{
                                    {event_fields}
                                }}
                            }},
                            potentialEarnings,
                            won,
                            active,
                        }}
                    }}
                }}
            }}
        """.format(
            event_fields=self.event_fields
        )
        result = self.client.execute(query)
        self.first_bet.refresh_from_db()
        self.second_bet.refresh_from_db()
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_bet.id,
            int(
                Node.from_global_id(
                    result.data["bets"]["edges"][0]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            float(self.first_bet.potential_earnings),
            result.data["bets"]["edges"][0]["node"]["potentialEarnings"],
        )
        self.assertEqual(
            self.first_bet.active,
            result.data["bets"]["edges"][0]["node"]["active"],
        )
        self.assertEqual(
            self.first_bet.won, result.data["bets"]["edges"][0]["node"]["won"]
        )
        self.assertEqual(
            self.first_bet.quota.id,
            int(
                Node.from_global_id(
                    result.data["bets"]["edges"][0]["node"]["quota"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.second_bet.id,
            int(
                Node.from_global_id(
                    result.data["bets"]["edges"][1]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            float(self.second_bet.potential_earnings),
            result.data["bets"]["edges"][1]["node"]["potentialEarnings"],
        )
        self.assertEqual(
            self.second_bet.active,
            result.data["bets"]["edges"][1]["node"]["active"],
        )
        self.assertEqual(
            self.second_bet.won, result.data["bets"]["edges"][1]["node"]["won"]
        )
        self.assertEqual(
            self.second_bet.quota.id,
            int(
                Node.from_global_id(
                    result.data["bets"]["edges"][1]["node"]["quota"]["id"]
                )[1]
            ),
        )

    def test_10_get_bet(self):
        """
        This test evaluates retrieving a single quota.
        """

        self.client.authenticate(self.user)
        query = """
            query getBetById {{
                bet: betById(id: "{id}") {{
                    id,
                    transaction {{
                        id,
                        amount,
                        description,
                    }},
                    quota {{
                        id,
                        probability,
                        active
                        event {{
                            {event_fields}
                        }}
                    }},
                    potentialEarnings,
                    won,
                    active,
                }}
            }}
        """.format(
            id=Node.to_global_id(BetType.__name__, self.first_bet.id),
            event_fields=self.event_fields,
        )
        result = self.client.execute(query)
        self.first_bet.refresh_from_db()
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_bet.id,
            int(Node.from_global_id(result.data["bet"]["id"])[1]),
        )
        self.assertEqual(
            float(self.first_bet.potential_earnings),
            result.data["bet"]["potentialEarnings"],
        )
        self.assertEqual(self.first_bet.active, result.data["bet"]["active"])
        self.assertEqual(self.first_bet.won, result.data["bet"]["won"])
        self.assertEqual(
            self.first_bet.quota.id,
            int(Node.from_global_id(result.data["bet"]["quota"]["id"])[1]),
        )

    def test_11_get_all_transactions(self):
        """
        This test evaluates retrieving all transactions.
        """

        self.client.authenticate(self.user)
        query = """
            query getAllTransactions {
                transactions: allTransactions {
                    edges {
                        node {
                            id,
                            amount,
                            description,
                        }
                    }
                }
            }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_bet.transaction.id,
            int(
                Node.from_global_id(
                    result.data["transactions"]["edges"][0]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            float(self.first_bet.transaction.amount),
            result.data["transactions"]["edges"][0]["node"]["amount"],
        )
        self.assertEqual(
            self.first_bet.transaction.description,
            result.data["transactions"]["edges"][0]["node"]["description"],
        )
        self.assertEqual(
            self.second_bet.transaction.id,
            int(
                Node.from_global_id(
                    result.data["transactions"]["edges"][1]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            float(self.second_bet.transaction.amount),
            result.data["transactions"]["edges"][1]["node"]["amount"],
        )
        self.assertEqual(
            self.second_bet.transaction.description,
            result.data["transactions"]["edges"][1]["node"]["description"],
        )

    def test_12_get_transaction(self):
        """
        This test evaluates retrieving a single transaction.
        """

        self.client.authenticate(self.user)
        query = """
            query getTransaction {{
                transaction: transactionById(id: "{id}") {{
                    id,
                    amount,
                    description,
                }}
            }}
        """.format(
            id=Node.to_global_id(
                TransactionType.__name__, self.first_bet.transaction.id
            )
        )
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_bet.transaction.id,
            int(Node.from_global_id(result.data["transaction"]["id"])[1]),
        )
        self.assertEqual(
            float(self.first_bet.transaction.amount),
            result.data["transaction"]["amount"],
        )
        self.assertEqual(
            self.first_bet.transaction.description,
            result.data["transaction"]["description"],
        )

    def test_13_get_all_prizes(self):
        """
        This test evaluates retrieving all prizes.
        """

        self.client.authenticate(self.user)
        self.first_event.completed = True
        self.first_event.save()
        self.first_prize = Prize.objects.first()
        self.second_prize = Prize.objects.exclude(
            id=self.first_prize.id
        ).first()
        query = """
            query getAllPrizes {
                prizes: allPrizes {
                    edges {
                        node {
                            id,
                            bet{
                                id
                            }
                            reward,
                        }
                    }
                }
            }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_prize.id,
            int(
                Node.from_global_id(
                    result.data["prizes"]["edges"][0]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            float(self.first_prize.reward),
            result.data["prizes"]["edges"][0]["node"]["reward"],
        )
        self.assertEqual(
            self.first_prize.bet.id,
            int(
                Node.from_global_id(
                    result.data["prizes"]["edges"][0]["node"]["bet"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.second_prize.id,
            int(
                Node.from_global_id(
                    result.data["prizes"]["edges"][1]["node"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            float(self.second_prize.reward),
            result.data["prizes"]["edges"][1]["node"]["reward"],
        )
        self.assertEqual(
            self.second_prize.bet.id,
            int(
                Node.from_global_id(
                    result.data["prizes"]["edges"][1]["node"]["bet"]["id"]
                )[1]
            ),
        )

    def test_14_get_prize(self):
        """
        This test evaluates retrieving a single prize.
        """

        self.client.authenticate(self.user)
        self.first_event.completed = True
        self.first_event.save()
        self.first_prize = Prize.objects.first()
        query = """
            query getPrize {{
                prize: prizeById(id: "{id}") {{
                    id,
                    bet{{
                        id
                    }}
                    reward,
                }}
            }}
        """.format(
            id=Node.to_global_id(PrizeType.__name__, self.first_prize.id)
        )
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_prize.id,
            int(Node.from_global_id(result.data["prize"]["id"])[1]),
        )
        self.assertEqual(
            float(self.first_prize.reward), result.data["prize"]["reward"]
        )
        self.assertEqual(
            self.first_prize.bet.id,
            int(Node.from_global_id(result.data["prize"]["bet"]["id"])[1]),
        )


class MutationAsManagerTest(JSONWebTokenTestCase):
    def setUp(self):
        self.bet_manager_group = Group.objects.get(name=BET_MANAGER)
        self.user = UserFactory.create(groups=(self.bet_manager_group,))
        self.manager = UserFactory.create(groups=(self.bet_manager_group,))
        self.first_tag = TagFactory.create()
        self.second_tag = TagFactory.create()
        self.affair = AffairFactory.create(
            manager=self.user,
            tags=(
                self.first_tag,
                self.second_tag,
            ),
        )
        self.another_affair = AffairFactory.create()
        self.event = EventFactory(
            active=True, manager=self.user, affair=self.affair
        )
        self.quota = QuotaFactory(
            event=self.event, active=True, manager=self.user
        )
        self.event_fields = """
            id,
            affair{
                id,
                description
            }
            name,
            description,
            rules,
            creationDate,
            modificationDate,
            expirationDate,
            active
        """
        self.request_factory = RequestFactory()
        self.context_value = self.request_factory.get(reverse("graphql"))
        self.client.authenticate(self.user)
        super().setUp()

    def test_01_create_affair(self):
        """
        This test evaluates creating an Affair via mutation.
        """

        mutation = """
            mutation createAffair($affairInput: AffairCreationInput!) {
                createAffair(affairInput: $affairInput) {
                    affair{
                        description,
                        tags {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        """
        description = "Description for the upcoming affair"
        first_tag = "Some tag"
        second_tag = "Another tag"
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                affairInput=dict(
                    description=description, tags=[first_tag, second_tag]
                )
            ),
        )
        self.assertEqual(
            description, executed.data["createAffair"]["affair"]["description"]
        )
        self.assertEqual(
            first_tag,
            executed.data["createAffair"]["affair"]["tags"]["edges"][0]["node"][
                "name"
            ],
        )
        self.assertEqual(
            second_tag,
            executed.data["createAffair"]["affair"]["tags"]["edges"][1]["node"][
                "name"
            ],
        )
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                affairInput=dict(
                    description=description,
                    tags=[self.first_tag.id, self.second_tag.id],
                )
            ),
        )
        self.assertEqual(
            description, executed.data["createAffair"]["affair"]["description"]
        )
        self.assertEqual(
            self.first_tag.name,
            executed.data["createAffair"]["affair"]["tags"]["edges"][0]["node"][
                "name"
            ],
        )
        self.assertEqual(
            self.second_tag.name,
            executed.data["createAffair"]["affair"]["tags"]["edges"][1]["node"][
                "name"
            ],
        )
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                affairInput=dict(
                    description=description,
                    tags=[
                        900,
                    ],
                )
            ),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(executed.errors[0]),
        )
        self.assertIsNone(executed.data["createAffair"])

    def test_02_update_affair(self):
        """
        This test evaluates updating an Affair via mutation.
        """

        mutation = """
            mutation updateAffair($affairInput: AffairUpdateInput!) {
                updateAffair(affairInput: $affairInput) {
                    affair{
                        id,
                        description,
                        tags {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                    }
                }
            }
        """
        description = "Description for the upcoming affair"
        first_tag = "Some tag"
        second_tag = "Another tag"
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                affairInput=dict(
                    id=self.affair.id,
                    description=description,
                    tags=[first_tag, second_tag],
                )
            ),
        )
        self.assertEqual(
            self.affair.id,
            int(
                Node.from_global_id(
                    executed.data["updateAffair"]["affair"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            description, executed.data["updateAffair"]["affair"]["description"]
        )
        self.assertEqual(
            first_tag,
            executed.data["updateAffair"]["affair"]["tags"]["edges"][0]["node"][
                "name"
            ],
        )
        self.assertEqual(
            second_tag,
            executed.data["updateAffair"]["affair"]["tags"]["edges"][1]["node"][
                "name"
            ],
        )
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                affairInput=dict(
                    id=self.affair.id,
                    description=description,
                    tags=[self.first_tag.id, self.second_tag.id],
                )
            ),
        )
        self.assertEqual(
            self.affair.id,
            int(
                Node.from_global_id(
                    executed.data["updateAffair"]["affair"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            description, executed.data["updateAffair"]["affair"]["description"]
        )
        self.assertEqual(
            self.first_tag.name,
            executed.data["updateAffair"]["affair"]["tags"]["edges"][0]["node"][
                "name"
            ],
        )
        self.assertEqual(
            self.second_tag.name,
            executed.data["updateAffair"]["affair"]["tags"]["edges"][1]["node"][
                "name"
            ],
        )
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(affairInput=dict(id=self.affair.id, tags=[])),
        )
        self.assertEqual(
            self.affair.id,
            int(
                Node.from_global_id(
                    executed.data["updateAffair"]["affair"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            0, len(executed.data["updateAffair"]["affair"]["tags"]["edges"])
        )
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                affairInput=dict(
                    id=self.affair.id,
                    description=description,
                    tags=[
                        900,
                    ],
                )
            ),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(executed.errors[0]),
        )
        self.assertIsNone(executed.data["updateAffair"])
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                affairInput=dict(
                    id=self.another_affair.id,
                )
            ),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(executed.errors[0]),
        )
        self.assertIsNone(executed.data["updateAffair"])

    def test_03_create_event(self):
        """
        This test evaluates creating an Event via mutation.
        """

        mutation = """
            mutation createEvent($eventInput: EventCreationInput!) {{
                createEvent(eventInput: $eventInput) {{
                    event{{
                        {fields}
                    }}
                }}
            }}
        """.format(
            fields=self.event_fields
        )
        event_name = "Upcoming event"
        description = "Description for the upcoming event"
        expiration_date = timezone.now()
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                eventInput=dict(
                    affair=self.affair.id,
                    name=event_name,
                    description=description,
                    expirationDate=expiration_date,
                )
            ),
        )
        self.assertEqual(
            event_name, executed.data["createEvent"]["event"]["name"]
        )
        self.assertEqual(
            description, executed.data["createEvent"]["event"]["description"]
        )
        self.assertEqual(
            expiration_date,
            datetime.strptime(
                executed.data["createEvent"]["event"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )

    def test_04_update_event(self):
        """
        This test evaluates updating an Event via mutation.
        """

        mutation = """
            mutation updateEvent($eventInput: EventUpdateInput!) {{
                updateEvent(eventInput: $eventInput) {{
                    event{{
                        {fields}
                    }}
                }}
            }}
        """.format(
            fields=self.event_fields
        )
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(eventInput=dict(id=self.event.id)),
        )
        self.assertEqual(
            self.event.id,
            int(
                Node.from_global_id(
                    executed.data["updateEvent"]["event"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            self.event.name,
            executed.data["updateEvent"]["event"]["name"],
        )
        self.assertEqual(
            self.event.description,
            executed.data["updateEvent"]["event"]["description"],
        )
        self.assertEqual(
            self.event.rules,
            executed.data["updateEvent"]["event"]["rules"],
        )
        self.assertEqual(
            self.event.expiration_date,
            datetime.strptime(
                executed.data["updateEvent"]["event"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        event_name = "Upcoming event"
        description = "Description for the upcoming event"
        expiration_date = timezone.now()
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                eventInput=dict(
                    id=self.event.id,
                    name=event_name,
                    description=description,
                    expirationDate=expiration_date,
                    active=True,
                )
            ),
        )
        self.assertEqual(
            event_name, executed.data["updateEvent"]["event"]["name"]
        )
        self.assertEqual(
            description, executed.data["updateEvent"]["event"]["description"]
        )
        self.assertTrue(executed.data["updateEvent"]["event"]["active"])

        # Authenticate with a different manager and test that changes are not
        # allowed
        self.client.authenticate(self.manager)
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                eventInput=dict(
                    id=self.event.id,
                    name=event_name,
                    description=description,
                    expirationDate=expiration_date,
                    active=True,
                )
            ),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(executed.errors[0]),
        )
        self.assertIsNone(executed.data["updateEvent"])

    def test_05_create_quota(self):
        """
        This test evaluates creating a Quota via mutation.
        """

        mutation = """
            mutation createQuota($quotaInput: QuotaCreationInput!) {{
                createQuota(quotaInput: $quotaInput) {{
                    quota{{
                        id,
                        probability,
                        active,
                        expirationDate,
                        event{{
                            {fields}
                        }}
                    }}
                }}
            }}
        """.format(
            fields=self.event_fields
        )
        probability = 0.25
        expiration_date = timezone.now()
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                quotaInput=dict(
                    probability=probability,
                    active=True,
                    expirationDate=expiration_date,
                    event=self.event.id,
                )
            ),
        )
        self.assertEqual(
            probability, executed.data["createQuota"]["quota"]["probability"]
        )
        self.assertTrue(executed.data["createQuota"]["quota"]["active"])
        self.assertEqual(
            expiration_date,
            datetime.strptime(
                executed.data["createQuota"]["quota"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.event.id,
            int(
                Node.from_global_id(
                    executed.data["createQuota"]["quota"]["event"]["id"]
                )[1]
            ),
        )

    def test_06_update_quota(self):
        """
        This test evaluates updating a Quota via mutation.
        """

        mutation = """
            mutation updateQuota($quotaInput: QuotaUpdateInput!) {{
                updateQuota(quotaInput: $quotaInput) {{
                    quota{{
                        id,
                        probability,
                        active,
                        expirationDate,
                        event{{
                            {fields}
                        }}
                    }}
                }}
            }}
        """.format(
            fields=self.event_fields
        )
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(quotaInput=dict(id=self.quota.id)),
        )
        self.assertEqual(
            self.quota.id,
            int(
                Node.from_global_id(
                    executed.data["updateQuota"]["quota"]["id"]
                )[1]
            ),
        )
        self.assertEqual(
            float(self.quota.probability),
            executed.data["updateQuota"]["quota"]["probability"],
        )
        self.assertEqual(
            self.quota.active,
            executed.data["updateQuota"]["quota"]["active"],
        )
        self.assertEqual(
            self.quota.expiration_date,
            datetime.strptime(
                executed.data["updateQuota"]["quota"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.quota.event.id,
            int(
                Node.from_global_id(
                    executed.data["updateQuota"]["quota"]["event"]["id"]
                )[1]
            ),
        )
        expiration_date = timezone.now()
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                quotaInput=dict(
                    id=self.quota.id,
                    expirationDate=expiration_date,
                    active=False,
                )
            ),
        )
        self.assertEqual(
            expiration_date,
            datetime.strptime(
                executed.data["updateQuota"]["quota"]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertFalse(executed.data["updateQuota"]["quota"]["active"])

        # Authenticate with a different manager and test that changes are not
        # allowed
        self.client.authenticate(self.manager)
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                quotaInput=dict(
                    id=self.quota.id,
                    expirationDate=expiration_date,
                    active=False,
                )
            ),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(executed.errors[0]),
        )
        self.assertIsNone(executed.data["updateQuota"])

    def test_07_delete_affair(self):
        """
        This test evaluates deleting an Affair via mutation.
        """

        mutation = """
            mutation deleteAffair($id: ID!) {
                deleteAffair(id: $id) {
                    deleted
                }
            }
        """
        before_deletion_count = Affair.objects.count()
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(id=self.affair.id),
        )
        self.assertTrue(executed.data["deleteAffair"]["deleted"])
        self.assertEqual(Affair.objects.count(), before_deletion_count - 1)

        # Authenticate with a different manager and test that deletions are not
        # allowed
        self.client.authenticate(self.manager)
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(id=self.affair.id),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(executed.errors[0]),
        )
        self.assertIsNone(executed.data["deleteAffair"])

    def test_08_delete_quota(self):
        """
        This test evaluates deleting a Quota via mutation.
        """

        mutation = """
            mutation deleteQuota($id: ID!) {
                deleteQuota(id: $id) {
                    deleted
                }
            }
        """
        before_deletion_count = Quota.objects.count()
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(id=self.quota.id),
        )
        self.assertTrue(executed.data["deleteQuota"]["deleted"])
        self.assertEqual(Quota.objects.count(), before_deletion_count - 1)

        # Authenticate with a different manager and test that deletions are not
        # allowed
        self.client.authenticate(self.manager)
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(id=self.quota.id),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(executed.errors[0]),
        )
        self.assertIsNone(executed.data["deleteQuota"])

    def test_09_delete_event(self):
        """
        This test evaluates deleting an Event via mutation.
        """

        mutation = """
            mutation deleteEvent($id: ID!) {
                deleteEvent(id: $id) {
                    deleted
                }
            }
        """
        before_deletion_count = Event.objects.count()
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(id=self.event.id),
        )
        self.assertTrue(executed.data["deleteEvent"]["deleted"])
        self.assertEqual(Event.objects.count(), before_deletion_count - 1)

        # Authenticate with a different manager and test that deletions are not
        # allowed
        self.client.authenticate(self.manager)
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(id=self.event.id),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(executed.errors[0]),
        )
        self.assertIsNone(executed.data["deleteEvent"])

    def test_10_place_bet_from_quota(self):
        """
        This test evaluates placing a bet as a Bet Manager.
        The bet should not be created.
        """

        mutation = """
            mutation placeBet($quotaId: ID!, $amount: Decimal!) {
                placeBetByQuota(quotaId: $quotaId, amount: $amount) {
                    bet{
                        id
                    }
                }
            }
        """
        result = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(quotaId=self.quota.id, amount=40),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(result.errors[0]),
        )
        self.assertIsNone(result.data["placeBetByQuota"])

    def test_11_place_bet_from_event(self):
        """
        This test evalutates placing a bet as a Bet Manager.
        The bet should not be created.
        """

        mutation = """
            mutation placeBet($eventId: ID!, $amount: Decimal!) {
                placeBetByEvent(eventId: $eventId, amount: $amount) {
                    bet{
                        id
                    }
                }
            }
        """
        result = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(eventId=self.event.id, amount=40),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(result.errors[0]),
        )
        self.assertIsNone(result.data["placeBetByEvent"])


class MutationAsConsumerTest(JSONWebTokenTestCase):
    def setUp(self):
        self.affair = AffairFactory()
        self.event = EventFactory(active=True, affair=self.affair)
        self.quota = QuotaFactory(event=self.event, active=True)
        self.event_fields = """
            id,
            affair{
                id,
                description
            }
            name,
            description,
            rules,
            creationDate,
            modificationDate,
            expirationDate,
            active
        """
        self.request_factory = RequestFactory()
        self.context_value = self.request_factory.get(reverse("graphql"))
        self.bet_consumer_group = Group.objects.get(name=BET_CONSUMER)
        self.user = UserFactory.create(groups=(self.bet_consumer_group,))
        self.client.authenticate(self.user)
        super().setUp()

    def test_01_execute_mutation(self):
        """
        This test tries creating an Event via mutation and should not do it.
        """

        mutation = """
            mutation createEvent($eventInput: EventCreationInput!) {{
                createEvent(eventInput: $eventInput) {{
                    event{{
                        {fields}
                    }}
                }}
            }}
        """.format(
            fields=self.event_fields
        )
        event_name = "Upcoming event"
        description = "Description for the upcoming event"
        expiration_date = timezone.now()
        executed = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                eventInput=dict(
                    affair=self.affair.id,
                    name=event_name,
                    description=description,
                    expirationDate=expiration_date,
                )
            ),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(executed.errors[0]),
        )
        self.assertIsNone(executed.data["createEvent"])


class NotLoggedInTest(JSONWebTokenTestCase):
    def setUp(self):
        self.affair = AffairFactory()
        self.event = EventFactory(affair=self.affair)
        self.quota = QuotaFactory(event=self.event, active=True)
        self.bet = BetFactory(quota=self.quota)
        self.request_factory = RequestFactory()
        self.context_value = self.request_factory.get(reverse("graphql"))

    def test_01_query(self):
        """
        This test evaluates the getAllEvents query without logging in.
        """

        query = """
            query getAllBets {
                bets: allBets {
                    edges{
                        node{
                            id,
                            potentialEarnings
                        }
                    }
                }
            }
        """
        result = self.client.execute(query)
        self.assertEqual(
            GraphQLLocatedError,
            type(result.errors[0]),
        )
        self.assertIsNone(result.data["bets"]["edges"][0]["node"])

    def test_02_mutation(self):
        """
        This test evaluates the createEvent query without logging in.
        """

        mutation = """
            mutation createEvent($eventInput: EventCreationInput!) {
                createEvent(eventInput: $eventInput) {
                    event{
                        id,
                        description
                    }
                }
            }
        """
        result = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(
                eventInput=dict(
                    name="Some name",
                    affair=self.affair.id,
                    description="Some description",
                    expirationDate=datetime.now(),
                )
            ),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(result.errors[0]),
        )
        self.assertIsNone(result.data["createEvent"])


class BetPlacement(JSONWebTokenTestCase):
    def setUp(self):
        self.affair = AffairFactory()
        self.disabled_event = EventFactory(active=False, affair=self.affair)
        self.enabled_event = EventFactory(active=True, affair=self.affair)
        self.disabled_quota = QuotaFactory(
            event=self.enabled_event,
            active=True,
        )
        self.enabled_quota = QuotaFactory(event=self.enabled_event, active=True)
        self.bet_fields = """
            id,
            quota{
                id,
                event{
                    id,
                    affair{
                        id,
                        description
                    }
                    description
                },
                probability,
                coeficient,
                active,
            }
            potentialEarnings,
            active,
            won,
        """
        self.request_factory = RequestFactory()
        self.context_value = self.request_factory.get(reverse("graphql"))
        self.bet_consumer_group = Group.objects.get(name=BET_CONSUMER)
        self.user = UserFactory.create(groups=(self.bet_consumer_group,))
        self.client.authenticate(self.user)
        super().setUp()

    def test_01_place_bet_enabled_quota(self):
        """
        This test evaluates placing a bet from an enabled Quota.
        The bet should be successfully created
        """

        mutation = """
            mutation placeBet($quotaId: ID!, $amount: Decimal!) {{
                placeBetByQuota(quotaId: $quotaId, amount: $amount) {{
                    bet{{
                        {fields}
                    }}
                }}
            }}
        """.format(
            fields=self.bet_fields
        )
        result = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(quotaId=self.enabled_quota.id, amount=40),
        )
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.enabled_quota.id,
            int(
                Node.from_global_id(
                    result.data["placeBetByQuota"]["bet"]["quota"]["id"]
                )[1]
            ),
        )

    def test_02_place_bet_disabled_quota(self):
        """
        This test evaluates placing a bet from a disabled Quota.
        The bet should not be created.
        """

        mutation = """
            mutation placeBet($quotaId: ID!, $amount: Decimal!) {{
                placeBetByQuota(quotaId: $quotaId, amount: $amount) {{
                    bet{{
                        {fields}
                    }}
                }}
            }}
        """.format(
            fields=self.bet_fields
        )
        result = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(quotaId=self.disabled_quota.id, amount=40),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(result.errors[0]),
        )
        self.assertIsNone(result.data["placeBetByQuota"])

    def test_03_place_bet_enabled_event(self):
        mutation = """
            mutation placeBet($eventId: ID!, $amount: Decimal!) {{
                placeBetByEvent(eventId: $eventId, amount: $amount) {{
                    bet{{
                        {fields}
                    }}
                }}
            }}
        """.format(
            fields=self.bet_fields
        )
        result = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(eventId=self.enabled_event.id, amount=40),
        )
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.enabled_event.id,
            int(
                Node.from_global_id(
                    result.data["placeBetByEvent"]["bet"]["quota"]["event"][
                        "id"
                    ]
                )[1]
            ),
        )
        self.assertEqual(
            self.enabled_quota.id,
            int(
                Node.from_global_id(
                    result.data["placeBetByEvent"]["bet"]["quota"]["id"]
                )[1]
            ),
        )

    def test_04_place_bet_disabled_event(self):
        """
        This test evaluates placing a bet from a disabled Event.
        The bet should not be created.
        """

        mutation = """
            mutation placeBet($eventId: ID!, $amount: Decimal!) {{
                placeBetByEvent(eventId: $eventId, amount: $amount) {{
                    bet{{
                        {fields}
                    }}
                }}
            }}
        """.format(
            fields=self.bet_fields
        )
        result = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(eventId=self.disabled_event.id, amount=40),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(result.errors[0]),
        )
        self.assertIsNone(result.data["placeBetByEvent"])

    def test_05_place_bet_enabled_event_with_disabled_quotas(self):
        """
        This test evaluates placing a bet from an enabled Event
        with no disabled Quotas. The bet should not be created.
        """

        self.enabled_quota.active = False
        self.enabled_quota.save()
        mutation = """
            mutation placeBet($eventId: ID!, $amount: Decimal!) {{
                placeBetByEvent(eventId: $eventId, amount: $amount) {{
                    bet{{
                        {fields}
                    }}
                }}
            }}
        """.format(
            fields=self.bet_fields
        )
        result = self.client.execute(
            mutation,
            context_value=self.context_value,
            variables=dict(eventId=self.enabled_event.id, amount=40),
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(result.errors[0]),
        )
        self.assertIsNone(result.data["placeBetByEvent"])
