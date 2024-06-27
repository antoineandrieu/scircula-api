import jwt
from django_cognito_jwt.validator import TokenError, TokenValidator


class CustomTokenValidator(TokenValidator):
    def validate(self, token):
        public_key = self._get_public_key(token)
        if not public_key:
            raise TokenError("No key found for this token")

        try:
            jwt_data = jwt.decode(
                token,
                public_key,
                issuer=self.pool_url,
                algorithms=["RS256"],
            )
        except (jwt.InvalidTokenError, jwt.ExpiredSignature, jwt.DecodeError) as exc:
            print(exc)
            raise TokenError(str(exc))
        return jwt_data
