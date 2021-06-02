from bets.graphql.types import (
    AffairType,
    BetType,
    EventType,
    PrizeType,
    QuotaType,
    TagType,
    TransactionType,
)
from graphene import ObjectType, String
from graphene.relay import Node
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required


class TagQuery(ObjectType):
    """
    Query for Tag objects
    """

    all_tags = DjangoFilterConnectionField(TagType)
    tag_by_id = Node.Field(TagType)


class AffairQuery(ObjectType):
    """
    Query for Affair objects
    """

    all_affairs = DjangoFilterConnectionField(AffairType)
    affair_by_id = Node.Field(AffairType)


class EventQuery(ObjectType):
    """
    Query for Event objects
    """

    all_events = DjangoFilterConnectionField(EventType)
    event_by_id = Node.Field(EventType)


class TransactionQuery(ObjectType):
    """
    Query for Transaction objects
    """

    all_transactions = DjangoFilterConnectionField(TransactionType)
    transaction_by_id = Node.Field(TransactionType)


class QuotaQuery(ObjectType):
    """
    Query for Quota objects
    """

    all_quotas = DjangoFilterConnectionField(QuotaType)
    quota_by_id = Node.Field(QuotaType)


class BetQuery(ObjectType):
    """
    Quota for Bet objects
    """

    all_bets = DjangoFilterConnectionField(BetType)
    bet_by_id = Node.Field(BetType)


class PrizeQuery(ObjectType):
    """
    Quota for Prize objects
    """

    all_prizes = DjangoFilterConnectionField(PrizeType)
    prize_by_id = Node.Field(PrizeType)


class HelloQuery(ObjectType):
    """
    Sample Hello Query
    """

    hello = String(name=String(default_value="stranger"))

    @login_required
    def resolve_hello(self, info, name):
        return f"Hello {name}!"
