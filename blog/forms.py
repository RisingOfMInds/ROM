from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone = forms.CharField(max_length=12, required=True)
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        help_text='Write here your message!',
        required=True
    )

    def clean(self):
        cleaned_data = super(ContactForm, self).clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        message = cleaned_data.get('message')
        phone = cleaned_data.get('phone')
        if not name and not email and not message and not phone:
            raise forms.ValidationError('You have to write something!')
