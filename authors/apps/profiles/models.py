from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
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


@receiver(post_save, sender=AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    This is triggered when a user is created in order to create their profile.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    This is triggered when a user is saved in order to save their profile.
    """
    instance.profile.save()
