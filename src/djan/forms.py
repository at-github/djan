from urllib.parse import urlparse, urlunparse

from django import forms
from django.http import QueryDict
from django.utils.translation import gettext_lazy as _

from djan.models import Redirection

UTM_PARAMS = ("utm_campaign", "utm_source", "utm_medium", "utm_content")


class RedirectionAdminForm(forms.ModelForm):
    utm_campaign = forms.CharField(label="utm_campaign", required=False)
    utm_source = forms.CharField(label="utm_source", required=False)
    utm_medium = forms.CharField(label="utm_medium", required=False)
    utm_content = forms.CharField(label="utm_content", required=False)

    class Meta:
        model = Redirection
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        query = QueryDict(urlparse(self.instance.destination_url).query)
        for param in UTM_PARAMS:
            self.initial.setdefault(param, query.get(param, ""))

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get("destination_url")
        filled = {
            param: cleaned_data[param] for param in UTM_PARAMS if cleaned_data[param]
        }
        cleared = [
            param
            for param in UTM_PARAMS
            if param in self.changed_data and not cleaned_data[param]
        ]
        if not url or not (filled or cleared):
            return cleaned_data

        parsed = urlparse(url)
        query = QueryDict(parsed.query, mutable=True)
        for param in cleared:
            query.pop(param, None)
        for param, value in filled.items():
            query[param] = value
        new_url = urlunparse(parsed._replace(query=query.urlencode()))
        if QueryDict(urlparse(new_url).query) == QueryDict(parsed.query):
            return cleaned_data
        url = new_url

        max_length = Redirection._meta.get_field("destination_url").max_length
        if len(url) > max_length:
            self.add_error(
                "destination_url",
                _("The destination URL with UTM parameters exceeds %(max)d characters.")
                % {"max": max_length},
            )
        else:
            cleaned_data["destination_url"] = url
        return cleaned_data
