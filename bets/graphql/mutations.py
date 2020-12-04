from graphene import Mutation, Field, ID, String, Boolean, DateTime
from graphene_django.forms.mutation import DjangoModelFormMutation

from bets.models import Event, Quota
from bets.forms import EventForm, QuotaForm
from bets.graphql.types import (
    EventType,
    QuotaType,
)

class CreateEventMutation(DjangoModelFormMutation):
    """
    ModelFormMutation for Event creation

    :cvar event: EventType field
    """

    event = Field(EventType)

    class Meta:
        form_class = EventForm


class CreateQuotaMutation(DjangoModelFormMutation):
    """
    ModelFormMutation for Quota creation

    :cvar quota: QuotaType field
    """

    quota = Field(QuotaType)

    class Meta:
        form_class = QuotaForm


class UpdateEventMutation(Mutation):
    """
    Mutation for Event update

    :cvar event: EventType field
    """
    
    class Arguments:
        """
        Arguments for Event update
        """

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
        """
        Mutation function.

        :param info: Request information
        :param id: Integer with Event ID
        :param name: String with Event name
        :param description: String with Event description
        :param rules: String with Event rules
        :param expiration_date: DateTime with Event expiration datetime
        :param active: Boolean indication whether Event is active
        :param completed: Boolean indicating Event completion
        """

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
    """
    Mutation for Quota update

    :cvar quota: QuotaType field
    """

    class Arguments:
        """
        Arguments for Quota update
        """

        id = ID()
        expiration_date = DateTime()
        active = Boolean()

    quota = Field(QuotaType)

    def mutate(self, info, id, expiration_date=None, active=None):
        """
        Mutation function.

        :param info: Request information
        :param id: Integer with Quota ID
        :param expiration_date: DateTime with Event expiration datetime
        :param active: Boolean indicating whether Quota is active
        """

        quota = Quota.objects.get(id=id)
        if expiration_date:
            quota.expiration_date = expiration_date
        if active is not None:
            quota.active = active
        quota.save()
        return UpdateQuotaMutation(quota=quota)
