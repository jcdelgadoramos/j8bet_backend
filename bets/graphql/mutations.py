from bets.graphql.input import (
    EventCreationInput,
    EventUpdateInput,
    QuotaCreationInput,
    QuotaUpdateInput,
)
from bets.graphql.types import EventType, QuotaType
from bets.models import Event, Quota
from graphene import ID, Boolean, Field, Mutation
from graphql import GraphQLError
from j8bet_backend.decorators import bet_manager


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

    @bet_manager
    def mutate(self, info, event_input):
        """
        Mutation function.

        :param info: Request information
        :param event_input: Mutation input
        """

        event_input['manager'] = info.context.user
        event = Event.objects.create(**event_input)
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

    @bet_manager
    def mutate(self, info, quota_input):
        """
        Mutation function.

        :param info: Request information
        :parma quota_input: Mutation input
        """

        event_input['manager'] = info.context.user
        quota_input["event"] = Event.objects.get(id=quota_input.event)
        quota = Quota.objects.create(**quota_input)
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

    @bet_manager
    def mutate(self, info, event_input):
        """
        Mutation function.

        :param info: Request information
        :param event_input: Mutation input
        """

        if not Event.objects.filter(
            id=event_input.id,
            manager=info.context.user
        ).count():
            raise GraphQLError("The event must belong to the bet manager.")
        event, _ = Event.objects.update_or_create(
            id=event_input.id, manager=info.context.user, defaults=event_input,
        )
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

    @bet_manager
    def mutate(self, info, quota_input):
        """
        Mutation function.

        :param info: Request information
        :parma quota_input: Mutation input
        """

        if not Quota.objects.filter(
            id=event_input.id,
            manager=info.context.user
        ).count():
            raise GraphQLError("The quota must belong to the bet manager.")
        quota, _ = Quota.objects.update_or_create(
            id=quota_input.id, manager=info.context.user, defaults=quota_input,
        )
        return UpdateQuotaMutation(quota=quota)


class DeleteEventMutation(Mutation):
    deleted = Boolean()

    class Arguments:
        """
        Arguments for Event deletion
        """

        id = ID()

    @bet_manager
    def mutate(self, info, id):

        if not Event.objects.filter(id=id, manager=info.context.user).count():
            raise GraphQLError("The event must belong to the bet manager.")
        Event.objects.filter(id=id, manager=info.context.user).delete()
        return DeleteEventMutation(deleted=True)


class DeleteQuotaMutation(Mutation):
    deleted = Boolean()

    class Arguments:
        """
        Arguments for Quota deletion
        """

        id = ID()

    @bet_manager
    def mutate(self, info, id):

        if not Quota.objects.filter(id=id, manager=info.context.user).count():
            raise GraphQLError("The quota must belong to the bet manager.")
        Quota.objects.filter(id=id, manager=info.context.user).delete()
        return DeleteQuotaMutation(deleted=True)
