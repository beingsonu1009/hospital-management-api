from app.db.session import SessionLocal

async def get_db():
    async with SessionLocal() as session:      #Reason: Database session ko safely open aur close karna hai.
        yield session                          #Reason: FastAPI ko current database session provide karna hai.