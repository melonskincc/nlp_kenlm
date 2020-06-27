import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from document.models import Document


@receiver(post_delete, sender=Document)
def delete_document(sender, instance, **kwargs):
    try:
        os.remove(instance.success_url)
    except:
        pass
