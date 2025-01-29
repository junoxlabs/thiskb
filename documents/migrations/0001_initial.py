# Generated by Django 5.1.5 on 2025-01-28 22:14

import django.contrib.postgres.indexes
import django.db.models.deletion
import pgvector.django.indexes
import pgvector.django.vector
import uuid_utils.compat
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('knowledge_bases', '0001_initial'),
        ('tenants', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.UUIDField(default=uuid_utils.compat.uuid7, editable=False, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('content_type', models.TextField()),
                ('file_size', models.BigIntegerField()),
                ('metadata', models.JSONField()),
                ('total_chunks', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('kb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='knowledge_bases.knowledgebase')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='Chunk',
            fields=[
                ('id', models.UUIDField(default=uuid_utils.compat.uuid7, editable=False, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('embedding', pgvector.django.vector.VectorField(dimensions=1536)),
                ('chunk_number', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('kb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='knowledge_bases.knowledgebase')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.tenant')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.document')),
            ],
        ),
        migrations.RunSQL(
            """
                CREATE INDEX chunks_search_idx ON documents_chunk
                USING bm25 (id, content, kb_id)
                WITH (
                    key_field='id',
                    text_fields='{
                        "content": {"record": "freq"}
                    }'
                );
            """
        ),
        migrations.AddIndex(
            model_name='document',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='documents_d_metadat_49c69d_gin'),
        ),
        migrations.AddIndex(
            model_name='chunk',
            index=pgvector.django.indexes.HnswIndex(ef_construction=64, fields=['embedding'], m=16, name='chunks_embedding_idx', opclasses=['vector_cosine_ops']),
        ),
    ]
