from core.mongo_client import get_connection, DocumentDBClient, DBConfig
from starlette.requests import Request
from starlette.responses import JSONResponse


class BaseViewModel:
    def __init__(self, request):
        self.request: Request = request

    @staticmethod
    def validate_fields(body, mandatory_fields):
        missing_fields = [field for field in mandatory_fields if field not in body.keys()]
        if len(missing_fields) > 0:
            raise Exception(f'Missing field(s): {str(missing_fields)}')

    @staticmethod
    def build_response(message, content=None):
        response = {'message': message}

        if content:
            response.update({'content': content})

        return JSONResponse(response)

    @staticmethod
    def db_connection(table, connection, pagination=None):
        collection_name = table
        return DocumentDBClient(connection, collection_name, max_pagination_size=pagination)