from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import UserManager as _UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from customers.models import Customer
from vendors.models import Vendor

import logging
import tldextract

logger = logging.getLogger(__name__)


class UserManager(_UserManager):
    def get_or_create_for_cognito(self, payload):
        # username = payload["cognito:username"]
        # groups = payload["cognito:groups"]
        # email = payload.get("email", "")
        # phone_number = payload.get("phone_number", "")

        # try:
        #     user = self.get(username=username)
        #     logger.debug(user.phone_number)
        #     if user.email != email and email != "":
        #         user.email = email
        #         user.save()
        #     if user.phone_number != phone_number and phone_number != "":
        #         user.phone_number = phone_number
        #         user.save()
        # except self.model.DoesNotExist:
        #     user = self.create(
        #         username=username,
        #         email=email,
        #         phone_number=phone_number,
        #         is_active=True,
        #     )

        # vendor_url = payload["vendor_url"]

        # if "customers" in groups:
        #     try:
        #         customer = Customer.objects.create(user=user)
        #     except IntegrityError:
        #         customer = Customer.objects.get(user=user)

        #     vendor_domain = tldextract.extract(vendor_url).domain
        #     try:
        #         vendor = Vendor.objects.get(url__contains=vendor_domain)
        #         customer.vendors.add(vendor)
        #         customer.save()
        #     except Vendor.DoesNotExist:
        #         logger.warning(f"Vendor with url {vendor_url} does not exist")

        # elif "vendors" in groups:
        #     try:
        #         Vendor.objects.create(user_id=user.id, name=vendor_url, url=vendor_url)
        #     except IntegrityError:
        #         pass

        user = User.objects.all().first()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), blank=True)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "username"

    def perform_create(self, serializer):
        user = self.request.user
        user = self.request.user

        vendor = Vendor.objects.get(user=user.id)
        serializer.save(vendor=vendor)
