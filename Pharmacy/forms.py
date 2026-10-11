from django import forms
from django.contrib.auth.models import User
from .models import Pharmacy


class PharmacyForm(forms.ModelForm):
    """
    ModelForm for the `Pharmacy` model.

    - Includes all fields from the model.
    - Adds Bootstrap 'form-control' styling and proper HTML5 input types.
    - Performs validation to ensure:
      * expiry_date is after manufacture_date
      * unit_price is non-negative
      * stock_available is non-negative
    """

    class Meta:
        model = Pharmacy
        fields = '__all__'
        widgets = {
            'medicine_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter medicine name'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter manufacturer name'}),
            'manufacture_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'stock_available': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0'}),
        }

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        manufacture_date = cleaned_data.get('manufacture_date')
        expiry_date = cleaned_data.get('expiry_date')
        unit_price = cleaned_data.get('unit_price')
        stock_available = cleaned_data.get('stock_available')

        # Validate expiry date comes after manufacture date
        if manufacture_date and expiry_date:
            if expiry_date <= manufacture_date:
                raise forms.ValidationError(
                    "Expiry date must be later than manufacture date."
                )

        # Validate non-negative price and stock
        if unit_price is not None and unit_price < 0:
            self.add_error('unit_price', 'Unit price must be non-negative.')

        if stock_available is not None and stock_available < 0:
            self.add_error('stock_available', 'Stock available must be non-negative.')

        return cleaned_data


class SellForm(forms.Form):
    """Simple form to perform a sale of a medicine.

    - medicine: selected via ModelChoiceField
    - quantity: integer quantity to sell
    """
    medicine = forms.ModelChoiceField(
        queryset=Pharmacy.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_medicine'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_quantity'})
    )


class UserRegistrationForm(forms.Form):
    """Form for user registration with password validation.

    - username: unique, alphanumeric, 3-150 characters
    - password: minimum 6 characters, any characters allowed
    - confirm_password: must match password for verification
    """
    username = forms.CharField(
        max_length=150,
        min_length=3,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username (3-150 characters)',
            'required': True
        }),
        help_text='3-150 characters. Letters, digits, and @/./+/-/_ allowed.'
    )

    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password (minimum 6 characters)',
            'required': True
        }),
        help_text='Minimum 6 characters.'
    )

    confirm_password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        })
    )

    def clean_username(self):
        """Validate that username is unique and doesn't already exist."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean(self):
        """Cross-field validation: check if passwords match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match. Please try again.")

        return cleaned_data