from datetime import datetime
from viewmodel.BaseViewModel import BaseViewModel
from passlib.context import CryptContext

CRIPTO = CryptContext(schemes=['bcrypt'], deprecated='auto')


class PersonViewModel(BaseViewModel):
    def __init__(self, request, connection, pagination=None):
        super().__init__(request)
        self.client = self.db_connection('person', connection, pagination)

    @staticmethod
    def gerar_hash_senha(senha: str) -> str:
        return CRIPTO.hash(senha)

    def insert_person(self, person):
        password = person.get('password')

        person.update({
            'password': self.gerar_hash_senha(password),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })

        return self.client.insert(person)

    def retrieve_person(self, person_id):
        # TODO validacao de cpf (valido e se existe no banco)
        return self.client.find_one({'cpf': person_id})
