import logging

from django.conf import settings
from django_cognito_jwt.backend import JSONWebTokenAuthentication
from django_cognito_jwt.validator import TokenValidator

from .validator import CustomTokenValidator

logger = logging.getLogger(__name__)


class CustomJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    """Token based authentication using the JSON Web Token standard."""

    def get_token_validator(self, request):
        # Required to manage two auth flows
        if request.headers.get("Vendor"):
            return TokenValidator(
                settings.COGNITO_AWS_REGION,
                settings.COGNITO_USER_POOL,
                settings.COGNITO_AUDIENCE,
            )
        else:
            return CustomTokenValidator(
                settings.COGNITO_AWS_REGION,
                settings.COGNITO_USER_POOL,
                settings.COGNITO_AUDIENCE,
            )
