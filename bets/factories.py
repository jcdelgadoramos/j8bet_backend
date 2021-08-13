import factory
from bets.models import Affair, Bet, Event, Prize, Quota, Tag, Transaction
from django.utils import timezone
from users.factories import UserFactory


class AbstractDateFactory:
    creation_date = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )
    modification_date = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )


class TagFactory(AbstractDateFactory, factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Faker("sentence", nb_words=4)


class AffairFactory(AbstractDateFactory, factory.django.DjangoModelFactory):
    class Meta:
        model = Affair

    manager = factory.SubFactory(UserFactory)
    description = factory.Faker("paragraph")

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class EventFactory(AbstractDateFactory, factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    manager = factory.SubFactory(UserFactory)
    affair = factory.SubFactory(AffairFactory)
    name = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    rules = factory.Faker("paragraph")
    expiration_date = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )
    active = factory.Faker("pybool")
    completed = factory.Faker("pybool")


class TransactionFactory(
    AbstractDateFactory,
    factory.django.DjangoModelFactory,
):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    amount = factory.Faker("pydecimal", min_value=0, right_digits=2)
    description = factory.Faker("sentence", nb_words=4)


class QuotaFactory(AbstractDateFactory, factory.django.DjangoModelFactory):
    class Meta:
        model = Quota

    manager = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactory)
    probability = factory.Faker(
        "pydecimal", min_value=0, max_value=1, right_digits=5
    )
    # coeficient = factory.Faker(
    #     "pydecimal", min_value=1, max_value=200, right_digits=2
    # )
    coeficient = 2.5
    expiration_date = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )
    active = factory.Faker("pybool")


class BetFactory(AbstractDateFactory, factory.django.DjangoModelFactory):
    class Meta:
        model = Bet

    transaction = factory.SubFactory(TransactionFactory)
    quota = factory.SubFactory(QuotaFactory)
    user = factory.SubFactory(UserFactory)
    potential_earnings = factory.Faker("pydecimal", min_value=0)
    won = factory.Faker("pybool")
    active = factory.Faker("pybool")


class PrizeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Prize

    bet = factory.SubFactory(BetFactory)
    user = factory.SubFactory(UserFactory)
    reward = factory.Faker("pydecimal", min_value=0)
    creation_date = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )
