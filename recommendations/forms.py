from allauth.account.forms import SignupForm
from django import forms

class CustomSignupForm(SignupForm):
    dob = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def save(self, request):
        # Save the standard user (email/password)
        user = super(CustomSignupForm, self).save(request)
        # Save our custom field
        user.dob = self.cleaned_data['dob']
        user.save()
        return user