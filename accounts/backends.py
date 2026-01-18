from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend which allows users to authenticate using either their
    username or email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # If the login form uses 'username' field for the input (which is standard),
        # the value will come in as 'username'.
        # We try to look up the user by username OR email.
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        if not username:
            return None

        try:
            # Check if the inputs is an email or username
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # This shouldn't happen if email and username are unique, but just in case
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
