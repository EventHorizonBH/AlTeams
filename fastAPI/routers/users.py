from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/users",
                   responses={404: {"message" : "No encontrado"}},
                   tags=["users"]
                   )

class User(BaseModel):
    id: int
    name: str
    surname: str
    password: str
    birthdate: str
    email: str
    address: str

users_list = []

@router.get("/")
async def users():
    return "users"

@router.get("/{id}")
async def users(id: int):
    return users_list[id]