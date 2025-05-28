from account.models import User


class UserService:
    """Service class for user-related business logic."""

    @staticmethod
    def register_user(email: str, password: str, user_type: str) -> User:
        """
        Register a new user.

        Args:
            email (str): The user's email address.
            password (str): The user's password.
            user_type (str): The type of user ('customer' or 'merchant').

        Returns:
            User: The created user instance.
        """
        user = User.objects.create_user(
            email=email,
            password=password,
            user_type=user_type
        )
        return user
