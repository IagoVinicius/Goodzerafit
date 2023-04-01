import uvicorn as uvicorn
from fastapi import FastAPI
from views import login, person


api = FastAPI()

api.include_router(login.router, prefix='/api')
api.include_router(person.router, prefix='/api')

if __name__ == "__main__":
    uvicorn.run(api, host="127.0.0.1", port=8000)
