from django.forms import ModelForm
from auctions.models import Listing, Bid, Comment
from django.core.exceptions import ValidationError
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from django_resized import ResizedImageField


class CreateListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'current_price', 'image', 'category']

    def clean(self):
        cleaned_data = super().clean()
        img = self.cleaned_data.get("image")
        category = self.cleaned_data.get("category")
        if not (img or category):
            raise ValidationError(
                "You must specify either an image or category")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('submit', 'Create Listing', css_class="btn-info"))


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price']
        labels = {
        "price": ""
    }

    def clean(self):
        cleaned_data = super().clean()
        price = self.cleaned_data.get("price")
        listing = self.instance.listing
        if price < listing.current_price:
            listing_bids = listing.bids
            if listing_bids:
                raise ValidationError(
                    f"Bid must be greater than the current bid: {listing.current_price}"
                )
            else:
                raise ValidationError(
                    f"Bid must be at least as large as the starting bid: {listing.current_price}"
                )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['price'].widget.attrs['placeholder'] = 'Bid'
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('submit', 'Place Bid', css_class="btn-info"))


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
        "text": ""
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['placeholder'] = 'Write a comment...'
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('submit', 'Add Comment', css_class="btn-info"))
