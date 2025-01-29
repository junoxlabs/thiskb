# Generated by Django 5.1.5 on 2025-01-28 20:04

from django.db import migrations
from django.contrib.postgres.operations import CreateExtension
from pgvector.django import VectorExtension


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        VectorExtension(),
        CreateExtension('pg_search'),
    ]
