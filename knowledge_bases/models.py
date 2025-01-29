from django.db import models
import uuid_utils.compat as uuid

class KnowledgeBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.TextField(null=False)
    description = models.TextField()
    metadata = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
