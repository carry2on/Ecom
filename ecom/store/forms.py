from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from .models import Profile

class UserInfoForm(forms.ModelForm):
    phone = forms.CharField(label='',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Phone'}),required=False)
    address1 = forms.CharField(label='',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Address 1'}),required=False)
    address2 = forms.CharField(label='',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Address 2'}),required=False)
    city = forms.CharField(label='',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'City'}),required=False)
    state = forms.CharField(label='',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'State'}),required=False)
    zipcode = forms.CharField(label='',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Zipcode'}),required=False)
    country = forms.CharField(label='',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Country'}),required=False)

    class Meta:
        model = Profile
        fields = ('phone', 'address1', 'address2', 'city', 'state', 'zipcode', 'country')

class UpdateUserform(forms.ModelForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),required=False)
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),required=False)
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),required=False)
    username = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'User Name'}),required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("The new passwords do not match!")
        return cleaned_data

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','password1','password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm,self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class':'form-control', 'placeholder':'User Name'})
        self.fields['username'].label=''
        self.fields['password1'].widget.attrs.update({'class':'form-control', 'placeholder':'Password'})
        self.fields['password1'].label=''
        self.fields['password2'].widget.attrs.update({'class':'form-control', 'placeholder':'Confirm Password'})
        self.fields['password2'].label=''

class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control', 'required': 'required'})