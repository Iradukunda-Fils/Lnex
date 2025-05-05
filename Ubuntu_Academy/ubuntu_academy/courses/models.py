from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from utils.slug_fields import (
    CourseSlug, CategorySlug, 
    ModuleSlug, LessonSlug
)

User = get_user_model()

class Category(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True, 
        db_index=True
        )
    slug = AutoSlugField(
        populate_from=CategorySlug.get_slug,
        unique=True,
        slugify_function=CategorySlug.slug_method  # Custom slugify function
    )
    description = models.TextField(
        blank=True, 
        db_index=True
        )
    icon = models.ImageField(upload_to='category_icon/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(
        auto_now_add=True,                
        db_index=True
        )

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_category_name'),
            models.UniqueConstraint(fields=['slug'], name='unique_category_slug'),
        ]
        indexes = [
            models.Index(fields=['is_active'], name='idx_category_is_active'),
        ]

    def __str__(self):
        return self.name
    
    @property
    def get_courses(self):
        return self.courses.all()
    


class Course(models.Model):

    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )

    LANGUAGE_CHOICES = (
        ('en', _('🇺🇸 English')),
        ('es', _('🇪🇸 Spanish')),
        ('fr', _('🇫🇷 French')),
        ('rw', _('🇷🇼 Kinyarwanda')),
    )

    title = models.CharField(
        max_length=255, 
        )
    slug = AutoSlugField(
        populate_from=CourseSlug.get_slug,
        unique=True,
        slugify_function=CourseSlug.slug_method  # Custom slugify function
    )   

    category = models.ForeignKey('courses.Category', on_delete=models.SET_NULL, null=True, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')

    short_description = models.CharField(
        max_length=300,
        db_index=True
        )
    description = models.TextField(
        db_index=True
        )

    price = models.DecimalField(
        max_digits=10, decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        default=0.00
        )
    is_free = models.BooleanField(default=False)

    level = models.CharField(
        max_length=20, 
        choices=LEVEL_CHOICES, 
        default='beginner',
        )
    language = models.CharField(
        max_length=10, 
        choices=LANGUAGE_CHOICES, 
        default='en'
        )

    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True
        )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_index=True
        )

    duration = models.DurationField(help_text="Total length of course (HH:MM:SS)", null=True, blank=True)

    is_featured = models.BooleanField(
        _("Whether the course is featured."), 
        default=False,
        db_index=True
        )

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        ordering = ['-created_at', '-updated_at']
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='unique_course_slug'),
            models.UniqueConstraint(fields=['title', 'instructor'], name='unique_course_title_per_instructor'),
            models.UniqueConstraint(fields=['title', 'category', 'instructor'], name='unique_course_title_category_instructor'),
        ]
        indexes = [
            models.Index(fields=['title'], name='idx_course_title'),
            models.Index(fields=['price'], name='idx_course_price'),
            models.Index(fields=['is_free'], name='idx_course_is_free'),
            models.Index(fields=['level'], name='idx_course_level'),
            models.Index(fields=['language'], name='idx_course_language'),
            models.Index(fields=['is_published'], name='idx_course_is_published'),
            models.Index(fields=['published_at'], name='idx_course_published_at'),
        ]

    def __str__(self):
        return self.title

    @property
    def is_paid(self):
        return self.price > 0

    @property
    def get_video_intro(self):
        return self.videointro.all()
    
    @property
    def get_documents(self):
        return self.documents.all()
    
    @property
    def get_thumbnails(self):
        return self.thumbnails.all()
    
    @property
    def get_tags(self):
        return self.targs.values_list('tags', flat=True)
    
    # def publish(self):
    #     if self.published_at <= now():
    #         self.is_published = True
    #         self.save()


class Tag(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name
    



class Module(models.Model):
    slug = AutoSlugField(
        populate_from=ModuleSlug.get_slug,
        unique=True,
        slugify_function=ModuleSlug.slug_method  # Custom slugify function
    )   
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(
        default=False, 
        db_index=True
        )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
        )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Course Module")
        verbose_name_plural = _("Course Modules")
        constraints = [
            models.UniqueConstraint(fields=['course', 'slug'], name='unique_module_course_slug'),
            models.UniqueConstraint(fields=['course', 'order'], name='unique_module_course_order')
        ]
        indexes = [
            models.Index(fields=['course', 'slug']),
            models.Index(fields=['course', 'order']),
        ]
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"    
    
    @property
    def get_thumbnails(self):
        self.thumbnails.all()

    @property
    def get_videos(self):
        self.videos.all()

    @property
    def get_thumbnails(self):
        self.get_document.all()
    

class Lesson(models.Model):
    slug = AutoSlugField(
        populate_from=LessonSlug.get_slug,
        unique=True,
        slugify_function=LessonSlug.slug_method  # Custom slugify function
    )   
    module = models.ForeignKey('courses.Module', on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    
    duration = models.DurationField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    is_preview = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Course Module Lesson")
        verbose_name_plural = _("Course Module Lessons")
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['module', 'slug'], name='unique_lesson_module_slug'),
            models.UniqueConstraint(fields=['module', 'order'], name='unique_lesson_module_order'),
        ]
        indexes = [
            models.Index(fields=['module', 'slug']),
            models.Index(fields=['module', 'order']),
            models.Index(fields=['is_preview', 'is_published']),
        ]

    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    @property
    def get_images(self):
        return self.images.all()
    
    @property
    def get_documents(self):
        return self.documents.all()
    
    @property
    def get_videos(self):
        return self.videos.all()





