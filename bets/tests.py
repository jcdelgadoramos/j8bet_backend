from datetime import datetime

from bets.factories import BetFactory, EventFactory, QuotaFactory
from bets.graphql.schema import Mutations as BetMutation
from bets.graphql.schema import Queries as BetQuery
from bets.models import Bet, Event, Prize, Quota
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from j8bet_backend.constants import BET_MANAGER, ALL_GROUPS
from graphene import Schema
from graphene.test import Client
from graphql_jwt.testcases import JSONWebTokenTestCase
from graphql.error.located_error import GraphQLLocatedError
from users.factories import UserFactory, GroupFactory

def create_groups():
    """
    Function which creates the different user groups used in J8Bet.

    :return: Dict with GroupFactory objects created.
    """

    groups = dict()
    for group in ALL_GROUPS:
        groups[group] = GroupFactory(name=group)

    return groups


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


class QueryTest(JSONWebTokenTestCase):
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
        self.user = UserFactory()
        self.client.authenticate(self.user)
        super().setUp()

    def test_00_hello(self):
        """
        This test evaluates the HelloQuery
        """

        query = """
            query hello {
                hola: hello(name: "tester")
            }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual("Hello tester!", result.data["hola"])

    def test_01_get_all_events(self):
        """
        This test evaluates retrieving all events.
        """

        query = """
            query getAllEvents {{
                events: allEvents {{
                    {fields}
                }}
            }}
        """.format(
            fields=self.event_fields
        )
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_event.id, int(result.data["events"][0]["id"])
        )
        self.assertEqual(
            self.first_event.name, result.data["events"][0]["name"]
        )
        self.assertEqual(
            self.first_event.description,
            result.data["events"][0]["description"],
        )
        self.assertEqual(
            self.first_event.rules, result.data["events"][0]["rules"]
        )
        self.assertEqual(
            self.first_event.creation_date,
            datetime.strptime(
                result.data["events"][0]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_event.modification_date,
            datetime.strptime(
                result.data["events"][0]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_event.expiration_date,
            datetime.strptime(
                result.data["events"][0]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.first_event.active, result.data["events"][0]["active"]
        )
        self.assertEqual(
            self.second_event.id, int(result.data["events"][1]["id"])
        )
        self.assertEqual(
            self.second_event.name, result.data["events"][1]["name"]
        )
        self.assertEqual(
            self.second_event.description,
            result.data["events"][1]["description"],
        )
        self.assertEqual(
            self.second_event.rules, result.data["events"][1]["rules"]
        )
        self.assertEqual(
            self.second_event.creation_date,
            datetime.strptime(
                result.data["events"][1]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_event.modification_date,
            datetime.strptime(
                result.data["events"][1]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_event.expiration_date,
            datetime.strptime(
                result.data["events"][1]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.second_event.active, result.data["events"][1]["active"]
        )

    def test_02_get_event(self):
        """
        This test evaluates retrieving a single event.
        """

        query = """
            query getEventById {{
                event: eventById(id: {id}) {{
                    {fields}
                }}
            }}
        """.format(
            id=self.first_event.id, fields=self.event_fields
        )
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(self.first_event.id, int(result.data["event"]["id"]))
        self.assertEqual(self.first_event.name, result.data["event"]["name"])
        self.assertEqual(
            self.first_event.description, result.data["event"]["description"]
        )
        self.assertEqual(self.first_event.rules, result.data["event"]["rules"])
        self.assertEqual(
            self.first_event.creation_date,
            datetime.strptime(
                result.data["event"]["creationDate"], "%Y-%m-%dT%H:%M:%S.%f%z",
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
                result.data["event"]["expirationDate"], "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.first_event.active, result.data["event"]["active"]
        )

    def test_03_get_all_quotas(self):
        """
        This test evaluates retrieving all quotas.
        """

        query = """
            query getAllQuotas {{
                quotas: allQuotas {{
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
            event_fields=self.event_fields
        )
        result = self.client.execute(query)
        self.first_quota.refresh_from_db()
        self.second_quota.refresh_from_db()
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_quota.id, int(result.data["quotas"][0]["id"])
        )
        self.assertEqual(
            float(self.first_quota.probability),
            result.data["quotas"][0]["probability"],
        )
        self.assertEqual(
            self.first_quota.creation_date,
            datetime.strptime(
                result.data["quotas"][0]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_quota.modification_date,
            datetime.strptime(
                result.data["quotas"][0]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.first_quota.expiration_date,
            datetime.strptime(
                result.data["quotas"][0]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.first_quota.active, result.data["quotas"][0]["active"]
        )
        self.assertEqual(
            self.first_quota.event.id,
            int(result.data["quotas"][0]["event"]["id"]),
        )
        self.assertEqual(
            self.second_quota.id, int(result.data["quotas"][1]["id"])
        )
        self.assertEqual(
            float(self.second_quota.probability),
            result.data["quotas"][1]["probability"],
        )
        self.assertEqual(
            self.second_quota.creation_date,
            datetime.strptime(
                result.data["quotas"][1]["creationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_quota.modification_date,
            datetime.strptime(
                result.data["quotas"][1]["modificationDate"],
                "%Y-%m-%dT%H:%M:%S.%f%z",
            ),
        )
        self.assertEqual(
            self.second_quota.expiration_date,
            datetime.strptime(
                result.data["quotas"][1]["expirationDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.second_quota.active, result.data["quotas"][1]["active"]
        )
        self.assertEqual(
            self.second_quota.event.id,
            int(result.data["quotas"][1]["event"]["id"]),
        )

    def test_04_get_quota(self):
        """
        This test evaluates retrieving a single quota.
        """

        query = """
            query getQuotaById {{
                quota: quotaById(id: {id}) {{
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
            id=self.first_quota.id, event_fields=self.event_fields
        )
        result = self.client.execute(query)
        self.first_quota.refresh_from_db()
        self.assertIsNone(result.errors)
        self.assertEqual(self.first_quota.id, int(result.data["quota"]["id"]))
        self.assertEqual(
            float(self.first_quota.probability),
            result.data["quota"]["probability"],
        )
        self.assertEqual(
            self.first_quota.creation_date,
            datetime.strptime(
                result.data["quota"]["creationDate"], "%Y-%m-%dT%H:%M:%S.%f%z",
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
                result.data["quota"]["expirationDate"], "%Y-%m-%dT%H:%M:%S%z",
            ),
        )
        self.assertEqual(
            self.first_quota.active, result.data["quota"]["active"]
        )
        self.assertEqual(
            self.first_quota.event.id, int(result.data["quota"]["event"]["id"])
        )

    def test_05_get_all_bets(self):
        """
        This test evaluates retrieving all bets.
        """

        query = """
            query getAllBets {{
                bets: allBets {{
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
            event_fields=self.event_fields
        )
        result = self.client.execute(query)
        self.first_bet.refresh_from_db()
        self.second_bet.refresh_from_db()
        self.assertIsNone(result.errors)
        self.assertEqual(self.first_bet.id, int(result.data["bets"][0]["id"]))
        self.assertEqual(
            float(self.first_bet.potential_earnings),
            result.data["bets"][0]["potentialEarnings"],
        )
        self.assertEqual(
            self.first_bet.active, result.data["bets"][0]["active"]
        )
        self.assertEqual(self.first_bet.won, result.data["bets"][0]["won"])
        self.assertEqual(
            self.first_bet.quota.id, int(result.data["bets"][0]["quota"]["id"])
        )
        self.assertEqual(self.second_bet.id, int(result.data["bets"][1]["id"]))
        self.assertEqual(
            float(self.second_bet.potential_earnings),
            result.data["bets"][1]["potentialEarnings"],
        )
        self.assertEqual(
            self.second_bet.active, result.data["bets"][1]["active"]
        )
        self.assertEqual(self.second_bet.won, result.data["bets"][1]["won"])
        self.assertEqual(
            self.second_bet.quota.id, int(result.data["bets"][1]["quota"]["id"])
        )

    def test_06_get_bet(self):
        """
        This test evaluates retrieving a single quota.
        """

        query = """
            query getBetById {{
                bet: betById(id: {id}) {{
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
            id=self.first_bet.id, event_fields=self.event_fields
        )
        result = self.client.execute(query)
        self.first_bet.refresh_from_db()
        self.assertIsNone(result.errors)
        self.assertEqual(self.first_bet.id, int(result.data["bet"]["id"]))
        self.assertEqual(
            float(self.first_bet.potential_earnings),
            result.data["bet"]["potentialEarnings"],
        )
        self.assertEqual(self.first_bet.active, result.data["bet"]["active"])
        self.assertEqual(self.first_bet.won, result.data["bet"]["won"])
        self.assertEqual(
            self.first_bet.quota.id, int(result.data["bet"]["quota"]["id"])
        )

    def test_07_get_all_transactions(self):
        """
        This test evaluates retrieving all transactions.
        """

        query = """
            query getAllTransactions {
                transactions: allTransactions {
                    id,
                    amount,
                    description,
                }
            }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_bet.transaction.id,
            int(result.data["transactions"][0]["id"]),
        )
        self.assertEqual(
            float(self.first_bet.transaction.amount),
            result.data["transactions"][0]["amount"],
        )
        self.assertEqual(
            self.first_bet.transaction.description,
            result.data["transactions"][0]["description"],
        )
        self.assertEqual(
            self.second_bet.transaction.id,
            int(result.data["transactions"][1]["id"]),
        )
        self.assertEqual(
            float(self.second_bet.transaction.amount),
            result.data["transactions"][1]["amount"],
        )
        self.assertEqual(
            self.second_bet.transaction.description,
            result.data["transactions"][1]["description"],
        )

    def test_08_get_transaction(self):
        """
        This test evaluates retrieving a single transaction.
        """

        query = """
            query getTransaction {{
                transaction: transactionById(id: {id}) {{
                    id,
                    amount,
                    description,
                }}
            }}
        """.format(
            id=self.first_bet.transaction.id
        )
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_bet.transaction.id, int(result.data["transaction"]["id"])
        )
        self.assertEqual(
            float(self.first_bet.transaction.amount),
            result.data["transaction"]["amount"],
        )
        self.assertEqual(
            self.first_bet.transaction.description,
            result.data["transaction"]["description"],
        )

    def test_09_get_all_prizes(self):
        """
        This test evaluates retrieving all prizes.
        """

        self.first_event.completed = True
        self.first_event.save()
        self.first_prize = Prize.objects.first()
        self.second_prize = Prize.objects.exclude(
            id=self.first_prize.id
        ).first()
        query = """
            query getAllPrizes {
                prizes: allPrizes {
                    id,
                    bet{
                        id
                    }
                    reward,
                }
            }
        """
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(
            self.first_prize.id, int(result.data["prizes"][0]["id"])
        )
        self.assertEqual(
            float(self.first_prize.reward), result.data["prizes"][0]["reward"]
        )
        self.assertEqual(
            self.first_prize.bet.id, int(result.data["prizes"][0]["bet"]["id"])
        )
        self.assertEqual(
            self.second_prize.id, int(result.data["prizes"][1]["id"])
        )
        self.assertEqual(
            float(self.second_prize.reward), result.data["prizes"][1]["reward"]
        )
        self.assertEqual(
            self.second_prize.bet.id, int(result.data["prizes"][1]["bet"]["id"])
        )

    def test_10_get_prize(self):
        """
        This test evaluates retrieving a single prize.
        """

        self.first_event.completed = True
        self.first_event.save()
        self.first_prize = Prize.objects.first()
        query = """
            query getPrize {{
                prize: prizeById(id: {id}) {{
                    id,
                    bet{{
                        id
                    }}
                    reward,
                }}
            }}
        """.format(
            id=self.first_prize.id
        )
        result = self.client.execute(query)
        self.assertIsNone(result.errors)
        self.assertEqual(self.first_prize.id, int(result.data["prize"]["id"]))
        self.assertEqual(
            float(self.first_prize.reward), result.data["prize"]["reward"]
        )
        self.assertEqual(
            self.first_prize.bet.id, int(result.data["prize"]["bet"]["id"])
        )


class MutationTest(JSONWebTokenTestCase):
    def setUp(self):
        self.groups = create_groups()
        self.event = EventFactory(active=True)
        self.quota = QuotaFactory(event=self.event, active=True)
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
        self.request_factory = RequestFactory()
        self.context_value = self.request_factory.get(reverse("graphql"))
        self.user = UserFactory()
        self.user.groups.add(self.groups[BET_MANAGER])
        self.client.authenticate(self.user)
        super().setUp()

    def test_01_create_event(self):
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

    def test_02_update_event(self):
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
            self.event.id, int(executed.data["updateEvent"]["event"]["id"]),
        )
        self.assertEqual(
            self.event.name, executed.data["updateEvent"]["event"]["name"],
        )
        self.assertEqual(
            self.event.description,
            executed.data["updateEvent"]["event"]["description"],
        )
        self.assertEqual(
            self.event.rules, executed.data["updateEvent"]["event"]["rules"],
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

    def test_03_create_quota(self):
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
            int(executed.data["createQuota"]["quota"]["event"]["id"]),
        )

    def test_04_update_quota(self):
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
            self.quota.id, int(executed.data["updateQuota"]["quota"]["id"]),
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
            int(executed.data["updateQuota"]["quota"]["event"]["id"]),
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

    def test_05_delete_quota(self):
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

    def test_06_delete_event(self):
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


class NotLoggedInTest(JSONWebTokenTestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        self.context_value = self.request_factory.get(reverse("graphql"))

    def test_01_query(self):
        """
        This test evaluates the getAllEvents query without logging in.
        """

        query = """
            query getAllEvents {
                events: allEvents {
                    id
                }
            }
        """
        result = self.client.execute(query)
        self.assertEqual(
            GraphQLLocatedError,
            type(result.errors[0]),
        )
        self.assertIsNone(result.data["events"])

    def test_02_mutation(self):
        """
        This test evaluates the createEvent query without logging in.
        """

        mutation = """
            mutation createEvent($eventInput: EventCreationInput!) {
                createEvent(eventInput: $eventInput) {
                    event{
                        id 
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
                    description="Some description",
                    expirationDate=datetime.now(),
                )
            )
        )
        self.assertEqual(
            GraphQLLocatedError,
            type(result.errors[0]),
        )
        self.assertIsNone(result.data["createEvent"])
