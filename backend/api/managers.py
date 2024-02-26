from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


# Adapted from: https://github.com/veryacademy/YT-Django-Theory-Create-Custom-User-Models-Admin-Testing/blob/master/users/models.py
# Accessed 2024-02-22
class CustomAuthorManager(BaseUserManager):
    def create_user(self, email, display_name, password=None, **other_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))

        user = self.model(
            email=self.normalize_email(email),
            display_name=display_name,
            **other_fields
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, display_name, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        user = self.create_user(
            email,
            display_name=display_name,
            password=password,
            **other_fields
        )
        user.is_admin = True
        user.save()
        return user
