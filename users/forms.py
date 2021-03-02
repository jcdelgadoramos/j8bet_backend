from django.contrib.auth import get_user_model
from django.forms import ModelForm


class UserForm(ModelForm):
    """
    Form for User model
    """

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "password",
            "email",
        )
