from django.db import models
import uuid_utils.compat as uuid
from django.contrib.postgres.indexes import GinIndex
from pgvector.django import VectorField, HnswIndex
from documents.utils import DocumentChunkingStatus


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)
    kb = models.ForeignKey("knowledge_bases.KnowledgeBase", on_delete=models.CASCADE)
    name = models.TextField(null=False)
    content_type = models.TextField(null=False)
    file_size = models.BigIntegerField()
    metadata = models.JSONField()
    chunking_status = models.CharField(
        max_length=20,
        choices=DocumentChunkingStatus.choices(),
        default=DocumentChunkingStatus.PENDING,
    )
    chunking_error = models.TextField(null=True)
    total_chunks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [GinIndex(fields=["metadata"])]


class Chunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    kb = models.ForeignKey("knowledge_bases.KnowledgeBase", on_delete=models.CASCADE)
    content = models.TextField(null=False, max_length=5000)
    embedding = VectorField(null=True, dimensions=1536)
    chunk_number = models.IntegerField(null=False, default=0)
    token_count = models.IntegerField(null=False, default=0)
    character_count = models.IntegerField(null=False, default=0)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chunk {self.chunk_number}/{self.document.total_chunks} of Document {self.document.name}"

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
