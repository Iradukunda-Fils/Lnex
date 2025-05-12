from django.core.files.storage import default_storage
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.timezone import now
from django_extensions.db.fields import AutoSlugField
from django_countries.fields import CountryField
from utils.slug_fields import UserSlug
from utils.sys_mixins.media import AutoDeleteFileMixin



class CustomUserManager(BaseUserManager):
    """Custom manager for User model with helpful methods."""
    
    def create_user(self, email: str, password: str=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError("Email field is required.")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_active") is not True:
            raise ValueError("is_active must have is_active=True.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with email-based authentication."""
    
    slug = AutoSlugField(
        populate_from=UserSlug.get_slug,
        unique=True,
        slugify_function=UserSlug.slug_method  # Custom slugify function
    )
    email = models.EmailField(unique=True)  # Index for quick lookups
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()  # Assign custom manager

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'date_joined']),  # Optimized for filtering users by activity
        ]
        ordering = ['-date_joined']  # Optimize queries that list users

    def __str__(self) -> str:
        return self.email
    
    @property
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    


class Profile(AutoDeleteFileMixin, models.Model):
    """User profile model for additional user information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to="user_profiles", default="user_profile/default.png", blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True) 
    country = CountryField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.email}"
    
    def save(self, *args, **kwargs) -> None:
        self.delete_old_file_on_change('profile_picture')
        super().save(*args, **kwargs)
        
    # def delete(self, *args, **kwargs):
    #     self.delete_file('profile_picture')
    #     super().delete(*args, **kwargs)
    
    
    def delete(self, *args, **kwargs):
        if self.profile_picture.name != "user_profile/default.png":
            self.delete_file('profile_picture')
        super().delete(*args, **kwargs)
