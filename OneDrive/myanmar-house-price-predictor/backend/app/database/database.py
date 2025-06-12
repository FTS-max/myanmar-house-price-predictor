#!/usr/bin/env python3
"""
Database configuration and connection management.

Handles SQLAlchemy engine creation, session management, and database initialization.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

# Database engines
engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def create_database_engines():
    """Create database engines for sync and async operations."""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    # Sync engine for migrations
    engine = create_engine(
        settings.database_url_sync,
        poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
        echo=settings.DEBUG
    )
    
    # Async engine for application
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=StaticPool if "sqlite" in settings.DATABASE_URL else None,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
        echo=settings.DEBUG
    )
    
    # Session factories
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logger.info(f"Database engines created for: {settings.DATABASE_URL}")


async def init_database():
    """Initialize database tables."""
    if async_engine is None:
        create_database_engines()
    
    async with async_engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.database import models
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    if AsyncSessionLocal is None:
        create_database_engines()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session for migrations."""
    if SessionLocal is None:
        create_database_engines()
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def close_database():
    """Close database connections."""
    global async_engine, engine
    
    if async_engine:
        await async_engine.dispose()
        logger.info("Async database engine disposed")
    
    if engine:
        engine.dispose()
        logger.info("Sync database engine disposed")


async def check_database_health() -> bool:
    """Check database connectivity."""
    try:
        async with get_async_session() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session."""
    async with get_async_session() as session:
        yield session