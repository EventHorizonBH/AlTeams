from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")


class User(BaseModel):
    name: str
    surname: str
    birthdate: str
    email: str
    address: str
    disabled: bool

class UserDB(User):
    password: str

users_db = {
    "Vert" : {
        "name": "Vert",
        "surname": "Cognom",
        "birthdate": "19/01/2001",
        "email": "test@test.com",
        "address": "C/ falsa 123",
        "disabled": False,
        "password": "123"
    },
    "German" : {
        "name": "German",
        "surname": "Traidor",
        "birthdate": "20/01/2001",
        "email": "test2@test.com",
        "address": "C/ falsa 234",
        "disabled": True,
        "password": "123"
    }
}

def search_user_db(name: str):
    if name in users_db:
        return UserDB(**users_db[name])
    
def search_user(name: str):
    if name in users_db:
        return User(**users_db[name])


async def current_user(token: str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="El usuario no está autorizado", 
                            headers={"WWW-Authenticate" : "Bearer"})
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="El usuario no está activo", 
                            headers={"WWW-Authenticate" : "Bearer"})
    return user

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe")
    
    user = search_user_db(form.username)
    if form.password != user.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")
    
    return {"access_token": user.name, "token_type": "bearer"}

@app.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user
