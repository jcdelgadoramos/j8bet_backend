from graphene_django import DjangoObjectType

from bets.models import Event, Transaction, Bet, Quota, Prize


class EventType(DjangoObjectType):
    """
    GraphQL object type for Event
    """

    class Meta:
        model = Event
        fields = "__all__"


class TransactionType(DjangoObjectType):
    """
    GraphQL object type for Transaction
    """

    class Meta:
        model = Transaction 
        fields = "__all__"


class QuotaType(DjangoObjectType):
    """
    GraphQL object type for Quota model
    """

    class Meta:
        model = Quota
        fields = "__all__"


class BetType(DjangoObjectType):
    """
    GraphQL object type for Bet model 
    """

    class Meta:
        model = Bet
        fields = "__all__"


class PrizeType(DjangoObjectType):
    """
    GraphQL object type for Prize model
    """

    class Meta:
        model = Prize
        fields = "__all__"
