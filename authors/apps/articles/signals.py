from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from authors.apps.ah_notifications.notifications import Verbs
from authors.apps.core.mail_sender import send_email
from notifications.signals import notify

from authors.apps.articles.models import Article

@receiver(post_save, sender=Article)
def send_create_article_notification_to_followers(sender, instance, created, **kwargs):
    followers = instance.author.profile.followers()

    for follower in followers:
        if follower.user.is_subscribed:
            data = {
                'username': follower.user.username,
                'article_title': instance.title,
                'author': instance.author.username
            }
            send_email(
                template='article_created.html',
                data=data,
                to_email=follower.user.email,
                subject='You have a new notification',
            )
        notify.send(instance, verb=Verbs.ARTICLE_CREATION, recipient=follower.user, 
                    description="An article by an author you follow has been created")


