from core.configs import settings
from viewmodel.BaseViewModel import BaseViewModel
from viewmodel._AuthDecorators import need_jwt
from core.data_sanitizer import sanitize
from decouple import config
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from pytz import timezone

CRIPTO = CryptContext(schemes=['bcrypt'], deprecated='auto')
JWT_SECRET: str = config('JWT_SECRET')
ALGORITHM: str = config('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7


class AuthViewModel(BaseViewModel):
    def __init__(self, request, connection, pagination=None):
        super().__init__(request)
        self.client = self.db_connection('person', connection, pagination)

    @staticmethod
    def _criar_token(tipo_token: str, tempo_vida: timedelta, sub: str) -> str:
        payload = {}

        sp = timezone('America/Sao_Paulo')
        expira = datetime.now(tz=sp) + tempo_vida

        payload["type"] = tipo_token
        payload["exp"] = expira
        payload["iat"] = datetime.now(tz=sp)
        payload["sub"] = str(sub)

        return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

    def verificar_senha(self, senha: str, hash_senha: str) -> bool:
        return CRIPTO.verify(senha, hash_senha)

    def decode_senha(self, senha: str) -> str:
        pass

    def autenticar(self, cpf: str, password: str):
        query = {'cpf': cpf}

        person = self.client.find_one(query)

        if not person:
            return None

        if not self.verificar_senha(password, person.get('password')):
            return None

        return person

    def criar_token_acesso(self, sub: str) -> str:
        return self._criar_token(
            tipo_token='access_token',
            tempo_vida=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            sub=sub
        )
