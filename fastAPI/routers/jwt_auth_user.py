from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1

SECRET = "6cf75f1e9ea5c74c3f028c66e7b81d26ac78625f935be92757689b688fc8839a"

app = FastAPI()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

class User(BaseModel):
    name: str
    surname: str
    birthdate: str
    email: str
    address: str
    disabled: bool

class UserDB(User):
    password: str

def search_user_db(email: str):
    if email in users_db:
        return UserDB(**users_db[email])

def search_user(email: str):
    if email in users_db:
        return User(**users_db[email])

async def auth_user(token: str = Depends(oauth2)):
    
    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="El usuario no está autorizado", 
                            headers={"WWW-Authenticate" : "Bearer"})
    
    try:
        email = jwt.decode(token, SECRET,algorithms=ALGORITHM).get("sub")
        if email is None:
            raise exception
    except JWTError:
        raise exception
    
    return search_user(email)


    

async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="El usuario no está activo", 
                            headers={"WWW-Authenticate" : "Bearer"})
    return user

users_db = {
    "test@test.com" : {
        "name": "Vert",
        "surname": "Apellido",
        "birthdate": "19/01/2001",
        "email": "test@test.com",
        "address": "C/ falsa 123",
        "disabled": False,
        "password": "$2a$12$IWJqETVqFmrPHJR/qk.zD.Jp9MooQSxkyl3i1uGAO0yQlCdvTHYkK"
    },
    "test2@test.com" : {
        "name": "German",
        "surname": "Traidor",
        "birthdate": "20/01/2001",
        "email": "test2@test.com",
        "address": "C/ falsa 234",
        "disabled": True,
        "password": "$2a$12$IWJqETVqFmrPHJR/qk.zD.Jp9MooQSxkyl3i1uGAO0yQlCdvTHYkK"
    }
}

@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe")
    
    user = search_user_db(form.username)
    
    
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contraseña no es correcta")
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)
    
    access_token = {"sub":user.email, 
                    "exp":expire,
                    }
    
    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@app.get("/users/me")
async def me(user: User = Depends(current_user)):
    return user

