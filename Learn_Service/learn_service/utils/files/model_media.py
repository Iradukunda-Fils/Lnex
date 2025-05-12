# # models.py

# from django.db import models
# import os
# from django.conf import settings
# import logging
# from django.utils.translation import gettext_lazy as _
# from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
# from typing import List, Optional, Dict, Any, Union, Tuple, ClassVar
# from django_extensions.db.fields import AutoSlugField
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.cache import cache
# from django.utils.functional import cached_property

# from utils.slug_fields import MediaSlug
# from .helper import get_file_upload_path
# from utils.sys_mixins.media import AutoDeleteFileMixin
# from utils.media.processors import VideoProcessor, AudioProcessor

# logger = logging.getLogger('models')


# class AbstractFileModel(AutoDeleteFileMixin, models.Model):
#     """
#     Abstract base model providing a unified structure for handling file uploads
#     across different file types (e.g., images, documents, videos, audios).

#     Common functionalities include:
#     - Metadata extraction (file size, MIME type, checksum)
#     - File integrity support via SHA-256 checksum
#     - Public/private access flag
#     - Slug generation for URL-friendly identifiers
#     - File deletion from both database and storage
#     """
    
#     file = models.FileField(
#         _('File'),
#         upload_to=get_file_upload_path,
#         max_length=255,
#         help_text=_('Uploaded file')    
#     )
        
#     original_filename = models.CharField(
#         _('Original filename'),
#         max_length=255,
#         blank=True,
#         null=True,
#         db_index=True,
#         help_text=_('Original name of the uploaded file')
#     )
    
#     title = models.CharField(
#         _('Title'),
#         max_length=255,
#         db_index=True,
#         help_text=_('Title for the file')
#     )
    
#     description = models.TextField(
#         _('Description'),
#         blank=True,
#         null=True,
#         help_text=_('Description of the file')
#     )
    
#     file_size = models.BigIntegerField(
#         _('File size'),
#         blank=True,
#         null=True,
#         editable=False,
#         db_index=True,
#         help_text=_('Size of the file in bytes')
#     )
    
#     content_type = models.CharField(
#         _('Content type'),
#         max_length=255,
#         blank=True,
#         editable=False,
#         db_index=True,
#         help_text=_('MIME type of the file')
#     )
    
#     checksum = models.CharField(
#         _('Checksum'),
#         max_length=64,
#         blank=True,
#         editable=False,
#         db_index=True,
#         help_text=_('SHA-256 checksum of the file for integrity verification')
#     )
    
#     created_at = models.DateTimeField(
#         _('Created at'),
#         auto_now_add=True,
#         db_index=True,
#         help_text=_('Timestamp when the file was uploaded')
#     )
    
#     updated_at = models.DateTimeField(
#         _('Updated at'),
#         auto_now=True,
#         db_index=True,
#         help_text=_('Timestamp when the file record was last updated')
#     )
    
#     is_public = models.BooleanField(
#         _('Is public'),
#         default=False,
#         db_index=True,
#         help_text=_('Whether the file is publicly accessible')
#     )
    
#     slug = AutoSlugField(
#         populate_from=MediaSlug.get_slug,
#         unique=True,
#         slugify_function=MediaSlug.slug_method
#     )
    
#     class Meta:
#         abstract = True
#         verbose_name = _('File')
#         verbose_name_plural = _('Files')
#         ordering = ['-created_at']
    
#     def __str__(self) -> str:
#         """
#         Returns a string representation of the file using the title,
#         original filename, or path as fallback.
#         """
#         return self.title or self.original_filename or str(self.file)
    
#     def save(self, *args: Any, **kwargs: Any) -> None:
#         """
#         Custom save method that handles:
#         - Capturing original filename
#         - Extracting file metadata (size, content type, checksum)
#         """
#         # Capture original filename
#         if not self.original_filename and hasattr(self.file, 'name'):
#             self.original_filename = os.path.basename(self.file.name)
            
#         self.delete_old_file_on_change('file')
        
#         # Initial save
#         super().save(*args, **kwargs)
        
#         update_fields = kwargs.get('update_fields', [])
#         if not self.checksum or 'file' in update_fields:
#             from utils.files.process_file import FileProcessor
#             metadata = FileProcessor(self.file).get_metadata()

#             self.content_type = metadata.get("mime_type", self.content_type)
#             self.checksum = metadata.get("checksum", self.checksum)
#             self.file_size = metadata.get("size", self.file_size)

#             update_fields = list(set(update_fields + [
#                 "content_type", "checksum", "file_size", 
#             ]))
        
#         if update_fields:
#             # Final save if needed
#             kwargs["update_fields"] = update_fields
#             super().save(*args, **kwargs)
    
#     @property
#     def get_extension(self) -> str:
#         """
#         Returns:
#             str: File extension (lowercase, without dot), or empty string.
#         """
#         name = self.file.name
#         return os.path.splitext(name)[1][1:].lower() if '.' in name else ''
    
#     @property
#     def get_file_size(self) -> str:
#         """
#         Returns:
#             str: Human-readable file size (e.g., 2 MB).
#         """
#         if not self.file_size:
#             return '0 B'
        
