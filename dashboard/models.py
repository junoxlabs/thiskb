from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class UserDashboard(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="dashboard"
    )
    bio = models.TextField(max_length=500, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s dashboard"


@receiver(post_save, sender=User)
def create_user_dashboard(sender, instance, created, **kwargs):
    if created:
        UserDashboard.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_dashboard(sender, instance, **kwargs):
    instance.dashboard.save()
