from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import RedirectResponse
from core.data_sanitizer import sanitize
from core.deps import remove_auth
from core.mongo_client import DocDBConnection, get_connection
from viewmodel.PersonViewModel import PersonViewModel
from viewmodel.AuthViewModel import AuthViewModel

router = APIRouter()


@router.get("/person-info/{cpf}")
def person_info(request: Request,
                person_id: str,
                connection: DocDBConnection = Depends(get_connection)):
    vm = PersonViewModel(request, connection)
    person = vm.retrieve_person(person_id)

    return vm.build_response('Pessoa encontrada com sucesso', content=sanitize(person, [], exclude=['password']))


@router.post('/signup')
async def insert_person(request: Request,
                        person: dict,
                        connection: DocDBConnection = Depends(get_connection)):
    try:
        vm = PersonViewModel(request, connection)
        saved = vm.insert_person(person)

        if saved:
            return vm.build_response('Cadastro realizado com sucesso')

    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))