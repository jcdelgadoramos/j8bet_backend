from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    """
    GraphQL object type for User
    """

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'password', 'email',]
