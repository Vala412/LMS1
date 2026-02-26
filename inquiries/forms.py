from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your name'})
    )
    email = forms.EmailField(
        widget= forms.EmailInput(attrs={'placeholder': 'Enter your email'})
    )
    subject = forms.CharField(max_length=100)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter your message here'})
    )
    file = forms.FileField(required=False)

    def clean_name(self):
        name = self.cleaned_data['name']
        if name and len(name) < 3:
            raise forms.ValidationError('Name must contain at least 3 characters')
        
        if not name.replace(' ', '').isalpha():
            raise forms.ValidationError("Name must contain letters and spaces")
        return name
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if email.strip() == ''.strip():
            self.add_error('email', 'Email is required')
            raise forms.ValidationError("Email is required")
        else:
            first, sec = str(email).split('@')
        # raise forms.ValidationError('Email error')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        message = cleaned_data.get('message')

        if subject and message:
            if subject.lower() in message.lower():
                raise forms.ValidationError("Subject and message should not be the same")

        return cleaned_data