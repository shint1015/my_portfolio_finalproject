from django.db import migrations, models
import pgvector.django


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Chunk",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField()),
                ("source", models.CharField(max_length=255)),
                ("embedding", pgvector.django.VectorField(dimensions=1536)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
