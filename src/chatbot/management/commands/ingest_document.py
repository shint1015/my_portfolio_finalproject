from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from chatbot.infrastructure.embeddings.openai_embedder import OpenAIEmbedder
from chatbot.models import Chunk


def chunk_text(text: str, max_chars: int = 1000) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for paragraph in paragraphs:
        if current_len + len(paragraph) + 1 > max_chars and current:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(paragraph)
        current_len += len(paragraph) + 1

    if current:
        chunks.append("\n".join(current))

    return chunks


class Command(BaseCommand):
    help = "Ingest a text document into the vector store."

    def add_arguments(self, parser):
        parser.add_argument("path", type=str, help="Path to a text file.")
        parser.add_argument("--source", type=str, default=None, help="Source label.")
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing chunks before ingesting.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        source = options["source"] or path.name
        text = path.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        if not chunks:
            raise CommandError("No content to ingest.")

        embedder = OpenAIEmbedder()

        with transaction.atomic():
            if options["clear"]:
                Chunk.objects.all().delete()

            objects = []
            for chunk in chunks:
                embedding = embedder.embed(chunk)
                objects.append(
                    Chunk(
                        content=chunk,
                        source=source,
                        embedding=embedding,
                    )
                )

            Chunk.objects.bulk_create(objects)

        self.stdout.write(self.style.SUCCESS(f"Ingested {len(objects)} chunks."))
