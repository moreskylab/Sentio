from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Article
from .vector_db import VectorService

@receiver(post_save, sender=Article)
def sync_article_to_vector_db(sender, instance, created, **kwargs):
    """
    Triggered whenever an Article is saved.
    """
    service = VectorService()
    # We update regardless of whether it's created or updated
    # because the content (and thus the embedding) might have changed.
    service.update_article(instance)

@receiver(post_delete, sender=Article)
def remove_article_from_vector_db(sender, instance, **kwargs):
    """
    Triggered whenever an Article is deleted.
    """
    service = VectorService()
    service.delete_article(instance.id)