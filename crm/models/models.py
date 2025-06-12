from django.db import models
# from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from prose.fields import RichTextField


class Client(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    secondary_phone = models.CharField(max_length=20, blank=True, null=True)
    other_phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    notes = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # address fields
    street_address = models.CharField(max_length=100, blank=True, null=True)
    street_address_2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    zip_code = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['first_name', 'last_name']


class Policy(models.Model):
    POLICY_TYPES = [
        ('life', 'Life Insurance'),
        ('auto', 'Auto Insurance'),
        ('home', 'Home Insurance'),
        ('health', 'Health Insurance'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='policies')
    policy_number = models.CharField(max_length=100, unique=True)
    policy_type = models.CharField(max_length=50, choices=POLICY_TYPES, null=True, blank=True)
    provider = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.policy_number


class Task(models.Model):
    ACTIVITY_TYPES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    subject = models.CharField(max_length=255)
    description = RichTextField()
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='activities')
    due_date = models.DateField(blank=True, null=True)
    completed_date = models.DateField(blank=True, null=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='clients', blank=True, null=True)
    policy = models.ForeignKey(Policy, on_delete=models.DO_NOTHING, related_name='policies', blank=True, null=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.subject

    def get_fieldsets(self):
        """Returns a dictionary of fieldsets for this task."""
        return [
            {
                "title": "Task Details",
                "fields": [
                    [
                        {"label": "Subject", "field": self.subject},
                        {"label": "Assigned to", "field": self.assigned_to}
                    ],
                    [
                        {"label": "Customer", "field": self.client},
                        {"label": "Due date", "field": self.due_date}
                    ],
                    {"label": "Description", "field": self.description},
                ],
            },
            {
                "title": "Additional Details",
                "fields": [
                    [
                        {"label": "Priority", "field": self.priority},
                        {"label": "Status", "field": self.status}
                    ],
                    {"label": "Activity Type", "field": self.activity_type},
                ]
            }
        ]

    class Meta:
        ordering = ['-due_date']


class Notes(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='notes')
    description = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Common additional fields
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True, default='default_img.png')
    bio = models.TextField(blank=True)

    # Preferences or settings
    dark_mode_enabled = models.BooleanField(default=False)
    receive_notifications = models.BooleanField(default=True)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name}'s Profile"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()



