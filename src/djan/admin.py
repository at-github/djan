from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import path
from djan.models import Redirection
from djan.two_factor import OptionalOTPAdminAuthenticationForm, two_factor_view


def short_url_with_copy_button(url):
    return format_html(
        '<a href="{url}" target="_blank" rel="noopener">{url}</a> '
        '<button type="button" class="button" data-url="{url}" '
        'onclick="navigator.clipboard.writeText(this.dataset.url)">{label}</button>',
        url=url,
        label=_("Copy"),
    )


@admin.register(Redirection)
class RedirectionAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "site",
                    "short_url",
                    "full_short_url",
                    "destination_url",
                    "http_status",
                )
            },
        ),
        (_("Parameters"), {"fields": ("params_mode", "unique_counter_mode")}),
        (_("Statistics"), {"fields": ("counter", "unique_counter")}),
    )

    list_display = ("short_url", "site", "destination_url", "http_status")
    readonly_fields = ("full_short_url", "counter", "unique_counter")
    search_fields = ("short_url", "destination_url")

    @admin.display(description=_("Full short URL"))
    def full_short_url(self, obj):
        if obj is None or obj.pk is None:
            return self.get_empty_value_display()
        return short_url_with_copy_button(obj.get_full_short_url())

    def response_add(self, request, obj, post_url_continue=None):
        self.message_user(
            request,
            format_html(
                "{} {}",
                _("Short URL created:"),
                short_url_with_copy_button(obj.get_full_short_url()),
            ),
            messages.SUCCESS,
        )
        return super().response_add(request, obj, post_url_continue)


# Double authentification optionnelle
admin.site.login_form = OptionalOTPAdminAuthenticationForm
admin.site.login_template = "admin/login_otp.html"
_admin_get_urls = admin.site.get_urls
admin.site.get_urls = (
    lambda: [
        path("2fa/", admin.site.admin_view(two_factor_view), name="two_factor"),
    ]
    + _admin_get_urls()
)
