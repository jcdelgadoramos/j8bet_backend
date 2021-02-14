from bets.forms import EventForm, QuotaForm
from bets.graphql.input import (
    EventCreationInput,
    EventUpdateInput,
    QuotaCreationInput,
    QuotaUpdateInput,
)
from bets.graphql.types import EventType, QuotaType
from bets.models import Event, Quota
from datetime import datetime, date
from graphene import ID, Boolean, DateTime, Decimal, Field, Mutation, String
from graphql_jwt.decorators import login_required


class CreateEventMutation(Mutation):
    """
    Mutation for Event creation

    :cvar event: EventType field
    """

    event = Field(EventType)

    class Arguments:
        """
        Arguments for Event creation 
        """

        event_input = EventCreationInput(required=True)

    @login_required
    def mutate(self, info, event_input):
        """
        Mutation function.

        :param info: Request information
        :param event_input: Mutation input
        """

        event = Event()
        event.name = event_input.name
        event.description = event_input.description
        event.expiration_date = event_input.expiration_date
        if event_input.active is not None:
            event.active = event_input.active
        event.completed = event_input.completed
        event.save()
        return CreateEventMutation(event=event)


class CreateQuotaMutation(Mutation):
    """
    ModelFormMutation for Quota creation

    :cvar quota: QuotaType field
    """

    quota = Field(QuotaType)

    class Arguments:
        """
        Arguments for Quota update
        """

        quota_input = QuotaCreationInput(required=True)

    @login_required
    def mutate(self, info, quota_input):
        """
        Mutation function.

        :param info: Request information
        :parma quota_input: Mutation input
        """

        quota = Quota()
        quota.probability = quota_input.probability
        quota.expiration_date = quota_input.expiration_date
        quota.event = Event.objects.get(id=quota_input.event)
        if quota_input.active is not None:
            quota.active = quota_input.active
        quota.save()
        return CreateQuotaMutation(quota=quota)


class UpdateEventMutation(Mutation):
    """
    Mutation for Event update

    :cvar event: EventType field
    """

    event = Field(EventType)

    class Arguments:
        """
        Arguments for Event update
        """

        event_input = EventUpdateInput(required=True)

    @login_required
    def mutate(self, info, event_input):
        """
        Mutation function.

        :param info: Request information
        :param event_input: Mutation input
        """

        event = Event.objects.get(id=event_input.id)
        if event_input.name:
            event.name = event_input.name
        if event_input.expiration_date:
            event.expiration_date = event_input.expiration_date
        if event_input.description:
            event.description = event_input.description
        if event_input.active is not None:
            event.active = event_input.active
        event.completed = event_input.completed
        event.save()
        return UpdateEventMutation(event=event)


class UpdateQuotaMutation(Mutation):
    """
    Mutation for Quota update

    :cvar quota: QuotaType field
    """

    quota = Field(QuotaType)

    class Arguments:
        """
        Arguments for Quota update
        """

        quota_input = QuotaUpdateInput(required=True)

    @login_required
    def mutate(self, info, quota_input):
        """
        Mutation function.

        :param info: Request information
        :parma quota_input: Mutation input
        """

        quota = Quota.objects.get(id=quota_input.id)
        if quota_input.expiration_date:
            quota.expiration_date = quota_input.expiration_date
        if quota_input.active is not None:
            quota.active = quota_input.active
        quota.save()
        return UpdateQuotaMutation(quota=quota)


class DeleteEventMutation(Mutation):
    deleted = Boolean()

    class Arguments:
        """
        Arguments for Event deletion
        """

        id = ID()

    @login_required
    def mutate(self, info, id):

        Event.objects.filter(id=id).delete()
        return DeleteEventMutation(deleted=True)


class DeleteQuotaMutation(Mutation):
    deleted = Boolean()

    class Arguments:
        """
        Arguments for Quota deletion
        """

        id = ID()

    @login_required
    def mutate(self, info, id):

        Quota.objects.filter(id=id).delete()
        return DeleteQuotaMutation(deleted=True)
