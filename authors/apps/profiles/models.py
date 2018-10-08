from django.db import models
from authors.settings import AUTH_USER_MODEL
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    """
    This model creates a user profile with bio and
    image field once a user creates an account.
    """
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(default="Update your bio description")
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def image_url(self):
        """
        Get the image url. This spits a url that resolves to the image.
        """
        return self.image.url

    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return self.user.username
