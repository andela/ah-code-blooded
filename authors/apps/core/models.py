from django.db import models


class BaseModel(models.Model):
    """
    A BaseModel has two fields, used to determine when the model was created and when the model was updated
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Set the model as abstract to prevent migrations from being created
        abstract = True

        # Will be ordered in order of models created first by default
        ordering = ['-created_at']
