from django.core.management.base import BaseCommand
from recommendations.models import Article
from recommendations.vector_db import VectorService


class Command(BaseCommand):
    help = 'Vectorizes Articles and stores them in LanceDB'

    def handle(self, *args, **kwargs):
        service = VectorService()
        articles = Article.objects.all()

        data_payload = []

        print(f"Processing {articles.count()} articles...")

        for article in articles:
            # Combine title and content for a richer embedding
            text_to_embed = f"{article.title}. {article.content}"
            embedding = service.get_embedding(text_to_embed)

            data_payload.append({
                "id": article.id,
                "vector": embedding,
                "title": article.title,  # Storing metadata in LanceDB is optional but fast
                "text": text_to_embed[:100]  # Store snippet for debug
            })

        if data_payload:
            service.upsert_data(data_payload)
            self.stdout.write(self.style.SUCCESS('Successfully indexed articles into LanceDB'))
        else:
            self.stdout.write(self.style.WARNING('No articles to index'))