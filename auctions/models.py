from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    """Model representing an auction listing."""
    title = models.CharField(max_length=80)
    description = models.TextField()
    current_price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='images/', default=None, null=True, blank=True)
    class Status(models.IntegerChoices):
        ACTIVE = 'a'
        CLOSED = 'c'
    status = models.IntegerField(choices=Status.choices,default='a',help_text="Listing Status")


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE,related_name="bids")
    price = models.DecimalField(max_digits=6, decimal_places=2)

