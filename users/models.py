from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid_utils.compat as uuid
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Model for users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    tenants = models.ManyToManyField('tenants.Tenant', through="UserTenantMembership")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class UserTenantMembership(models.Model):
    class Roles(models.TextChoices):
        ADMIN = 'admin', _('Admin')
        EDITOR = 'editor', _('Editor')
        CONTRIBUTOR = 'contributor', _('Contributor')
        VIEWER = 'viewer', _('Viewer')
        ANALYST = 'analyst', _('Analyst')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    role = models.CharField(
        max_length=255,
        choices=Roles.choices,
        default=Roles.EDITOR,
    )

    class Meta:
        unique_together = ('user', 'tenant')


# class ApiKey(models.Model):
#     """
#     Model for API keys.
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
#     name = models.TextField(default="default", null=False)
#     tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     key = models.TextField(unique=True, null=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.key

