from django.db.models.signals import (
    pre_save, post_save, pre_delete, post_delete
)
from django.dispatch import receiver
from django.contrib.auth import get_user_model  # Get the custom user model if using one

User = get_user_model()


