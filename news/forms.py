import pytz
from django import forms
from django.apps import apps
from django.utils.translation import gettext_lazy as _


class PostForm(forms.ModelForm):
    class Meta:
        model = apps.get_model("news", "Post")
        fields = ["title", "text", "author"]


class TimezoneForm(forms.Form):
    timezone = forms.ChoiceField(
        label=_("Выберите часовой пояс"),
        choices=[(tz, tz) for tz in pytz.common_timezones],
        initial="UTC",
    )
