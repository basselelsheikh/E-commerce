from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.conf import settings
from django_resized import ResizedImageField


class Listing(models.Model):
    lister = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=80)
    description = models.TextField()
    current_price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(
         upload_to='images/', default=None, null=True, blank=True)
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True, blank=True)

    class Status(models.TextChoices):
        ACTIVE = 'a'
        CLOSED = 'c'
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.ACTIVE, help_text="Listing Status")

    @property
    def dollar_amount(self):
        
        return "$%s" % self.current_price if self.current_price else ""

    def get_absolute_url(self):
        # adjust model detail view
        
        return reverse('listing-detail', args=[str(self.id)])

    def __str__(self) -> str:
        return self.title


class Bid(models.Model):
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids")
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def get_absolute_url(self):
        # adjust model detail view
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self) -> str:
        return self.price


class Comment(models.Model):
    commenter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()

    def get_absolute_url(self):
        # adjust model detail view
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self) -> str:
        return f"{self.commenter} commented on {self.listing}"


class Category(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "categories"

    def get_absolute_url(self):
        # adjust model detail view
        return reverse('model-detail-view', args=[str(self.id)])

    def __str__(self) -> str:
        return self.name
