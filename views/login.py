from datetime import datetime

from fastapi import APIRouter, status, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from starlette.requests import Request
from starlette.responses import RedirectResponse

from core.mongo_client import DocDBConnection, get_connection
from core.deps import remove_auth
from viewmodel.PersonViewModel import PersonViewModel
from viewmodel.AuthViewModel import AuthViewModel

# from schemas.person_schema import PersonSchemasBase, PersonSchemaCreate

router = APIRouter()


@router.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url='/login', status_code=status.HTTP_302_FOUND)
    remove_auth(response)

    return response


@router.post('/login', status_code=status.HTTP_200_OK)
async def login_empregador(request: Request,
                           form_data: OAuth2PasswordRequestForm = Depends(),
                           connection: DocDBConnection = Depends(get_connection)):
    vm = AuthViewModel(request, connection)
    person = vm.autenticar(form_data.username, form_data.password)

    if not person:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User or Password is incorrect")

    return JSONResponse(content={"access_token": vm.criar_token_acesso(sub=person.get('_id')), "token_type": "Bearer"})

# @router.get('/logado', response_model=PersonSchemasBase)
# def get_logado(person_logado: PersonModel = Depends(get_current_user)):
#     return person_logado
