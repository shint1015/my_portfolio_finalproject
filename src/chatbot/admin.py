from django.contrib import admin

from chatbot.models import Chunk


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ("source", "created_at")
    search_fields = ("source", "content")

# Register your models here.
