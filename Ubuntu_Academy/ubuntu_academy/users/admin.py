from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture', 'country')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'country')
    list_filter = ('country', 'user__first_name')

    fieldsets = (
        (None, {
            'fields': ('user', 'profile_picture', 'bio', 'country'),
        }),
    )

# Define Profile Inline for inline editing of the Profile in the User admin
class ProfileInline(admin.TabularInline):
    model = Profile
    fields = ('profile_picture', 'bio', 'country')
    extra = 0  # No extra empty fields for new profiles
    readonly_fields = ('profile_picture', 'bio', 'country')
    


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields to be displayed in the list view
    list_display = ('email', 'get_fullname', 'slug', 'is_active', 'is_staff', 'date_joined', 'updated_at', 'last_login')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'date_joined', 'updated_at')
    ordering = ('-date_joined',)

    # Fields to be displayed in the detail view (edit page)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'slug', 'get_fullname')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('date_joined', 'updated_at')}),
    )

    # Customize the form for adding and editing
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'is_staff'),
        }),
    )

    # Readonly fields
    readonly_fields = ('date_joined', 'updated_at', 'get_fullname', 'slug')

    # Add Profile Inline for user details
    inlines = [ProfileInline]

    # Custom method to display full name properly
    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name and obj.last_name else obj.email
    get_fullname.admin_order_field = 'first_name'
    get_fullname.short_description = _('Full Name')

    # Custom actions to bulk activate/deactivate users
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = _("Activate selected users")

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = _("Deactivate selected users")
