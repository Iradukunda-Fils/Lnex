from django.db import models
from .abstract import ImageFile, DocumentFile, VideoFile, AudioFile
from django.utils.translation import gettext_lazy as _
    

class MetaFile:
    order_by = ('-created_at', '-original_filename', "-file_size")


class CourseThumbnail(ImageFile):
    course = models.ForeignKey(
        'courses.Course', 
        on_delete=models.CASCADE, 
        related_name='thumbnails',
        )
    class Meta(MetaFile):
        app_label = "courses"
        verbose_name = _("Course Thumbnail")
        verbose_name_plural = _("Course Thumbnails")
    def get_absolute_url(self):
        ...
        
class CourseDocument(DocumentFile):
    course = models.ForeignKey(
        'courses.Course', 
        on_delete=models.CASCADE, 
        related_name='documents',
        )
    class Meta(MetaFile):
        app_label = "courses"
        verbose_name = _("Course Document")
        verbose_name_plural = _("Course Documents")
        
    def get_absolute_url(self):
        ...

class CourseVideoIntro(VideoFile):
    course = models.ForeignKey(
        'courses.Course', 
        on_delete=models.CASCADE, 
        related_name='videointro',
        )
    class Meta(MetaFile):
        app_label = "courses"
        verbose_name = _("Course Video Intro")
        verbose_name_plural = _("Course Video Intros")
        
    def get_absolute_url(self):
        ...


class ModuleThumbnail(ImageFile):
    module = models.ForeignKey(
        'courses.Module', 
        on_delete=models.CASCADE, 
        related_name='thumbnails',
        )
    class Meta(MetaFile):
        app_label = "courses"
        verbose_name = _("Module Thumbnail")
        verbose_name_plural = _("Module Thumbnails")
    def get_absolute_url(self):
        ...

class ModuleVideoIntro(VideoFile):
    module = models.ForeignKey(
        'courses.Module', 
        on_delete=models.CASCADE, 
        related_name='video_intro',
        )
    class Meta(MetaFile):
        app_label = "courses"
        verbose_name = _("Module Video Intro")
        verbose_name_plural = _("Module Video Intro")
    def get_absolute_url(self):
        ...

class ModuleDocument(DocumentFile):
    module = models.ForeignKey(
        'courses.Module', 
        on_delete=models.CASCADE, 
        related_name='documents',
        )
    class Meta(MetaFile):
        app_label = "courses"
        verbose_name = _("Module Document Intro")
        verbose_name_plural = _("Module Document Intro")
    def get_absolute_url(self):
        ...



class ModuleImageLesson(ImageFile):
    lesson = models.ForeignKey(
        'courses.Lesson', 
        on_delete=models.CASCADE, 
        related_name='images',
        )
    class Meta(MetaFile):
        app_label = "courses"
        verbose_name = _("Module Lesson image")
        verbose_name_plural = _("Module Lesson images")
    def get_absolute_url(self):
        ...
        
class ModuleDocumentLesson(DocumentFile):
    lesson = models.ForeignKey(
        'courses.Lesson', 
        on_delete=models.CASCADE, 
        related_name='documents',
        )
    class Meta(MetaFile):
        app_label = "courses"
        verbose_name = _("Module Lesson Document")
        verbose_name_plural = _("Module Lesson Documents")
        
    def get_absolute_url(self):
        ...

class ModuleVideoLesson(VideoFile):
    lesson = models.ForeignKey(
        'courses.Lesson', 
        on_delete=models.CASCADE, 
        related_name='videos',
        )
    class Meta(MetaFile):
        app_label = "courses"
        verbose_name = _("Module Lesson Video")
        verbose_name_plural = _("Module Lesson videos")
        
    def get_absolute_url(self):
        ...