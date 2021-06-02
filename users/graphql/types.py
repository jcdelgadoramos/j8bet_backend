from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from graphene import Boolean, String
from graphene.relay import Node
from graphene_django import DjangoObjectType


class UserType(DjangoObjectType):
    """
    Relay Node for User
    """
    
    archived = Boolean()
    secondary_email = String()
    verified = Boolean()

    class Meta:
        model = get_user_model()
        filter_fields = {
            "username": ['exact', 'icontains', 'istartswith'],
            "email": ['exact', 'icontains', 'istartswith'],
            "first_name": ['exact', 'icontains', 'istartswith'],
            "last_name": ['exact', 'icontains', 'istartswith'],
            "secondary_email": ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (Node,)
        fields = [
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "archived",
            "secondary_email",
            "verified",
            "groups",
        ]
    
    def resolve_archived(self, info):
        return self.status.archived

    def resolve_secondary_email(self, info):
        return self.status.secondary_email

    def resolve_verified(self, info):
        return self.status.verified


class GroupType(DjangoObjectType):
    """
    GraphQL object type for Group
    """

    class Meta:
        model = Group
        filter_fields = ["name",]
        interfaces = (Node,)
        fields = [
            "name",
        ]
