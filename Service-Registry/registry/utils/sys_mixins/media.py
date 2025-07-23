from django.core.files.storage import default_storage
from django.db import models

class AutoDeleteFileMixin:
    """
    Mixin to automatically delete a file when it is replaced or the object is deleted.
    And it is specific only on the models specifically on the media files.
    """

    def delete_old_file_on_change(self, field_name: str):
        """
        Deletes the old file from storage if a new file is uploaded.
        """
        if not self.pk:
            return  # Object is not saved yet, no need to check
        
        try:
            old_instance = self.__class__.objects.get(pk=self.pk)
        except self.__class__.DoesNotExist:
            return  # New object, nothing to compare
        
        old_file = getattr(old_instance, field_name, None)
        new_file = getattr(self, field_name, None)

        if not old_file or not old_file.name:
            return  # No old file to delete

        if old_file.name != getattr(new_file, 'name', None):
            self._delete_file_safely(old_file)

    def delete_file(self, field_name: str):
        """
        Deletes a specific file from the instance.
        """
        file = getattr(self, field_name, None)
        if file and getattr(file, 'name', None):
            self._delete_file_safely(file)


    def _delete_file_safely(self, file: models.FileField):
        """
        Deletes the file from storage, handling common exceptions.
        """
        try:
            if default_storage.exists(file.name):
                default_storage.delete(file.name)
        except Exception as e:
            # Log this in real-world apps instead of printing
            print(f"[Warning] Could not delete file '{file.name}': {e}")

        
