from django.db import models
import os
import logging
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from typing import List, Optional
from django_extensions.db.fields import AutoSlugField
from utils.slug_fields import MediaSlug
from .helper import get_file_upload_path
from utils.files.process_file import FileProcessor, DocumentPageCounter
from django.core.files.storage import default_storage
import io
from PIL import Image
from utils.sys_mixins.media import AutoDeleteFileMixin

logger = logging.getLogger('models')

class AbstractFileModel(AutoDeleteFileMixin, models.Model):
    """
    Abstract base model providing a unified structure for handling file uploads
    across different file types (e.g., images, documents, videos, audios).

    Common functionalities include:
    - Metadata extraction (file size, MIME type, checksum)
    - File integrity support via SHA-256 checksum
    - Public/private access flag
    - Slug generation for URL-friendly identifiers
    - File deletion from both database and storage

    Fields:
        file (FileField): The actual uploaded file.
        original_filename (CharField): Original name of the file from the client.
        title (CharField): Descriptive title of the file.
        description (TextField): Optional textual description.
        file_size (BigIntegerField): Size of the file in bytes.
        content_type (CharField): MIME type of the file.
        checksum (CharField): SHA-256 hash to validate file integrity.
        created_at (DateTimeField): Timestamp of file creation.
        updated_at (DateTimeField): Timestamp of last update.
        is_public (BooleanField): Visibility flag for public access.
        slug (AutoSlugField): Unique slug for reference in URLs.

    Abstract: True
    """
    
    file = models.FileField(
        _('File'),
        upload_to=get_file_upload_path,
        max_length=255,
        help_text=_('Uploaded file')    
    )
        
    original_filename = models.CharField(
        _('Original filename'),
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text=_('Original name of the uploaded file')
    )
    
    title = models.CharField(
        _('Title'),
        max_length=255,
        db_index=True,
        help_text=_('Title for the file')
    )
    
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True,
        db_index=True,
        help_text=_('Description of the file')
    )
    
    file_size = models.BigIntegerField(
        _('File size'),
        blank=True,
        null=True,
        editable=False,
        db_index=True,
        help_text=_('Size of the file in bytes')
    )
    
    content_type = models.CharField(
        _('Content type'),
        max_length=255,
        blank=True,
        editable=False,
        db_index=True,
        help_text=_('MIME type of the file')
    )
    
    checksum = models.CharField(
        _('Checksum'),
        max_length=64,
        blank=True,
        editable=False,
        db_index=True,
        help_text=_('SHA-256 checksum of the file for integrity verification')
    )
    
    created_at = models.DateTimeField(
        _('Created at'),
        auto_now_add=True,
        db_index=True,
        help_text=_('Timestamp when the file was uploaded')
    )
    
    updated_at = models.DateTimeField(
        _('Updated at'),
        auto_now=True,
        db_index=True,
        help_text=_('Timestamp when the file record was last updated')
    )
    
    is_public = models.BooleanField(
        _('Is public'),
        default=False,
        db_index=True,
        help_text=_('Whether the file is publicly accessible')
    )
    
    slug = AutoSlugField(
        populate_from=MediaSlug.get_slug,
        unique=True,
        slugify_function=MediaSlug.slug_method
    )
    
        
    class Meta:
        abstract: bool = True
        verbose_name: str = _('File')
        verbose_name_plural: str = _('Files')
        ordering: List[str] = ['-created_at']
    
    def __str__(self):
        """
        Returns a string representation of the file using the title,
        original filename, or path as fallback.
        """
        return self.title or self.original_filename or str(self.file)
    
    def save(self, *args, **kwargs):
        """
        Custom save method that handles:
        - Capturing original filename
        - Extracting file metadata (size, content type, checksum)
        """
        # Capture original filename
        if not self.original_filename and hasattr(self.file, 'name'):
            self.original_filename = os.path.basename(self.file.name)
            
        self.delete_old_file_on_change('file')  # ← this is your custom helper
        
        # Initial save
        super().save(*args, **kwargs)
        
        update_fields = kwargs.get('update_fields', [])
        if not self.checksum or 'file' in update_fields:

            metadata = FileProcessor(self.file).get_metadata()

            self.content_type = metadata.get("mime_type", self.content_type)
            self.checksum = metadata.get("checksum", self.checksum)
            self.file_size = metadata.get("size", self.file_size)

            update_fields = list(set(update_fields + [
                "content_type", "checksum", "file_size", 
            ]))
        
        if update_fields:
            # Final save if needed
            kwargs["update_fields"] = update_fields
            super().save(*args, **kwargs)
    
    @property
    def get_extension(self) -> str:
        """
        Returns:
            str: File extension (lowercase, without dot), or empty string.
        """
        name = self.file.name
        return os.path.splitext(name)[1][1:].lower() if '.' in name else ''
    
    @property
    def get_file_size(self) -> str:
        """
        Returns:
            str: Human-readable file size (e.g., 2 MB).
        """
        if not self.file_size:
            return '0 B'
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024 or unit == 'TB':
                return f"{size:.2f} {unit}".replace('.00', '')
            size /= 1024
    
    def get_absolute_url(self):
        """
        This method must be implemented in subclasses to provide
        the URL where the file can be accessed.

        Raises:
            NotImplementedError: If called on base class.
        """
        raise NotImplementedError("get_absolute_url must be implemented in a subclass")
    
    def delete(self, *args, **kwargs):
        """
        Deletes both the model instance and its file from storage.
        """
        # Store the file path
        self.delete_file('file')
        
        # Delete the model instance
        super().delete(*args, **kwargs)


