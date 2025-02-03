from django import forms
from django.apps import apps

class PostForm(forms.ModelForm):
    class Meta:
        model = apps.get_model('news', 'Post')
        field = ['title', 'text', 'author']