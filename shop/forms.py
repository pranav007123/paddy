from django import forms
from .models import Shop, Category, Plant, Complaint, Review, Booking

# Note: UserRegistrationForm and ShopRegistrationForm are removed/replaced
# because user management is handled by the main paddy app's existing logic.

class ShopProfileForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['shop_name', 'contact_number', 'email', 'address', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = ['name', 'category', 'description', 'price', 'stock', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'description', 'shop']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'shop': 'Related Shop (Optional)',
        }


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.Select())

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'service_type', 'description']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)


class OrderForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