class ImageFile(AbstractFileModel):
    """
    Model for storing image files, inheriting metadata and logic from
    AbstractFileModel. Includes image-specific properties such as width,
    height, and alt text.

    Fields:
        width (PositiveIntegerField): Width of the image in pixels.
        height (PositiveIntegerField): Height of the image in pixels.
        alt_text (CharField): Alternative text for accessibility.
    """
    
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
    
    file = models.ImageField(
        _('Image file'),
        upload_to=get_file_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        max_length=255,
        blank=True,
        help_text=_('Uploaded image file')
    )
    
    width = models.PositiveIntegerField(
        _('Width'),
        blank=True,
        null=True,
        editable=False,
        db_index=True,
        help_text=_('Width of the image in pixels')
    )
    
    height = models.PositiveIntegerField(
        _('Height'),
        blank=True,
        null=True,
        editable=False,
        db_index=True,
        help_text=_('Height of the image in pixels')
    )
    
    alt_text = models.CharField(
        _('Alt text'),
        max_length=255,
        blank=True,
        null=True,
        db_index=True,
        help_text=_('Alternative text for accessibility')
    )
    
    class Meta(AbstractFileModel.Meta):
        abstract: bool = True
        verbose_name: str = _('Image file')
        verbose_name_plural: str = _('Image files')
    
    def save(self, *args, **kwargs):
        """
        Saves the image file and updates width/height after saving,
        if not already set.
        """
        super().save(*args, **kwargs)
        
        # Update image dimensions if not set
        update_fields = []
        if (self.width is None or self.height is None) and self.file:
            try:
                with default_storage.open(self.file.name) as file_content:
                    f = file_content.read() 
                    img = Image.open(io.BytesIO(f))
                    self.width, self.height = img.size
                    update_fields.extend(['width', 'height'])
            except (ImportError, OSError, AttributeError, Exception):
                pass
        
        if update_fields:
            super().save(update_fields=update_fields)


class DocumentFile(AbstractFileModel):
    """
    Model for document uploads such as PDFs, DOCs, and spreadsheets.

    Fields:
        page_count (PositiveIntegerField): Optional number of pages.
    """
    
    ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'rtf', 'odt']
    
    file = models.FileField(
        _('Document file'),
        upload_to=get_file_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        max_length=255,
        help_text=_('Uploaded document file')
    )
    
    page_count = models.PositiveIntegerField(
        _('Page count'),
        blank=True,
        null=True,
        editable=False,
        db_index=True,
        help_text=_('Number of pages in the document')
    )
    
    def save(self, *args, **kwargs) -> None:
        # Check if the object is being created for the first time
        # is_new = self._state.adding
    
        # Save the file first so it's available in storage for reading
        super().save(*args, **kwargs)
        
        pages = DocumentPageCounter(self.file).count_pages()
        if pages is not None:
           self.page_count = pages  
        else: self.page_count = 1
        # Save only the updated field to avoid triggering full update
        super().save(update_fields=['page_count'])
            
    
    class Meta(AbstractFileModel.Meta):
        abstract: bool = True
        verbose_name: str = _('Document file')
        verbose_name_plural: str = _('Document files')
    
        


class VideoFile(AbstractFileModel):
    """
    Model for uploading video content with additional fields for
    duration and an optional thumbnail.

    Fields:
        duration (PositiveIntegerField): Video duration in seconds.
        thumbnail (ImageField): Optional preview image.
    """
    
    ALLOWED_EXTENSIONS = ['mp4', 'webm', 'mov', 'avi', 'mkv']
    
    file = models.FileField(
        _('Video file'),
        upload_to=get_file_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        max_length=255,
        help_text=_('Uploaded video file')
    )
    
    duration = models.PositiveIntegerField(
        _('Duration'),
        blank=True,
        null=True,
        editable=False,
        db_index=True,
        help_text=_('Duration of the video in seconds')
    )
    
    thumbnail = models.ImageField(
        _('Thumbnail'),
        upload_to=get_file_upload_path,
        blank=True,
        null=True,
        help_text=_('Thumbnail image for the video')
    )
    
    class Meta(AbstractFileModel.Meta):
        abstract: bool = True
        verbose_name = _('Video file')
        verbose_name_plural = _('Video files')


class AudioFile(AbstractFileModel):
    """
    Model for uploading audio files. Provides fields for duration
    and inherits metadata functionality from the base class.

    Fields:
        duration (PositiveIntegerField): Duration in seconds.
    """
    
    ALLOWED_EXTENSIONS = ['mp3', 'wav', 'ogg', 'flac', 'm4a']
    
    file = models.FileField(
        _('Audio file'),
        upload_to=get_file_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        max_length=255,
        help_text=_('Uploaded audio file')
    )
    
    duration = models.PositiveIntegerField(
        _('Duration'),
        blank=True,
        null=True,
        editable=False,
        db_index=True,
        help_text=_('Duration of the audio in seconds')
    )
    
    class Meta(AbstractFileModel.Meta):
        abstract: bool = True
        verbose_name: str = _('Audio file')
        verbose_name_plural: str = _('Audio files')
        
    