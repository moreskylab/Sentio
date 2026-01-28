from django.core.management.base import BaseCommand
from recommendations.models import Article

class Command(BaseCommand):
    help = 'Populates the database with sample articles for semantic search testing'

    def handle(self, *args, **kwargs):
        # Clear existing data to avoid duplicates
        Article.objects.all().delete()
        self.stdout.write(self.style.WARNING('Existing articles deleted.'))

        # Dataset with 4 distinct categories: Tech, Nature, Food, Finance
        sample_data = [
            # --- Category: Technology / AI ---
            {
                "title": "Introduction to Transformers in NLP",
                "content": "Transformers have revolutionized Natural Language Processing by using attention mechanisms. Models like BERT and RoBERTa allow computers to understand context better than ever before."
            },
            {
                "title": "Getting Started with Django and Python",
                "content": "Django is a high-level Python web framework that encourages rapid development and clean design. It follows the Model-View-Template architectural pattern."
            },
            {
                "title": "The Future of Vector Databases",
                "content": "Vector databases like LanceDB and Pinecone are essential for RAG applications. They allow for high-speed similarity search on high-dimensional data vectors."
            },

            # --- Category: Nature / Environment ---
            {
                "title": "The Ecosystem of the Amazon Rainforest",
                "content": "The Amazon represents over half of the planet's remaining rainforests and comprises the largest and most biodiverse tract of tropical rainforest in the world."
            },
            {
                "title": "Understanding Climate Change",
                "content": "Global warming is driving long-term shifts in temperatures and weather patterns. These shifts may be natural, but human activities have been the main driver since the 1800s."
            },
            {
                "title": "Marine Life in the Pacific Ocean",
                "content": "The Pacific Ocean contains the deepest point on Earth, the Mariana Trench. It is home to diverse species ranging from microscopic plankton to the massive blue whale."
            },

            # --- Category: Food / Cooking ---
            {
                "title": "How to Make Authentic Carbonara",
                "content": "True Roman carbonara requires only eggs, hard cheese (Pecorino Romano), cured pork (guanciale), and black pepper. No cream is added to the traditional recipe."
            },
            {
                "title": "The Art of Sourdough Bread",
                "content": "Sourdough bread is made by the fermentation of dough using naturally occurring lactobacilli and yeast. It has a more sour taste and better keeping qualities than baker's yeast bread."
            },
            {
                "title": "Spicy Tacos and Mexican Cuisine",
                "content": "Tacos are a traditional Mexican dish consisting of a small hand-sized corn or wheat tortilla topped with a filling. Common fillings include beef, pork, chicken, and vegetables."
            },

            # --- Category: Finance / Economy ---
            {
                "title": "Basics of Stock Market Investing",
                "content": "The stock market refers to the collection of markets and exchanges where regular activities of buying, selling, and issuance of shares of publicly-held companies take place."
            },
            {
                "title": "Understanding Inflation Rates",
                "content": "Inflation is a rise in the general price level of an economy over a period of time. When the general price level rises, each unit of currency buys fewer goods and services."
            },
            {
                "title": "Cryptocurrency and Blockchain",
                "content": "A cryptocurrency is a digital currency designed to work as a medium of exchange through a computer network that is not reliant on any central authority, such as a government or bank."
            }
        ]

        # Bulk Create
        articles = [Article(**item) for item in sample_data]
        Article.objects.bulk_create(articles)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(articles)} sample articles.'))