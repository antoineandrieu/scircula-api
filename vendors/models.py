from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models
from django.utils import timezone


class Vendor(models.Model):
    # TODO: remove user field
    user = models.OneToOneField(
        "users.User", blank=True, null=True, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=64)
    # TODO: make required
    email = models.EmailField()
    admin_url = models.CharField(max_length=200, blank=True)
    # TODO: make required
    shop_url = models.CharField(max_length=200, unique=True)
    # TODO: make required and unique
    button_url = models.URLField(blank=True)
    script_external_id = models.CharField(max_length=64, blank=True, null=True)
    scircula_plan = models.CharField(max_length=64, default="noplan")
    currency = models.CharField(max_length=3, default="EUR")
    # Brand or marketplace
    category = models.CharField(max_length=64, blank=True)
    platform = models.CharField(max_length=64)
    platform_plan = models.CharField(max_length=64, blank=True)
    shopify_access_token = models.CharField(max_length=200, blank=True, null=True)
    # Do not ask for new pricing plan
    legacy = models.BooleanField(default=False)
    shopify_subscription_id = models.CharField(max_length=200, blank=True, null=True)
    plan_chosen_at = models.DateTimeField(blank=True, null=True)
    integration_to_be_paid = models.BooleanField(default=False)
    integration_paid_at = models.DateTimeField(blank=True, null=True)
    plan_chosen_at = models.DateTimeField(blank=True, null=True)
    fmf_loaded_at = models.DateTimeField(blank=True, null=True)
    fmf_unloaded_at = models.DateTimeField(blank=True, null=True)
    uninstalled_at = models.DateTimeField(blank=True, null=True)
    last_logged = models.DateTimeField(blank=True, null=True)
    integrated_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name or ""

    def save(self, *args, **kwargs):
        if self.shopify_access_token:
            fernet = Fernet(settings.SECRET_KEY)
            self.shopify_access_token = fernet.encrypt(
                bytes(self.shopify_access_token, encoding="utf8")
            )
        super(Vendor, self).save(*args, **kwargs)

    class Meta:
        db_table = "vendor"


class Visit(models.Model):
    vendor = models.ForeignKey("Vendor", on_delete=models.DO_NOTHING)
    returning = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "visit"
