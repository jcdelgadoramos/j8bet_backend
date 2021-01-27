from django.contrib.auth import get_user_model
from graphene import Field, ID, List, ObjectType
from users.graphql.types import UserType


class UserQuery(ObjectType):
    all_users = List(UserType)
    event_by_id = Field(UserType, id=ID())

    def resolve_all_events(parent, info):
        return get_user_model.objects.all()

    def resolve_user_by_id(parent, info, id):
        return get_user_model.objects.get(id=id)
