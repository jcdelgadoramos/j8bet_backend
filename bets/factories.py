import factory
from django.utils import timezone

from bets.models import Event

class EventFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Event

    name = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('sentence', nb_words=10)
    rules = factory.Faker('sentence', nb_words=10)
    expiration_date = factory.Faker('date_time', tzinfo=timezone.get_current_timezone())
    active = factory.Faker('pybool')
    completed = factory.Faker('pybool')
