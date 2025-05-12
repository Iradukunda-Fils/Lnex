import os
from django.utils import timezone
from django.db import models
import uuid


def get_file_upload_path(
    instance: models.Model,  # Or your custom AbstractFileModel type
    filename: str
) -> str:
    """
    Generates a unique path for uploaded files.
    Format: uploads/<model_name>/<year>/<month>/<unique_id>
    """
    
    # Get model name in lowercase for folder structure
    model_name = instance._meta.model_name  # type: ignore (Django model-specific attribute)
    now = timezone.now()
    
    return os.path.join(
        'uploads',
        model_name,
        str(now.year),
        str(now.month),
        f"{uuid.uuid4()}_{filename}"
    )