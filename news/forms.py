import pytz
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text", "categories"]
        widgets = {
            "categories": forms.CheckboxSelectMultiple,  # 👈 чекбоксы вместо списка
        }


class TimezoneForm(forms.Form):
    timezone = forms.ChoiceField(
        label=_("Выберите часовой пояс"),
        choices=[(tz, tz) for tz in pytz.common_timezones],
        initial="UTC",
    )
