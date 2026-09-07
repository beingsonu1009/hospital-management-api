# Is file mein hum later database session infrastructure rakhenge:
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
# create_async_engine SQLAlchemy ka function hai jo:
# setup karne ke liye use hoga.
from sqlalchemy import text
import os
from dotenv import load_dotenv



load_dotenv()

# load_dotenv() → .env ko load karega
# os.getenv() → environment variable read karega
# DATABASE_URL → PostgreSQL connection information provide karega
# load_dotenv() .env file ko read karke uske variables ko environment mein load karta hai.

DATABASE_URL = os.getenv("DATABASE_URL")       
# Environment se DATABASE_URL ki value read karo.

engine = create_async_engine(DATABASE_URL)
# engine ko database ke saath asynchronous connections manage karne ke liye use karenge.


SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

 













async def test_session():
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        print(result.scalar())