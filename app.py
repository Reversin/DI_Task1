from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
users = {}

class User(BaseModel):
    email: str
    full_name: str

@app.post("/users/")
async def create_user(user: User):
    if user.email in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user.email] = user.full_name
    return {"message": "User created successfully"}

@app.get("/users/{email}")
async def get_user(email: str):
    if email not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return {"email": email, "full_name": users[email]}

@app.get("/users/")
async def get_all_users():
    if not users:
        return {"message": "No users found"}
    return users