#         size = self.file_size
#         for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
#             if size < 1024 or unit == 'TB':
#                 return f"{size:.2f} {unit}".replace('.00', '')
#             size /= 1024
    
#     def get_absolute_url(self) -> str:
#         """
#         This method must be implemented in subclasses to provide
#         the URL where the file can be accessed.

#         Raises:
#             NotImplementedError: If called on base class.
#         """
#         raise NotImplementedError("get_absolute_url must be implemented in a subclass")
    
#     def delete(self, *args: Any, **kwargs: Any) -> Tuple[int, Dict[str, int]]:
#         """
#         Deletes both the model instance and its file from storage.
#         """
#         # Store the file path
#         self.delete_file('file')
        
#         # Delete the model instance
#         return super().delete(*args, **kwargs)


# class VideoFile(AbstractFileModel):
#     """
#     Enhanced model for video content with metadata and playback options.
#     Processing logic is delegated to the VideoProcessor service class.
    
#     Features:
#     - Complete video metadata tracking (duration, resolution, codec, bitrate)
#     - Automatic thumbnail generation with customizable timestamps
#     - Video playback preferences (autoplay, loop, mute)
#     - Streaming optimization flags
#     - Accessibility features like captions and transcripts
#     """
    
#     ALLOWED_EXTENSIONS: ClassVar[List[str]] = ['mp4', 'webm', 'mov', 'avi', 'mkv', 'flv', 'm4v']
#     MAX_DURATION: ClassVar[int] = 7200  # Maximum 2 hours (in seconds)
#     MAX_RESOLUTION: ClassVar[int] = 7680  # Maximum 8K resolution
    
#     file = models.FileField(
#         _('Video file'),
#         upload_to=get_file_upload_path,
#         validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
#         max_length=255,
#         help_text=_('Uploaded video file (supported formats: mp4, webm, mov, avi, mkv, flv, m4v)')
#     )
    
#     # Video metadata fields
#     duration = models.PositiveIntegerField(
#         _('Duration'),
#         blank=True,
#         null=True,
#         db_index=True,
#         editable=False,
#         validators=[MaxValueValidator(MAX_DURATION)],
#         help_text=_('Duration of the video in seconds')
#     )
    
#     width = models.PositiveIntegerField(
#         _('Width'),
#         blank=True,
#         null=True,
#         db_index=True,
#         editable=False,
#         validators=[MaxValueValidator(MAX_RESOLUTION)],
#         help_text=_('Width of the video in pixels')
#     )
    
#     height = models.PositiveIntegerField(
#         _('Height'),
#         blank=True,
#         null=True,
#         db_index=True,
#         editable=False,
#         validators=[MaxValueValidator(MAX_RESOLUTION)],
#         help_text=_('Height of the video in pixels')
#     )
    
#     framerate = models.FloatField(
#         _('Frame rate'),
#         blank=True,
#         null=True,
#         editable=False,
#         help_text=_('Frames per second')
#     )
    
#     bitrate = models.PositiveIntegerField(
#         _('Bitrate'),
#         blank=True,
#         null=True,
#         editable=False,
#         help_text=_('Video bitrate in kbps')
#     )
    
#     codec = models.CharField(
#         _('Codec'),
#         max_length=100,
#         blank=True,
#         null=True,
#         editable=False,
#         help_text=_('Video codec information')
#     )
    
#     # Thumbnails
#     thumbnail = models.ImageField(
#         _('Thumbnail'),
#         upload_to=get_file_upload_path,
#         blank=True,
#         null=True,
#         help_text=_('Thumbnail image for the video')
#     )
    
#     thumbnail_timestamp = models.FloatField(
#         _('Thumbnail timestamp'),
#         blank=True,
#         null=True,
#         default=0.0,
#         help_text=_('Time position in seconds for thumbnail generation')
#     )
    
#     # Accessibility features
#     captions = models.FileField(
#         _('Captions'),
#         upload_to=get_file_upload_path,
#         blank=True,
#         null=True,
#         validators=[FileExtensionValidator(allowed_extensions=['srt', 'vtt'])],
#         help_text=_('Subtitle/caption file (SRT or VTT format)')
#     )
    
#     transcript = models.TextField(
#         _('Transcript'),
#         blank=True,
#         null=True,
#         help_text=_('Full text transcript of the video content')
#     )
    
#     # Playback preferences
#     autoplay = models.BooleanField(
#         _('Autoplay'),
#         default=False,
#         help_text=_('Whether the video should autoplay when loaded')
#     )
    
#     loop = models.BooleanField(
#         _('Loop'),
#         default=False,
#         help_text=_('Whether the video should loop continuously')
#     )
    
#     mute_default = models.BooleanField(
#         _('Default muted'),
#         default=False,
#         help_text=_('Whether the video should be muted by default')
#     )
    
#     # Technical flags
#     streaming_optimized = models.BooleanField(
#         _('Streaming optimized'),
#         default=False,
#         help_text=_('Whether the video is optimized for streaming (e.g., HLS, DASH)')
#     )
    
#     class Meta(AbstractFileModel.Meta):
#         abstract = True
#         verbose_name = _('Video file')
#         verbose_name_plural = _('Video files')
#         indexes = [
#             models.Index(fields=['duration']),
#             models.Index(fields=['width])]