from bets.models import Affair, Bet, Event, Prize, Quota, Tag, Transaction
from graphene_django import DjangoObjectType
from graphene.relay import Node
from graphql_jwt.decorators import login_required


@login_required
def login_required_resolver(attname, default_value, root, info, **args):
    """
    Prevents resolver from being accessed without proper authentication
    """

    return getattr(root, attname, default_value)


class TagType(DjangoObjectType):
    """
    Relay Node for Tag
    """

    class Meta:
        model = Tag
        filter_fields = ["name"]
        interfaces = (Node,)
        default_resolver = login_required_resolver


class AffairType(DjangoObjectType):
    """
    Relay Node for Affair
    """

    class Meta:
        model = Affair
        filter_fields = {
            "description": ["exact", "icontains", "istartswith"],
        }
        interfaces = (Node,)
        default_resolver = login_required_resolver


class EventType(DjangoObjectType):
    """
    Relay Node for Event
    """

    class Meta:
        model = Event
        filter_fields = {
            "id": ["exact"],
            "name": ["exact", "icontains", "istartswith"],
            "description": ["exact", "icontains", "istartswith"],
            "active": ["exact"],
            "completed": ["exact"],
        }
        interfaces = (Node,)
        default_resolver = login_required_resolver


class TransactionType(DjangoObjectType):
    """
    Relay Node for Transaction
    """

    class Meta:
        model = Transaction
        filter_fields = ["description"]
        interfaces = (Node,)
        default_resolver = login_required_resolver


class QuotaType(DjangoObjectType):
    """
    Relay Node for Quota model
    """

    class Meta:
        model = Quota
        filter_fields = ["active"]
        interfaces = (Node,)
        default_resolver = login_required_resolver


class BetType(DjangoObjectType):
    """
    Relay Node for Bet model
    """

    class Meta:
        model = Bet
        filter_fields = ["won", "active"]
        interfaces = (Node,)
        default_resolver = login_required_resolver


class PrizeType(DjangoObjectType):
    """
    Relay Node for Prize model
    """

    class Meta:
        model = Prize
        filter_fields = ["creation_date"]
        interfaces = (Node,)
        default_resolver = login_required_resolver
