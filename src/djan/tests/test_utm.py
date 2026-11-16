import pytest
from django.urls import reverse

from djan.models import Redirection

pytestmark = pytest.mark.django_db


def form_data(**overrides):
    return {
        "site": 1,
        "short_url": "abc",
        "destination_url": "https://www.example.org/page?a=1",
        "http_status": 302,
        "params_mode": "DEFAULT",
        "unique_counter_mode": "SSID",
        **overrides,
    }


def test_add_redirection_with_utm_fields(admin_client):
    admin_client.post(
        reverse("admin:djan_redirection_add"),
        data=form_data(utm_campaign="rentree", utm_source="twitter", utm_medium=""),
    )

    assert (
        Redirection.objects.get(short_url="abc").destination_url
        == "https://www.example.org/page?a=1&utm_campaign=rentree&utm_source=twitter"
    )


def test_add_redirection_without_utm_fields_keeps_url(admin_client):
    admin_client.post(
        reverse("admin:djan_redirection_add"),
        data=form_data(destination_url="https://www.example.org/?utm_source=mail"),
    )

    assert (
        Redirection.objects.get(short_url="abc").destination_url
        == "https://www.example.org/?utm_source=mail"
    )


def test_change_form_prefills_utm_fields(admin_client):
    redirection = Redirection.objects.create(
        site_id=1,
        short_url="abc",
        destination_url="https://www.example.org/?utm_source=mail",
    )

    res = admin_client.get(
        reverse("admin:djan_redirection_change", args=[redirection.pk])
    )

    assert res.context["adminform"].form["utm_source"].value() == "mail"


def test_change_redirection_utm_fields(admin_client):
    redirection = Redirection.objects.create(
        site_id=1,
        short_url="abc",
        destination_url="https://www.example.org/?utm_source=mail&utm_medium=email",
    )

    admin_client.post(
        reverse("admin:djan_redirection_change", args=[redirection.pk]),
        data=form_data(
            destination_url=redirection.destination_url,
            utm_source="",
            utm_medium="email",
            utm_content="bouton",
        ),
    )

    redirection.refresh_from_db()
    assert (
        redirection.destination_url
        == "https://www.example.org/?utm_medium=email&utm_content=bouton"
    )


def test_change_destination_url_without_touching_utm_fields(admin_client):
    redirection = Redirection.objects.create(
        site_id=1,
        short_url="abc",
        destination_url="https://www.example.org/?utm_source=mail",
    )

    admin_client.post(
        reverse("admin:djan_redirection_change", args=[redirection.pk]),
        data=form_data(
            destination_url="https://www.example.org/?utm_source=sms",
            utm_source="mail",
        ),
    )

    redirection.refresh_from_db()
    assert redirection.destination_url == "https://www.example.org/?utm_source=sms"
