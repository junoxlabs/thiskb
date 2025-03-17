from django.db import models
import uuid_utils.compat as uuid
from django.contrib.postgres.indexes import GinIndex
from pgvector.django import VectorField, HnswIndex


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)
    kb = models.ForeignKey("knowledge_bases.KnowledgeBase", on_delete=models.CASCADE)
    name = models.TextField(null=False)
    content_type = models.TextField(null=False)
    file_size = models.BigIntegerField()
    metadata = models.JSONField()
    total_chunks = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [GinIndex(fields=["metadata"])]


class Chunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    kb = models.ForeignKey("knowledge_bases.KnowledgeBase", on_delete=models.CASCADE)
    content = models.TextField(null=False)
    embedding = VectorField(null=False, dimensions=1536)
    chunk_number = models.IntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chunk {self.chunk_number} of Document {self.document.name}"

    class Meta:
        indexes = [
            HnswIndex(
                name="chunks_embedding_idx",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
        ]
