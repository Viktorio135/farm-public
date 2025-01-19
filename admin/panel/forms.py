from django import forms
from .models import Folder, FolderUser

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']

class FolderUserForm(forms.ModelForm):
    class Meta:
        model = FolderUser
        fields = ['user']



