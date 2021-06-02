from bets.graphql.input import (
    AffairCreationInput,
    AffairUpdateInput,
    EventCreationInput,
    EventUpdateInput,
    QuotaCreationInput,
    QuotaUpdateInput,
)
from bets.graphql.types import AffairType, BetType, EventType, QuotaType
from bets.models import Affair, Bet, Event, Quota, Tag, Transaction
from graphene import ID, Boolean, Decimal, Field, Mutation
from graphql import GraphQLError
from j8bet_backend.decorators import bet_consumer, bet_manager

# CRUD Mutations

class CreateAffairMutation(Mutation):
    """
    Mutation for Affair creation

    :cvar affair: AffairType field
    """

    affair = Field(AffairType)

    class Arguments:
        """
        Arguments for Affair creation
        """

        affair_input = AffairCreationInput(required=True)

    @bet_manager
    def mutate(self, info, affair_input):
        """
        Mutation function.

        :param info: Request information
        :param affair_input: Mutation input
        """

        affair_input["manager"] = info.context.user
        tags = list()
        for tag_entry in affair_input.tags:
            try:
                tags.append(Tag.objects.get(id=int(tag_entry)))
            except ValueError:
                tag, _ = Tag.objects.get_or_create(name=tag_entry)
                tags.append(tag)
            except Tag.DoesNotExist:
                raise GraphQLError(
                    f"The tag with ID {tag_entry} does not exist."
                )
        affair_input.pop("tags")
        affair = Affair.objects.create(**affair_input)
        affair.tags.set(tags)
        return CreateAffairMutation(affair=affair)


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

        event_input["manager"] = info.context.user
        event_input["affair"] = Affair.objects.get(id=event_input.affair)
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

        quota_input["manager"] = info.context.user
        quota_input["event"] = Event.objects.get(id=quota_input.event)
        quota = Quota.objects.create(**quota_input)
        return CreateQuotaMutation(quota=quota)


class UpdateAffairMutation(Mutation):
    """
    Mutation for Affair update

    :cvar affair: AffairType field
    """

    affair = Field(AffairType)

    class Arguments:
        """
        Arguments for Affair update
        """

        affair_input = AffairUpdateInput(required=True)

    @bet_manager
    def mutate(self, info, affair_input):
        """
        Mutate function.

        :param info: Request information
        :param affair_input: Mutation input
        """

        if not Affair.objects.filter(
            id=affair_input.id, manager=info.context.user
        ).count():
            raise GraphQLError("The affair must belong to the bet manager.")
        tags = list()
        if affair_input.tags:
            for tag_entry in affair_input.tags:
                try:
                    tags.append(Tag.objects.get(id=int(tag_entry)))
                except ValueError:
                    tag, _ = Tag.objects.get_or_create(name=tag_entry)
                    tags.append(tag)
                except Tag.DoesNotExist:
                    raise GraphQLError(
                        f"The tag with ID {tag_entry} does not exist."
                    )
        affair_input.pop("tags")
        affair, _ = Affair.objects.update_or_create(
            id=affair_input.id, manager=info.context.user, defaults=affair_input,
        )
        affair.tags.set(tags)
        return UpdateAffairMutation(affair=affair)


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
            id=event_input.id, manager=info.context.user
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
            id=quota_input.id, manager=info.context.user,
        ).count():
            raise GraphQLError("The quota must belong to the bet manager.")
        quota, _ = Quota.objects.update_or_create(
            id=quota_input.id, manager=info.context.user, defaults=quota_input,
        )
        return UpdateQuotaMutation(quota=quota)


class DeleteAffairMutation(Mutation):
    deleted = Boolean()

    class Arguments:
        """
        Arguments for Affair deletion
        """

        id = ID()

    @bet_manager
    def mutate(self, info, id):

        if not Affair.objects.filter(id=id, manager=info.context.user).count():
            raise GraphQLError("The affair must belong to the bet manager.")
        Affair.objects.filter(id=id, manager=info.context.user).delete()
        return DeleteAffairMutation(deleted=True)


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


# Functional mutations


class BetPlacementByQuotaMutation(Mutation):
    bet = Field(BetType)

    class Arguments:
        """
        Arguments for Bet Placement by Quota
        """

        quota_id = ID()
        amount = Decimal()

    @bet_consumer
    def mutate(self, info, quota_id, amount):
        if not Quota.objects.filter(
            id=quota_id, active=True, event__active=True,
        ).exists():
            raise GraphQLError("Not a valid quota.")
        quota = Quota.objects.filter(id=quota_id).first()

        # TODO change the way Transactions are managed when the time comes
        transaction = Transaction.objects.create(
            amount=amount, description="Bet placement", user=info.context.user,
        )
        bet = Bet.objects.create(
            transaction=transaction, quota=quota, user=info.context.user,
        )

        return BetPlacementByQuotaMutation(bet=bet)


class BetPlacementByEventMutation(Mutation):
    bet = Field(BetType)

    class Arguments:
        """
        Arguments for Bet Placement by Event
        """

        event_id = ID()
        amount = Decimal()

    @bet_consumer
    def mutate(self, info, event_id, amount):
        if not Event.objects.filter(id=event_id, active=True).exists():
            raise GraphQLError("Not a valid event.")
        if not Quota.objects.filter(event__id=event_id, active=True).exists():
            raise GraphQLError("Event does not have any valid Quotas.")
        quota = (
            Quota.objects.filter(event__id=event_id, active=True,)
            .order_by("creation_date")
            .first()
        )

        # TODO change the way Transactions are managed when the time comes
        transaction = Transaction.objects.create(
            amount=amount, description="Bet placement", user=info.context.user,
        )
        bet = Bet.objects.create(
            transaction=transaction, quota=quota, user=info.context.user,
        )

        return BetPlacementByEventMutation(bet=bet)
