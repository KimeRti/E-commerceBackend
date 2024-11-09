from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from src.settings import config

from src.complaint.models import Complaint


async def init_mongo_db():
    client = AsyncIOMotorClient(config.mongo_uri)
    await init_beanie(database=client[config.mongo_db],
                      document_models=[Complaint])
    print("mongo db created.")
