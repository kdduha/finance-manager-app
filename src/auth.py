import datetime

import jwt
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from src.config import cfg
from src.db import find_user
from src.errors import AuthorizationException
from src.schemas.users import User


class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"])
    secret = cfg.auth.secret

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, pwd: str, hashed_pwd: str) -> bool:
        return self.pwd_context.verify(pwd, hashed_pwd)

    def encode_token(self, email: str) -> any:
        payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=cfg.auth.ttl),
            "iat": datetime.datetime.utcnow(),
            "sub": email,
        }
        return jwt.encode(payload, self.secret, algorithm=cfg.auth.alg)

    def decode_token(self, token: str) -> any:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[cfg.auth.alg])
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise AuthorizationException(detail="Expired signature")
        except jwt.InvalidTokenError:
            raise AuthorizationException(detail="Invalid token")

    def get_current_user(self, creds: HTTPAuthorizationCredentials = Security(security)) -> User | None:
        email = self.decode_token(creds.credentials)
        if email is None:
            raise AuthorizationException(detail="Could not validate credentials")

        user = find_user(email)
        if user is None:
            raise AuthorizationException(detail="User is not found")

        return user


auth = AuthHandler()
