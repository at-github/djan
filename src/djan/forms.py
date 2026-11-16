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
        changed = [param for param in UTM_PARAMS if param in self.changed_data]
        if not url or not changed:
            return cleaned_data

        parsed = urlparse(url)
        query = QueryDict(parsed.query, mutable=True)
        for param in changed:
            if cleaned_data[param]:
                query[param] = cleaned_data[param]
            else:
                query.pop(param, None)
        url = urlunparse(parsed._replace(query=query.urlencode()))

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
