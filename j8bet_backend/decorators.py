from graphql_jwt.decorators import user_passes_test
from j8bet_backend.constants import BET_MANAGER

# The following decorators will remain commented until they're used
# and thus been able to be included in unit testing.

# application_manager = user_passes_test(
#     lambda u: u.is_authenticated and
#         u.groups.filter(name=APPLICATION_MANAGER).exists()
# )

bet_consumer = user_passes_test(
    lambda u: u.is_authenticated and
        u.groups.filter(name=BET_CONSUMER).exists()
)

bet_manager = user_passes_test(
    lambda u: u.is_authenticated and u.groups.filter(name=BET_MANAGER).exists()
)

# is_manager = user_passes_test(
#     lambda u: u.is_authenticated and
#         u.groups.filter(name__in=MANAGER_GROUPS).exists()
# )
