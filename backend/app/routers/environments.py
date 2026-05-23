"""Environments Router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.environment import Environment
from app.schemas.environment import EnvironmentCreate, EnvironmentResponse

router = APIRouter()


@router.get("/", response_model=List[EnvironmentResponse])
async def list_environments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Environment).order_by(Environment.created_at))
    return result.scalars().all()


@router.post("/", response_model=EnvironmentResponse, status_code=status.HTTP_201_CREATED)
async def create_environment(data: EnvironmentCreate, db: AsyncSession = Depends(get_db)):
    env = Environment(**data.model_dump())
    db.add(env)
    await db.commit()
    await db.refresh(env)
    return env


@router.get("/{env_id}", response_model=EnvironmentResponse)
async def get_environment(env_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    env = result.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    return env


@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_environment(env_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Environment).where(Environment.id == env_id))
    env = result.scalar_one_or_none()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    await db.delete(env)
    await db.commit()
