from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String

# Настройка базы данных
DATABASE_URL = "postgresql+asyncpg://user:password@db:5432/mydatabase"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# Модель данных
class UserModel(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, unique=True, index=True)
    full_name = Column(String)

# Инициализация таблиц
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Зависимость для получения сессии
async def get_db():
    async with async_session() as session:
        yield session

# FastAPI приложение
app = FastAPI()

class User(BaseModel):
    email: str
    full_name: str

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.post("/users/")
async def create_user(user: User, db: AsyncSession = Depends(get_db)):
    existing_user = await db.get(UserModel, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = UserModel(email=user.email, full_name=user.full_name)
    db.add(new_user)
    await db.commit()
    return {"message": "User created successfully"}

@app.get("/users/{email}")
async def get_user(email: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(UserModel, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"email": user.email, "full_name": user.full_name}

from sqlalchemy.sql import text

@app.get("/users/")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT * FROM users"))
        users = result.fetchall()
        if not users:
            return {"message": "No users found"}
        return [{"email": user.email, "full_name": user.full_name} for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

