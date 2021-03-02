import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = get_user_model()

    username = factory.Faker("user_name")


class GroupFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Group
