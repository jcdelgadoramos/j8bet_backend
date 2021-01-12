from bets.graphql.types import (
    BetType,
    EventType,
    PrizeType,
    QuotaType,
    TransactionType,
)
from bets.models import Bet, Event, Prize, Quota, Transaction
from graphene import ID, Field, ObjectType, String
from graphene_django import DjangoListField


class EventQuery(ObjectType):
    all_events = DjangoListField(EventType)
    event_by_id = Field(EventType, id=ID())

    def resolve_all_events(parent, info):
        return Event.objects.all()

    def resolve_event_by_id(parent, info, id):
        return Event.objects.get(id=id)


class TransactionQuery(ObjectType):
    all_transactions = DjangoListField(TransactionType)
    transaction_by_id = Field(TransactionType, id=ID())

    def resolve_all_transaction(parent, info):
        return Transaction.objects.all()

    def resolve_transaction_by_id(parent, info, id):
        return Transaction.objects.get(id=id)


class QuotaQuery(ObjectType):
    all_quotas = DjangoListField(QuotaType)
    quota_by_id = Field(QuotaType, id=ID())

    def resolve_quota_by_id(parent, info, id):
        return Quota.objects.get(id=id)

    def resolve_all_prizes(parent, info):
        return Prize.objects.all()


class BetQuery(ObjectType):
    all_bets = DjangoListField(BetType)
    bet_by_id = Field(BetType, id=ID())

    def resolve_all_bets(parent, info):
        return Bet.objects.all()

    def resolve_bet_by_id(parent, info, id):
        return Bet.objects.get(id=id)


class PrizeQuery(ObjectType):
    all_prizes = DjangoListField(PrizeType)
    prize_by_id = Field(PrizeType, id=ID())

    def resolve_prize_by_id(parent, info, id):
        return Prize.objects.get(id=id)

    def resolve_hello(parent, info, name):
        return f"Hello {name}!"


class HelloQuery(ObjectType):
    hello = String(name=String(default_value="stranger"))

    def resolve_all_quotas(parent, info):
        return Quota.objects.all()
