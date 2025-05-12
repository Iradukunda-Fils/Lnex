from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    """Profile model linked to User for extended attributes."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True, help_text="Short bio about the user.")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True, help_text="User's address.")
    social_links = models.JSONField(
        blank=True, null=True,
        help_text="Social media links, e.g., {'twitter': 'url', 'linkedin': 'url'}"
    )
    website = models.URLField(blank=True, null=True, help_text="Personal or professional website URL.")
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Profile"

