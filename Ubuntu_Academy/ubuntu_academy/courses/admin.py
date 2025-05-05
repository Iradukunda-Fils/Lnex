from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import *
from django.urls import reverse
from django.utils import timezone
from sys_media.courses import *
from sys_media.mixins import (
    VideoAdminMixin, 
    DocumentAdminMixin, 
    ImageAdminMixin
    )



@admin.register(CourseThumbnail)
class CourseThumbnaileAdmin(ImageAdminMixin, admin.ModelAdmin):
    list_display = (
        'course__title',
        'title',
        'original_filename',
        'human_readable_size',
        'content_type',
        'slug',
        "width",
        'height',
        'created_at',
        'is_public',
        'is_image_preview',
    )

    fieldsets = (
        (_('File Info'), {
            'fields': (
                'course',
                'file',
                'file_preview',
                'original_filename',
                'title',
                'description',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'content_type',
                'file_size',
                'checksum',
                'height',
                'width',
                'slug',
            )
        }),
        (_('Visibility & Tracking'), {
            'fields': (
                'is_public',
                'created_at',
                'updated_at',
            )
        }),
    )
    
@admin.register(CourseDocument)
class CourseDocumentAdmin(DocumentAdminMixin, admin.ModelAdmin):
    list_display = (
        'course__title',
        'title',
        'original_filename',
        'human_readable_size',
        'content_type',
        'slug',
        'page_count',
        'created_at',
        'is_public',
    )    
    fieldsets = (
        (_('File Info'), {
            'fields': (
                'course',
                'file',
                'document_preview',
                'original_filename',
                'title',
                'description',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'content_type',
                'file_size',
                'checksum',
                'page_count',
                'slug',
            )
        }),
        (_('Visibility & Tracking'), {
            'fields': (
                'is_public',
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(CourseVideoIntro)
class CourseVideoIntroAdmin(VideoAdminMixin, admin.ModelAdmin):
    list_display = (
        'course__title',
        'title',
        'original_filename',
        'human_readable_size',
        'content_type',
        'slug',
        'created_at',
        'is_public',
    )

    fieldsets = (
        (_('File Info'), {
            'fields': (
                'course',
                'file',
                'video_preview',
                'original_filename',
                'title',
                'description',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'content_type',
                'file_size',
                'checksum',
                'slug',
            )
        }),
        (_('Visibility & Tracking'), {
            'fields': (
                'is_public',
                'created_at',
                'updated_at',
            )
        }),
    )



@admin.register(ModuleThumbnail)
class ModuleThumbnailAdmin(ImageAdminMixin, admin.ModelAdmin):
    list_display = (
        'module__title',
        'title',
        'original_filename',
        'human_readable_size',
        'content_type',
        'slug',
        "width",
        'height',
        'created_at',
        'is_public',
        'is_image_preview',
    )
    

    fieldsets = (
        (_('File Info'), {
            'fields': (
                'module',
                'file',
                'file_preview',
                'original_filename',
                'title',
                'description',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'content_type',
                'file_size',
                'checksum',
                'height',
                'width',
                'slug',
            )
        }),
        (_('Visibility & Tracking'), {
            'fields': (
                'is_public',
                'created_at',
                'updated_at',
            )
        }),
    )


@admin.register(ModuleVideoIntro)
class ModuleVideoIntroAdmin(VideoAdminMixin, admin.ModelAdmin):
    list_display = (
        'module__title',
        'title',
        'original_filename',
        'human_readable_size',
        'content_type',
        'slug',
        'created_at',
        'is_public',
    )

    fieldsets = (
        (_('File Info'), {
            'fields': (
                'module',
                'file',
                'video_preview',
                'original_filename',
                'title',
                'description',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'content_type',
                'file_size',
                'checksum',
                'slug',
            )
        }),
        (_('Visibility & Tracking'), {
            'fields': (
                'is_public',
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(ModuleDocument)
class ModuleDocumentAdmin(DocumentAdminMixin, admin.ModelAdmin):
    list_display = (
        'module__title',
        'title',
        'original_filename',
        'human_readable_size',
        'content_type',
        'slug',
        'created_at',
        'is_public',
    )
    fieldsets = (
        (_('File Info'), {
            'fields': (
                'module',
                'file',
                'document_preview',
                'original_filename',
                'title',
                'description',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'content_type',
                'file_size',
                'checksum',
                'page_count',
                'slug',
            )
        }),
        (_('Visibility & Tracking'), {
            'fields': (
                'is_public',
                'created_at',
                'updated_at',
            )
        }),
    )


@admin.register(ModuleImageLesson)
class ModuleImageLessonAdmin(ImageAdminMixin, admin.ModelAdmin):
    list_display = (
        'lesson__title',
        'title',
        'original_filename',
        'human_readable_size',
        'content_type',
        'slug',
        'created_at',
        'is_public',
    )


    fieldsets = (
        (_('File Info'), {
            'fields': (
                'lesson',
                'file',
                'file_preview',
                'original_filename',
                'title',
                'description',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'content_type',
                'file_size',
                'checksum',
                'height',
                'width',
                'slug',
            )
        }),
        (_('Visibility & Tracking'), {
            'fields': (
                'is_public',
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(ModuleVideoLesson)
class ModuleVideoLessonAdmin(VideoAdminMixin, admin.ModelAdmin):
    list_display = (
        'lesson__title',   # Corrected (custom method)
        'title',
        'original_filename',
        'human_readable_size',
        'content_type',
        'slug',
        'created_at',
        'is_public',
    )

    readonly_fields = (
        'video_preview',   # ← Add it here!
        'created_at',
        'updated_at',
        'checksum',
        'file_size',
        'content_type',
        'slug',
    )

    fieldsets = (
        (_('File Info'), {
            'fields': (
                'lesson',
                'file',
                'video_preview',
                'original_filename',
                'title',
                'description',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'content_type',
                'file_size',
                'checksum',
                'slug',
            )
        }),
        (_('Visibility & Tracking'), {
            'fields': (
                'is_public',
                'created_at',
                'updated_at',
            )
        }),
    )

@admin.register(ModuleDocumentLesson)
class ModuleDocumentLessonAdmin(DocumentAdminMixin, admin.ModelAdmin):
    list_display = (
        'lesson__title',
        'title',
        'original_filename',
        'human_readable_size',
        'content_type',
        'slug',
        'created_at',
        'is_public',
    )

    fieldsets = (
        (_('File Info'), {
            'fields': (
                'lesson',
                'file',
                'document_preview',
                'original_filename',
                'title',
                'description',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'content_type',
                'file_size',
                'checksum',
                'page_count',
                'slug',
            )
        }),
        (_('Visibility & Tracking'), {
            'fields': (
                'is_public',
                'created_at',
                'updated_at',
            )
        }),
    )
    


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',  'is_active', 'created_at', 'course_count')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
    readonly_fields = ('created_at',)
    # prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    def course_count(self, obj):
        # return obj.courses.count()
        ...
    course_count.short_description = 'Courses'





@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title_with_status', 'category_display', 
        'instructor__last_name',
        'level',  'language_flag', "duration_formatted",
        'price_display',
         'created_at'
    )
    list_display_links = ('title_with_status',)
    list_filter = (
        ('is_published', admin.BooleanFieldListFilter),
        ('is_featured', admin.BooleanFieldListFilter),
        ('is_free', admin.BooleanFieldListFilter),
        ('level', admin.ChoicesFieldListFilter),
        ('language', admin.ChoicesFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
    )
    date_hierarchy = 'created_at'
    search_fields = (
        'title', 'short_description', 'description',
        'instructor__first_name', 'instructor__last_name', 'instructor__email',
        'category__name'
    )
    actions = ['publish_selected', 'unpublish_selected', 'feature_selected', 'unfeature_selected']
    fieldsets = (
        (_('Basic Information'), {'fields': ('title', 'slug', 'short_description', 'description')}),
        (_('Classification'), {'fields': ('category', 'instructor', 'level', 'language'), 'classes': ('collapse',)}),
        (_('Pricing'), {'fields': ('price', 'is_free'), 'classes': ('collapse',)}),
        (_('Publication'), {'fields': ('is_published', 'published_at', 'is_featured'), 'classes': ('collapse',)}),
        (_('Metadata'), {'fields': ('duration', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('slug', 'created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('instructor', 'category')

    def title_with_status(self, obj):
        status = '✅' if obj.is_published else '❌'
        featured = '⭐' if obj.is_featured else ''
        return format_html('{} {} {}', status, obj.title, featured)
    title_with_status.short_description = _('Course Title')
    title_with_status.admin_order_field = 'title'

    def instructor_link(self, obj):
        url = reverse("admin:courses_instructor_change", args=[obj.instructor.id])
        return format_html('<a href="{}">{}</a>', url, obj.instructor.name)

    instructor_link.short_description = 'Instructor'  # This is optional, for better column name
    instructor_link.admin_order_field = 'instructor__first_name'

    def category_display(self, obj):
        if obj.category:
            url = reverse(f'admin:{obj.category._meta.app_label}_{obj.category._meta.model_name}_change', args=[obj.category.pk])
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return "-"
    category_display.short_description = _('Category')
    category_display.admin_order_field = 'category__name'

    def level_badge(self, obj):
        colors = {
            'beginner': '#28a745',
            'intermediate': '#007bff',
            'advanced': '#dc3545',
        }
        color = colors.get(obj.level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 7px; border-radius: 3px;">{}</span>',
            color, obj.get_level_display()
        )
    level_badge.short_description = _('Level')
    level_badge.admin_order_field = 'level'

    def price_display(self, obj):
        if obj.is_free:
            return format_html('<span style="color: green;">Free</span>')
        return format_html('${}', obj.price)
    price_display.short_description = _('Price')
    price_display.admin_order_field = 'price'

    def language_flag(self, obj):
        flags = {
            'en': '🇺🇸 English',
            'es': '🇪🇸 Spanish',
            'fr': '🇫🇷 French',
            'rw': '🇷🇼 Kinyarwanda',
        }
        return flags.get(obj.language, obj.get_language_display())
    language_flag.short_description = _('Language')
    language_flag.admin_order_field = 'language'

    def duration_formatted(self, obj):
        if not obj.duration:
            return "-"
        hours, remainder = divmod(obj.duration.total_seconds(), 3600)
        minutes = remainder // 60
        if hours:
            return f"{int(hours)} hr {int(minutes)} min"
        return f"{int(minutes)} min"
    duration_formatted.short_description = _('Duration')
    duration_formatted.admin_order_field = 'duration'

    def publish_selected(self, request, queryset):
        updated = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(request, _(f"{updated} courses were successfully published."))
    publish_selected.short_description = _("Publish selected courses")

    def unpublish_selected(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, _(f"{updated} courses were successfully unpublished."))
    unpublish_selected.short_description = _("Unpublish selected courses")

    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, _(f"{updated} courses were marked as featured."))
    feature_selected.short_description = _("Mark selected courses as featured")

    def unfeature_selected(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, _(f"{updated} courses were unmarked as featured."))
    unfeature_selected.short_description = _("Unmark selected courses as featured")

    def save_model(self, request, obj, form, change):
        if not change and not obj.instructor:
            obj.instructor = request.user
        if 'is_published' in form.changed_data and obj.is_published and not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)




class TagsInline(admin.TabularInline):
    model = Tag
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_link', 'usage_count', 'colored_tag')
    list_display_links = ('name',)
    search_fields = ('name', 'course__title')
    list_filter = ('course__category', 'course__level', 'course__language')
    autocomplete_fields = ('course',)
    
    # Performance optimization
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course').annotate(
            usage_count=Count('id')
        )
    
    def course_link(self, obj):
        """Display a link to the related course"""
        if obj.course:
            url = reverse('admin:courses_course_change', args=[obj.course.slug])
            return format_html('<a href="{}">{}</a>', url, obj.course.title)
        return "-"
    course_link.short_description = _("Course")
    course_link.admin_order_field = 'course__title'
    
    def usage_count(self, obj):
        """Display how many times this tag is used"""
        # This relies on the annotated queryset
        return obj.usage_count
    usage_count.short_description = _("Usage Count")
    usage_count.admin_order_field = 'usage_count'
    
    def colored_tag(self, obj):
        """Display the tag with a colored background"""
        # Create a simple hash of the tag name to get a consistent color
        hash_value = sum(ord(c) for c in obj.name) % 360
        bg_color = f"hsl({hash_value}, 70%, 80%)"
        text_color = "#000"
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; '
            'border-radius: 12px; font-size: 0.9em;">{}</span>',
            bg_color, text_color, obj.name
        )
    colored_tag.short_description = _("Tag Display")
    
    # Custom fieldsets
    fieldsets = (
        (None, {
            'fields': ('name', 'course'),
        }),
    )
    
    # Auto-complete for course field
    autocomplete_fields = ['course']
    
    # Actions
    actions = ['merge_tags', 'copy_tags_to_selected_courses']
    
    def merge_tags(self, request, queryset):
        """Merge selected tags into one"""
        if queryset.count() <= 1:
            self.message_user(request, "You need to select at least two tags to merge", level='error')
            return
            
        # Implementation would merge tags, keeping the first one
        # and updating all relationships to point to it
        primary_tag = queryset.first()
        tag_names = list(queryset.values_list('name', flat=True))
        
        # Display what would be merged
        self.message_user(
            request, 
            f"Would merge tags: {', '.join(tag_names)} into '{primary_tag.name}'"
        )
    merge_tags.short_description = _("Merge selected tags")
    
    def copy_tags_to_selected_courses(self, request, queryset):
        """Copy selected tags to multiple courses"""
        # This would show a form to select target courses
        # Then create new Tag objects with the same names for those courses
        self.message_user(
            request,
            f"Selected {queryset.count()} tags. Use the form below to copy them to other courses."
        )
    copy_tags_to_selected_courses.short_description = _("Copy tags to other courses")
    
    # Inline for Course admin
    class Meta:
        model = Tag


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_published', 'created_at')
    list_filter = ('is_published', 'course')
    search_fields = ('title', 'slug', 'course__title')
    ordering = ('order',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'is_published', 'is_preview', 'order', 'created_at')
    list_filter = ('is_published', 'is_preview', 'created_at', 'module')
    search_fields = ('title', 'module__title', 'slug')
    ordering = ('order',)



# Register Tag as an inline for Course
class TagInline(admin.TabularInline):
    model = Tag
    extra = 1
    fields = ('name',)
    

# Update the CourseAdmin to include TagInline
class CourseAdmin(admin.ModelAdmin):
    # ... existing CourseAdmin code ...
    inlines = [TagInline]
    

# If you already registered Course elsewhere, unregister it first
# admin.site.unregister(Course)
# admin.site.register(Course, CourseAdmin)





    
