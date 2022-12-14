from django.forms import ModelForm
from auctions.models import Listing
from django.core.exceptions import ValidationError
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from django_resized import ResizedImageField

class CreateListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title','description','current_price','image','category']

    def clean(self):
        cleaned_data = super().clean()
        img = self.cleaned_data.get("image")
        category = self.cleaned_data.get("category")
        print(self.cleaned_data)
        if not (img or category):
            raise ValidationError("You must specify either an image or category")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create Listing', css_class="btn-info"))