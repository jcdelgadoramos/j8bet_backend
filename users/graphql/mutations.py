from graphene import Field
from graphene_django.forms.mutation import DjangoModelFormMutation
from users.forms import UserForm
from users.graphql.types import UserType


class CreateUserMutation(DjangoModelFormMutation):
    user = Field(UserType)

    class Meta:
        form_class = UserForm
