from graphene import (
    ID,
    Boolean,
    DateTime,
    Decimal,
    InputObjectType,
    List,
    Scalar,
    String,
)


class AffairCreationInput(InputObjectType):
    """
    Input class for Affair creation.
    """

    description = String(required=True)
    tags = List(ID)
    creation_date = DateTime()
    modification_date = DateTime()


class AffairUpdateInput(InputObjectType):
    """
    Input class for Affair update.
    """

    id = ID(required=True)
    description = String()
    tags = List(ID)


class EventCreationInput(InputObjectType):
    """
    Input class for Event creation.
    """

    name = String(required=True)
    affair = ID(required=True)
    description = String(required=True)
    rules = String()
    creation_date = DateTime()
    modification_date = DateTime()
    expiration_date = DateTime(required=True)
    active = Boolean()
    completed = Boolean()


class EventUpdateInput(InputObjectType):
    """
    Input class for Event update.
    """

    id = ID(required=True)
    name = String()
    description = String()
    rules = String()
    creation_date = DateTime()
    modification_date = DateTime()
    expiration_date = DateTime()
    active = Boolean()
    completed = Boolean()


class QuotaCreationInput(InputObjectType):
    """
    Input class for Quota creation.
    """

    probability = Decimal(required=True)
    expiration_date = DateTime(required=True)
    event = ID(required=True)
    active = Boolean()


class QuotaUpdateInput(InputObjectType):
    """
    Input class for Quota update.
    """

    id = ID()
    expiration_date = DateTime()
    active = Boolean()
