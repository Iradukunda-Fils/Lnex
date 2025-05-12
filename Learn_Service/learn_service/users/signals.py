from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from .models import Profile
from django.core.files.storage import default_storage

@receiver(pre_delete, sender=Profile)
def auto_delete_profile_picture_on_delete(sender, instance, **kwargs):
    if default_storage.exists(instance.profile_picture.name) and instance.profile_picture.name != "user_profile/default.png":
        default_storage.delete(instance.profile_picture.name)