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
from graphql_jwt.decorators import login_required


class EventQuery(ObjectType):
    all_events = DjangoListField(EventType)
    event_by_id = Field(EventType, id=ID())

    @login_required
    def resolve_all_events(self, info):
        return Event.objects.all()

    @login_required
    def resolve_event_by_id(self, info, id):
        return Event.objects.get(id=id)


class TransactionQuery(ObjectType):
    all_transactions = DjangoListField(TransactionType)
    transaction_by_id = Field(TransactionType, id=ID())

    @login_required
    def resolve_all_transactions(self, info):
        return Transaction.objects.all()

    @login_required
    def resolve_transaction_by_id(self, info, id):
        return Transaction.objects.get(id=id)


class QuotaQuery(ObjectType):
    all_quotas = DjangoListField(QuotaType)
    quota_by_id = Field(QuotaType, id=ID())

    @login_required
    def resolve_all_quotas(self, info):
        return Quota.objects.all()

    @login_required
    def resolve_quota_by_id(self, info, id):
        return Quota.objects.get(id=id)


class BetQuery(ObjectType):
    all_bets = DjangoListField(BetType)
    bet_by_id = Field(BetType, id=ID())

    @login_required
    def resolve_all_bets(self, info):
        return Bet.objects.all()

    @login_required
    def resolve_bet_by_id(self, info, id):
        return Bet.objects.get(id=id)


class PrizeQuery(ObjectType):
    all_prizes = DjangoListField(PrizeType)
    prize_by_id = Field(PrizeType, id=ID())

    @login_required
    def resolve_prize_by_id(self, info, id):
        return Prize.objects.get(id=id)

    @login_required
    def resolve_all_prizes(self, info):
        return Prize.objects.all()


class HelloQuery(ObjectType):
    hello = String(name=String(default_value="stranger"))

    @login_required
    def resolve_hello(self, info, name):
        return f"Hello {name}!"
