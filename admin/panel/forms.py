from django import forms
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError


from .models import Folder, FolderUser, User

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']

class FolderUserForm(forms.ModelForm):
    class Meta:
        model = FolderUser
        fields = ['user']



class ReferralForm(forms.Form):
    referrer = forms.ChoiceField(label='Пригласивший', choices=[], widget=forms.Select(attrs={'class': 'form-control'}))
    referred = forms.ChoiceField(label='Приглашенный', choices=[], widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, user_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_choices is not None:
            # Заполняем выбор пользователей в формате "username (user_id)"
            self.fields['referrer'].choices = user_choices
            self.fields['referred'].choices = user_choices

    def clean(self):
        cleaned_data = super().clean()
        referrer_id = cleaned_data.get('referrer')
        referred_id = cleaned_data.get('referred')

        # Проверяем, что пользователь не выбирает самого себя
        if referrer_id == referred_id:
            raise ValidationError("Пользователь не может пригласить самого себя.")

        return cleaned_data