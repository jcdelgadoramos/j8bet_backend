import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from j8bet_backend.constants import ALL_GROUPS


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker("user_name")

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Iterator(ALL_GROUPS)
