from bets.models import Affair, Bet, Event, Prize, Quota, Tag, Transaction
from graphene_django import DjangoObjectType


class TagType(DjangoObjectType):
    """
    GraphQL object type for Tag
    """

    class Meta:
        model = Tag
        fields = "__all__"


class AffairType(DjangoObjectType):
    """
    GraphQL object type for Affair
    """

    class Meta:
        model = Affair
        fields = "__all__"


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
