from django.db import models
from pgvector.django import VectorField


class Chunk(models.Model):
    content = models.TextField()
    source = models.CharField(max_length=255)
    embedding = VectorField(dimensions=1536)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source}: {self.content[:40]}"
