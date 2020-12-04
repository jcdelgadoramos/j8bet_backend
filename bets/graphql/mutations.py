from graphene import Mutation, Field, ID, String, Boolean, DateTime
from graphene_django.forms.mutation import DjangoModelFormMutation

from bets.models import Event, Quota
from bets.forms import EventForm, QuotaForm
from bets.graphql.types import (
    EventType,
    QuotaType,
)

class CreateEventMutation(DjangoModelFormMutation):
    event = Field(EventType)

    class Meta:
        form_class = EventForm


class CreateQuotaMutation(DjangoModelFormMutation):
    quota = Field(QuotaType)

    class Meta:
        form_class = QuotaForm


class UpdateEventMutation(Mutation):
    
    class Arguments:
        id = ID()
        name = String()
        description = String()
        rules = String()
        creation_date = DateTime()
        modification_date = DateTime()
        expiration_date = DateTime()
        active = Boolean()
        completed = Boolean()

    event = Field(EventType)

    def mutate(self, info, id, name=None, description=None,
               rules=None, expiration_date=None, active=None, completed=None):
        event = Event.objects.get(id=id)
        if name:
            event.name = name
        if description:
            event.description = description
        if expiration_date:
            event.expiration_date = expiration_date
        if active is not None:
            event.active = active
        event.completed = completed
        event.save()
        return UpdateEventMutation(event=event)


class UpdateQuotaMutation(Mutation):

    class Arguments:
        id = ID()
        expiration_date = DateTime()
        active = Boolean()

    quota = Field(QuotaType)

    def mutate(self, info, id, expiration_date=None, active=None):
        quota = Quota.objects.get(id=id)
        if expiration_date:
            quota.expiration_date = expiration_date
        if active is not None:
            quota.active = active
        quota.save()
        return UpdateQuotaMutation(quota=quota)
