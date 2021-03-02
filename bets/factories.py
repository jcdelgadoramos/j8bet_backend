import factory
from bets.models import Bet, Event, Prize, Quota, Transaction
from django.utils import timezone
from users.factories import UserFactory


class AbstractDateFactory:
    creation_date = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )
    modification_date = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )


class EventFactory(AbstractDateFactory, factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    name = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph")
    rules = factory.Faker("paragraph")
    expiration_date = factory.Faker(
        "date_time", tzinfo=timezone.get_current_timezone()
    )
    active = factory.Faker("pybool")
    completed = factory.Faker("pybool")


class TransactionFactory(
    AbstractDateFactory, factory.django.DjangoModelFactory,
):
    class Meta:
        model = Transaction

    amount = factory.Faker("pydecimal", min_value=0, right_digits=2)
    description = factory.Faker("sentence", nb_words=4)


class QuotaFactory(AbstractDateFactory, factory.django.DjangoModelFactory):
    class Meta:
        model = Quota

    event = factory.SubFactory(EventFactory)
    probability = factory.Faker(
        "pydecimal", min_value=0, max_value=1, right_digits=5
    )
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
