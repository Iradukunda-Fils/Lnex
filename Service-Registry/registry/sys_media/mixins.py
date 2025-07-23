from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .abstract import ImageFile, VideoFile, DocumentFile

class VideoAdminMixin:
    search_fields = ('title', 'original_filename', 'description', 'checksum')
    list_filter = ('is_public', 'created_at', 'content_type')
    ordering = ('-created_at',)
    readonly_fields = (
        'video_preview',
        'created_at',
        'updated_at',
        'checksum',
        'file_size',
        'content_type',
        'slug',
    )

    

    def human_readable_size(self, obj):
        """Displays human-readable file size."""
        if obj.file_size:
            return obj.get_file_size
        return _("Unknown")
    human_readable_size.short_description = _('File Size')  

    def video_preview(self, obj):
        if obj.pk and obj.file and obj.content_type and obj.content_type.startswith('video/'):
            return format_html(
                '<video width="320" height="240" controls>'
                '<source src="{}" type="{}">'
                '</video>',
                obj.file.url, obj.content_type
            )
        return format_html('<p style="color: gray;">{}</p>', _("Upload the video to preview it."))
    video_preview.short_description = _('Video Preview')


class DocumentAdminMixin:
    search_fields = ('title', 'original_filename', 'description', 'checksum', 'page_count')
    list_filter = ('is_public', 'created_at', 'content_type')
    ordering = ('-created_at',)
    readonly_fields = (
        'document_preview',
        'created_at',
        'updated_at',
        'checksum',
        'file_size',
        'content_type',
        'page_count',
        'slug',
    )

    def human_readable_size(self, obj):
        """Displays human-readable file size."""
        if obj.file_size:
            return obj.get_file_size
        return _("Unknown")
    human_readable_size.short_description = _('File Size')

    def document_preview(self, obj):
        if obj.pk and obj.file and obj.content_type:
            if obj.content_type == 'application/pdf':
                # Embedded PDF preview
                return format_html(
                    '<iframe src="{}" width="100%" height="500px" style="border:1px solid #ccc;"></iframe>',
                    obj.file.url
                )
            else:
                # Download link for other documents (Word, Excel, etc.)
                return format_html(
                    '<a href="{}" target="_blank" style="color: blue;">{}</a>',
                    obj.file.url,
                    _("Download Document")
                )
        return format_html('<p style="color: gray;">{}</p>', _("Upload the document to preview it."))
    document_preview.short_description = _('Document Preview')


class ImageAdminMixin:
    search_fields = ('title', 'original_filename', 'description', 'checksum', 'width', 'file_preview')
    list_filter = ('is_public', 'created_at', 'content_type')
    ordering = ('-created_at',)
    readonly_fields = (
        'created_at',
        'updated_at',
        'checksum',
        'file_size',
        'content_type',
        'height',
        'width',
        'slug',
        'file_preview',
    )

    def human_readable_size(self, obj: ImageFile):
        """Displays human-readable file size."""
        if obj.file_size:
            return obj.get_file_size
        return _("Unknown")
    human_readable_size.short_description = _('File Size')

    def is_image_preview(self, obj):
        """Shows a thumbnail preview if the file is an image."""
        if obj.content_type and obj.content_type.startswith('image/'):
            return format_html(
                '<img src="{}" width="60" height="30" style="object-fit: cover; border: 1px solid #ccc;" />',
                obj.file.url
            )
        return "-"
    is_image_preview.short_description = _('Preview')

    def file_preview(self, obj: ImageFile):
        """Large preview for detail view."""
        if obj.content_type and obj.content_type.startswith('image/'):
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 100%; object-fit: contain; border: 1px solid #ccc;" />',
                obj.file.url
            )
        return _("No preview available")
    file_preview.short_description = _('File Preview')