from graphene import Mutation, Field, String, Boolean, DateTime
from graphene_django.forms.mutation import DjangoModelFormMutation

from bets.models import Event, Transaction, Bet, Quota, Prize
from bets.forms import EventForm, TransactionForm, BetForm, QuotaForm, PrizeForm
from bets.graphql.types import (
    EventType,
    TransactionType,
    BetType,
    QuotaType,
    PrizeType,
)

class EventMutation(DjangoModelFormMutation):
    event = Field(EventType)

    class Meta:
        form_class = EventForm
