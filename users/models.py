from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid_utils.compat as uuid
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    Model for users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    tenants = models.ManyToManyField("tenants.Tenant", through="UserTenantMembership")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    @property
    def default_tenant(self):
        """Get the user's explicitly marked default tenant"""
        membership = self.usertenantmembership_set.filter(is_default=True).first()
        if membership:
            return membership.tenant
        # Fallback to first admin tenant if no default is set
        return self.tenants.filter(
            usertenantmembership__user=self,
            usertenantmembership__role=UserTenantMembership.Roles.ADMIN,
        ).first()

    def get_administered_tenants(self):
        """Get all tenants where user is an admin"""
        return self.tenants.filter(
            usertenantmembership__user=self,
            usertenantmembership__role=UserTenantMembership.Roles.ADMIN,
        )

    def get_tenant_role(self, tenant):
        """Get user's role in specific tenant"""
        membership = self.usertenantmembership_set.filter(tenant=tenant).first()
        return membership.role if membership else None

    def get_accessible_tenants(self):
        """Get all tenants user has access to"""
        return self.tenants.all().order_by("name")


class UserTenantMembership(models.Model):
    class Roles(models.TextChoices):
        ADMIN = "admin", _("Admin")
        EDITOR = "editor", _("Editor")
        CONTRIBUTOR = "contributor", _("Contributor")
        VIEWER = "viewer", _("Viewer")
        ANALYST = "analyst", _("Analyst")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)
    role = models.CharField(
        max_length=255,
        choices=Roles.choices,
        default=Roles.EDITOR,
    )
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default per user
            UserTenantMembership.objects.filter(user=self.user, is_default=True).update(
                is_default=False
            )
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("user", "tenant")


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


@receiver(post_save, sender=User)
def create_default_tenant(sender, instance, created, **kwargs):
    if created:
        from tenants.models import Tenant
        from django.db import transaction
        from django.core.exceptions import ValidationError

        try:
            with transaction.atomic():
                # Sanitize organization name
                org_name = f"{instance.username}'s Organization"
                if not org_name.strip():
                    org_name = f"Organization {instance.id}"

                # Create default tenant
                default_tenant = Tenant.objects.create(name=org_name)

                # Create membership with ADMIN role
                membership = UserTenantMembership.objects.create(
                    user=instance,
                    tenant=default_tenant,
                    role=UserTenantMembership.Roles.ADMIN,
                    is_default=True,
                )

                # Validate the created objects
                default_tenant.full_clean()
                membership.full_clean()

        except ValidationError as e:
            # Handle validation errors
            raise ValidationError(f"Failed to create default tenant: {str(e)}")
        except Exception as e:
            # Handle other errors (DB errors, etc.)
            raise Exception(
                f"Error creating default tenant for user {instance.username}: {str(e)}"
            )
