import pytest
from django.urls import reverse

from djan.models import Redirection

pytestmark = pytest.mark.django_db

COPY_BUTTON = 'data-url="https://example.com/abc"'


def test_add_redirection_displays_full_short_url(admin_client):
    res = admin_client.post(
        reverse("admin:djan_redirection_add"),
        data={
            "site": 1,
            "short_url": "abc",
            "destination_url": "https://www.example.org/",
            "http_status": 302,
            "params_mode": "DEFAULT",
            "unique_counter_mode": "SSID",
        },
        follow=True,
    )

    assert res.status_code == 200
    assert Redirection.objects.filter(short_url="abc").exists()
    assert COPY_BUTTON in res.content.decode()


def test_change_redirection_displays_full_short_url(admin_client):
    redirection = Redirection.objects.create(
        site_id=1, short_url="abc", destination_url="https://www.example.org/"
    )

    res = admin_client.get(
        reverse("admin:djan_redirection_change", args=[redirection.pk])
    )

    assert COPY_BUTTON in res.content.decode()


def test_add_form_renders_without_short_url(admin_client):
    res = admin_client.get(reverse("admin:djan_redirection_add"))

    assert res.status_code == 200
